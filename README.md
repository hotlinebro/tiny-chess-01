# tiny-chess-01 — engine10 (4KB Sunfish-style engine)

A compact 4KB Sunfish-style chess engine, packed into a single `main.py` (3,987 bytes).

- Full PeSTO tapered evaluation
- Alpha-beta search with PVS, LMR, transposition table, quiescence, and null-move pruning
- Fixed 70,000 nodes per move, deterministic — same position, same move

## Trial scores

- Practice trial 0: Elo 1,191 (gate floor 1,154 — passed)
- General Elo: 1,365 (Sunfish-class strength in under 4KB)

## Run

```sh
python main.py
```
