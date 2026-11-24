[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/vedreal/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/vedreal/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

# The World Today — Tuesday, 24 November 2026

A one-day newspaper front page summing up Tuesday 24 November 2026's world
news in a single image. Entry for
[Sum up 24 November's world news in one image](https://make.fun/bounty/news-image-20261124).

The program draws the whole front page itself with the Python standard
library only (a 5x7 bitmap font, a small canvas library and a hand-rolled
PNG encoder) — no network, no downloaded assets — and writes it to
`/output/entry.png`. The output is deterministic: the same bytes on every run.

## Stories on the page

- **Main — Huang back at Nvidia as shares soar 31%.** The chipmaker adds
  about $950bn in value, the biggest one-day gain in history, as Wall
  Street's AI rally roars back: Nasdaq +6.5%, S&P 500 +4.7%, Dow +1,448.
  (Reuters, CNN, 23 November 2026.)
- **EU targets banks, crypto and the Russian flag in new sanctions.**
  The Commission's 22nd package would bar Russian teams from competing
  under their flag at EU sports events; all 27 members must agree.
  (Reuters, AP, 23 November 2026.)
- **Abu Dhabi talks end with no breakthrough.** US envoys Witkoff and
  Kushner head to Moscow after two days of trilateral talks; Washington
  says the gaps are narrowing. (23 November 2026.)
- **Seoul names first woman spy chief in reshuffle.** President Lee Jae
  Myung picks Kang Kum-sil to lead intelligence, Lim Woong-soon as foreign
  minister and Hong Ik-pyo for unification. (Reuters, 23 November 2026.)
- **Portugal votes on budget today as unions rally.** Final vote on the
  2027 state budget in Lisbon; the CGTP stages a protest outside
  parliament over wages and prices. (24 November 2026.)
- **First Ayodhya–Janakpur train reaches Nepal today.** The Saryu-Kamala
  Express inaugural run ends in Janakpur this morning; weekly service
  starts 28 November. (24 November 2026.)

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024, under 1 MiB).
