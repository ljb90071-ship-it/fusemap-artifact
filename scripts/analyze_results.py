"""Validate and summarize archived aggregate tables; no benchmark execution."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):
 with (ROOT/'results'/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
runtime=read('runtime.csv')
for r in runtime:
 p,w,f=(float(r[k]) for k in ('preprocess_seconds','profile_warm_seconds','fusemap_seconds'))
 assert abs(w/f-float(r['search_speedup']))<=0.0051
 assert abs((p+w)/(p+f)-float(r['complete_speedup']))<=0.0051
quality=read('quality.csv')
summary={m:{k:round(sum(float(r[k]) for r in quality if r['method']==m)/5,1) for k in ('schema_f1_percent','entity_f1_percent')} for m in sorted({r['method'] for r in quality})}
cost=json.loads((ROOT/'results/search_cost.json').read_text(encoding='utf-8'))
assert sum(cost['candidate_outcomes_percent'].values())==100
assert all(next(x for x in quality if x['method']=='FuseMap' and x['domain']==r['domain'])['entity_f1_percent']==r['entity_f1_percent'] for r in quality if r['method']=='Profile-Full')
print(json.dumps({'analysis':'archived aggregate data','macro_f1_percent':summary,'runtime_rows_checked':len(runtime)},indent=2))

coverage=read('column_coverage.csv')
gold=sum(int(r['gold_per_level']) for r in coverage)
retained=sum(sum(int(r[k]) for k in ('low_retained','medium_retained','high_retained')) for r in coverage)
assert gold==332 and retained==968
assert round(100*retained/(3*gold),1)==97.2
assert round(100*sum(int(r['high_retained']) for r in coverage)/gold,1)==93.7
joint={r['method']:float(r['joint_row_percent']) for r in read('joint_row.csv')}
assert abs(joint['FuseMap']-joint['Alternating']-6.7)<1e-9
print(json.dumps({'column_gold_pairs':3*gold,'retained_gold_pairs':retained,'column_recall_percent':round(100*retained/(3*gold),1),'joint_row_gain_points':6.7},indent=2))

budget=read('restart_budget.csv')
for r in budget:
 assert int(r['alternating8_complete_s'])==int(r['prep_s'])+int(r['alternating8_search_s'])
 rt=next(x for x in runtime if x['domain']==r['domain'])
 assert int(r['fuse_budget_s'])==int(rt['fusemap_seconds'])
 for method,prefix in [('Alternating-8','alternating8'),('FuseMap','fuse')]:
  qr=next(x for x in quality if x['domain']==r['domain'] and x['method']==method)
  assert float(r[prefix+'_schema_f1'])==float(qr['schema_f1_percent'])
  assert float(r[prefix+'_entity_f1'])==float(qr['entity_f1_percent'])
macro={k:round(sum(float(r[k]) for r in budget)/5,1) for k in ['alternating_time_schema_f1','alternating_time_entity_f1']}
assert macro=={'alternating_time_schema_f1':89.6,'alternating_time_entity_f1':87.1}
print(json.dumps({'matched_budget_macro':macro},indent=2))
