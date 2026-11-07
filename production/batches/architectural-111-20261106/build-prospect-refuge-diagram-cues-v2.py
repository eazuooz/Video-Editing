"""CPU-only06.02 P04/P25 actual word-clock cue plans; no render/model jobs."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os
from pathlib import Path
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read

PROJECT=ROOT/'projects/shorts-leveldesign-06-02';TOPIC=MEDIA/PROJECT.name
CAPTION=HERE/'build-prospect-refuge-caption-timing-v2.py';CAPTION_SHA='1b15170b292d6acc557e4bd1b0dbbbf6aaf4a7cd4d64a8a51c800b693df6fee8'
PREP=PROJECT/'relationship-diagram-preparation-v1.json'
PREP_SHA='1c1bf6c1b15d03a50c7bb16657f3bec16616b1ac88f5314130e3842f42a62331'
SOURCE=ROOT/'motion-canvas/src/projects/shorts-leveldesign-06-02'
PINS={'project.ts':'eb07a11c42e2ce4f49e7f605951481bcedcd543783cbcaba24eaa6e725b4990f','refuge-relationships.tsx':'8715978499db1c72ada9baefd7babf8f2a0ad7044f9d8d431554b5ec5a52c55b'}
SCHEMA='06-02-authored-diagram-cues-v2';FONT=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf');FONT_SHA='018174e8cdd366aff67c8d366c7dc806a7babbe7f2819fc23b00d59f7b8353d0'
COMPLETE_WORD_ANCHORS={'06.02-p04-01-current-reference':'머무는 은신처와 바로 앞의 조망 공간이 현재의 기준입니다.','06.02-p25-04-relationship':'어디에서 무엇을 읽고 다음 어디로 움직일 수 있는지를'}

def sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class Pending(RuntimeError):pass
def require(value,message):
 if not value:raise Pending(message)
def caption_module():
 require(CAPTION_SHA and sha(CAPTION)==CAPTION_SHA,'Reviewed06.02 caption adapter changed')
 spec=importlib.util.spec_from_file_location('prospect_diagram_actual_caption_clock',CAPTION);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def source_contract():
 require(sha(PREP)==PREP_SHA,'Reviewed eight-cue source-preparation contract changed')
 for name,want in PINS.items():require(sha(SOURCE/name)==want,'Reviewed06.02 MC source changed')
 require(sha(FONT)==FONT_SHA,'Approved MC font changed')
 prep=read(PREP);cues=prep['cueMap']
 require(prep['topicId']=='06.02'and len(cues)==8 and [c['paragraph']for c in cues]==[4]*4+[25]*4,'Exact eight P04/P25 authored source cues required')
 for row in prep['sourceFiles']:require(pin(row['path'])==row,'Historical source-preparation MC pin changed')
 return cues
def phase_map(cues,total,expected):
 require(type(total)is int and total>=6,'Finite positive actual paragraph frame count required')
 require([x.get('id')for x in cues]==[x['id']for x in expected],'Exact ordered source cue IDs required')
 points=[dict(frame=0,phase=0.)];last=0
 for cue,source in zip(cues,expected):
  frame=cue.get('frame');phase=source['normalizedAuthorPhase']
  require(type(frame)is int and last<frame<total-1,'Actual semantic cues must increase strictly inside paragraph endpoints')
  require(type(phase)in(int,float)and 0<phase<1,'Reviewed normalized author phase required')
  points.append(dict(frame=frame,phase=phase));last=frame
 points.append(dict(frame=total-1,phase=1.))
 require(all(a['phase']<b['phase']for a,b in zip(points,points[1:])),'Source semantic phase order changed')
 return points
def exact_phrase_interval(sentence,phrase,caption):
 start=caption.resolve_literal_start(sentence,phrase);offset=sentence['canonicalKo'].index(phrase)+len(phrase);original=offset
 # Source cue descriptions may omit the source comma. Punctuation has no word
 # timestamp of its own: bind its EXACT canonical trailing punctuation to the
 # same actual word edge, never interpolate or extend over spoken characters.
 while offset<len(sentence['canonicalKo'])and sentence['canonicalKo'][offset]in',.!?;:':offset+=1
 end=caption.char_boundary(sentence,offset)
 require(end['sample']>start['sample'],'Exact spoken cue phrase has no positive actual word span')
 return dict(sceneId=sentence['sceneId'],exactSpokenAnchorKo=phrase,startSample=start['sample'],endSample=end['sample'],startFrame=start['frame'],endFrameExclusive=end['frame'],startBoundary=start,endBoundary=end,canonicalTrailingPunctuation=sentence['canonicalKo'][original:offset])
def build_segment(timing,expected,segment,caption):
 paragraph=int(segment[1:]);rows=[p for p in timing['paragraphs']if p['paragraph']==paragraph]
 require(len(rows)==1,'Actual paragraph clock missing');row=rows[0];start,end=row['startFrame'],row['endFrameExclusive'];cues=[]
 for source in expected:
  phrase=COMPLETE_WORD_ANCHORS.get(source['id'],source['exactSpokenAnchorKo']);candidates=[s for s in timing['sentences']if s['paragraph']==paragraph and s['canonicalKo'].count(phrase)==1]
  require(len(candidates)==1,'Source phrase is not unique inside actual paragraph: '+source['id'])
  boundary=exact_phrase_interval(candidates[0],phrase,caption)
  # Cue phases describe visual states achieved at a spoken phrase END. First
  # whole-sentence end gives a nonzero introductory interval, never frame0.
  cues.append(dict(id=source['id'],frame=boundary['endFrameExclusive']-start,globalFrame=boundary['endFrameExclusive'],actualRawSample=boundary['endSample'],sceneId=candidates[0]['sceneId'],exactSpokenAnchorKo=phrase,sourceAuthoredAnchorKo=source['exactSpokenAnchorKo'],boundary='actual exact phrase end word offset/gap boundary',literalInterval=boundary,reason='Reach the authored visual state as its complete spoken relationship is established; P04 first cue omits only the root-approved removed leading 지금; P25 final cue includes canonical particle 를 to end at an actual complete word rather than interpolate inside 있는지를'))
 phase=phase_map(cues,end-start,expected)
 return dict(segment=segment,segmentStartGlobalFrame=start,segmentEndGlobalFrameExclusive=end,totalFrames=end-start,paragraph=paragraph,cues=cues,phaseFrameMap=phase)
def prepare(timing_path=None):
 expected=source_contract()
 if not timing_path:raise Pending('Actual complete103physical/96logical06.02 voice/blind-ASR caption timing is not available')
 caption=caption_module();verified=caption.verify_existing(timing_path);timing=verified['timing']
 inputs=[dict(role='captionTiming',**pin(timing_path)),dict(role='captionAdapter',**pin(CAPTION)),dict(role='sourcePreparation',**pin(PREP)),dict(role='font',**pin(FONT)),dict(role='cueBuilder',**pin(__file__))]+[dict(role='motionSource:'+name,**pin(SOURCE/name))for name in PINS]+timing['inputs']
 plans={}
 for segment in ('p04','p25'):
  rows=[x for x in expected if x['paragraph']==int(segment[1:])];body=build_segment(timing,rows,segment,caption)
  result=dict(schemaVersion=SCHEMA,topicId='06.02',timingStatus='actual-asr-word-aligned',**body,inputPins=inputs,captionTiming=pin(timing_path),voiceEvidence=next({k:r[k]for k in ('path','sha256')}for r in timing['inputs']if r['role']=='voiceEvidence'),rawVoice=verified['voice']['aggregateWav'],sourcePreparationRole='Historical unchanged geometry/typecheck evidence only; current immutableV4/103physical/96logical/ASR pins come from fresh captionV2 timing',sourceClock='Exact complete paragraph raw PCM at60fps; no extra silence, default duration, time ratio or fabricated observation hold',automaticSpeechPass=False,actualRendered=False,actualListening=False,humanApproval=False)
  result['fingerprint']=digest(result);plans[segment]=result
 return plans
def verify_existing(path):
 actual=read(path);require(actual.get('schemaVersion')==SCHEMA and actual.get('segment')in('p04','p25'),'Not selected06.02 diagram cues')
 expected=prepare(actual['captionTiming']['path'])[actual['segment']];require(actual==expected,'Cue plan differs from current verified actual word boundaries')
 require(Path(path).resolve()==(TOPIC/'diagram-cue-plans-v2'/expected['fingerprint'][:24]/(actual['segment']+'.json')).resolve(),'Cue plan is outside exact immutable selected output')
 return expected
def write(plans):
 paths={}
 for segment,body in plans.items():
  target=TOPIC/'diagram-cue-plans-v2'/body['fingerprint'][:24]/(segment+'.json');text=json.dumps(body,ensure_ascii=False,indent=2)+'\n'
  if target.exists():require(target.read_text(encoding='utf8')==text,'Preserve different existing cue plan')
  else:
   for p in body['inputPins']:require(pin(p['path'])=={k:p[k]for k in ('path','sha256')},'Cue input changed before write')
   target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('x',encoding='utf8')as f:f.write(text)
  paths[segment]=str(target)
 return paths
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--caption-timing');p.add_argument('--write',action='store_true');a=p.parse_args()
 try:
  plans=prepare(a.caption_timing);print(json.dumps(dict(ready=True,plans=write(plans)if a.write else{k:v['fingerprint']for k,v in plans.items()},written=a.write,rendererStarted=False)))
 except Pending as e:
  if a.write:raise
  print(json.dumps(dict(ready=False,reason=str(e),written=False,rendererStarted=False)))
if __name__=='__main__':main()
