"""Keep a finished explanation visible; preserve all audio and unaffected cuts."""
from pathlib import Path
import json,hashlib,subprocess,sys,shutil
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;O=R/'projects/avoid-game-comparisons/production/local/reference-preserving-v2/edit';B=O/'before-static-hold'
assert json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['selectedVideo']=='avoid-game-comparisons'
assert not B.exists();B.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={p.name:sha(p) for p in O.glob('cut[0-9][0-9].mp4')}
aac=sha(O/'final-mix.m4a');asr=sha(O/'final-mix-asr.json')
for name in ['avoid-game-comparisons-v2-captioned.mp4','avoid-game-comparisons-v2-clean.mp4']:
 shutil.copy2(O/name,B/name)
for p in [O/'qa',B/'qa']:p.resolve().relative_to(O.resolve())
(O/'qa').rename(B/'qa')
p=V/'edit-plan.json';plan=json.loads(p.read_text(encoding='utf8'));c=next(c for c in plan['cuts'] if c['id']=='cut25');c['holdAfterFrames']=1200;c['holdReason']='All reveals settled before19.1s; completed diagram held from20s to the narration end. No commercial footage speed change.';p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for name,args in [('conclusion',['compose-video.py','slices']),('pair',['compose-video.py','pair']),('integrity',['verify-output.py','--integrity-only'])]:
 assert json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['selectedVideo']=='avoid-game-comparisons'
 print('Starting static hold',name,flush=True)
 with (O/('static-hold-'+name+'.log')).open('w',encoding='utf8') as f:r=subprocess.run([sys.executable,'-X','utf8',str(V/args[0]),*args[1:]],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,name
after={p.name:sha(p) for p in O.glob('cut[0-9][0-9].mp4')};changed=[p for p in before if before[p]!=after[p]];assert changed==['cut25.mp4'];assert sha(O/'final-mix.m4a')==aac and sha(O/'final-mix-asr.json')==asr
old=json.loads((B/'qa/integrity.json').read_text());new=json.loads((O/'qa/integrity.json').read_text());assert {r['aacSha256'] for r in old['outputs']}=={r['aacSha256'] for r in new['outputs']}
proof=json.loads((O/'retained-range-proof.json').read_text());proof['after']=after;proof['findingsRepaired'].append('Hold fully revealed conclusion at20s through its23.6s end; repaired unintended missing title glyphs');proof['staticHold']={'priorCurrentOutput':old['outputs'],'changedCut':'cut25','holdAfterFrames':1200,'holdFrames':216,'sameAacStream':True,'sameFullAsrEvidence':True,'prior108Samples':str(B/'qa/changed-pixel-index.json'),'finalOnlyChangedCutReview':'pending'};(O/'retained-range-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Static conclusion repaired;25 cuts and encoded audio unchanged',flush=True)
