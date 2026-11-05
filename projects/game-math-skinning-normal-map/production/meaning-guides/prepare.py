from pathlib import Path
from datetime import datetime,timezone
import json, hashlib, shutil, re, importlib.util
from lesson import ROWS,ANCHORS
P=Path(__file__).resolve().parents[2]; R=P.parents[1]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=P/'production/local/audio-v4';assert not a.exists()
 old=a.with_name('audio-v3');ko=read(P/'script/narration.ko.json');en=read(P/'script/narration.en.json')
 bind=read(P/'planning/scene-bindings.json');plan=read(P/'planning/production-plan.json')
 stamp=datetime.now(timezone.utc).isoformat()
 for i,rows in ROWS.items():
  ko['scenes'][i]['lines']=[' '.join(x[0] for x in rows)]
  ko['scenes'][i]['displayLines']=[ko['scenes'][i]['lines'][0].replace('유브이','UV').replace('여덟 비트','8비트')]
  en['scenes'][i]['lines']=[' '.join(x[1] for x in rows)]
  row=bind['scenes'][i]; row['speech']=ko['scenes'][i]['lines'][0]
  row['speechPhaseAnchors']=[dict(phrase=p,position=t,character=row['speech'].index(p)) for p,t in ANCHORS[i]]
  plan['learningSteps'][i]['retainedExplanation']=row['speech']
 for row in bind['scenes']:row['clockFields']=['stepSeconds','stepPositions']
 # ASR grouped the sounds at the start of "좌표를 바꿔"; the next accurately heard phrase marks the same lighting handoff.
 row=bind['scenes'][34];row['speechPhaseAnchors']=[x for x in row['speechPhaseAnchors'] if x['phrase']!='좌표를 바꿔']
 for lang,obj in [('ko',ko),('en',en)]:
  save(P/f'script/narration.{lang}.json',obj)
  (P/f'script/integrated-readthrough.{lang}.txt').write_text('\n\n'.join(x['lines'][0] for x in obj['scenes'])+'\n','utf-8')
  plan['scriptReadthrough'][lang+'Sha256']=sha(P/f'script/narration.{lang}.json')
 bind['sourceNarrationSha256']=sha(P/'script/narration.ko.json');save(P/'planning/scene-bindings.json',bind)
 plan['teachingRevision']={'date':stamp,'rules':['meaning-before-values-v1','surface-symbol-guides-v1'],'revoiced':sorted(ROWS),'source':'10.8 and 10.9 in original order','games':'3 original independently captured native-speed cuts','keyExamples':['sleeve vertex and two bone proposals','button in the bind and current bone frames','normal-data channel and surface axes','paired model and UV triangles']}
 save(P/'planning/production-plan.json',plan)
 integ=read(P/'planning/script-integration.json');integ['readThrough'].update(plan['scriptReadthrough']);integ['meaningRevision']=plan['teachingRevision'];save(P/'planning/script-integration.json',integ)
 # Existing translated sentences are unchanged outside the selected retakes.
 b=P/'planning/bilingual-caption-map.json';bm=read(b)
 for i,rows in ROWS.items():
  bm['scenes'][i]['groups']=[dict(koStart=j,koCount=1,enStart=j,enCount=1,ko=k,en=e) for j,(k,e) in enumerate(rows)]
 bm.update(koSha256=sha(P/'script/narration.ko.json'),enSha256=sha(P/'script/narration.en.json'));save(b,bm)
 a.mkdir();(a/'chunks').mkdir();copied=[]
 for f in (old/'chunks').glob('*.wav'):
  if int(f.name[:3]) not in ROWS:
   out=a/'chunks'/f.name;shutil.copy2(f,out);assert sha(f)==sha(out);copied.append(dict(file=f.name,sha256=sha(out)))
 assert len(copied)==36-len(ROWS)
 manifest=read(P/'production/tts-manifest-audio-v3.json');manifest['tts']['outputDir']=a.relative_to(R).as_posix();manifest['retake']=dict(scenes=sorted(ROWS),reason='Purpose before formula; map the inputs to the moving object; remove arithmetic-only examples.')
 save(P/'production/tts-manifest-audio-v4.json',manifest);save(a/'retake-plan.json',dict(retakeScenes=sorted(ROWS),copiedUnchangedRawTakes=copied))
if __name__=='__main__':main()

