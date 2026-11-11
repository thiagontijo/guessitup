#!/usr/bin/env python3
"""Guessitup Arena: helper for data.json, the only data source of the app.

Play money only. Standard library only. Run it from the root of the gh-pages branch.

  python3 tools/arena.py add --date 2026-11-10 --bot chico --price 0.715 \\
      --leg "nba|Knicks|Bucks|2026-11-11T00:30Z|0.891" --leg "nba|Heat|Jazz|2026-11-11T02:00Z|0.783"
  python3 tools/arena.py say  --date 2026-11-10 --bot chico --pt "..." --en "..." --es "..."
  python3 tools/arena.py skip --date 2026-11-10 --bot chico --pt "..." --en "..." --es "..."
  python3 tools/arena.py pending
  python3 tools/arena.py game --lg nba --team Knicks --opp Bucks --score 112-101      # final score, --team first
  python3 tools/arena.py game --lg nba --team Knicks --opp Bucks --score 54-48 --live "Q2 3:21"   # snapshot only
  python3 tools/arena.py game --lg nba --team Knicks --opp Bucks --void                # postponed or cancelled
  python3 tools/arena.py report [--you 100]
  python3 tools/arena.py validate

Leg format:  league|pick|opponent|start time in UTC (ISO)|pre-game chance[|kind]
  kind: ml (default: the pick wins) · spread:-4.5 · over:224.5 · under:224.5 · dc (pick wins or draws)
  Use the names the scoreboard uses: pro teams by nickname (Knicks, Maple Leafs), college teams
  by school (Florida, Michigan State), soccer clubs by their usual full name (Real Madrid).
Leagues: nba wnba nfl nhl mlb ncaab ncaaw ncaaf epl laliga seriea bundesliga ligue1 ucl uel mls
  brasileirao libertadores ligamx, or a "sport/league" scoreboard path (for example soccer/por.1).

Stake = the bot's share of its current bankroll (Chico 2%, Arnaldo 3%, Herman 1%).
Payout = stake / price, where price is what the app charges as a fraction (0.715 = 71.5%).
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

PATH = os.environ.get("ARENA_DATA") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data.json")
BOTS = {"chico": (0.02, 5), "arnaldo": (0.03, 6), "herman": (0.01, 5)}   # stake share, max bets a day
LEAGUES = ("nba wnba nfl nhl mlb ncaab ncaaw ncaaf epl laliga seriea bundesliga ligue1 ucl uel mls "
           "brasileirao libertadores ligamx").split()
KINDS = ("ml", "spread", "over", "under", "dc")


def norm(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def load():
    if os.path.exists(PATH):
        with open(PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"v": 1, "bank": 1000, "updated": "", "days": []}


def save(d):
    d["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")


def get_day(d, date, create=True):
    for x in d["days"]:
        if x["date"] == date:
            return x
    if not create:
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        sys.exit("Date must be YYYY-MM-DD.")
    x = {"date": date, "say": {}, "skip": {}, "bets": []}
    d["days"].append(x)
    d["days"].sort(key=lambda y: y["date"])
    return x


def state(b):
    rs = [l.get("r") for l in b["legs"]]
    if "l" in rs:
        return "lost"
    if all(r == "w" for r in rs):
        return "won"
    if all(r in ("w", "v") for r in rs):
        return "void"
    return "open"


def profit(b, k=1.0):
    s = state(b)
    return (b["payout"] - b["stake"]) * k if s == "won" else -b["stake"] * k if s == "lost" else 0.0


def all_bets(d):
    for x in d["days"]:
        for b in x["bets"]:
            yield x, b


def bankroll(d, bot):
    return d["bank"] + sum(profit(b) for _, b in all_bets(d) if b["bot"] == bot)


def parse_leg(s):
    p = [x.strip() for x in s.split("|")]
    if len(p) < 5:
        sys.exit(f"Bad leg '{s}'. Use league|pick|opponent|start UTC|chance[|kind].")
    lg, pick, opp, t, pr = p[:5]
    if lg not in LEAGUES and "/" not in lg:
        sys.exit(f"Unknown league '{lg}'.")
    try:
        dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
    except ValueError:
        sys.exit(f"Bad start time '{t}'. Example: 2026-11-11T00:30Z")
    if dt.tzinfo is None:
        sys.exit(f"Start time '{t}' needs a time zone. Use UTC with a Z at the end.")
    leg = {"lg": lg, "pick": pick, "opp": opp,
           "t": dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "p": float(pr)}
    if not 0 < leg["p"] < 1:
        sys.exit("Chance must be a fraction between 0 and 1 (0.78 = 78%).")
    if len(p) > 5 and p[5] and p[5] != "ml":
        kind, _, line = p[5].partition(":")
        if kind not in KINDS:
            sys.exit(f"Unknown kind '{kind}'.")
        leg["k"] = kind
        if kind in ("spread", "over", "under"):
            leg["line"] = float(line)
    return leg


def check(bot, legs, price, edge):
    n, kinds, ps = len(legs), [l.get("k", "ml") for l in legs], [l["p"] for l in legs]
    plain = all(k in ("ml", "dc") for k in kinds)
    if bot == "chico":
        if not plain or n > 2 or min(ps) < 0.70:
            return "Chico: winner at 70% or more, or a 2-leg combo with each leg at 70% or more."
    elif bot == "arnaldo":
        if n == 1 and kinds[0] in ("spread", "under") and edge < 3:
            return "Arnaldo: spread and under need an edge of 3 points or more (--edge)."
        if n == 1 and kinds[0] == "over" and edge < 5:
            return "Arnaldo: over needs an edge of 5 points or more (--edge)."
        if n == 1 and plain and ps[0] < 0.60:
            return "Arnaldo: winner at 60% or more."
        if n > 1 and (n > 3 or not plain or min(ps) < 0.60):
            return "Arnaldo: combos of 2 or 3 legs, each at 60% or more."
    elif bot == "herman":
        if n == 1:
            if not plain or ps[0] <= price + 0.05:
                return "Herman: a single bet must be a value underdog (chance above price + 5 points)."
        elif n < 4 or n > 6 or price > 1 / 3:
            return "Herman: combos of 4 to 6 legs that pay 3x or more."
    return None


def cmd_add(a):
    d = load()
    day = get_day(d, a.date)
    legs = [parse_leg(s) for s in a.leg]
    why = None if a.force else check(a.bot, legs, a.price, a.edge)
    if why:
        sys.exit("Refused. " + why)
    today = [b for b in day["bets"] if b["bot"] == a.bot]
    if len(today) >= BOTS[a.bot][1] and not a.force:
        sys.exit(f"Refused. {a.bot} already has {len(today)} bets on {a.date}.")
    if not 0 < a.price < 1:
        sys.exit("Price must be a fraction between 0 and 1 (0.715 = 71.5%).")
    stake = a.stake if a.stake else round(bankroll(d, a.bot) * BOTS[a.bot][0], 2)
    prob = 1.0
    for l in legs:
        prob *= l["p"]
    bet = {"id": max([b["id"] for _, b in all_bets(d)] or [0]) + 1, "bot": a.bot,
           "stake": stake, "payout": round(stake / a.price, 2), "p": round(prob, 4), "legs": legs}
    day["bets"].append(bet)
    day.get("skip", {}).pop(a.bot, None)
    save(d)
    print(f"#{bet['id']} {a.bot}: " + " + ".join(l["pick"] for l in legs) +
          f" — stake ${stake:.2f}, payout ${bet['payout']:.2f}, chance {prob:.0%}")


def words(a):
    w = {k: getattr(a, k) for k in ("pt", "en", "es") if getattr(a, k)}
    if "pt" not in w and "en" not in w:
        sys.exit("Give the text in --pt and --en (and --es if you can).")
    return w


def cmd_say(a):
    d = load()
    get_day(d, a.date).setdefault("say", {})[a.bot] = words(a)
    save(d)
    print(f"{a.bot} says it for {a.date}.")


def cmd_skip(a):
    d = load()
    day = get_day(d, a.date)
    if any(b["bot"] == a.bot for b in day["bets"]):
        sys.exit(f"{a.bot} already has bets on {a.date}; use 'say' for a comment instead.")
    day.setdefault("skip", {})[a.bot] = words(a)
    save(d)
    print(f"{a.bot} sits out {a.date}.")


def open_games(d):
    g = {}
    for day, b in all_bets(d):
        for l in b["legs"]:
            if not l.get("r"):
                g.setdefault((l["lg"], norm(l["pick"]), norm(l["opp"])), (l, []))[1].append(b["id"])
    return g


def cmd_pending(a):
    g = open_games(load())
    if not g:
        print("No open games.")
    for (lg, _, _), (l, ids) in sorted(g.items(), key=lambda x: x[1][0]["t"]):
        kind = f" [{l['k']} {l.get('line', '')}]" if l.get("k") else ""
        print(f"{l['t']}  {lg:6} {l['pick']} x {l['opp']}{kind}  bets {sorted(set(ids))}")


def leg_result(l, ps, os_):
    k, line = l.get("k", "ml"), l.get("line", 0)
    m = {"ml": ps - os_, "dc": ps - os_ + 0.5, "spread": ps + line - os_,
         "over": ps + os_ - line, "under": line - ps - os_}[k]
    return "v" if m == 0 and k in ("spread", "over", "under") else "w" if m > 0 else "l"


def cmd_game(a):
    d = load()
    T, O = norm(a.team), norm(a.opp)
    if not a.void:
        m = re.fullmatch(r"\s*(\d+)\s*[-x:]\s*(\d+)\s*", a.score or "")
        if not m:
            sys.exit("Give --score as TEAM-OPP, for example 112-101 (or use --void).")
        ts, os_ = int(m.group(1)), int(m.group(2))
    hit = set()
    for day, b in all_bets(d):
        if a.date and day["date"] != a.date:
            continue
        for l in b["legs"]:
            if l["lg"] != a.lg or (l.get("r") and not a.redo):
                continue
            P, Q = norm(l["pick"]), norm(l["opp"])
            if (P, Q) == (T, O):
                ps, os2 = (ts, os_) if not a.void else (0, 0)
            elif (P, Q) == (O, T):
                ps, os2 = (os_, ts) if not a.void else (0, 0)
            else:
                continue
            if a.void:
                l["r"] = "v"
                l.pop("st", None)
                l.pop("det", None)
            elif a.live:
                l["sc"], l["st"], l["det"] = [ps, os2], "in", a.live
            else:
                l["sc"], l["r"] = [ps, os2], leg_result(l, ps, os2)
                l.pop("st", None)
                l.pop("det", None)
            hit.add(b["id"])
    if not hit:
        sys.exit("No open leg matches that game. Check 'pending' for the exact names.")
    save(d)
    for _, b in all_bets(d):
        if b["id"] in hit:
            print(f"#{b['id']} {b['bot']}: {state(b)}" + (f" ({profit(b):+.2f})" if state(b) != "open" else ""))


def cmd_report(a):
    d = load()
    print(f"{'bot':9}{'bank':>10}{'return':>9}{'hits':>8}{'open':>6}")
    for bot in BOTS:
        bs = [b for _, b in all_bets(d) if b["bot"] == bot]
        w = sum(state(b) == "won" for b in bs)
        n = sum(state(b) in ("won", "lost") for b in bs)
        bk = bankroll(d, bot)
        print(f"{bot:9}{bk:>10.2f}{(bk - d['bank']) / d['bank']:>+9.1%}{f'{w}/{n}':>8}"
              f"{sum(state(b) == 'open' for b in bs):>6}")
    if a.you:
        bs = [b for _, b in all_bets(d)]
        tot = sum(profit(b, a.you / b["stake"]) for b in bs)
        w = sum(state(b) == "won" for b in bs)
        n = sum(state(b) in ("won", "lost") for b in bs)
        print(f"{'you':9}{tot:>+10.2f}{'':>9}{f'{w}/{n}':>8}   (following every bet with ${a.you:g})")
        for day in d["days"]:
            dp = sum(profit(b, a.you / b["stake"]) for b in day["bets"])
            print(f"  {day['date']}: {dp:+.2f}")


def cmd_validate(a):
    d = load()
    ids, errs = set(), []
    for day, b in all_bets(d):
        if b["id"] in ids:
            errs.append(f"duplicate id {b['id']}")
        ids.add(b["id"])
        if b["bot"] not in BOTS:
            errs.append(f"#{b['id']}: unknown bot")
        if not (b["payout"] > b["stake"] > 0):
            errs.append(f"#{b['id']}: payout must be above stake")
        for l in b["legs"]:
            for k in ("lg", "pick", "opp", "t", "p"):
                if k not in l:
                    errs.append(f"#{b['id']}: leg without '{k}'")
            if l.get("r") not in (None, "w", "l", "v"):
                errs.append(f"#{b['id']}: bad result")
    if [x["date"] for x in d["days"]] != sorted(x["date"] for x in d["days"]):
        errs.append("days out of order")
    print("\n".join(errs) if errs else f"OK: {len(d['days'])} days, {len(ids)} bets.")
    sys.exit(1 if errs else 0)


def main():
    p = argparse.ArgumentParser(description="Guessitup Arena data helper (play money).")
    s = p.add_subparsers(dest="cmd", required=True)
    c = s.add_parser("add")
    c.add_argument("--date", required=True)
    c.add_argument("--bot", required=True, choices=BOTS)
    c.add_argument("--leg", action="append", required=True)
    c.add_argument("--price", type=float, required=True, help="app price as a fraction (0.715 = 71.5%%)")
    c.add_argument("--stake", type=float)
    c.add_argument("--edge", type=float, default=0.0, help="edge in points, for spread and totals")
    c.add_argument("--force", action="store_true")
    for name in ("say", "skip"):
        c = s.add_parser(name)
        c.add_argument("--date", required=True)
        c.add_argument("--bot", required=True, choices=BOTS)
        c.add_argument("--pt")
        c.add_argument("--en")
        c.add_argument("--es")
    s.add_parser("pending")
    c = s.add_parser("game")
    c.add_argument("--lg", required=True)
    c.add_argument("--team", required=True)
    c.add_argument("--opp", required=True)
    c.add_argument("--score")
    c.add_argument("--live", help="status text for a snapshot while the game is on")
    c.add_argument("--void", action="store_true")
    c.add_argument("--redo", action="store_true")
    c.add_argument("--date")
    c = s.add_parser("report")
    c.add_argument("--you", type=float)
    s.add_parser("validate")
    a = p.parse_args()
    {"add": cmd_add, "say": cmd_say, "skip": cmd_skip, "pending": cmd_pending, "game": cmd_game,
     "report": cmd_report, "validate": cmd_validate}[a.cmd](a)


if __name__ == "__main__":
    main()
