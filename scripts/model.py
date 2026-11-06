#!/usr/bin/env python3
"""Ferramentas numéricas do guessitup (somente biblioteca padrão).

Técnicas inspiradas em projetos abertos (penaltyblog, Kairos, GoallineIQ), reescritas do zero.

Subcomandos:
  poisson --home MU --away MU [--rho R] [--max N]    gols esperados -> 1X2, O/U, BTTS, placares (Dixon-Coles)
  decay --values V1 V2 ... --half-life N             média ponderada por tempo (mais recente por último)
  strength --gf A --ga B --league-gf L [--home]      força de ataque/defesa relativa à liga
  elo --a RA --b RB [--adv PTS] [--draw P]           pontuação esperada por Elo (--draw converte p/ 1X2)
  elo-update --a RA --b RB --score S [--k 32]        atualiza Elo (S: 1 vitória de A, 0.5 empate, 0 derrota)
  devig --odds O1 O2 [O3 ...]                        remove margem: proporcional, potência e Shin
  blend --probs P1 P2 ... [--weights W1 W2 ...]      combina modelos e mostra divergência
  normal --diff D --sd S [--line L]                  prob. de vencer / cobrir linha (basquete, NFL)
  value --prob P --odds O [--kelly-frac F --cap C]   EV e Kelly fracionado com teto
  clv --taken O --closing O                          closing line value de uma aposta
  ledger add|result|report                           registro de palpites e calibração (Brier, RPS, CLV, ROI)
"""
import argparse
import json
import math
import os
import sys
from datetime import date

LEDGER = os.environ.get("GUESSITUP_LEDGER") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "ledger", "predictions.jsonl")


def pois(k, mu):
    return math.exp(-mu) * mu ** k / math.factorial(k)


# ---------- gols ----------
def cmd_poisson(a):
    n = a.max

    def tau(i, j):  # correção Dixon-Coles para placares baixos
        r = a.rho
        if r == 0:
            return 1.0
        if i == 0 and j == 0:
            return 1 - a.home * a.away * r
        if i == 0 and j == 1:
            return 1 + a.home * r
        if i == 1 and j == 0:
            return 1 + a.away * r
        if i == 1 and j == 1:
            return 1 - r
        return 1.0

    grid = {(i, j): max(pois(i, a.home) * pois(j, a.away) * tau(i, j), 0) for i in range(n + 1) for j in range(n + 1)}
    s = sum(grid.values())
    grid = {k: v / s for k, v in grid.items()}
    ph = sum(v for (i, j), v in grid.items() if i > j)
    pd = sum(v for (i, j), v in grid.items() if i == j)
    pa = sum(v for (i, j), v in grid.items() if i < j)
    btts = sum(v for (i, j), v in grid.items() if i > 0 and j > 0)
    print(f"1X2: Casa {ph:.1%} | Empate {pd:.1%} | Fora {pa:.1%}")
    print(f"Dupla chance: 1X {ph+pd:.1%} | X2 {pd+pa:.1%} | 12 {ph+pa:.1%}")
    print(f"Empate anula aposta (DNB): Casa {ph/(ph+pa):.1%} | Fora {pa/(ph+pa):.1%}")
    print(f"Ambos marcam: Sim {btts:.1%} | Não {1-btts:.1%}")
    for line in (0.5, 1.5, 2.5, 3.5, 4.5):
        over = sum(v for (i, j), v in grid.items() if i + j > line)
        print(f"Over {line}: {over:.1%} | Under {line}: {1-over:.1%}")
    # handicap asiático -0.5 / +0.5 (sem push)
    print(f"Handicap -0.5 Casa: {ph:.1%} | +0.5 Fora: {pd+pa:.1%}")
    top = sorted(grid.items(), key=lambda kv: -kv[1])[:6]
    print("Placares mais prováveis: " + " | ".join(f"{i}-{j} {p:.1%}" for (i, j), p in top))


def cmd_decay(a):
    """Peso exponencial: jogo k passos atrás vale 0.5**(k/half_life)."""
    vals = a.values
    n = len(vals)
    w = [0.5 ** ((n - 1 - i) / a.half_life) for i in range(n)]
    m = sum(v * x for v, x in zip(vals, w)) / sum(w)
    print(f"Média simples: {sum(vals)/n:.3f} | Média com decaimento (meia-vida {a.half_life:g} jogos): {m:.3f}")
    print("Pesos (antigo -> recente): " + " ".join(f"{x:.2f}" for x in w))


def cmd_strength(a):
    s = a.gf / a.league_gf
    t = a.ga / a.league_gf
    print(f"Força de ataque: {s:.3f} | Força de defesa (maior = pior defesa): {t:.3f}")
    print("Uso: lambda_casa = média_casa * ataque_casa * defesa_fora ; lambda_fora = média_fora * ataque_fora * defesa_casa")


# ---------- ratings ----------
def cmd_elo(a):
    diff = a.a + a.adv - a.b
    p = 1 / (1 + 10 ** (-diff / 400))
    print(f"Pontuação esperada: A {p:.1%} | B {1-p:.1%}  (empate conta meio ponto)")
    if a.draw is not None:
        wa, wb = p - a.draw / 2, 1 - p - a.draw / 2
        print(f"Com empate {a.draw:.0%}: A vence {wa:.1%} | Empate {a.draw:.1%} | B vence {wb:.1%}")
    else:
        print("Esporte com empate? passe --draw P (ex.: 0.28). Sem empate (tênis, NBA), a pontuação já é a prob. de vencer.")


def cmd_elo_update(a):
    exp = 1 / (1 + 10 ** (-(a.a + a.adv - a.b) / 400))
    mult = 1.0
    if a.margin is not None:  # multiplicador por margem (estilo FiveThirtyEight)
        mult = math.log(abs(a.margin) + 1) * 2.2 / ((abs(a.a - a.b) * 0.001) + 2.2)
    d = a.k * mult * (a.score - exp)
    print(f"Esperado {exp:.3f} | Novo Elo A {a.a + d:.1f} | Novo Elo B {a.b - d:.1f} (variação {d:+.1f})")


# ---------- mercado ----------
def shin(odds):
    imp = [1 / o for o in odds]
    B = sum(imp)
    f = lambda z: sum((math.sqrt(z * z + 4 * (1 - z) * x * x / B) - z) / (2 * (1 - z)) for x in imp) - 1
    lo, hi = 0.0, 0.4
    if f(lo) * f(hi) > 0:
        return None, None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    z = (lo + hi) / 2
    p = [(math.sqrt(z * z + 4 * (1 - z) * x * x / B) - z) / (2 * (1 - z)) for x in imp]
    s = sum(p)
    return [x / s for x in p], z


def cmd_devig(a):
    imp = [1 / o for o in a.odds]
    total = sum(imp)
    print(f"Margem da casa (overround): {total-1:.2%}")
    print("Proporcional: " + " | ".join(f"{x/total:.1%}" for x in imp))
    lo, hi = 0.5, 2.0
    for _ in range(100):
        k = (lo + hi) / 2
        if sum(x ** k for x in imp) > 1:
            lo = k
        else:
            hi = k
    print("Potência:     " + " | ".join(f"{x**k:.1%}" for x in imp))
    p, z = shin(a.odds)
    if p:
        print("Shin:         " + " | ".join(f"{x:.1%}" for x in p) + f"   (z={z:.3f}, fração de apostadores informados)")
    print("Dica: com favorito/azarão marcados, Shin e Potência são mais fiéis que o proporcional.")


def cmd_blend(a):
    w = a.weights or [1] * len(a.probs)
    if len(w) != len(a.probs):
        raise SystemExit("weights e probs precisam ter o mesmo tamanho")
    p = sum(x * y for x, y in zip(a.probs, w)) / sum(w)
    spread = max(a.probs) - min(a.probs)
    print(f"Probabilidade combinada: {p:.1%}")
    print(f"Divergência entre modelos: {spread:.1%}" + ("  <- >10pp: rebaixar confiança / usar dupla chance" if spread > 0.10 else ""))


def cmd_normal(a):
    cdf = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
    pw = cdf(a.diff / a.sd)
    print(f"Prob. de A vencer (margem>0): {pw:.1%} | B {1-pw:.1%}")
    if a.line is not None:
        print(f"Prob. de A cobrir {a.line:+g}: {cdf((a.diff - a.line) / a.sd):.1%}")


def cmd_value(a):
    ev = a.prob * a.odds - 1
    b = a.odds - 1
    kelly = max((b * a.prob - (1 - a.prob)) / b, 0) if b > 0 else 0
    stake = min(kelly * a.kelly_frac, a.cap)
    print(f"Prob. implícita (com margem): {1/a.odds:.1%} | Sua prob.: {a.prob:.1%}")
    print(f"EV por unidade: {ev:+.1%} -> {'VALUE' if ev > 0 else 'sem value'}")
    print(f"Kelly pleno {kelly:.1%} | fracionado ({a.kelly_frac:g}x) com teto {a.cap:.0%}: {stake:.1%} da banca")
    if ev > 0 and a.prob - 1 / a.odds < 0.03:
        print("Aviso: vantagem < 3 pp sobre o preço — dentro do erro típico de modelo; trate como 'sem aposta'.")


def cmd_clv(a):
    clv = a.taken / a.closing - 1
    print(f"CLV: {clv:+.2%} ({'bateu' if clv > 0 else 'não bateu'} a linha de fechamento)")


# ---------- ledger ----------
def _read():
    if not os.path.exists(LEDGER):
        return []
    with open(LEDGER) as f:
        return [json.loads(l) for l in f if l.strip()]


def _write(rows):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _parse_probs(s):
    d = {}
    for part in s.split(","):
        k, v = part.split(":")
        d[k.strip()] = float(v)
    t = sum(d.values())
    if abs(t - 1) > 0.02:
        raise SystemExit(f"probabilidades somam {t:.3f}, devem somar 1")
    return d


def cmd_ledger(a):
    rows = _read()
    if a.action == "add":
        if any(r["id"] == a.id for r in rows):
            raise SystemExit("id já existe (duplicado recusado)")
        probs = _parse_probs(a.probs)
        rows.append({"id": a.id, "date": a.date or str(date.today()), "event": a.event, "sport": a.sport,
                     "probs": probs, "pick": a.pick, "odds": a.odds, "confidence": a.confidence,
                     "outcome": None, "closing_odds": None})
        _write(rows)
        print(f"Registrado: {a.id}")
    elif a.action == "result":
        r = next((x for x in rows if x["id"] == a.id), None)
        if not r:
            raise SystemExit("id desconhecido")
        if r["outcome"] is not None:
            raise SystemExit("resultado já registrado para este id (segundo resultado recusado)")
        if a.outcome not in r["probs"]:
            raise SystemExit(f"resultado deve ser um de {list(r['probs'])}")
        r["outcome"], r["closing_odds"] = a.outcome, a.closing_odds
        _write(rows)
        print(f"Resultado registrado: {a.id} -> {a.outcome}")
    else:
        done = [r for r in rows if r["outcome"]]
        print(f"Palpites: {len(rows)} | com resultado: {len(done)}")
        if not done:
            return
        brier = rps = ll = 0
        for r in done:
            keys = list(r["probs"])
            p = [r["probs"][k] for k in keys]
            o = [1.0 if k == r["outcome"] else 0.0 for k in keys]
            brier += sum((x - y) ** 2 for x, y in zip(p, o))
            if len(keys) > 2:
                cp = co = 0
                s = 0
                for x, y in list(zip(p, o))[:-1]:
                    cp += x
                    co += y
                    s += (cp - co) ** 2
                rps += s / (len(keys) - 1)
            ll += -math.log(max(r["probs"][r["outcome"]], 1e-9))
        n = len(done)
        print(f"Brier (multiclasse): {brier/n:.4f} | Log loss: {ll/n:.4f}" + (f" | RPS: {rps/n:.4f}" if rps else ""))
        print("Referência: Brier de chute uniforme em 3 resultados = 0.667; menor é melhor.")
        hits = [r for r in done if r["pick"]]
        if hits:
            ok = sum(1 for r in hits if r["pick"] == r["outcome"])
            print(f"Acerto do palpite principal: {ok}/{len(hits)} = {ok/len(hits):.1%}")
            buckets = {}
            for r in hits:
                pr = r["probs"].get(r["pick"], 0)
                b = min(int(pr * 10), 9) / 10
                buckets.setdefault(b, []).append(1 if r["pick"] == r["outcome"] else 0)
            print("Calibração (prob. dada -> acerto real):")
            for b in sorted(buckets):
                v = buckets[b]
                print(f"  {b:.0%}-{b+0.1:.0%}: {sum(v)/len(v):.0%} em {len(v)} palpites")
        bets = [r for r in done if r["odds"]]
        if bets:
            roi = sum((r["odds"] - 1) if r["pick"] == r["outcome"] else -1 for r in bets) / len(bets)
            print(f"ROI (1 unidade por palpite com odds): {roi:+.1%} em {len(bets)}")
        clvs = [r["odds"] / r["closing_odds"] - 1 for r in done if r["odds"] and r["closing_odds"]]
        if clvs:
            print(f"CLV médio: {sum(clvs)/len(clvs):+.2%} em {len(clvs)} (medida principal de edge; acerto isolado engana)")
        if n < 30:
            print("Amostra pequena (<30): nada aqui é conclusivo ainda.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        s = sp.add_parser(name)
        s.set_defaults(f=fn)
        return s

    s = add("poisson", cmd_poisson); s.add_argument("--home", type=float, required=True); s.add_argument("--away", type=float, required=True); s.add_argument("--rho", type=float, default=-0.05); s.add_argument("--max", type=int, default=10)
    s = add("decay", cmd_decay); s.add_argument("--values", type=float, nargs="+", required=True); s.add_argument("--half-life", type=float, default=5)
    s = add("strength", cmd_strength); s.add_argument("--gf", type=float, required=True); s.add_argument("--ga", type=float, required=True); s.add_argument("--league-gf", type=float, required=True)
    s = add("elo", cmd_elo); s.add_argument("--a", type=float, required=True); s.add_argument("--b", type=float, required=True); s.add_argument("--adv", type=float, default=0); s.add_argument("--draw", type=float)
    s = add("elo-update", cmd_elo_update); s.add_argument("--a", type=float, required=True); s.add_argument("--b", type=float, required=True); s.add_argument("--score", type=float, required=True); s.add_argument("--k", type=float, default=32); s.add_argument("--adv", type=float, default=0); s.add_argument("--margin", type=float)
    s = add("devig", cmd_devig); s.add_argument("--odds", type=float, nargs="+", required=True)
    s = add("blend", cmd_blend); s.add_argument("--probs", type=float, nargs="+", required=True); s.add_argument("--weights", type=float, nargs="+")
    s = add("normal", cmd_normal); s.add_argument("--diff", type=float, required=True); s.add_argument("--sd", type=float, required=True); s.add_argument("--line", type=float)
    s = add("value", cmd_value); s.add_argument("--prob", type=float, required=True); s.add_argument("--odds", type=float, required=True); s.add_argument("--kelly-frac", type=float, default=0.25); s.add_argument("--cap", type=float, default=0.05)
    s = add("clv", cmd_clv); s.add_argument("--taken", type=float, required=True); s.add_argument("--closing", type=float, required=True)
    s = add("ledger", cmd_ledger)
    s.add_argument("action", choices=["add", "result", "report"])
    s.add_argument("--id"); s.add_argument("--event"); s.add_argument("--sport"); s.add_argument("--date")
    s.add_argument("--probs", help='ex.: "H:0.33,D:0.28,A:0.39" (ordem = ordem dos resultados, usada no RPS)')
    s.add_argument("--pick"); s.add_argument("--odds", type=float); s.add_argument("--confidence")
    s.add_argument("--outcome"); s.add_argument("--closing-odds", type=float)
    a = p.parse_args()
    if a.cmd == "ledger" and a.action == "add" and not (a.id and a.probs):
        sys.exit("ledger add exige --id e --probs")
    if a.cmd == "ledger" and a.action == "result" and not (a.id and a.outcome):
        sys.exit("ledger result exige --id e --outcome")
    a.f(a)


if __name__ == "__main__":
    main()
