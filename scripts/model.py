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
  combo --probs P1 P2 ... [--stake 10 --pays Y]      chance do combo e o pagamento mínimo em dólar para valer a pena
  hedge --stake S --payout P --opp-pct C             aposta de proteção (hedge): quanto apostar no lado contrário e lucro garantido
  livewp --lead L --minutes-left M --spread S        chance ao vivo (NFL/NBA) e sinal MANTER/SAIR contra o % do app
  odds --odd X [--prob P]                            converte odd (americana, decimal ou %) e diz a odd mínima para a chance P
  compare --apps App=odd ... [--prob P]              compara a mesma aposta em vários apps e diz qual paga mais
  aggregate --home MU --away MU --lead N             mata-mata de ida e volta: chance de classificar
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


# ---------- mercados de previsão (Kalshi etc.), combos, hedge, ao vivo ----------
def cmd_combo(a):
    """Combo = todas as pernas precisam acertar. Só vale para pernas independentes."""
    p = math.prod(a.probs)
    fair = a.stake / p
    minpay = a.stake / max(p - a.margin, 0.01)
    print(f"Chance de acertar todas as {len(a.probs)} pernas: {p:.0%}")
    print(f"Apostando ${a.stake:.2f}, só vale se o app pagar pelo menos ${minpay:.2f} (pagamento justo: ${fair:.2f})")
    if a.pays is not None:
        ev = p * a.pays / a.stake - 1
        print(f"O app paga ${a.pays:.2f} -> {'bom preço' if ev > 0.03 else 'caro' if ev < -0.03 else 'preço justo'} (ganho médio {ev:+.0%})")
    for k in range(1, len(a.probs)):
        print(f"  Se as {k} primeiras pernas acertarem, a chance do combo sobe para {math.prod(a.probs[k:]):.0%}")


def cmd_hedge(a):
    """Aposta de proteção no lado contrário da última perna para garantir lucro."""
    opp = a.opp_pct / 100
    for share in (1.0, 0.5):
        cover = a.payout * share               # quanto a proteção paga se o lado contrário ganhar
        cost = cover * opp                     # quanto apostar na proteção
        win = a.payout - a.stake - cost
        lose = cover - a.stake - cost
        nome = "Proteção total" if share == 1 else "Proteção pela metade"
        print(f"{nome}: aposte ${cost:.2f} no lado contrário (ela paga ${cover:.2f} se ele ganhar)")
        print(f"  Se a sua aposta ganhar: {win:+.2f} | se o lado contrário ganhar: {lose:+.2f}")
    print(f"Sem proteção: {1-opp:.0%} de chance de {a.payout - a.stake:+.2f} e {opp:.0%} de chance de {-a.stake:+.2f}")
    print("Lembrete: a proteção não cria dinheiro; ela troca o lucro máximo por segurança.")


def cmd_livewp(a):
    """Chance ao vivo (NFL/NBA): vantagem atual + favoritismo de antes do jogo proporcional ao tempo restante."""
    cdf = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
    frac = max(a.minutes_left, 0.01) / a.game_minutes
    p = cdf((a.lead + a.spread * frac) / (a.sd * math.sqrt(frac)))
    print(f"Chance ao vivo: {p:.0%} (vantagem {a.lead:+g}, {a.minutes_left:g} min restantes, favoritismo antes do jogo {a.spread:+g})")
    if a.app_pct is not None:
        d = p * 100 - a.app_pct
        sig = "MANTER" if d > 3 else "CONSIDERE SAIR" if d < -3 else "TANTO FAZ (sua escolha)"
        print(f"O app mostra {a.app_pct:g}% -> diferença {d:+.0f} pontos -> {sig}")


# ---------- simulação de 10.000 jogos: handicap (spread) e over/under ----------
SIM_SD = {"nba": (12.0, 18.0), "nfl": (13.5, 10.0), "ncaab": (11.0, 16.0), "ncaafb": (16.0, 14.0)}  # (sd margem, sd total)
POISSON_SPORTS = {"soccer", "futebol", "nhl", "mlb"}


def _poisson_draw(rng, lam):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def _side(p, label):
    p = min(max(p, 0.001), 0.999)
    d = 1 / p
    am = f"+{(d-1)*100:.0f}" if d >= 2 else f"-{100/(d-1):.0f}"
    return f"{label}: {p:.0%}  (justo: Kalshi {p*100:.0f}% | americana {am} | aposta $10 recebe ${10*d:.2f})"


def cmd_sim(a):
    """Simula N jogos e devolve vencedor, handicap (spread), over/under e a distribuição da margem."""
    import random
    rng = random.Random(a.seed)
    sport = a.sport.lower()
    H, A = a.home_name, a.away_name
    poisson = sport in POISSON_SPORTS

    if poisson:
        if a.home is None or a.away is None:
            sys.exit("Para futebol/NHL/MLB use --home e --away (gols/corridas esperados de cada time).")
        mu_h, mu_a = a.home, a.away
    else:
        sd_m, sd_t = SIM_SD.get(sport, SIM_SD["nba"])
        if a.sd_margin: sd_m = a.sd_margin
        if a.sd_total: sd_t = a.sd_total
        if a.market_spread is not None and a.market_total is not None:
            mkt_m, mkt_t = -a.market_spread, a.market_total     # spread do mandante: -7.5 = mandante favorito por 7,5
            if a.home is not None and a.away is not None:     # mistura 2:1 mercado:modelo (regra da skill)
                mu_m = (2 * mkt_m + (a.home - a.away)) / 3
                mu_t = (2 * mkt_t + (a.home + a.away)) / 3
            else:
                mu_m, mu_t = mkt_m, mkt_t
        elif a.home is not None and a.away is not None:
            mu_m, mu_t = a.home - a.away, a.home + a.away
        else:
            sys.exit("Use --market-spread e --market-total (linhas do app) e/ou --home e --away (pontos esperados).")
        mu_h, mu_a = (mu_t + mu_m) / 2, (mu_t - mu_m) / 2

    margins, totals = [], []
    for _ in range(a.n):
        if poisson:
            h, w = _poisson_draw(rng, mu_h), _poisson_draw(rng, mu_a)
            if sport == "nhl" and h == w:          # prorrogação/pênaltis: decide 1 gol
                if rng.random() < mu_h / (mu_h + mu_a): h += 1
                else: w += 1
        else:
            m = rng.gauss(mu_m, sd_m); t = rng.gauss(mu_t, sd_t)
            h, w = round((t + m) / 2), round((t - m) / 2)
            if h == w:                             # NBA/NFL quase nunca empata: prorrogação
                if rng.random() < 0.5 + mu_m / 40: h += 1
                else: w += 1
            if sport in ("nfl", "ncaafb"):         # números-chave da NFL: muitos jogos terminam por 3 ou 7
                d = h - w; s_ = 1 if d > 0 else -1
                if abs(d) in (1, 2, 4, 5) and rng.random() < 0.35: w = h - 3 * s_
                elif abs(d) in (6, 8) and rng.random() < 0.30: w = h - 7 * s_
        margins.append(h - w); totals.append(h + w)

    n = a.n
    ph = sum(m > 0 for m in margins) / n
    pd = sum(m == 0 for m in margins) / n
    print(f"Simulação de {n:,} jogos ({sport.upper()}) — placar médio: {H} {mu_h:.1f} x {mu_a:.1f} {A}".replace(",", "."))
    print("\nVENCEDOR")
    print("  " + _side(ph, f"{H} vence"))
    if pd > 0.005:
        print("  " + _side(pd, "Empate"))
    print("  " + _side(1 - ph - pd, f"{A} vence"))

    for line in a.spread or []:
        cover = sum(m + line > 0 for m in margins) / n
        push = sum(m + line == 0 for m in margins) / n
        print(f"\nHANDICAP {H} {line:+g}  (= {A} {-line:+g})")
        print("  " + _side(cover, f"{H} cobre {line:+g}"))
        print("  " + _side(1 - cover - push, f"{A} cobre {-line:+g}"))
        if push > 0.005:
            print(f"  Empate na linha (devolve o dinheiro): {push:.0%}")

    for line in a.total or []:
        over = sum(t > line for t in totals) / n
        push = sum(t == line for t in totals) / n
        print(f"\nOVER/UNDER {line:g}")
        print("  " + _side(over, f"Mais de {line:g}"))
        print("  " + _side(1 - over - push, f"Menos de {line:g}"))
        if push > 0.005:
            print(f"  Exatamente {line:g} (devolve): {push:.0%}")

    print("\nCOMO O JOGO TERMINA (margem)")
    if poisson:
        from collections import Counter
        for (h, w), c in Counter(zip([(m + t) // 2 for m, t in zip(margins, totals)],
                                     [(t - m) // 2 for m, t in zip(margins, totals)])).most_common(6):
            print(f"  Placar {H} {h} x {w} {A}: {c/n:.0%}")
    else:
        cuts = [(1, 5), (6, 10), (11, 15), (16, 999)] if sport in ("nba", "ncaab") else [(1, 3), (4, 7), (8, 14), (15, 999)]
        for team, sign in ((H, 1), (A, -1)):
            for lo, hi in cuts:
                pr = sum(lo <= sign * m <= hi for m in margins) / n
                faixa = f"{lo}+" if hi == 999 else f"{lo} a {hi}"
                print(f"  {team} vence por {faixa} pontos: {pr:.0%}")
    st = sorted(totals)
    print(f"\nTOTAL: metade dos jogos entre {st[n//4]} e {st[3*n//4]} pontos/gols (mediana {st[n//2]})")
    print("Regra: só aposte se o app pagar MAIS que o justo (no Kalshi, preço ABAIXO da chance).")


# ---------- apps de apostas: formatos de odd e comparação ----------
def _to_dec(x):
    """Aceita odd americana (-150, +130), decimal (1.80) ou % de app de previsão (55%)."""
    x = str(x).strip().replace(",", ".")
    if x.endswith("%"):
        return 100 / float(x[:-1])
    v = float(x)
    if x.startswith("+") or v >= 100:
        return 1 + v / 100
    if v <= -100:
        return 1 + 100 / abs(v)
    return v


def _fmt(d):
    am = f"+{(d-1)*100:.0f}" if d >= 2 else f"-{100/(d-1):.0f}"
    return f"americana {am} | decimal {d:.2f} | app de previsão {100/d:.0f}% | aposta $10 recebe ${10*d:.2f}"


def cmd_odds(a):
    """Converte uma odd para todos os formatos e, com --prob, diz a odd mínima para valer a pena."""
    if a.odd:
        print("Essa odd em todos os formatos: " + _fmt(_to_dec(a.odd)))
    if a.prob:
        d = 1 / max(a.prob - a.margin, 0.01)
        print(f"Chance {a.prob:.0%} -> odd mínima: " + _fmt(d))
        print("Regra: só aposte se o app pagar igual ou mais que isso.")


def cmd_compare(a):
    """Compara a mesma aposta em vários apps (formato app=odd) e ordena por quanto paga."""
    rows = []
    for item in a.apps:
        app, odd = item.split("=", 1)
        d = _to_dec(odd)
        rows.append((d, app))
    rows.sort(reverse=True)
    for d, app in rows:
        ev = a.prob * d - 1 if a.prob else None
        tag = "" if ev is None else f" | ganho médio {ev:+.0%} ({'vale' if ev > 0.03 else 'caro' if ev < -0.03 else 'justo'})"
        print(f"{app:<14} aposta $10 recebe ${10*d:.2f}{tag}")
    print(f"Melhor: {rows[0][1]} (paga ${10*rows[0][0]:.2f} por $10). Se o seu app pagar menos, considere apostar no melhor.")


def cmd_aggregate(a):
    """Mata-mata de ida e volta: chance de classificar dado o placar agregado da ida."""
    g = {(i, j): pois(i, a.home) * pois(j, a.away) for i in range(11) for j in range(11)}
    # lead = vantagem do time VISITANTE (o que joga fora na volta) no agregado
    out = sum(v for (i, j), v in g.items() if i - j > a.lead)
    pens = sum(v for (i, j), v in g.items() if i - j == a.lead)
    adv = 1 - out - pens * a.pen
    print(f"Visitante classifica: {adv:.1%} (direto {1-out-pens:.1%} + pênaltis {pens*a.pen:.1%}) | mandante: {1-adv:.1%}")
    print(f"Mandante precisa vencer por {a.lead+1}+ (prob. {out:.1%}); vencer por {a.lead} leva aos pênaltis ({pens:.1%})")


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
    s = add("combo", cmd_combo); s.add_argument("--probs", type=float, nargs="+", required=True); s.add_argument("--stake", type=float, default=10, help="quanto vai apostar ($)"); s.add_argument("--pays", type=float, help="quanto o app paga se ganhar ($)"); s.add_argument("--margin", type=float, default=0.01)
    s = add("hedge", cmd_hedge); s.add_argument("--stake", type=float, required=True, help="quanto você apostou ($)"); s.add_argument("--payout", type=float, required=True, help="quanto recebe se ganhar ($)"); s.add_argument("--opp-pct", type=float, required=True, help="chance do lado contrário que o app mostra (%%)")
    s = add("livewp", cmd_livewp); s.add_argument("--lead", type=float, required=True); s.add_argument("--minutes-left", type=float, required=True); s.add_argument("--spread", type=float, required=True, help="pontos que o time era favorito antes do jogo (+ favorito, - azarão)"); s.add_argument("--game-minutes", type=float, default=60, help="60 NFL, 48 NBA"); s.add_argument("--sd", type=float, default=13.5, help="13.5 NFL, 12 NBA"); s.add_argument("--app-pct", type=float, help="chance que o app mostra agora (%%)")
    s = add("odds", cmd_odds); s.add_argument("--odd", help="-150, +130, 1.80 ou 55%%"); s.add_argument("--prob", type=float); s.add_argument("--margin", type=float, default=0.01)
    s = add("compare", cmd_compare); s.add_argument("--apps", nargs="+", required=True, help="ex.: HardRock=-210 Kalshi=68%% Bet365=1.47"); s.add_argument("--prob", type=float)
    s = add("aggregate", cmd_aggregate); s.add_argument("--home", type=float, required=True, help="gols esperados do mandante da volta"); s.add_argument("--away", type=float, required=True); s.add_argument("--lead", type=int, required=True, help="vantagem do visitante no agregado"); s.add_argument("--pen", type=float, default=0.5)
    s = add("sim", cmd_sim)
    s.add_argument("--sport", required=True, help="nba, nfl, ncaab, ncaafb, nhl, mlb, soccer")
    s.add_argument("--market-spread", type=float, help="linha do mandante no app (ex.: -7.5 = mandante favorito por 7,5)")
    s.add_argument("--market-total", type=float, help="linha de total do app (ex.: 228.5)")
    s.add_argument("--home", type=float, help="pontos/gols esperados do mandante pelo modelo")
    s.add_argument("--away", type=float, help="pontos/gols esperados do visitante pelo modelo")
    s.add_argument("--spread", type=float, nargs="*", help="linhas de handicap do mandante para avaliar (ex.: -7.5 -9.5)")
    s.add_argument("--total", type=float, nargs="*", help="linhas de over/under para avaliar (ex.: 224.5 228.5)")
    s.add_argument("--home-name", default="Mandante"); s.add_argument("--away-name", default="Visitante")
    s.add_argument("--sd-margin", type=float); s.add_argument("--sd-total", type=float)
    s.add_argument("--n", type=int, default=10000); s.add_argument("--seed", type=int, default=7)
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
