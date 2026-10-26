"""Prepare exact reused visual cuts for D30 fresh audio/visual v3, without running media jobs."""
from pathlib import Path
import json,hashlib,os,copy
HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1];ROOT=HERE.parents[3]
old=PROJECT/'production/local/batch-v1/edit';new=PROJECT/'production/local/batch-v1/final-v3';new.mkdir(exist_ok=True)
plan_file=HERE/'edit-plan.json';plan=json.loads(plan_file.read_text('utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Every excluded field controls only sound selection/provenance; cut rendering always uses -an.
nonvisual={'sourceAudioEnabled','sourceAudioReviewStatus','audioRightsReview'}
visual=lambda cut:{k:v for k,v in cut.items() if k not in nonvisual}
receipt={'kind':'byte-exact-visual-cut-reuse','planSha256':sha(plan_file),'excludedAudioOnlyFields':sorted(nonvisual),'reused':[],'needsRender':[],'previousMasterPreserved':True}
def link(src,dst):
 if dst.exists():
  assert sha(src)==sha(dst),str(dst)
 else:os.link(src.resolve(),dst.resolve())
for c in plan['cuts']:
 f=old/(c['id']+'-render.json');movie=old/(c['id']+'.mp4')
 if not f.exists():receipt['needsRender'].append(c['id']);continue
 r=json.loads(f.read_text('utf-8'))
 if visual(r['signature']['cut'])!=visual(c):receipt['needsRender'].append(c['id']);continue
 assert sha(movie)==r['outputSha256']
 link(movie,new/movie.name)
 updated=copy.deepcopy(r);updated['signature']['cut']=c
 updated['visualReuseEvidence']={'originalReceipt':str(f.relative_to(ROOT)).replace('\\','/'),'originalReceiptSha256':sha(f),'originalCutSha256':sha(movie),'pixelBytesReencoded':False,'reason':'Same source/time/crop/marks/renderer/encoder; only native source audio selection metadata may differ.'}
 target=new/f.name
 if target.exists():assert json.loads(target.read_text('utf-8'))==updated
 else:target.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+'\n','utf-8')
 receipt['reused'].append(c['id'])
for name in ['branding.mp4','membership.mp4','captions.ko.ass','captions.en.ass','captions.ko.srt','captions.en.srt','captions.json','caption-layout.json','caption-alignment.json','caption-input.json']:
 if (old/name).exists():link(old/name,new/name)
(new/'visual-reuse.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'reused':len(receipt['reused']),'needsRender':receipt['needsRender']},ensure_ascii=False))
