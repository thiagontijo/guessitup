#!/usr/bin/env python3
"""Bots de teste da guessitup: Chico, Arnaldo e Herman.

Apostam com DINHEIRO DE MENTIRA para medir, com o tempo, qual estilo de
aposta funciona melhor. Nunca fazem aposta real e nunca entram em conta de app.
Só biblioteca padrão. O registro fica em bots/ledger.csv (fora do git).

  python3 bots.py init [--bank 1000]
  python3 bots.py rules [--bot chico]
  python3 bots.py check --bot herman --type combo --legs 0.8,0.75,0.7,0.65
  python3 bots.py add --bot chico --date 2026-11-10 --sport nba --game "Knicks x Nets" \
      --bet "Knicks vencem" --type winner --legs 0.82 --price 0.78 [--grade B] [--edge 0]
  python3 bots.py pending
  python3 bots.py settle --id 3 --result win|loss|void
  python3 bots.py report
"""
import argparse
import csv
import os
import sys
from datetime import date

DIR = os.environ.get("GUESSITUP_BOTS") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "bots")
LEDGER = os.path.join(DIR, "ledger.csv")
CONFIG = os.path.join(DIR, "config.csv")
FIELDS = ["id", "bot", "date", "sport", "game", "bet", "type", "legs", "prob",
          "price", "edge", "grade", "stake", "payout", "result", "profit"]

BOTS = {
    "chico": {
        "nome": "Chico", "estilo": "Seguro", "stake": 0.02, "max_dia": 5,
        "regras": "Vencedor com chance >= 70%, ou combo de até 2 pernas com cada "
                  "perna >= 70%. Nunca aposta em Over. Aposta 2% da banca, até 5 por dia.",
    },
    "arnaldo": {
        "nome": "Arnaldo", "estilo": "Moderado", "stake": 0.03, "max_dia": 6,
        "regras": "Vencedor com chance >= 60%, combo de 2 a 3 pernas (cada uma >= 60%). "
                  "Handicap/Under só com vantagem >= 3 pontos; Over só com >= 5. "
                  "Aposta 3% da banca, até 6 por dia.",
    },
    "herman": {
        "nome": "Herman", "estilo": "Agressivo", "stake": 0.01, "max_dia": 5,
        "regras": "Combo de 4 a 6 pernas que pague 3x ou mais, ou zebra com valor "
                  "(chance do modelo > preço do app + 5 pontos). Aposta 1% da banca, até 5 por dia.",
    },
}
TYPES = ("winner", "combo", "handicap", "over", "under", "underdog")


def prod(xs):
    p = 1.0
    for x in xs:
        p *= x
    return p


def check(bot, typ, legs, price=None, edge=0.0):
    """Devolve (ok, motivo). legs = chances do modelo de cada perna."""
    n = len(legs)
    if bot == "chico":
        if typ in ("over", "handicap", "under", "underdog"):
            return False, "Chico só aposta em vencedor ou combo curto (sem Over, handicap, zebra)."
        if typ == "winner" and (n != 1 or legs[0] < 0.70):
            return False, "Chico precisa de chance >= 70%."
        if typ == "combo" and (n < 2 or n > 2 or min(legs) < 0.70):
            return False, "Combo do Chico: 2 pernas, cada uma >= 70%."
        return True, "ok"
    if bot == "arnaldo":
        if typ == "winner" and (n != 1 or legs[0] < 0.60):
            return False, "Arnaldo precisa de chance >= 60%."
        if typ == "combo" and (n < 2 or n > 3 or min(legs) < 0.60):
            return False, "Combo do Arnaldo: 2 a 3 pernas, cada uma >= 60%."
        if typ in ("handicap", "under") and edge < 3:
            return False, "Handicap/Under do Arnaldo precisa de vantagem >= 3 pontos."
        if typ == "over" and edge < 5:
            return False, "Over do Arnaldo precisa de vantagem >= 5 pontos."
        if typ == "underdog":
            return False, "Arnaldo não aposta em zebra."
        return True, "ok"
    if bot == "herman":
        if typ == "combo":
            if n < 4 or n > 6:
                return False, "Combo do Herman: 4 a 6 pernas."
            p = price if price else prod(legs)
            if p > 1 / 3:
                return False, "Combo do Herman precisa pagar 3x ou mais."
            return True, "ok"
        if typ == "underdog":
            if price is None or legs[0] <= price + 0.05:
                return False, "Zebra do Herman: chance do modelo > preço do app + 5 pontos."
            return True, "ok"
        return False, "Herman só faz combo longo ou zebra com valor."
    return False, "Bot desconhecido. Use chico, arnaldo ou herman."


def load():
    if not os.path.exists(LEDGER):
        return []
    with open(LEDGER, newline="") as f:
        return list(csv.DictReader(f))


def save(rows):
    os.makedirs(DIR, exist_ok=True)
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def bank_start():
    if os.path.exists(CONFIG):
        with open(CONFIG) as f:
            for line in f:
                if line.startswith("bank,"):
                    return float(line.split(",")[1])
    return 1000.0


def bankroll(rows, bot):
    return bank_start() + sum(float(r["profit"] or 0) for r in rows if r["bot"] == bot)


def money(x):
    return f"${x:,.0f}"


def cmd_init(a):
    os.makedirs(DIR, exist_ok=True)
    with open(CONFIG, "w") as f:
        f.write(f"bank,{a.bank}\n")
    if not os.path.exists(LEDGER):
        save([])
    print(f"Bots ligados: Chico, Arnaldo e Herman, cada um com {money(a.bank)} de mentira.")
    print(f"Registro: {os.path.abspath(LEDGER)}")


def cmd_rules(a):
    for k, b in BOTS.items():
        if a.bot and a.bot != k:
            continue
        print(f"{b['nome']} ({b['estilo']}): {b['regras']}")


def parse_legs(s):
    return [float(x) for x in s.split(",") if x.strip()]


def cmd_check(a):
    ok, why = check(a.bot, a.type, parse_legs(a.legs), a.price, a.edge)
    print(("PODE" if ok else "NÃO PODE") + f" ({BOTS[a.bot]['nome']}): {why}")
    sys.exit(0 if ok else 1)


def cmd_add(a):
    legs = parse_legs(a.legs)
    ok, why = check(a.bot, a.type, legs, a.price, a.edge)
    if not ok:
        sys.exit(f"Recusada: {why}")
    rows = load()
    d = a.date or date.today().isoformat()
    today = [r for r in rows if r["bot"] == a.bot and r["date"] == d]
    if len(today) >= BOTS[a.bot]["max_dia"]:
        sys.exit(f"Recusada: {BOTS[a.bot]['nome']} já fez {len(today)} apostas em {d}.")
    prob = prod(legs)
    price = a.price if a.price else prob
    stake = round(bankroll(rows, a.bot) * BOTS[a.bot]["stake"], 2)
    payout = round(stake / price, 2)
    nid = max([int(r["id"]) for r in rows] or [0]) + 1
    rows.append({"id": nid, "bot": a.bot, "date": d, "sport": a.sport, "game": a.game,
                 "bet": a.bet, "type": a.type, "legs": a.legs, "prob": round(prob, 4),
                 "price": round(price, 4), "edge": a.edge, "grade": a.grade or "",
                 "stake": stake, "payout": payout, "result": "pendente", "profit": ""})
    save(rows)
    print(f"#{nid} {BOTS[a.bot]['nome']}: {a.bet} — aposta {money(stake)}, recebe {money(payout)} "
          f"(chance {prob:.0%}).")


def cmd_pending(a):
    rows = [r for r in load() if r["result"] == "pendente"]
    if not rows:
        print("Nenhuma aposta pendente.")
    for r in rows:
        print(f"#{r['id']} {r['date']} {BOTS[r['bot']]['nome']}: {r['game']} — {r['bet']} "
              f"(aposta {money(float(r['stake']))}, recebe {money(float(r['payout']))})")


def cmd_settle(a):
    rows = load()
    for r in rows:
        if r["id"] == str(a.id):
            st, po = float(r["stake"]), float(r["payout"])
            r["result"] = a.result
            r["profit"] = {"win": round(po - st, 2), "loss": -st, "void": 0}[a.result]
            save(rows)
            print(f"#{a.id} {BOTS[r['bot']]['nome']}: {a.result}, lucro {money(float(r['profit']))}")
            return
    sys.exit(f"Aposta #{a.id} não encontrada.")


def cmd_report(a):
    rows = load()
    start = bank_start()
    print(f"{'Bot':<10}{'Banca':>10}{'Retorno':>10}{'Acertos':>11}{'Pend.':>7}")
    for k, b in BOTS.items():
        mine = [r for r in rows if r["bot"] == k]
        done = [r for r in mine if r["result"] in ("win", "loss")]
        wins = sum(r["result"] == "win" for r in done)
        bk = bankroll(rows, k)
        hit = f"{wins}/{len(done)}" + (f" {wins / len(done):.0%}" if done else "")
        pend = sum(r["result"] == "pendente" for r in mine)
        print(f"{b['nome']:<10}{money(bk):>10}{(bk - start) / start:>+10.1%}{hit:>11}{pend:>7}")
    print("Dinheiro de mentira. Com menos de ~30 apostas conferidas por bot, nada é conclusivo.")


def main():
    p = argparse.ArgumentParser(description="Bots de teste da guessitup (dinheiro de mentira).")
    s = p.add_subparsers(dest="cmd", required=True)
    i = s.add_parser("init"); i.add_argument("--bank", type=float, default=1000.0)
    r = s.add_parser("rules"); r.add_argument("--bot", choices=BOTS)
    for name in ("check", "add"):
        c = s.add_parser(name)
        c.add_argument("--bot", required=True, choices=BOTS)
        c.add_argument("--type", required=True, choices=TYPES)
        c.add_argument("--legs", required=True, help="chances do modelo, ex.: 0.82 ou 0.8,0.75")
        c.add_argument("--price", type=float, help="preço no app em fração (0.78 = 78%%)")
        c.add_argument("--edge", type=float, default=0.0, help="vantagem em pontos (handicap/total)")
        if name == "add":
            c.add_argument("--date"); c.add_argument("--sport", default="")
            c.add_argument("--game", required=True); c.add_argument("--bet", required=True)
            c.add_argument("--grade")
    s.add_parser("pending")
    st = s.add_parser("settle"); st.add_argument("--id", required=True, type=int)
    st.add_argument("--result", required=True, choices=("win", "loss", "void"))
    s.add_parser("report")
    a = p.parse_args()
    {"init": cmd_init, "rules": cmd_rules, "check": cmd_check, "add": cmd_add,
     "pending": cmd_pending, "settle": cmd_settle, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
