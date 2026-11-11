# Guessitup Arena

**Open the app: https://thiagontijo.github.io/guessitup/**

A small web app you can install on your phone. Three bots (Chico, Arnaldo and Herman) bet **play money**
on real games every day. The app shows their bets, follows the real scores live and tells you what you
would have won or lost by following them with your own amount per bet.

- **Install on iPhone:** open the link in Safari, tap Share, then "Add to Home Screen".
- **Install on Android:** open the link in Chrome and tap "Install the app".
- Portuguese, English and Spanish. Your settings stay on your device.

Play money only. The bots place no real bets, the app is not a sportsbook and it does not point to one.
Probabilities, not guarantees. For adults 18 and over.

The bots run on the [Guessitup skill for Claude](https://github.com/thiagontijo/guessitup) (the `main` branch
of this repository). This `gh-pages` branch holds only the app.

## How it works

| File | What it is |
|---|---|
| `index.html` | The whole app (no build step, no dependencies) |
| `data.json` | The bots' bets and results. The only thing that changes day to day |
| `tools/arena.py` | Helper that edits `data.json` (adds bets, settles games, prints the scoreboard) |
| `sw.js`, `manifest.webmanifest`, `icons/` | What makes it installable and available offline |
| `fonts/bsd-800.woff2` | Big Shoulders Display, SIL Open Font License 1.1 |

Live scores come straight from a public scoreboard feed in your browser. The app asks for them every
20 to 30 seconds while a game is on, and stops when the round is over. "Chance now" is an estimate from the
score and the time left (a normal model for basketball, football, hockey and soccer).

## Daily update

```bash
python3 tools/arena.py pending                      # games still open
python3 tools/arena.py game --lg nba --team Knicks --opp Bucks --score 112-101   # settle a game
python3 tools/arena.py add --date 2026-11-11 --bot chico --price 0.715 \
    --leg "nba|Knicks|Cavaliers|2026-11-12T00:00Z|0.78"
python3 tools/arena.py say --date 2026-11-11 --bot chico --pt "..." --en "..." --es "..."
python3 tools/arena.py report --you 100
python3 tools/arena.py validate
```

`python3 tools/arena.py --help` and the top of the file explain the leg format and the bots' rules.
