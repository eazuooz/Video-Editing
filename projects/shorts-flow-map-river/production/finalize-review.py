"""Record the exact local review master, without claiming human review or publishing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, subprocess
import numpy as np

P=Path(__file__).resolve().parents[1]; R=P.parents[1]
L=P/'production/local/final-reviewed'; A=P/'production/local/audio'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return str(Path(p).relative_to(R)).replace('\\','/')
now=datetime.now(timezone.utc).isoformat()
pair=read(L/'pair-build.json'); integrity=read(L/'integrity.json')
assert integrity['status']=='pass' and sha(L/'captioned.mp4')==pair['captioned']
assert pair['captioned']=='cb258e87d1e3aa033efbc366735e29e2a79c6f7a03b2163db008cee6f2de5d59'
raw=subprocess.run(['ffmpeg','-v','error','-i',str(L/'captioned.mp4'),'-vf','crop=1080:420:0:0,scale=108:42,format=gray','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
frames=np.frombuffer(raw,np.uint8).reshape(-1,42,108).astype(float)
delta=np.abs(frames-frames[0]).mean((1,2))
assert len(frames)==3067 and delta.max()<1
header=dict(masterSha256=pair['captioned'],frames=3067,scope='Fixed top420px; all decoded frames compared with first frame after 10x downsampling',meanAbsPixelDeltaMax=float(delta.max()),threshold=1,status='pass',repair='Fixed title and term/source-kind chips composed by libass over black header; original Motion Canvas render retained.')
save(L/'header-integrity.json',header)

# Saved editable scene controls use the Game view, not the private offline RenderTexture.
scene_root=R/'unity/VideoEditing/Assets/VideoScenes'/P.name
scenes=sorted((scene_root/'Scenes').glob('*.unity')); assert len(scenes)==6
for scene in scenes:
    text=scene.read_text(encoding='utf-8')
    text,n=re.subn(r'(Camera:\n(?:(?!---).)*?  m_Enabled:) 0',r'\1 1',text,flags=re.S)
    text=re.sub(r'  m_TargetTexture: \{fileID: \d+\}', '  m_TargetTexture: {fileID: 0}',text)
    text=text.replace('  animate: 0','  animate: 1')
    scene.write_text(text,encoding='utf-8')
    assert '  animate: 1' in text and '  m_TargetTexture: {fileID: 0}' in text

m=read(P/'project.json'); m['status']='awaiting-local-final-review'
m['paths']['videoClean']=rel(L/'clean.mp4'); m['paths']['videoBurnedCaptions']=rel(L/'captioned.mp4')
m['video'].update(durationSeconds=pair['durationSeconds'],frames=pair['frames'])
m['finalRender']=dict(revision='flow-map-v1',sha256=pair['captioned'],technicalChecks='passed',knownIssues=[],openItems=['사용자 최종 시청·청취 검수 대기. ASR·연속성 검사는 사람의 청취 승인이 아닙니다.'])
m['delivery'].update(captioned=f'output/{P.name}/{P.name}.captioned.mp4',index=f'output/{P.name}/index.html')
save(P/'project.json',m)

plan=read(P/'planning/production-plan.json'); plan['status']='local-final-review-ready'; plan['sceneSaveStatus']='six-independent-editable-scenes-saved'
plan['durationSeconds']=pair['durationSeconds']; plan['frames']=3067
plan['recommendedChoices'][0]=dict(choice='51.1167 seconds at original natural speech speed; one river test bed',reason='Measured completed narration accommodates the worked RG example, two-phase reset and changing-obstacle limit without padding.')
plan['technicalLimits']=[x.replace('; not material colour and not the same quantity as normal direction','; these stored values are directional data, not material colour') for x in plan['technicalLimits']]
plan['capture']=dict(editor='Unity6000.6.0f1',project='unity/VideoEditing',mainProjectPipeline='URP17.6.0',actualCapturePipeline='Isolated Built-in project, linear colour, custom SRPDefaultUnlit-compatible shader. URP runtime not certified.',isolatedProject=rel(P/'production/local/unity-capture'),width=1080,height=1080,fps=60,frames=3067,finalCanvas=[1080,1920],readback=rel(P/'production/local/capture-full/readback.json'),sharedUserEditorStopped=False)
plan['glossary']=[dict(en='Flow Map',ko='플로 맵',meaning='위치마다 그림을 움직일 방향을 저장한 지도'),dict(en='Texture Coordinates (UV)',ko='텍스처 좌표',meaning='물결 그림의 어느 위치를 읽을지 정하는 좌표'),dict(en='Shader',ko='셰이더',meaning='지도 값을 읽고 화면에 표시할 물결을 계산하는 프로그램',tts='셰이더'),dict(en='Phase Offset',ko='위상차',meaning='같은 반복을 서로 다른 시점에 시작하는 것')]
plan['workedExample']=dict(storage='Linear RGBAFloat data; R horizontal/U, G vertical/V',decode='direction = RG * 2 - 1',neutral='(0.5,0.5) → (0,0)',right='(1,0.5) → (1,0)',arrows='84 lattice positions, excluding near-zero values at the obstacle. Same texture samples as shader; screen projection saved in readback.',implementation='Two half-cycle-offset UV distortion phases with triangular blend weights; periodic local distortion, not a fluid solver.')
timing=read(P/'production/visual-timing.json'); plan['realizedTeachingBeats']=timing
for i,s in enumerate(plan['scenes']):
    s['unityScene']=rel(scenes[i]); s['sharedAssetPaths']=[rel(scene_root/x) for x in ['FlowWater.shader','FlowRiverDemo.cs','Generated/Flow.asset','Generated/Ripple.asset']]
    s['speechVisualOverlap']=True
plan['finalMaster']=dict(path=m['paths']['videoBurnedCaptions'],sha256=pair['captioned'])
plan['savedSceneReview']='Capture scene runtime passed in isolated project. Saved camera enabled/target cleared and animate enabled for editing; live main URP editor not operated.'
save(P/'planning/production-plan.json',plan)

sources=read(P/'sources/sources.json')
sources['sources'][0]['localFile']=rel(P/'production/local/research/valve-waterflow.pdf')
sources['sources'][0]['sha256']=sha(P/'production/local/research/valve-waterflow.pdf')
for a in sources['assets']:
    if a['kind']=='licensed-music': a['sha256']=sha(R/a['path'])
    elif a['kind']=='owned-brand': a['files']=[dict(path=rel(R/a['path']/(n+'.png')),sha256=sha(R/a['path']/(n+'.png'))) for n in ['puzzled','realize','relief']]
    elif a['kind']=='self-authored': a['sceneRoot']=rel(scene_root)
save(P/'sources/sources.json',sources)

ledger=read(P/'production/review-ledger.json'); ledger.update(updatedAt=now,masterSha256=pair['captioned'])
ledger['checks']=[x for x in ledger['checks'] if x['id'] in ['source-reading','duplicate-review']]+[
 dict(id='native-unity-capture',status='pass',evidence=rel(P/'production/local/capture-full/success.json')),
 dict(id='video-audio-integrity',status='pass',evidence=rel(L/'integrity.json'),summary='Both3067-frame1080x1920/60CFR H264 masters decoded fully; identical unmodified AAC;24KO/EN cues inside duration.'),
 dict(id='continuous-header',status='pass',evidence=rel(L/'header-integrity.json')),
 dict(id='visual-cue-mobile-review',status='pass',evidence=rel(L/('qa-'+pair['captioned'][:12])/'index.json'),summary='Native/cue/boundary frames and375px playback inspected; same river, colour examples, arrows, mascot and fixed captions. Pre-repair QA images remain historical only.'),
 dict(id='audio-continuity',status='technical-pass',evidence=rel(A/'audio-continuity.json'),summary='Full unprompted voice and mix ASR. Orthography/particle timing reconciliation retained separately. No digital truncation or speech ducking detected;2source-quiet candidates near6.55–7.25s and24.65–25.25s need final listening.'),
 dict(id='human-full-listening',status='pending'),dict(id='human-final-video-review',status='pending',sha256=pair['captioned'])]
ledger['platform']={'youtube':'not-uploaded','drive':'not-requested','automaticNextVideo':False}
save(P/'production/review-ledger.json',ledger)
cp=read(P/'production/checkpoint.json'); cp.update(stage='local-final-review-ready',nextAction='User watches/listens to this exact captioned master. No upload, scheduling or next video without the applicable instruction.',updatedAt=now,finalMaster=plan['finalMaster'],delivery=m['delivery'],technicalChecks='passed',humanFinalReview='pending')
save(P/'production/checkpoint.json',cp)
wpath=R/'shared/publishing/shorts-worklist.json'; w=read(wpath)
matches=[]
def visit(obj):
    if isinstance(obj,list):
        for x in obj: visit(x)
    elif isinstance(obj,dict):
        if obj.get('slug')==P.name and 'title' in obj: matches.append(obj)
        else:
            for x in obj.values(): visit(x)
visit(w); assert len(matches)==1
matches[0].update(status='awaiting-local-final-review',production='Complete51.1167s1080x1920/60Unity+MotionCanvas;BGMincluded',review='user-final-viewing-and-listening-pending',finalMaster=plan['finalMaster'],delivery=m['delivery'])
w['updatedAt']=now; save(wpath,w)
print(json.dumps(dict(status='recorded',captioned=pair['captioned'],duration=pair['durationSeconds'],humanReview='pending')))
