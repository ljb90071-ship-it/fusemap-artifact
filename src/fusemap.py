"""Exact small-graph FuseMap reference. Integer edge scores; rational objectives."""
from functools import lru_cache
from fractions import Fraction
from itertools import product


def assignment(n, p, weights):
    """Partial maximum matching and complementary optimal dual, exponential in p."""
    if p > 20:
        raise ValueError('Reference backend supports at most 20 columns per component')
    @lru_cache(None)
    def dp(i, used):
        if i == n:
            return 0, ()
        score, tail = dp(i + 1, used)
        best = score, (-1,) + tail
        for j in range(p):
            if (i, j) in weights and not (used >> j) & 1:
                score, tail = dp(i + 1, used | (1 << j))
                candidate = score + weights[i, j], (j,) + tail
                if candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1] < best[1]):
                    best = candidate
        return best
    score, matching = dp(0, 0)
    owner = {j: i for i, j in enumerate(matching) if j >= 0}
    u = [0] * n
    # Longest-path relaxation of complementary-slackness difference constraints.
    for step in range(n + 1):
        changed = False
        for (i, j), w in sorted(weights.items()):
            lower = u[owner[j]] + w - weights[owner[j], j] if j in owner else w
            if lower > u[i]:
                u[i] = lower
                changed = True
        if not changed:
            break
    else:
        raise ArithmeticError('Positive dual constraint cycle')
    v = [weights[owner[j], j] - u[owner[j]] if j in owner else 0 for j in range(p)]
    assert min(u + v, default=0) >= 0
    assert all(u[i] + v[j] >= w for (i, j), w in weights.items())
    assert sum(u) + sum(v) == score
    return {'score': score, 'matching': matching, 'u': u, 'v': v}


def bounds(weights, state):
    u, v = state['u'], state['v']
    row = [max([0] + [w - v[j] for (r, j), w in weights.items() if r == i]) for i in range(len(u))]
    col = [max([0] + [w - u[i] for (i, c), w in weights.items() if c == j]) for j in range(len(v))]
    transfer = sum(u) + sum(v) + min(sum(max(0, a-b) for a, b in zip(row, u)), sum(max(0, a-b) for a, b in zip(col, v)))
    reset = min(sum(row) + sum(v), sum(u) + sum(col))
    zero = min(sum(max([0] + [w for (r, j), w in weights.items() if r == i]) for i in range(len(u))), sum(max([0] + [w for (i, c), w in weights.items() if c == j]) for j in range(len(v))))
    lower = max(0, sum(weights[i, j] for i, j in enumerate(state['matching']) if j >= 0))
    return {'transfer': transfer, 'reset': reset, 'zero': zero, 'lower': lower}


def valid(mapping, candidates):
    nonnull = [c for c in mapping if c != -1]
    return len(nonnull) == len(set(nonnull)) and all(c in candidates[k] for k, c in enumerate(mapping))


def neighbors(mapping, candidates):
    result = set()
    for k, choices in enumerate(candidates):
        for c in choices:
            m = list(mapping); m[k] = c
            if tuple(m) != mapping and valid(m, candidates): result.add(tuple(m))
    for k in range(len(mapping)):
        for l in range(k + 1, len(mapping)):
            m = list(mapping); m[k], m[l] = m[l], m[k]
            if tuple(m) != mapping and valid(m, candidates): result.add(tuple(m))
    return sorted(result)


class Problem:
    def __init__(self, data):
        self.n, self.p = data['rows'], data['columns']
        if min(self.n, self.p) <= 0: raise ValueError('Nonempty tables required')
        self.candidates = data['candidates']
        self.metadata = data['metadata']
        self.edges = data['edges']
        self.scale = Fraction(str(data['lambda'])) / min(self.n, self.p)
        if self.scale <= 0: raise ValueError('Positive lambda required')
        assert self.candidates and all(-1 in c for c in self.candidates)
        assert len({(e['i'], e['j']) for e in self.edges}) == len(self.edges)
        assert all(0 <= e['i'] < self.n and 0 <= e['j'] < self.p for e in self.edges)
        assert all(isinstance(e['base'], int) and all(isinstance(x, int) for x in e['contributions'].values()) for e in self.edges)
        pending = set(range(len(self.edges))); self.components = []
        while pending:
            ids = {min(pending)}; rows = set(); cols = set()
            while True:
                rows |= {self.edges[e]['i'] for e in ids}; cols |= {self.edges[e]['j'] for e in ids}
                new = {e for e in pending if self.edges[e]['i'] in rows or self.edges[e]['j'] in cols}
                if new <= ids: break
                ids |= new
            pending -= ids
            self.components.append((sorted(rows), sorted(cols), sorted(ids)))

    def schema(self, m):
        return sum(Fraction(str(self.metadata[k][str(c)])) for k, c in enumerate(m)) / len(m)

    def weights(self, m):
        result = []
        for rows, cols, ids in self.components:
            result.append({(rows.index(self.edges[e]['i']), cols.index(self.edges[e]['j'])): self.edges[e]['base'] + sum(self.edges[e]['contributions'].get(f'{k}:{c}', 0) for k, c in enumerate(m) if c != -1) for e in ids})
        return result

    def solve(self, index, weights):
        rows, cols, _ = self.components[index]
        return assignment(len(rows), len(cols), weights)

    def decode(self, mapping):
        """Fresh deterministic DP decoding, independent of internal search states."""
        pairs = []
        for index, weights in enumerate(self.weights(mapping)):
            rows, cols, _ = self.components[index]
            state = self.solve(index, weights)
            pairs.extend([rows[i], cols[j]] for i, j in enumerate(state['matching']) if j >= 0)
        return sorted(pairs)

    def restart_starts(self, limit=8, metadata_unit=1):
        """Distinct metadata-diversified starts; metadata_unit is one logit unit."""
        mappings = sorted(m for m in product(*self.candidates) if valid(m, self.candidates))
        chosen = []
        while len(chosen) < min(limit, len(mappings)):
            r = len(chosen)
            def score(m):
                if not r: return self.schema(m)
                agreements = sum(c == previous[k] for previous in chosen for k,c in enumerate(m))
                return self.schema(m) - Fraction(str(metadata_unit)) * Fraction(agreements, r*len(m))
            remaining = [m for m in mappings if m not in chosen]
            chosen.append(max(remaining, key=score))
        return chosen

    def alternating_restarts(self, limit=8, metadata_unit=1):
        """Complete every requested start; this is not a wall-clock scheduler."""
        starts = self.restart_starts(limit, metadata_unit)
        best = None
        endpoints = []
        for start in starts:
            answer = self.alternating(start)
            endpoints.append({'start':list(start), 'mapping':answer['mapping'], 'objective':answer['objective']})
            if best is None or Fraction(answer['objective']) > Fraction(best['objective']):
                best = answer
        return {'best':best, 'starts':[list(m) for m in starts], 'endpoints':endpoints}

    def alternating(self, start=None):
        """Exact schema and row blocks, retaining the previous block on equality."""
        mappings = sorted(m for m in product(*self.candidates) if valid(m, self.candidates))
        current = tuple(start) if start is not None else max(mappings, key=self.schema)
        if current not in mappings: raise ValueError('Invalid initial mapping')
        states = [self.solve(i, w) for i, w in enumerate(self.weights(current))]
        objective = self.schema(current) + self.scale * sum(s['score'] for s in states)
        path = [list(current)]
        while True:
            chosen, best = current, objective
            for candidate in mappings:
                fixed = sum(sum(w[i,j] for i,j in enumerate(state['matching']) if j >= 0)
                            for w,state in zip(self.weights(candidate), states))
                value = self.schema(candidate) + self.scale * fixed
                if value > best: chosen, best = candidate, value
            if chosen == current: break
            new_states = [self.solve(i,w) for i,w in enumerate(self.weights(chosen))]
            # Keeping the previous matching on a tied row block is feasible.
            for i,(w,state) in enumerate(zip(self.weights(chosen), states)):
                old_score = sum(w[r,c] for r,c in enumerate(state['matching']) if c >= 0)
                if old_score == new_states[i]['score']:
                    new_states[i]['matching'] = state['matching']
            current, states = chosen, new_states
            objective = self.schema(current) + self.scale * sum(s['score'] for s in states)
            path.append(list(current))
        return {'mapping':list(current), 'objective':str(objective), 'path':path,
                'row_pairs':self.decode(current)}

    def search(self, mode='transfer'):
        if mode not in ('full', 'transfer', 'zero'): raise ValueError(mode)
        mappings = sorted(m for m in product(*self.candidates) if valid(m, self.candidates))
        current = max(mappings, key=self.schema)  # First lexicographic maximum.
        old_weights = self.weights(current)
        states = [self.solve(i, w) for i, w in enumerate(old_weights)]
        objective = self.schema(current) + self.scale * sum(s['score'] for s in states)
        path = [current]; stats = {'initial_solves': len(states), 'candidate_solves': 0, 'candidates': 0, 'rejected': 0, 'partial_rejected': 0, 'reused': 0}
        while True:
            chosen, best, chosen_states = current, objective, states
            for candidate in neighbors(current, self.candidates):
                stats['candidates'] += 1
                ws = self.weights(candidate); cs = list(states); pending = set(); upper = []; lower = []; bs = []
                for i, w in enumerate(ws):
                    b = bounds(w, states[i]); bs.append(b)
                    if w == old_weights[i]:
                        upper.append(states[i]['score']); lower.append(states[i]['score']); stats['reused'] += 1
                    else:
                        pending.add(i); upper.append(b['zero' if mode == 'zero' else 'transfer']); lower.append(b['lower'])
                discarded = False; solves = 0
                while pending:
                    if mode != 'full' and self.schema(candidate) + self.scale * sum(upper) <= best:
                        discarded = True; break
                    i = min(pending, key=lambda j: (-(upper[j] - lower[j]), j))
                    if mode == 'transfer':
                        upper[i] = min(upper[i], bs[i]['reset'])
                        if self.schema(candidate) + self.scale * sum(upper) <= best:
                            discarded = True; break
                    cs[i] = self.solve(i, ws[i]); upper[i] = cs[i]['score']; pending.remove(i)
                    stats['candidate_solves'] += 1; solves += 1
                if discarded:
                    stats['rejected'] += 1; stats['partial_rejected'] += int(solves > 0)
                else:
                    value = self.schema(candidate) + self.scale * sum(upper)
                    if value > best: chosen, best, chosen_states = candidate, value, cs
            if chosen == current: break
            current, objective, states = chosen, best, chosen_states
            old_weights = self.weights(current); path.append(current)
        return {'mapping': list(current), 'objective': str(objective), 'row_pairs': self.decode(current), 'path': [list(m) for m in path], 'stats': stats}
