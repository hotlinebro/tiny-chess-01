# tiny-chess-01 — engine140k (4KB Sunfish-style engine)

[![make.fun bounty](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)

A compact 4KB Sunfish-style chess engine, packed into a single `main.py` (3,912 bytes).

- Full PeSTO tapered evaluation
- Alpha-beta search with PVS, LMR, transposition table, quiescence, and null-move pruning
- Fixed 140,000 nodes per move, deterministic — same position, same move

## Trial scores

- Practice trial 0: Elo 1,364 (gate floor 1,154 — passed)
- Practice trial 1: Elo 1,364
- Practice trial 2: Elo 2,112 (perfect 6W)
- General Elo: 1,738 (+373 vs Sunfish baseline 1,365)

## Run

```sh
python main.py
```

Built for the [make.fun tiny-chess-01 bounty](https://make.fun/bounty/tiny-chess-01). Referral: 5rtys7wh.
