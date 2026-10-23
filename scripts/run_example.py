"""Execute the small reference search, not the archived benchmark."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fusemap import Problem
path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'examples/reassignment.json'
p=Problem(json.loads(path.read_text(encoding='utf-8')))
results={mode:p.search(mode) for mode in ('full','transfer','zero')}
results['alternating']=p.alternating()
results['alternating_8']=p.alternating_restarts()
print(json.dumps(results,indent=2))
