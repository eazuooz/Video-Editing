from pathlib import Path
import hashlib,json,math
H=Path(__file__).resolve().parent;ROOT=H.parents[2];R=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/production-resume-20261115T055255Z');read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));pin=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest());rows=[]
for x in read(H/'native-film-bindings-source-review-v37.json')['bindings']:
 bp=Path(x['path']);b=read(bp);cp=Path(b['captionTiming']['path']);caps=read(cp);pp=Path(b['filmPlan']['path']);plan=read(pp);selection=read(Path(b['voiceSelection']['path']));duration=read(Path(selection['voice']['path']))['canonical']['duration'];beats=[]
 for para in plan['paragraphs']:
  for beat in para['beats']:
   cue=next(c for c in caps['cues']if c['paragraph']==para['id']and c['clauseIndex']==beat['firstClauseIndex']);beats.append(dict(beat,start=cue['start'],paragraph=para['id']))
 for i,beat in enumerate(beats):
  end=beats[i+1]['start']if i+1<len(beats)else duration
  if beat['kind']!='native':continue
  stop=beat['startFrame']+math.ceil((end-beat['start'])*60)
  rows.append(dict(project=bp.parents[1].name,topic=beat['topic'],mode=beat['mode'],view=beat['view'],paragraph=beat['paragraph'],sourceFrameRange=[beat['startFrame'],stop],filmPlan=pin(pp),captionTiming=pin(cp)))
out=R/'selected-native-ranges-v51.json';assert not out.exists();out.write_text(json.dumps(dict(ranges=rows,allWithinActual720Frames=all(x['sourceFrameRange'][1]<=720 for x in rows)),indent=2)+'\n','utf8');print(json.dumps([dict(project=x['project'],mode=x['mode'],paragraph=x['paragraph'],frames=x['sourceFrameRange'])for x in rows]))
