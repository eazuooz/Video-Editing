"""CPU-only07.04 picture timeline; real current captions, MC crops and mix required.

No decoder/encoder/model/engine, queue, platform action or first-film mutation.
Pure planning may be tested with synthetic clocks; --write requires all actual
hash-bound media and independently verified selected ASR timing.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PROJECT=ROOT/'projects/shorts-leveldesign-07-04'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-07-04')

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p,role=None):
    v=dict(path=str(Path(p).resolve()),sha256=sha(p))
    if role:v['role']=role
    return v
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class Pending(RuntimeError):pass

def plan(timing,game,crops):
    """Pure ordered picture construction. No file/proof or media operations."""
    groups={g['id']:g for g in timing['groups']};paragraphs={p['paragraph']:p for p in timing['paragraphs']};sections=[];cursor=0
    def at(name):return groups[name]['startFrame']
    def cut(end,**value):
        nonlocal cursor
        if type(end)is not int or end<cursor:raise Pending('Actual semantic interval is too short for unchanged native motion')
        if end==cursor:return
        sections.append(dict(id=f's{len(sections)+1:03}',startFrame=cursor,endFrameExclusive=end,**value));cursor=end
    def native(end,mode,layout,frame,reason=None,parts=(),term=None,count=None):
        source=dict(mode=mode,layout=layout,startNativeFrame=frame,frameCount=1 if reason else count,playbackRate=1,holdPolicy=dict(frame=frame,reason=reason)if reason else None)
        value=dict(kind='native',native=source,guideParts=list(parts))
        if term:value['termChips']=[term]
        cut(end,**value)
    def still(end,mode,layout,frame,reason,parts=(),term=None):native(end,mode,layout,frame,reason,parts,term)
    def mc(n):
        row=crops['p'+str(n)];p=paragraphs[n];start=next(x['startFrame']for x in timing['diagramCues']if x['id']=='07.04-p6-01-same-visible-chest')if n==6 else p['startFrame']
        if cursor!=start or row['contract']['frames']!=p['endFrameExclusive']-start:raise Pending('Real MC crop duration/start differs from current actual paragraph')
        cut(p['endFrameExclusive'],kind='mc',sourcePath=row['output']['path'],sourceSHA256=row['output']['sha256'],sourceStartFrame=0,frameCount=row['contract']['frames'],rate=1,cropManifest=row['_pin'])
    actual=dict(sourceId=game['id'],sourcePath=game['path'],sourceSHA256=game['sha256'])
    hero=at('P1d');freeze_frames=hero-390
    if freeze_frames<=0:raise Pending('First observed speech must contain complete selected6.5s native source plus a purposeful sign observation')
    cut(120,kind='gameplay',sourceLocalInPts=.5,rate=1,**actual)
    cut(120+freeze_frames,kind='observation-freeze',sourceFrameIndex=150,sourceLocalPts=2.5,label='관찰용 정지',holdReason='Locate the actual briefly visible window sign before the carriage wall occludes it; duration derived from first two actual spoken sentences.',detailInset=dict(sourceCropXYXY=[1500,280,1740,500],destinationXYWH=[70,1010,360,330],label='창밖 표지판 확대'),**actual)
    cut(hero,kind='gameplay',sourceLocalInPts=2.5,rate=1,**actual)
    still(at('P1f'),'narrow','singlePlayer',239,'Show the aligned target in our separate sea/slit experiment while the abstract explains a fleeting view.')
    still(paragraphs[2]['startFrame'],'narrow','sameClockAB',0,'Preview the width-only comparison with exactly matched camera/path sample; no new traversal.')
    mc(2)
    still(at('P3b'),'narrow','singlePlayer',0,'Introduce the same thick wall and distant target before the path traversal.')
    still(at('P3c'),'narrow','dual',0,'Locate the actual diagonal near/far opening mouths in the same scene.',parts=('mouths',))
    native(cursor+240,'narrow','dual',0,count=240)
    still(at('P3e'),'narrow','dual',239,'Pause at the actual aligned center sample while the narration identifies eye/opening/lighthouse alignment; source motion is not slowed.')
    native(cursor+240,'narrow','dual',240,count=240)
    still(paragraphs[4]['startFrame'],'narrow','dual',479,'After native passage, retain the occluded destination-path relationship while its reward role is explained.')
    still(at('P4b'),'narrow','dual',239,'Revisit the same aligned instant from eye level and above; both cameras share actual frame239.')
    still(at('P4c'),'narrow','dual',239,'Draw the actual center ray from the sampled eye toward the target.',parts=('centerline',))
    still(at('P4d'),'narrow','dual',239,'Reveal the actual near/far mouth span and the clear center ray together.',parts=('centerline','mouths'))
    still(at('P4g'),'narrow','dual',255,'Show the true center-ray hit inside the thick wall; partial lighthouse pixels remain untouched.',parts=('centerline','mouths'))
    wide_start=min(at('P4h'),at('P5d')-480)
    if wide_start<=cursor:raise Pending('No actual interval for width-change confirmation before the unchanged8s wide traversal')
    still(wide_start,'narrow','sameClockAB',255,'At the same sample, only opening width changes; compare actual center-clear/blocked states.',parts=('centerline',))
    native(wide_start+480,'wide','dual',0,count=480,parts=('centerline',))
    still(at('P5d'),'narrow','sameClockAB',0,'Compare a path sample outside the narrow clear interval with the continuously open wider view.',parts=('centerline',))
    term=dict(english='Zen View',korean='젠 뷰',meaning='목적지로 가는 길에서 잠깐 마주치는 풍경',presentation='definition')
    term_end=min(cursor+180,paragraphs[5]['endFrameExclusive'])
    still(term_end,'narrow','singlePlayer',239,'Name the mechanism after the narrow/wide comparison, over the same dimmed explanation scene.',term=term)
    term=copy.deepcopy(term);term['presentation']='chip'
    still(paragraphs[5]['endFrameExclusive'],'narrow','singlePlayer',239,'Retain the named aligned instant while explaining the landscape as a passing reward.',term=term)
    entry=next(c['startFrame']for c in timing['diagramCues']if c['id']=='07.04-p6-01-same-visible-chest')
    still(entry,'narrow','singlePlayer',239,'Carry the same vista into the next example before contrasting a visible treasure with an unknown route.',term=term)
    mc(6);mc(7)
    if cursor!=timing['totalFrames']:raise Pending('Picture timeline leaves a final PCM-rounding frame uncovered')
    cats=[]
    for start,end,pose in [(max(at('P1e'),hero),min(at('P1e')+120,at('P1f')),'puzzled'),(max(at('P5g'),term_end),min(at('P5g')+120,paragraphs[5]['endFrameExclusive']),'realize')]:
        if end-start>=60:cats.append(dict(startFrame=start,endFrameExclusive=end,pose=pose,easeInFrames=9,easeOutFrames=12))
    return dict(schemaVersion='07-04-final-timeline-v1',topicId='07.04',status='final-asr-aligned',format=dict(width=1080,height=1920,fps=60),totalFrames=timing['totalFrames'],sections=sections,catCues=cats,captions=copy.deepcopy(timing['captions']),screenTime=dict(actualMovingGameplayFrames=390,gameplayObservationFreezeFrames=freeze_frames,explanationFrames=timing['totalFrames']-390,policy='Shorts concept-sized evidence, no fixed long-form60:40 quota; all own Unity/MC/held-source explanations count as explanation'),actualListening=False,wholeRealtimePlayback=False,humanApproval=False,platformActions=[])

def prepare(timing_path,audio_path,crop_paths):
    captions=module('zen_timeline_caption_provenance',HERE/'build-selected-caption-timing.py');renderer=module('zen_timeline_renderer_contract',HERE/'render-zen-view-film.py')
    timing_path=Path(timing_path).resolve();timing=read(timing_path)
    for item in timing['inputs']:
        if sha(item['path'])!=item['sha256']:raise Pending('Actual caption timing input changed')
    asr=next(x for x in timing['inputs']if Path(x['path']).name=='review.json');review=captions.verified_asr_review(asr['path'])
    voice_pin=next(x for x in timing['inputs']if Path(x['path']).name=='07-04-voice-evidence.json');voice=read(voice_pin['path']);draft=read(PROJECT/'narration-draft.json');binding=captions.voice_binding(voice,review,draft)
    fresh=captions.build(draft,read(PROJECT/'caption-clauses-v1.json'),review,read(PROJECT/'2d-scene-plan-v1.json'))
    if any(timing.get(k)!=v for k,v in fresh.items())or timing.get('voiceBinding')!=binding or timing['fingerprint']!=captions.digest(timing['inputs']):raise Pending('Use exact current immutable caption timing')
    if timing_path.parent.name!=timing['fingerprint'][:24]or not timing_path.is_relative_to((MEDIA/'caption-timing').resolve()):raise Pending('Canonical selected caption timing path required')
    crops={}
    for path in crop_paths:
        path=Path(path).resolve();row=read(path)
        if not row.get('complete')or row.get('topicId')!='07.04':raise Pending('Actual completed selected MC crop required')
        row['_pin']=pin(path);segment=row.get('segment')
        if segment not in ('p2','p6','p7')or segment in crops:raise Pending('Exactly one real MC crop per selected segment')
        crops[segment]=row
    if set(crops)!=set(('p2','p6','p7')):raise Pending('All three actual speech-bound MC crops required')
    source=read(PROJECT/'source-footage.json');game=next(x for x in source['sources']if x['id']==source['selectedSourceId']and x['selectedForCut'])
    result=plan(timing,game,crops);audio=read(audio_path)
    audio_tools=module('zen_timeline_actual_audio_proof',HERE/'prepare-zen-view-audio.py')
    _,recipe=audio_tools.prepare(asr['path'],audio['rawNumericalLevelReview']['path'],audio['acceptedComponentsReview']['path'])
    if recipe is None:raise Pending('Actual accepted14component voice+BGM mix required')
    expected_audio=audio_tools.DEST/recipe['fingerprint'][:24]/'audio-build.json'
    if Path(audio_path).resolve()!=expected_audio.resolve()or audio_tools.reuse_audio(expected_audio.parent,recipe)!=audio:raise Pending('Current canonical reviewed audio artifact differs')
    if audio['rawVoiceFingerprint']!=voice['fingerprint']or audio['canonicalTiming']!=voice['timing']:raise Pending('Audio mix belongs to another current voice clock')
    result['audio']=dict(voice=voice['aggregateWav'],mix=audio['mixWav'],build=pin(audio_path))
    result['subtitles']={lang:pin(timing_path.parent/f'captions.{lang}.srt')for lang in ('ko','en')}
    roles={'layout':PROJECT/'edit-layout-v1.json','native-evidence':PROJECT/'native-evidence-v1.json','native-helper':HERE/'prepare-zen-view-previews.py','style':ROOT/'projects/shorts-leveldesign-03-02/visual-layout-v1.json','style-helper':ROOT/'projects/shorts-leveldesign-03-02/production/composite-native-frame.py','stream-helper':HERE/'render-first-film.py','opening-focus':PROJECT/'opening-focus-v1.json','source-footage':PROJECT/'source-footage.json','narration':PROJECT/'narration-draft.json','render-helper':HERE/'render-zen-view-film.py','caption-timing':timing_path,'voice-evidence':Path(voice_pin['path']),'asr':Path(asr['path']),'timeline-helper':Path(__file__),'caption-helper':HERE/'build-selected-caption-timing.py','audio-helper':HERE/'prepare-zen-view-audio.py','audio-build':Path(audio_path),'mc-plan':PROJECT/'2d-scene-plan-v1.json'}
    result['inputs']=[pin(path,role)for role,path in roles.items()]+[pin(x['_pin']['path'],'mc-'+key)for key,x in crops.items()]
    renderer.verify_inputs(result,require_mix=True);result['fingerprint']=digest(result)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--caption-timing');p.add_argument('--audio-build');p.add_argument('--mc-crop',action='append',default=[]);p.add_argument('--write',action='store_true');a=p.parse_args()
    if not a.caption_timing or not a.audio_build or len(a.mc_crop)!=3:
        print(json.dumps(dict(ready=False,requires='Current caption-timing, three actual silentMC crop manifests, and actual reviewed voice+BGM audio-build',mediaStarted=False)));return
    result=prepare(a.caption_timing,a.audio_build,a.mc_crop)
    if not a.write:print(json.dumps(dict(ready=True,fingerprint=result['fingerprint'],sections=len(result['sections']),written=False)));return
    target=MEDIA/'film-timelines'/result['fingerprint'][:24];target.mkdir(parents=True,exist_ok=True);path=target/'timeline.json';text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if path.exists()and path.read_text(encoding='utf-8-sig')!=text:raise Pending('Preserve differing prior timeline')
    if not path.exists():path.write_text(text,encoding='utf-8')
    print(json.dumps(dict(timeline=str(path),fingerprint=result['fingerprint'],mediaStarted=False)))

if __name__=='__main__':main()
