import json, os, time
import urllib.request as u
from urllib.error import HTTPError as HE

# Sunfish-style 120-char board, PSTs packed as strings (a1-first, even-rounded).
# decode: [(ord(c)-64)*2 for c in s]. 7 tables: P N B R Q K-mid K-end.
# Tables retuned to Round 4 formula values (gentle, proven 1384 Elo):
# P flat rank bonus, N/B/Q/E centrality, R 7th-rank, K back-rank + taper.
_PS = {
 'P': "@@@@@@@@AAAAAAAACCCCCCCCFFFFFFFFJJJJJJJJPPPPPPPP[[[[[[[[@@@@@@@@",
 'N': "8:=??=:8:=?BB?=:=?BEEB?=?BEGGEB??BEGGEB?=?BEEB?=:=?BB?=:8:=??=:8",
 'B': ";=?BB?=;=?BDDB?=?BDFFDB?BDFHHFDBBDFHHFDB?BDFFDB?=?BDDB?=;=?BB?=;",
 'R': "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@GGGGGGGG@@@@@@@@",
 'Q': "=>?@@?>=>?@AA@?>?@ABBA@?@ABCCBA@@ABCCBA@?@ABBA@?>?@AA@?>=>?@@?>=",
 'K': "ILE@@ELI9999999933333333,,,,,,,,))))))))))))))))))))))))))))))))",
 'E': "58<??<858<?CC?<8<?CGGC?<?CGJJGC??CGJJGC?<?CGGC?<8<?CC?<858<??<85"}
PST = {k: [(ord(c) - 64) * 2 for c in s] for k, s in _PS.items()}
VAL = {c: v for c, v in zip('PNBRQKpnbrqk', [100, 320, 330, 500, 900, 0] * 2)}
# 120-board index -> 64-index (a1=0); -1 off board.
A = [((9 - s // 10) * 8 + s % 10 - 1) if 0 <= s % 10 - 1 < 8 and 0 <= 9 - s // 10 < 8 else -1 for s in range(120)]
INF = 1000000
MATE = 100000
LIM = 60000
KD = (-11, -10, -9, -1, 1, 9, 10, 11)
GD = (-21, -19, -12, -8, 8, 12, 19, 21)
BD = (-11, -9, 9, 11)
RD = (-10, -1, 1, 10)
ENV = os.environ.get("MAKEFUN_ENV_URL")
# state
B = ""
S = 0
T = 0
C = 0
E = -1
H = 0
K = [0, 0]
M = [0, 0]
U = []
TT = {}
ND = 0
AB = False
T0 = 0.0


def atk(sq, by):
    b = B
    if by == 0:
        for s in (sq + 11, sq + 9):
            if b[s] == 'P':
                return True
    else:
        for s in (sq - 11, sq - 9):
            if b[s] == 'p':
                return True
    pc = 'K' if by == 0 else 'k'
    for d in KD:
        if b[sq + d] == pc:
            return True
    pc = 'N' if by == 0 else 'n'
    for d in GD:
        if b[sq + d] == pc:
            return True
    for d in BD:
        s = sq + d
        while b[s] > ' ':
            p = b[s]
            if p != '.':
                if p == ('B' if by == 0 else 'b') or p == ('Q' if by == 0 else 'q'):
                    return True
                break
            s += d
    for d in RD:
        s = sq + d
        while b[s] > ' ':
            p = b[s]
            if p != '.':
                if p == ('R' if by == 0 else 'r') or p == ('Q' if by == 0 else 'q'):
                    return True
                break
            s += d
    return False


def chk():
    return atk(K[T], T ^ 1)


def gen():
    ms = []
    b = B
    them = T ^ 1
    up = 'P' if T == 0 else 'p'
    dr = -10 if T == 0 else 10
    sr = 8 if T == 0 else 3
    pr = 3 if T == 0 else 8
    for frm in range(120):
        pc = b[frm]
        if pc == ' ' or pc == '\n' or pc == '.':
            continue
        if (pc.isupper()) != (T == 0):
            continue
        t = pc.upper()
        if t == 'P':
            one = frm + dr
            if b[one] == '.':
                if frm // 10 == pr:
                    for pt in (5, 4, 3, 2):
                        ms.append(frm | (one << 7) | (pt << 14))
                else:
                    ms.append(frm | (one << 7))
                    if frm // 10 == sr:
                        two = one + dr
                        if b[two] == '.':
                            ms.append(frm | (two << 7))
            for to in (one - 1, one + 1):
                if b[to] <= ' ':
                    continue
                tgt = b[to]
                if tgt != '.' and (tgt.isupper()) != (T == 0):
                    if frm // 10 == pr:
                        for pt in (5, 4, 3, 2):
                            ms.append(frm | (to << 7) | (pt << 14))
                    else:
                        ms.append(frm | (to << 7))
                elif to == E and E != -1:
                    ms.append(frm | (to << 7) | (1 << 17))
        elif t == 'N' or t == 'K':
            for d in (GD if t == 'N' else KD):
                to = frm + d
                if b[to] <= ' ':
                    continue
                tgt = b[to]
                if tgt == '.' or (tgt.isupper()) != (T == 0):
                    ms.append(frm | (to << 7))
        else:
            ds = BD if t == 'B' else RD if t == 'R' else BD + RD
            for d in ds:
                to = frm + d
                while b[to] > ' ':
                    tgt = b[to]
                    if tgt == '.':
                        ms.append(frm | (to << 7))
                    else:
                        if (tgt.isupper()) != (T == 0):
                            ms.append(frm | (to << 7))
                        break
                    to += d
    if not chk():
        if T == 0:
            _cs = ((1, 95, 97, 98), (2, 95, 93, 91))
        else:
            _cs = ((4, 25, 27, 28), (8, 25, 23, 21))
        for bit, kf, kt, rf in _cs:
            if not (C & bit):
                continue
            if b[kf] != ('K' if T == 0 else 'k'):
                continue
            if b[rf] != ('R' if T == 0 else 'r'):
                continue
            ks = 1 if kt > kf else -1
            if b[kf + ks] != '.' or b[kt] != '.':
                continue
            if ks < 0 and b[kt - 1] != '.':
                continue
            if atk(kf, them) or atk(kf + ks, them) or atk(kt, them):
                continue
            ms.append(kf | (kt << 7) | (1 << 18))
    return ms


def make(m):
    global B, S, T, C, E, H, M
    frm = m & 127
    to = (m >> 7) & 127
    pc = B[frm]
    up = pc.upper()
    npc = pc
    pr = (m >> 14) & 7
    if pr:
        npc = 'PNBRQK'[pr - 1] if T == 0 else 'pnbrqk'[pr - 1]
    cap = B[to]
    csq = to
    if (m >> 17) & 1:
        csq = to + 10 if T == 0 else to - 10
        cap = B[csq]
    b0 = B
    s0 = S
    c0 = C
    e0 = E
    h0 = H
    m0 = M[0] + M[1] * 100000
    k0 = K[T]
    # incremental score (S is white-perspective). sg flips the sign for black.
    i0 = A[frm]
    i1 = A[to]
    sg = 1 if T == 0 else -1
    j0 = i0 if T == 0 else i0 ^ 56
    j1 = i1 if T == 0 else i1 ^ 56
    S += sg * (VAL[npc] + PST[npc.upper()][j1] - VAL[pc] - PST[up][j0])
    if cap != '.':
        ci = A[csq]
        cj = ci ^ 56 if T == 0 else ci
        S += sg * (VAL[cap] + PST[cap.upper()][cj])
        if cap.upper() != 'P':
            M[T ^ 1] -= VAL[cap]
    if pr and up == 'P':
        M[T] += VAL[npc] - 100
    nb = b0[:frm] + '.' + b0[frm + 1:]
    nb = nb[:to] + npc + nb[to + 1:]
    if cap != '.' and (m >> 17) & 1:
        nb = nb[:csq] + '.' + nb[csq + 1:]
    if (m >> 18) & 1:
        rf = to + 1 if to in (97, 27) else to - 2
        rt = to - 1 if to in (97, 27) else to + 1
        rpc = nb[rf]
        rk0 = A[rf] if T == 0 else A[rf] ^ 56
        rk1 = A[rt] if T == 0 else A[rt] ^ 56
        S += sg * (PST['R'][rk1] - PST['R'][rk0])
        nb = nb[:rf] + '.' + nb[rf + 1:]
        nb = nb[:rt] + rpc + nb[rt + 1:]
    B = nb
    E = (frm + to) // 2 if up == 'P' and abs(to - frm) == 20 else -1
    H = 0 if up == 'P' or cap != '.' else H + 1
    if up == 'K':
        K[T] = to
        C &= ~3 if T == 0 else ~12
    for s, b in ((91, 2), (98, 1), (21, 8), (28, 4)):
        if frm == s or to == s:
            C &= ~b
    U.append((m, cap, b0, s0, c0, e0, h0, m0, k0))
    T ^= 1
    if atk(K[T ^ 1], T):
        unmake()
        return False
    return True


def unmake():
    global B, S, T, C, E, H, M
    m, cap, b0, s0, c0, e0, h0, m0, k0 = U.pop()
    T ^= 1
    B = b0
    S = s0
    C = c0
    E = e0
    H = h0
    M = [m0 % 100000, m0 // 100000]
    K[T] = k0


def ev():
    ph = M[0] + M[1]
    if ph > 6400:
        ph = 6400
    s = S
    for col in (0, 1):
        sq = K[col]
        i = A[sq] if col == 0 else A[sq] ^ 56
        mg = PST['K'][i]
        tp = (mg * ph + PST['E'][i] * (6400 - ph)) // 6400 - mg
        s += tp if col == 0 else -tp
    # bishop pair +30 (Round 4 term; board scan is C-speed, node budget fixed)
    s += 30 * ((B.count('B') > 1) - (B.count('b') > 1))
    return s if T == 0 else -s


def order(ms, ttm):
    def sc(m):
        if m == ttm:
            return 1 << 20
        to = (m >> 7) & 127
        tgt = B[to]
        s = 0
        if (m >> 17) & 1:
            s = 10000 + 1000 - 100
        elif tgt != '.':
            s = 10000 + 10 * VAL[tgt] - VAL[B[m & 127]]
        pr = (m >> 14) & 7
        if pr:
            s += 9000 + VAL['PNBRQK'[pr - 1]]
        return s
    ms.sort(key=sc, reverse=True)


def qs(a, b, ply):
    global ND, AB
    ND += 1
    if ND >= LIM:
        AB = True
        return 0
    if ply >= 100:
        return ev()
    c = chk()
    best = -INF
    if not c:
        best = ev()
        if best >= b:
            return best
        if best > a:
            a = best
    ms = gen()
    order(ms, 0)
    legal = 0
    for m in ms:
        to = (m >> 7) & 127
        if c or B[to] != '.' or (m >> 14) & 7 or (m >> 17) & 1:
            if make(m):
                legal += 1
                s = -qs(-b, -a, ply + 1)
                unmake()
                if AB:
                    return 0
                if s > best:
                    best = s
                if best >= b:
                    return best
                if best > a:
                    a = best
    if c and legal == 0:
        return -MATE + ply
    return best


def ab(d, a, b, ply):
    global ND, AB, H, E, T
    if ply > 0 and H >= 100:
        return 0
    if d <= 0:
        return qs(a, b, ply)
    ND += 1
    if ND >= LIM:
        AB = True
        return 0
    key = (B, T, C, E)
    e = TT.get(key)
    ttm = 0
    if e:
        dep, fl, sc, mv = e
        if dep >= d:
            s = sc - ply if sc > MATE - 100 else sc + ply if sc < -MATE + 100 else sc
            if fl == 1:
                return s
            if fl == 2 and s >= b:
                return s
            if fl == 3 and s <= a:
                return s
        ttm = mv
    c = chk()
    # NMP: depth>=3, not in check, side to move has non-pawn pieces (zugzwang guard)
    # R = 2 + depth//6 (spec max; R=3 at depth>=6, matching Round 4's aggression)
    if d >= 3 and not c and M[T] > 0:
        e0 = E
        h0 = H
        E = -1
        H += 1
        T ^= 1
        s = -ab(d - 2 - d // 6, -b, -b + 1, ply + 1)
        T ^= 1
        E = e0
        H = h0
        if AB:
            return 0
        if s >= b:
            return b
    ms = gen()
    order(ms, ttm)
    best = -INF
    bestm = 0
    legal = 0
    cnt = 0
    a0 = a
    for m in ms:
        to = (m >> 7) & 127
        tac = B[to] != '.' or (m >> 14) & 7 or (m >> 17) & 1
        if make(m):
            legal += 1
            cnt += 1
            # LMR: non-tactical, moves_searched>=4, depth>=3: reduce 1 ply,
            # zero-window; re-search full depth if score > alpha.
            if not tac and cnt >= 4 and d >= 3 and not c:
                s = -ab(d - 2, -a - 1, -a, ply + 1)
                if AB:
                    unmake()
                    return 0
                if s > a:
                    s = -ab(d - 1, -b, -a, ply + 1)
            else:
                s = -ab(d - 1, -b, -a, ply + 1)
            unmake()
            if AB:
                return 0
            if s > best:
                best = s
                bestm = m
            if best >= b:
                break
            if best > a:
                a = best
    if legal == 0:
        return -MATE + ply if chk() else 0
    fl = 3 if best <= a0 else 2 if best >= b else 1
    TT[key] = (d, fl, best + ply if best > MATE - 100 else best - ply if best < -MATE + 100 else best, bestm)
    return best


def root(legal):
    global ND, AB, T0
    ND = 0
    AB = False
    T0 = time.monotonic()
    om = [[m, 0] for m in legal]
    bestm = legal[0]
    for d in range(1, 100):
        om = sorted(om, key=lambda x: -x[1])
        a = -MATE - 1
        for x in om:
            m = x[0]
            if make(m):
                s = -ab(d - 1, -MATE - 1, -a, 1)
                unmake()
                if AB:
                    return bestm
                x[1] = s
                if s > a:
                    a = s
                    bestm = m
        if om[0][1] >= MATE - 100:
            break
        # safety valve only: node budget is the deterministic limit;
        # time never decides the move unless a move runs pathologically long.
        if time.monotonic() - T0 > 8.0:
            break
    return bestm


def setup(fen):
    global B, S, T, C, E, H, K, M, U, TT
    rows = [' ' * 9 + '\n'] * 2
    p = fen.split()
    rk = p[0].split('/')
    for r, row in enumerate(rk):
        line = ' '
        f = 0
        for ch in row:
            if ch.isdigit():
                line += '.' * int(ch)
                f += int(ch)
            else:
                line += ch
                f += 1
        rows.append(line + '\n')
    rows += [' ' * 9 + '\n'] * 2
    B = ''.join(rows)
    T = 0 if p[1] == 'w' else 1
    C = 0
    for ch in p[2]:
        if ch in 'KQkq':
            C |= 1 << 'KQkq'.index(ch)
    E = -1 if p[3] == '-' else (10 - int(p[3][1])) * 10 + (ord(p[3][0]) - 96)
    H = int(p[4])
    K = [0, 0]
    M = [0, 0]
    S = 0
    U = []
    for sq in range(120):
        pc = B[sq]
        if pc == ' ' or pc == '\n' or pc == '.':
            continue
        i = A[sq]
        up = pc.upper()
        if up == 'K':
            K[0 if pc.isupper() else 1] = sq
            continue
        if pc.isupper():
            S += VAL[pc] + PST[up][i]
            if up != 'P':
                M[0] += VAL[pc]
        else:
            S -= VAL[pc] + PST[up][i ^ 56]
            if up != 'P':
                M[1] += VAL[pc]
    # king mg PST into score
    for col in (0, 1):
        i = A[K[col]] if col == 0 else A[K[col]] ^ 56
        if col == 0:
            S += PST['K'][i]
        else:
            S -= PST['K'][i]


def uci(m):
    def nm(sq):
        return chr(97 + (sq % 10 - 1)) + str(10 - sq // 10)
    s = nm(m & 127) + nm((m >> 7) & 127)
    pr = (m >> 14) & 7
    if pr:
        s += 'nbrq'[pr - 2]
    return s


def post(path, data):
    req = u.Request(ENV + path, json.dumps(data).encode(),
                    {'content-type': 'application/json'}, method='POST')
    try:
        with u.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except HE as e:
        return {'error': e.code}


def main():
    global TT
    if not ENV:
        raise SystemExit('no ENV')
    last = -1
    while True:
        g = post('/game', {})
        if g.get('status') == 'done':
            break
        if 'error' in g:
            raise SystemExit(f"/game failed: {g}")
        if g['game'] != last:
            TT.clear()
            last = g['game']
        while g.get('status') == 'your_move':
            setup(g['fen'])
            legal = [m for m in gen() if make(m) and not unmake()]
            if not legal:
                raise SystemExit('no legal move')
            m = root(legal)
            u = uci(m)
            lm = g['legal_moves']
            if u not in lm:
                u = lm[0]
            g = post('/move', {'game': g['game'], 'move': u})
            if 'error' in g:
                g = post('/move', {'game': g['game'], 'move': lm[0]})


if __name__ == '__main__':
    main()
