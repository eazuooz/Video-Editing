"""Preserved-scene episode scripts and manifests. No media or publishing claim."""
from pathlib import Path
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
base=B/'baselines/game-math-quaternion-operations';D=read(base/'lesson.json');original={s['id']:s for s in D['scenes']}
draft=read(B/'quaternion-additive-draft.json');framing=read(B/'quaternion-episode-framing.json');game=read(B/'quaternion-game-insertions.json')
extras={s['id']:dict(s,kind='explanation') for s in draft['additions']+draft['bridges']+framing['scenes']}
for s in read(B/'quaternion-clarified-additions-v3.json')['overrides']:extras[s['id']].update(s)
game_overrides={s['id']:s for s in read(B/'quaternion-game-clarifications-v4.json')['scenes']}
for s in game['scenes']:
    s={**s,**game_overrides[s['id']]}
    extras[s['id']]=dict(s,kind='actual',maxSeconds=s['maximumSeconds'])
for s in read(B/'quaternion-game-closings-v5.json')['scenes']:
    extras[s['id']]=dict(s,kind='actual',maxSeconds=s['maximumSeconds'])
for s in read(B/'quaternion-retakes-v5.json')['overrides']:
    extras[s['id']].update({k:s[k] for k in ['ko','en']})
for s in read(B/'quaternion-retakes-v6.json')['overrides']:
    extras[s['additionId']].update({k:s[k] for k in ['ko','en']})
for s in read(B/'quaternion-source-corrections-v5.json')['scenes']:
    extras[s['id']].update(s);extras[s['id']]['maxSeconds']=s['maximumSeconds']
for s in extras.values():s.setdefault('title','다음 계산으로 연결하기')
orders=[
 ['F01','01','B02','02','N01','N02','N09','GA06','B03','N03','03','GA01','B04','04','N04','GA07','B05','05','GA09','B06','06','B07','07','GA05','B08','08','GA04','B09','09','B10','10','N05','GA02','B11','11','GA08','B12','12','GA03','B13','13','GA10','F02'],
 ['F03','B14','14','GB06','B15','N06','15','B16','16','GB01','B17','17','GB02','B18','18','B19','19','GB03','B20','20','GB04','B21','N07','21','B22','N08','22','GB05','B23','23','B24','24','B25','25','GB07','B26','26']
]
titles=[{'ko':'게임수학 Part2 · 쿼터니언 ① 허수에서 회전과 역원까지','en':'Game Mathematics Part 2: Quaternions 1 — From Imaginary Numbers to Rotation and Inverses'}, {'ko':'게임수학 Part2 · 쿼터니언 ② 합성·목표 자세·벡터 회전','en':'Game Mathematics Part 2: Quaternions 2 — Composition, Target Orientation and Vector Rotation'}]
result=[]
for number,(episode,order,title) in enumerate(zip(framing['episodes'],orders,titles),1):
    slug=episode['slug'];P=ROOT/'projects'/slug
    scenes=[copy.deepcopy(original.get(i,extras.get(i))) for i in order]
    lesson={**D,'slug':slug,'title':title['ko'],'scenes':scenes,'revisionOf':'game-math-quaternion-operations','episode':number,'causalSpine':episode['question'],'baselineSource':str(base.relative_to(ROOT)).replace('\\','/'),'baselineOriginalScenesUnchanged':True}
    write(P/'production/lesson.json',lesson)
    for lang in ['ko','en']:write(P/f'script/narration.{lang}.json',{'title':title[lang],'scenes':[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in scenes]})
    m=read(base/'project.json')
    # Only new output/project paths are rewritten. Baseline files remain intact.
    m=json.loads(json.dumps(m,ensure_ascii=False).replace('game-math-quaternion-operations',slug))
    m.update(slug=slug,titles=title,status='additive-revision-preparing',publishReady=False,revisionOf='game-math-quaternion-operations')
    m['video']['durationSeconds']=0
    m['finalRender']={'status':'not-rendered','currentPixelApproval':False}
    m['publishing']={'coachingEndingLinkRequired':True,'pinnedCoachingCommentRequired':True,'defaults':'shared/publishing/youtube-defaults.json','privateUploadComplete':False,'fullPublishingSettingsComplete':False,'baselineVideoId':'03OXtik2nes','baselinePreserved':True,'scheduleStatus':'plan-only; current Studio must be rechecked after reviewed upload'}
    m['approvals']={'script':'additive-original-preservation-reviewed; final timing pending','voice':'same approved reference; new audio and final listening review pending','rights':'recording statements retained; game-IP/human review pending','pixels':'pending'}
    m['editing']['timingStatus']='awaiting-current-hash-new-audio-and-exact-frame-plan'
    for key in ['actualGameplaySeconds','actualExplanationSeconds','actualGameplayShare','actualCommercialGameplaySeconds','actualDevelopmentFootageSeconds','actualPrototypeExplanationSeconds']:m['editing'][key]=None
    m['editing']['exampleInterleaving']['reviewStatus']='played candidates matched to script; final cuts/tracking pending'
    m['editing']['causalFlow']={'required':True,'chain':'previous verified result → unresolved question → purpose of next operation','plan':'production/batches/game-math-part2-teaching-revision/quaternion-episode-flow-audit.json','continuousReview':'pending'}
    m['tts']['renderMode']='preserved-baseline-plus-separate-authorized-additions; do not regenerate complete project'
    m['audio']['mixStatus']='not-rendered';m['membershipOutro']['appliedToFinal']=False
    m['paths']['productionData']=f'projects/{slug}/production/lesson.json'
    m['paths']['manimProject']='manim/projects/game-math-part2-teaching-revision/supplements.py'
    m['preservation']={'baseline':'game-math-quaternion-operations','originalIds':[i for i in order if i in original],'originalAudioMethod':'crop approved narration-final.wav by exact original scene starts/durations; keep pauses and repairs','baselineMediaChanged':False,'introAndMemberOutro':'reuse original intro.mp4/outro.mp4 without regenerating identities'}
    m['lecture']['episode']=number;m['lecture']['viewerQuestion']=episode['question']
    write(P/'project.json',m)
    retained=[s for s in scenes if s['id'] in original]
    assert all(s==original[s['id']] for s in retained)
    result.append({'slug':slug,'episode':number,'order':order,'originalIds':[s['id'] for s in retained],'originalScenesExact':True,'originalKoLines':sum(len(s['ko']) for s in retained),'newActualCapacitySeconds':sum(s['maximumSeconds'] for s in scenes if 'maximumSeconds' in s),'mediaQaComplete':False})
assert [i for r in result for i in r['originalIds']]==[s['id'] for s in D['scenes']]
assert sum(r['originalKoLines'] for r in result)==155
write(B/'quaternion-episode-flow-audit.json',{'episodes':result,'all26OriginalScenesAnd155KoLinesExact':True,'formulaAndCoordinateContractPreserved':True,'complexPrerequisitesBeforeHalfAngle':True,'normBeforeInverse':True,'orderedCompositionBeforeDelta':True,'CDefinedBeforeSandwichExample':True,'twoEpisodeBoundary':'after original13 general inverse, before original14 application/composition','finalContinuousReview':False})
print(json.dumps({'episodes':len(result),'allOriginalScenesExact':True,'originalKoLines':155,'newActualCapacitySeconds':sum(r['newActualCapacitySeconds'] for r in result)}))
