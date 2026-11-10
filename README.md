# guessitup

**English** · [Português](README.pt-BR.md)

**[⬇️ Download the skill (ZIP)](https://github.com/thiagontijo/guessitup/archive/refs/heads/main.zip)**

A skill for Claude ([app](https://claude.ai) and [Claude Code](https://claude.com/claude-code)) that makes **sports picks from statistics, not hunches**, for any sport: soccer, NBA, NFL, MLB, NHL, tennis, MMA/UFC, F1, volleyball, esports and more.

For each game or fight, the skill pulls current data from the web and builds a report with:

- form across five windows: career, season, last month, last 5 games and game context (home/away, surface, rest);
- head-to-head record, weighted by sample size;
- injuries and context;
- calculated probabilities for both sides (Poisson/Dixon-Coles, Elo, normal distribution for points sports), compared with the no-vig market price;
- a pick with a confidence level, the fair price, what would change the pick, and data gaps;
- a final summary of every pick, sorted by confidence;
- bet options and parlays (safe, balanced, risky) for the app you choose (Hard Rock, FanDuel, DraftKings, bet365, Kalshi, Betano...), with the minimum payout that makes each bet worth it and which app pays more;
- a hedge plan in dollars: how much to bet on the other side and how much profit is locked in;
- live advisor mode: follows your bets and says "hold" or "consider cashing out" based on live win probability (the decision is always yours).

Every request opens a button menu: **App** (Kalshi, Hard Rock, FanDuel, DraftKings or other), **Bet type** (single, parlay or both), **Hedge protection** (on or off) and **Markets** (moneyline, spread, over/under, with a 10,000-game simulation). Each game comes as a **full game card**: season numbers, context, simulation and an A–D confidence grade.

### Test bots (optional): Chico, Arnaldo and Herman

Want to test before you bet real money? Turn on three bots that bet **play money** using the skill's picks:

- **Chico** (safe): moneylines at 70% or more, parlays of up to 2 legs, 2% of bankroll per bet.
- **Arnaldo** (moderate): moneylines at 60% or more, 2–3 leg parlays, spreads and totals only with an edge, 3% of bankroll.
- **Herman** (aggressive): 4–6 leg parlays that pay 3x or more and value underdogs, 1% of bankroll.

Say "turn on the bots" and choose **how much money each bot gets**, **each bot's daily limit** (number of bets and, if you want, a dollar cap) and whether they run every day on their own or only when you ask.

The bots have **a mind of their own**: each one picks bets within its style, and when nothing is worth it, it sits the day out and tells you why ("no safe game today, I'm keeping the bankroll"). They are models to follow: every day each bot shows the bets it would make, and **you choose** whether to follow Chico, Arnaldo, Herman, just a few bets, or skip the day. **You decide how much to put on each bet.** The scoreboard shows the three bots plus a "You" line with the result of what you chose to follow: bankroll, % return, hit rate and days skipped. Everything stays on your computer (`bots/ledger.csv`). Details in [references/bots.md](references/bots.md).

> These are probabilities, not guarantees. No model guarantees a result, and betting involves risk. The skill never places bets and never logs into your betting accounts.

## Install

### In the Claude app (web, desktop or mobile)

1. Download the **[skill ZIP](https://github.com/thiagontijo/guessitup/archive/refs/heads/main.zip)** (same as the green **Code → Download ZIP** button).
2. In Claude, open **Settings → Capabilities → Skills** (or **Customize → Skills**) and upload the ZIP.
3. Ask: "guessitup, today's games".

### In Claude Code

Needs Python 3 (standard library only).

```bash
git clone https://github.com/thiagontijo/guessitup ~/.claude/skills/guessitup
```

To update later:

```bash
cd ~/.claude/skills/guessitup && git pull
```

### Language

The skill answers in **English** by default (dollar amounts in betting-app format: "bet $20, get back $38"). Want Portuguese? Just ask ("responde em português") or write to it in Portuguese, and it stays in Portuguese until you ask otherwise. Other languages work the same way.

### Example requests

- `/guessitup this weekend's Premier League games`
- "who wins Lakers vs Celtics? give me both sides' chances"
- "picks for Saturday's UFC card"
- "build parlay options for tonight on Hard Rock and compare with other apps"
- "follow my bets and tell me if I should hold or cash out"
- "turn on the bots with $500 each, Herman max 2 bets a day"

## Structure

```
guessitup/
├── SKILL.md                 skill instructions (flow, rules, report format)
├── references/esportes.md   metrics, sources and model per sport
├── references/apostas.md    Kalshi, parlays, hedge, live advisor and lessons learned
├── references/ficha-jogo.md full game card format
├── references/handicap-total.md  spreads and totals with the 10,000-game simulation
├── references/bots.md       test bots Chico, Arnaldo and Herman (play money)
├── scripts/model.py         numeric tools (standard library only)
└── scripts/bots.py          test bots: rules, limits, proposals, follow mode, scoreboard
```

### `scripts/model.py`

| Command | What it does |
|---|---|
| `poisson --home 1.6 --away 1.1` | expected goals → 1X2, double chance, draw no bet, over/under, both teams score, scorelines (Dixon-Coles correction) |
| `decay --values ... --half-life 5` | time-decayed average (recent games weigh more) |
| `strength --gf --ga --league-gf` | attack and defense strength relative to the league |
| `elo --a --b --adv --draw` | Elo probabilities (with 1X2 conversion) |
| `elo-update` | updates Elo after a result, with margin multiplier |
| `devig --odds ...` | removes the bookmaker margin: proportional, power and Shin |
| `normal --diff --sd --line` | points sports: chance to win and to cover the spread |
| `tennis --pa --pb --best-of` | tennis: serve points won → hold, set, match and set scores (Markov chain) |
| `log5 --a --b --home` | baseball and similar: each side's win% → head-to-head chance, with home edge |
| `blend --probs --weights` | combines models and measures disagreement |
| `value --prob --odds` | expected value and fractional Kelly (0.25x, 5% cap) |
| `clv --taken --closing` | closing line value |
| `combo --probs ... --stake --pays` | parlay chance and minimum payout to be worth it |
| `hedge --stake --payout --opp-pct` | full and half hedge: how much to bet on the other side and the locked profit |
| `sim --sport --market-spread --market-total ...` | simulates 10,000 games: winner, spread, over/under, margin and fair price |
| `expected --sport nba or nfl ...` | expected score from season stats (pace, offense, defense, rest, injuries) |
| `grade --prob --app-pct --divergence --data --games` | A–D confidence grade with reasons |
| `livewp --lead --minutes-left --spread --app-pct` | live win probability (NFL/NBA) and HOLD / CONSIDER CASHING OUT signal |
| `odds --odd --prob` | converts American, decimal or % odds to dollars and gives the minimum price |
| `compare --apps App=odd ... --prob` | same bet across apps: which pays more |
| `aggregate --home --away --lead` | two-leg knockout ties: chance to advance on aggregate |
| `temper --probs --k` | recalibrates probabilities with the "temperature" learned from past results |
| `ledger add/result/void/pending/report/calibrate` | pick log and calibration: Brier, skill score, vs market, expected vs actual hits, by sport/confidence, ROI, CLV |

### `scripts/bots.py`

| Command | What it does |
|---|---|
| `init --bank 1000` | turns on the three bots with the same bankroll |
| `config --bot herman --bank 200 --max-bets 2 --max-dollars 30` | each bot's own bankroll and daily limits |
| `check` / `add` | checks a bet against the bot's rules and logs it (stake calculated automatically) |
| `skip --bot chico --reason "..."` | the bot sits the day out and says why |
| `offers` | today's proposals from each bot |
| `follow --id 3 --amount 15` / `follow --pass-day` | you follow a proposal with your own amount, or skip the day |
| `settle` / `pending` / `report` | settles results (including the bets you followed) and shows the scoreboard |

The pick log lives in `ledger/predictions.jsonl` and the bots in `bots/` (both outside git). After the games, ask "compare the results": the skill finds the scores, logs them and shows whether the percentages held up. With fewer than ~30 picks, nothing is conclusive.

## Sources and inspiration

Techniques rewritten from scratch, inspired by open projects: [penaltyblog](https://github.com/martineastwood/penaltyblog) (goal models, ratings, metrics), [Kairos](https://github.com/m1r4g3-code/kairos) (ledger, CLV, capped Kelly, market anchoring) and [GoallineIQ](https://github.com/gmalbert/world-cup) (Elo + Poisson).

## License

MIT
