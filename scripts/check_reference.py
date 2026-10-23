"""Independent exhaustive checks on deterministic small graphs."""
import json
import random
import sys
from itertools import product
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from fusemap import assignment, bounds, Problem, neighbors


def brute(n, p, weights):
    best = 0
    for m in product(range(-1, p), repeat=n):
        js = [j for j in m if j >= 0]
        if len(js) != len(set(js)) or any((i, j) not in weights for i, j in enumerate(m) if j >= 0):
            continue
        best = max(best, sum(weights[i, j] for i, j in enumerate(m) if j >= 0))
    return best


def main():
    rng = random.Random(20261021)
    for trial in range(300):
        n, p = rng.randint(1, 4), rng.randint(1, 4)
        old = {(i, j): rng.randint(-8, 12) for i in range(n) for j in range(p) if rng.random() < .7}
        new = {e: rng.randint(-8, 12) for e in old}
        state = assignment(n, p, old)
        assert state['score'] == brute(n, p, old)
        target = brute(n, p, new)
        b = bounds(new, state)
        assert b['lower'] <= target <= min(b['transfer'], b['reset'], b['zero'])
        assert assignment(n, p, new)['score'] == target
    counts = {'rejected': 0, 'partial_rejected': 0, 'reused': 0}
    for trial in range(100):
        data = {'rows':4, 'columns':4, 'lambda':rng.choice([.5, 1, 2]),
                'candidates':[[-1, 0, 1, 2]] * 3,
                'metadata':[{str(c):(0 if c == -1 else rng.randint(-4, 4)) for c in [-1, 0, 1, 2]} for _ in range(3)],
                'edges':[{'i':i, 'j':j, 'base':rng.randint(-5, 5),
                          'contributions':{f'{k}:{c}':rng.randint(-4, 8) for k in range(3) for c in range(3) if rng.random() < .5}}
                         for start in [0, 2] for i in range(start, start+2) for j in range(start, start+2)]}
        problem = Problem(data)
        answers = [problem.search(mode) for mode in ['full', 'transfer', 'zero']]
        assert answers[0]['path'] == answers[1]['path'] == answers[2]['path']
        assert answers[0]['objective'] == answers[1]['objective'] == answers[2]['objective']
        starts = problem.restart_starts()
        assert len(starts) == len(set(starts)) == 8
        alt = problem.alternating_restarts()
        assert alt['starts'] == [list(x) for x in starts]
        assert Fraction(alt['best']['objective']) >= Fraction(problem.alternating()['objective'])
        m = tuple(answers[0]['mapping'])
        value = problem.schema(m) + problem.scale * sum(brute(len(rows), len(cols), w) for (rows, cols, _), w in zip(problem.components, problem.weights(m)))
        for neighbor in neighbors(m, problem.candidates):
            v = problem.schema(neighbor) + problem.scale * sum(brute(len(rows), len(cols), w) for (rows, cols, _), w in zip(problem.components, problem.weights(neighbor)))
            assert v <= value
        for k in counts: counts[k] += answers[1]['stats'][k]
    assert counts['rejected'] > 0 and counts['partial_rejected'] > 0 and counts['reused'] > 0
    # Connected double-star: reset and zero bounds have no general dominance.
    for d in range(3, 8):
        old = {(i, 0): 10 for i in range(d-1)}
        old.update({(d-1, j): 10 for j in range(1, d)})
        old[d-1, 0] = 0
        state = assignment(d, d, old)
        changed = dict(old); changed[0, 0] = 9
        b = bounds(changed, state)
        assert b['reset'] == 20 and b['zero'] == d*10-1
        b = bounds({e:0 for e in old}, state)
        assert b['zero'] == 0 and b['reset'] == 10
    # Tied terminal matchings can have different labels; all modes decode afresh.
    tied = {'rows':2, 'columns':2, 'lambda':2, 'candidates':[[-1,0,1]],
            'metadata':[{'-1':0,'0':1,'1':0}],
            'edges':[{'i':i,'j':j,'base':0,'contributions':{'0:0':int(i!=j),'0:1':2}}
                     for i in range(2) for j in range(2)]}
    p = Problem(tied)
    answers = [p.search(mode) for mode in ('full','transfer','zero')]
    assert all(a['mapping'] == [1] and a['objective'] == '4' for a in answers)
    assert all(a['row_pairs'] == [[0,0],[1,1]] for a in answers)
    alt = p.alternating()
    assert alt['mapping'] == [1] and alt['row_pairs'] == [[0,0],[1,1]]
    example = Problem(json.loads((ROOT/'examples/reassignment.json').read_text(encoding='utf-8')))
    answer = example.search()
    assert answer['path'] == [[0], [1]] and answer['objective'] == '18'
    assert example.alternating()['mapping'] == [0]
    assert example.alternating()['objective'] == '13'
    restarted = example.alternating_restarts()
    assert len(restarted['starts']) == 3  # finite feasible-space exhaustion
    assert restarted['best']['objective'] == '18'
    assert restarted['best']['row_pairs'] == answer['row_pairs']
    assert example.restart_starts() == example.restart_starts()
    assert bounds(example.weights((1,))[0], example.solve(0, example.weights((0,))[0]))['lower'] == 10
    print(json.dumps({'assignment_and_bound_cases':300, 'three_mode_search_cases':100,
                      'table_1_checked':True, 'double_star_cases':10,
                      'transfer_execution_counts':counts}, indent=2))


if __name__ == '__main__':
    main()
