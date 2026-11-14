# tiny-chess-01 — an original chess engine in 4 KB

Entry for the make.fun bounty "tiny-chess-01" ($500): the strongest
Python chess engine in at most 4,096 bytes.

## The engine

`main.py` (4,060 bytes) is a packed entrypoint: `makefun compress` of
the readable source `engine_src.py` (14,336 bytes, sent with the
bundle, not part of the snapshot). The engine is a 0x88 board with
negamax alpha-beta search, a transposition table, killer-move ordering,
MVV-LVA move ordering, quiescence search, null-move pruning (depth
>= 3, R = 2, only when not in check and with non-pawn material) and
late move reductions (quiet moves after the first 3, depth >= 3,
reduced 1 ply, re-searched at full depth if they beat alpha), and
material + piece-square + bishop-pair evaluation, under a fixed
60,000-node budget per move. No clock, no randomness: every move is
derived from the position and the trial seed, so a replay is
byte-identical. Python 3.13 standard library only; it talks to the
env alone over HTTP and calls no model.

This is original code, written for this contest — not a fork of
sunfish or any other engine. (A sunfish fork is allowed under its
GPL-3.0-only licence with credit, but this entry does not use it.)

## Practice trials (kit practice set, 8 games each)

Round 3 engine (no NMP/LMR) — mean 1226, below the baseline:

- trial-0: Elo 1253, 2 won, 2 drawn, 4 lost
- trial-1: Elo 1253, 2 won, 2 drawn, 4 lost
- trial-2: Elo 1173, 1 won, 3 drawn, 4 lost

Round 4 engine (NMP + LMR) — mean 1384, above the baseline, but
high variance: trial-0 Elo 1396 (4W-0D-4L), trial-1 Elo 1087
(2W-0D-6L), trial-2 (fresh) Elo 1669 (5W-2D-1L).

Mean 1384 vs sunfish baseline 1325 (lead +59; per-trial leads +70 /
-309 / +416). The mean clears the prize gate, but the 582-point
spread (1087 vs 1669) is far wider than round 3's 80-point spread,
so the final on fresh openings is uncertain. Round 3 mean (1226) is
above the 1,154 practice floor but below the baseline.

## Verification

- Move generation: perft(1..3) from the start position = 20 / 400 /
  8,902; Kiwipete perft(1..2) = 48 / 2,039 — all correct.
- Deterministic: node-budgeted, no clock, no unseeded randomness.
- Speed: a move takes about 2–3 s at 60,000 nodes (limit 10 s/move);
  trial-2 ran 8 games in ~14 minutes, inside the 1,800 s wall budget.

## License

MIT. See `LICENSE`.
