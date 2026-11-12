# tiny-chess-01 — the strongest chess engine in 4 KB

Entry for the make.fun bounty "tiny-chess-01" ($500): build the strongest
Python chess engine in at most 4,096 bytes.

## The engine

`main.py` (3,938 bytes) unpacks an lzma payload and runs it. The engine
itself is a 0x88 board with negamax alpha-beta search, quiescence search,
a transposition table, killer-move ordering and piece-square evaluation,
under a fixed 60,000-node budget per move — never a clock, so the trial's
replay matches. Python 3.13 standard library only; it talks to the env
alone over HTTP and calls no model.

The readable development version is `engine.py` in the author's workspace
(`tiny-chess-01-dev/`); `pack.py` next to it reproduces `main.py` byte for
byte from it.

## Verification (local, 2026-11-12)

- Move generation: perft(1..3) from the start position = 20 / 400 / 8,902,
  Kiwipete perft(1..2) = 48 / 2,039 — all correct.
- Packed `main.py` picks the same move as the dev engine on start, middle
  game and tactical test positions, is deterministic across runs, and its
  slowest tested move took 2.4 s (limit 10 s/move).
- Played against the kit's local env server on practice trial-0 (see the
  trial log in the workspace).

## License

MIT. See `LICENSE`.
