"""Assemble additive bilingual episodes after actual candidate comparison.

All supplied dictionaries, wording, examples, contracts and audio remain exact.
This prepares text and numerical checks, never claims finished media or QA.
"""
from pathlib import Path
import copy, json, hashlib, importlib.util, math
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision'
BASE='game-math-rotation-interpolation';AUX='game-math-interpolation-teaching-additions-v2'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not any((ROOT/f'shared/output/narration/{AUX}').rglob('*.wav')),'Freeze script after audio exists'
source=read(B/'interpolation-game-insertions.json')
assert source['review']['allSelectedNativePlaybackCompared'] and source['review']['denseActionPixelsCompared']
draft=read(B/'interpolation-additive-draft.json');flow=read(B/'interpolation-flow-insertions.json')
refine=read(B/'interpolation-transition-refinement.json')
base=B/'baselines'/BASE;old=read(base/'lesson.json');original={s['id']:s for s in old['scenes']}
extras={s['id']:copy.deepcopy(s) for s in draft['additions']+flow['scenes'] if s['id'] not in refine['omit']}
for row in refine['overrides']:extras[row['id']].update(row)
# The unrecorded prerequisite makes the number four unambiguous to TTS.
extras['IP04']['ko'][0]='행렬에서 각도를 되찾기 전에 두 함수의 역할을 볼까요? 하이폿은 직각삼각형의 빗변 길이입니다. 가로 길이가 삼이고 세로 길이가 사라면, 제곱합의 제곱근인 오입니다.'
for row in source['scenes']:extras[row['id']]=copy.deepcopy(row)
orders=[
 ['IF01','01','02','IB03','03','04','IP01','IG01','05','IP02','06','IG10','IB07','07','08','IB09','09','10','IG02','11','IB12','12','IB13','13','IG07','14','IP03','15','IF02'],
 ['IF03','16','17','IG03','IP04','18','IB19','19','IG04','20','IG11','IP05','21','IG05','22','IG08','23','IB24','24','IG09','IB25','25','IG06','26','IP06']
]
audits=[]
for number,(e,order) in enumerate(zip(flow['episodes'],orders),1):
    slug=e['slug'];P=ROOT/'projects'/slug
    scenes=[copy.deepcopy(original[i] if i in original else extras[i]) for i in order]
    lesson={**copy.deepcopy(old),'slug':slug,'title':e['titleKo'],'scenes':scenes,'revisionOf':BASE,'episode':number,'causalSpine':e['question'],'baselineOriginalScenesUnchanged':True,'baselineSource':base.relative_to(ROOT).as_posix()}
    write(P/'production/lesson.json',lesson)
    titles={'ko':e['titleKo'],'en':e['titleEn']}
    for lang in ['ko','en']:write(P/f'script/narration.{lang}.json',{'title':titles[lang],'scenes':[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in scenes]})
    m=json.loads(json.dumps(read(base/'project.json'),ensure_ascii=False).replace(BASE,slug))
    m.update(slug=slug,titles=titles,status='additive-revision-preparing',publishReady=False,revisionOf=BASE)
    m['video']['durationSeconds']=0;m['finalRender']={'status':'not-rendered','currentPixelApproval':False}
    m['publishing']={'defaults':'shared/publishing/youtube-defaults.json','privateUploadComplete':False,'fullPublishingSettingsComplete':False,'baselineVideoId':'mGBYkpSC9Mw','baselinePreserved':True,'scheduleStatus':'plan only; save actual matching slot after reviewed upload','coachingEndingLinkRequired':True,'pinnedCoachingCommentRequired':True}
    m['approvals']={'script':'preservation and prerequisites checked; final audio/flow pending','voice':'same approved reference; final listening pending','rights':'recording reuse statement retained; game-IP/human review pending','pixels':'pending'}
    m['editing'].update(timingStatus='awaiting measured current-hash new audio and exact frame plan',backgroundMusic=False)
    for key in ['actualGameplaySeconds','actualExplanationSeconds','actualGameplayShare','actualCommercialGameplaySeconds','actualDevelopmentFootageSeconds','actualPrototypeExplanationSeconds']:m['editing'][key]=None
    m['editing']['causalFlow']={'required':True,'chain':'previous verified result → unresolved question → purpose of next operation','plan':(B/'interpolation-episode-flow-audit.json').relative_to(ROOT).as_posix(),'continuousReview':'pending'}
    m['editing']['exampleInterleaving']['reviewStatus']='native candidate comparisons completed; final annotated footage pending'
    m['tts']['renderMode']='preserved-baseline-plus-separate-authorized-additions; do not regenerate complete project'
    m['audio']['mixStatus']='not-rendered';m['membershipOutro']['appliedToFinal']=False
    m['paths']['productionData']=f'projects/{slug}/production/lesson.json';m['paths']['manimProject']='manim/projects/game-math-part2-teaching-revision/interpolation_additions.py'
    m['preservation']={'baseline':BASE,'originalIds':[i for i in order if i in original],'originalAudioMethod':'copy exact baseline scene samples and encoded clips; preserve approved wording and timing','baselineMediaChanged':False,'introAndMemberOutro':'reuse original intro/outro encoded clips with member profiles/name/badges','palette':'preserved existing research-paper-white-v1, project exception'}
    m['lecture'].update(episode=number,viewerQuestion=e['question'])
    write(P/'project.json',m)
    retained=[s for s in scenes if s['id'] in original];assert all(s==original[s['id']] for s in retained)
    audits.append({'slug':slug,'episode':number,'order':order,'originalIds':[s['id'] for s in retained],'originalScenesExact':True,'originalKoLines':sum(len(s['ko']) for s in retained),'newActualCapacitySeconds':sum(s['maximumSeconds'] for s in scenes if 'maximumSeconds' in s),'mediaQaComplete':False})
assert [i for e in audits for i in e['originalIds']]==list(original)
retained=[s for e in flow['episodes'] for s in read(ROOT/'projects'/e['slug']/'production/lesson.json')['scenes'] if s['id'] in original]
assert retained==old['scenes']
assert all(read(ROOT/'projects'/e['slug']/'production/lesson.json')['contract']==old['contract'] for e in flow['episodes'])
write(B/'interpolation-episode-flow-audit.json',{'episodes':audits,'allOriginalSceneDictionariesExact':True,'originalScenes':len(original),'originalKoLines':sum(len(s['ko']) for s in retained),'originalEnLines':sum(len(s['en']) for s in retained),'originalOrderAndContractExact':True,'omittedUnrecordedRepetition':refine['omit'],'completeBoundary':'after original15; interpolation/time/history/task choice completed before conversion conventions','finalContinuousReview':False})
items=[extras[i] for order in orders for i in order if i in extras]
assert len({s['id'] for s in items})==len(items)
mapping=[{'ttsScene':f'{i:02d}','additionId':s['id'],'sourceType':'actual-footage' if s['kind']=='actual' else 'bridge' if s['id'].startswith('IB') else 'framing' if s['id'].startswith('IF') else 'supplement'} for i,s in enumerate(items,1)]
oldm=read(base/'project.json');tts={**oldm['tts'],'outputDir':f'shared/output/narration/{AUX}/qwen3-1.7b-balanced-v1','filenameStem':AUX+'-qwen3-1.7b-balanced-v1','renderMode':'line'}
manifest={'schemaVersion':1,'slug':AUX,'title':'회전 보간·표현 변환의 새 기초 설명과 유기적 연결','status':'narration-preparation','revisionOf':BASE,'standaloneUploadAllowed':False,'authorizationQueue':(B/'queue.json').relative_to(ROOT).as_posix(),'paths':{'script':f'projects/{AUX}/script/narration.ko.json','scriptEn':f'projects/{AUX}/script/narration.en.json','captionsKo':f'projects/{AUX}/script/voice-aligned.ko.srt','captionsEn':f'projects/{AUX}/script/voice-aligned.en.srt'},'tts':tts,'editing':{'exampleSeconds':0,'narrationPlacement':'continuous-across-all-three-segments','backgroundMusic':False},'preservation':{'baselineAudioOverwritten':False,'originalScenes':len(original),'existingVoiceReferencePreserved':True},'contract':old['contract']}
write(ROOT/'projects'/AUX/'project.json',manifest)
for lang in ['ko','en']:write(ROOT/'projects'/AUX/f'script/narration.{lang}.json',{'project':AUX,'language':lang,'status':'authorized-new-only-additive-narration','scenes':[{'id':r['ttsScene'],'title':s['title'],'lines':s[lang]} for r,s in zip(mapping,items)]})
write(B/'interpolation-addition-tts-map.json',mapping)
# Independent numerical checks of narrated examples and critical boundaries.
spec=importlib.util.spec_from_file_location('rotation_reference',ROOT/'production/batches/game-math-part2-full-series/rotation-conversions.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
checks=[]
def check(name,value,expected,tol=1e-9):
    a=np.asarray(value);b=np.asarray(expected);assert np.allclose(a,b,atol=tol,rtol=0),name
    checks.append({'name':name,'computed':a.tolist(),'expected':b.tolist(),'passed':True})
qa=np.array([1.,0,0,0]);qb=r.axis_quaternion([0,0,1],math.pi/2)
for t in [.25,.5,.75]:
    q=r.interpolate(qa,qb,t);check(f'90 degree physical rotation at t={t}',math.degrees(2*math.acos(q[0])),90*t)
    check(f'unit length t={t}',np.linalg.norm(q),1)
check('dot30',np.array([1.,0])@np.array([math.sqrt(3)/2,.5]),math.sqrt(3)/2)
check('acos dot30 degrees',math.degrees(math.acos(math.sqrt(3)/2)),30)
check('four component angle is half physical90',math.degrees(math.acos(qa@qb)),45)
check('hypot3,4',math.hypot(3,4),5);check('atan2 1,1 degrees',math.degrees(math.atan2(1,1)),45)
check('atan2 positive y negative x quadrant',math.degrees(math.atan2(1,-1)),135)
R=r.to_matrix(r.axis_quaternion([0,0,1],math.pi));check('Rz180 diagonal',np.diag(R),[-1,-1,1]);check('trace180',np.trace(R),-1);check('w180 zero within roundoff',r.from_matrix(R)[0],0)
check('dominant z extraction returns same matrix',r.to_matrix(r.from_matrix(R)),R)
check('midpoint vector',r.to_matrix(r.interpolate(qa,qb,.5))@np.array([1.,0,0]),[math.sqrt(2)/2,math.sqrt(2)/2,0])
q120=r.axis_quaternion([0,0,1],2*math.pi/3)
check('SLERP physical120 at quarter',math.degrees(r.quaternion_axis(r.interpolate(qa,q120,.25))[1]),30)
check('NLERP quarter approximately27.8',math.degrees(r.quaternion_axis(r.interpolate(qa,q120,.25,'nlerp'))[1]),27.79577249602797)
for pitch in [math.pi/2,-math.pi/2]:
    m=r.to_matrix(r.euler_quaternion(.3,pitch,.7));angles=r.matrix_euler(m);check(f'singular Euler roundtrip pitch={pitch}',r.to_matrix(r.euler_quaternion(*angles)),m)
try:r.unit([0,0,0,0]);raise AssertionError('zero quaternion accepted')
except ValueError:checks.append({'name':'zero quaternion rejected','passed':True})
audit={'status':'pre-TTS preservation and numerical checks; audio/pixels/listening pending','allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'originalScenes':len(original),'originalKoLines':sum(len(s['ko']) for s in retained),'originalEnLines':sum(len(s['en']) for s in retained),'gameplayComparedBeforeDependentNarration':True,'newOnlyScenes':len(items),'newKoLines':sum(len(s['ko']) for s in items),'checks':checks,'scriptSha256':{lang:hashlib.sha256((ROOT/'projects'/AUX/f'script/narration.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']},'humanListening':'pending','engineInternalsAsserted':False}
write(B/'interpolation-pretts-audit.json',audit)
q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']==BASE);item['status']='additive-preparation';item['revision'].update(episodeSlugs=[e['slug'] for e in flow['episodes']],originalPreservationAuditPassed=True,footageComparisonPassed=True,episodePlanReviewed=True,flowReviewPassed=False,narrationComplete=False,renderComplete=False)
write(B/'queue.json',q)
print(json.dumps({'originalScenes':len(original),'originalKoLines':audit['originalKoLines'],'newTtsScenes':len(items),'newKoLines':audit['newKoLines'],'mathChecks':len(checks),'actualCapacitySeconds':[e['newActualCapacitySeconds'] for e in audits],'mediaComplete':False},ensure_ascii=False))
