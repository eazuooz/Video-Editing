from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));pin=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,s):assert not p.exists(),p;p.write_text(s,'utf8')
rows=[]
for slug in ['shorts-control-destruction-pipeline','shorts-doom-push-forward-healing']:
 P=ROOT/'projects'/slug;bp=P/'production/film-inputs-v37.json';b=read(bp);prior=Path(b['filmPlan']['path']);plan=read(prior)
 if'control'in slug:
  next(p['beats']for p in plan['paragraphs']if p['id']=='p001').append(dict(firstClauseIndex=4,kind='diagram',key='control-hierarchy',localModelStartSeconds=0));beats=next(p['beats']for p in plan['paragraphs']if p['id']=='p005');assert beats[1]['firstClauseIndex']==3;beats[1]['firstClauseIndex']=2
 else:
  beat=next(x for p in plan['paragraphs']if p['id']=='p001'for x in p['beats']if x['kind']=='native');assert beat['startFrame']==60;beat['startFrame']=54
 pp=P/'planning/film-beats-v53.json';write(pp,json.dumps(plan,ensure_ascii=False,indent=2)+'\n');b.update(filmPlan=pin(pp),priorBindings=pin(bp),changeReason='Use actual source ranges at natural speed. Control switches to its hierarchy explanation at the corresponding whole-word clause, and DOOM starts its illustrative approach0.1second earlier. No voice, captions, actual game cuts, speed, loops, freeze frames or audio changes.');out=P/'production/film-inputs-v53.json';write(out,json.dumps(b,ensure_ascii=False,indent=2)+'\n');rows.append(pin(out))
for source,target in [('run-lesson-film-v37-cooperative-v19.py','run-lesson-film-v53-cooperative-v19.py'),('finalize-local-bundle-v37.py','finalize-local-bundle-v53.py')]:
 s=(H/source).read_text(encoding='utf8').replace("P/('production/film-inputs-v37.json'if","P/('production/film-inputs-v53.json'if(P/'production/film-inputs-v53.json').exists()else'production/film-inputs-v37.json'if");write(H/target,s)
write(H/'bounded-native-cut-source-review-v53.json',json.dumps(dict(priorRangeObservation=pin(Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/production-resume-20261115T055255Z/selected-native-ranges-v51.json')),bindings=rows,allOriginalPlansAndPcmPreserved=True,newMediaGenerated=False),indent=2)+'\n');print('Prepared two explicit natural-speed cut repairs53')
