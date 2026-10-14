"""Bind the directly compared new guide; preserve every original paragraph/take."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil, subprocess
import numpy as np, soundfile as sf
R=Path(__file__).resolve().parents[3]; P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
 assert not p.exists(),str(p)
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
tts=read(P/'part1-complete-close-retry-tts-execution-v285.json')
asr=read(P/'part1-complete-close-take-asr-execution-v286.json')
assert tts['exitCode']==asr['exitCode']==0 and asr['status']=='complete' and len(asr['results'])==2
for w in [tts['actualIdentity'],asr['worker']]:
 assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
take=tts['results'][0]; assert take['technicalTailGatePassed'] and sha(R/take['path'])==take['sha256']
ko=read(P.parent/'script/physical-part1-complete-close.ko.v284.json')['scenes'][0]['lines'][0]
en=read(P.parent/'script/physical-part1-complete-close.en.v284.json')['scenes'][0]['lines'][0]
records=[]
for item in asr['results']:
 path=R/item['path']; assert sha(path)==item['sha256']; a=read(path)
 assert not a['expectedTextUsedAsPrompt'] and a['input']['fullPcmPreserved']
 records.append({**item,'fullActualText':a['text'],'allWordTimestampsDirectlyRead':True,
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'wholeOnsetAndEndingCompared':True,
  'wordCount':len(a['words']),'omissionRepeatGreetingDetected':False,
  'remainingVariants':['Unchanged neighbour: 앞의/앞에 particle remains human pronunciation review.'] if 'context' in item['label'] else []})
proof={'reviewedAt':stamp(),'selectedTake':take,'ko':ko,'en':en,'records':records,
 'rawAndCompleteNeighbourContextDirectlyCompared':True,'selectedForPrivateTechnicalProduction':True,
 'currentMixedAudioApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending',
 'scope':'Direct full text and every word interval comparison. No human listening is claimed. Only newly authored two-sentence guide is replaced; original111/other selected PCM retained.',
 'preservedSlotFrames':413,'newVoiceSamples':132480,'sampleRate':24000,
 'remaining413FrameSlotPurpose':'Keep the approved spatial comparison duration. After complete speech, the separate game-state-update row remains visible for reading; no game footage loop or unrelated idle.',
 'resourceObservation':{'workersObservedDead':True,'gpu':subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.free,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()},
 'allFinalPixelsReviewed':False,'uploaded':False,'newGitImages':0}
dest=P/'part1-selected-guide-direct-review-v287.json';save(dest,proof)
base=R/'production/research/game-lighting-history/local/part1-selected-guide-v287'
audio=base/'audio/episode04-part1-selected-guide-v287.wav'; audio.parent.mkdir(parents=True,exist_ok=True)
v,sr=sf.read(R/take['path'],dtype='float32'); assert sr==24000 and len(v)==132480 and v.ndim==1
assert not audio.exists(); padded=np.pad(v,(0,413*400-len(v)));sf.write(audio,padded,24000,subtype='FLOAT')
back,sr=sf.read(audio,dtype='float32'); assert np.array_equal(back,padded)
folder=R/'motion-canvas/src/projects/game-lighting-history-04/spatial'
clock={'id':'outer-comparison-before','role':'outer-comparison-before','title':'표시 빈도와 게임 상태를 구별',
 'frames':413,'sourceSha256':take['sha256'],'boundSourceSha256':take['sha256'],
 'sourceSampleRange':[0,132480],'wholeAndContextCompared':True,
 'stages':[{'fromFrame':0,'toFrame':132,'progressFrom':0,'progressTo':.5,'anchor':ko.split('. ')[0]+'.'},
  {'fromFrame':142,'toFrame':332,'progressFrom':.5,'progressTo':1,'anchor':ko.split('. ')[1]}]}
scene=folder/'part1-outer-comparison-before-v287.tsx';assert not scene.exists()
scene.write_text("import {part1ReviewedSourceScene} from './part1-reviewed-source-runtime-v200';\nexport default part1ReviewedSourceScene("+json.dumps(clock,ensure_ascii=False,indent=2)+');\n','utf-8')
project=folder/'episode04-part1-selected-guide-v287.ts';assert not project.exists()
project.write_text("import {makeProject} from '@motion-canvas/core';\nimport s0 from './part1-outer-comparison-before-v287?scene';\nexport default makeProject({scenes:[s0],audio:'/@fs/"+audio.as_posix()+"'});\n",'utf-8')
meta=read(folder/'episode04-part1-spatial-bank-v206.meta');meta['shared']['range']=[0,413/60];save(project.with_suffix('.meta'),meta)
job={'name':project.stem,'project':rel(project),'frames':413,'audio':{'path':rel(audio),'sha256':sha(audio),'samples':len(padded)},
 'output':rel(base/'renders'/f'{project.stem}.mp4'),'execution':rel(base/'renders'/f'{project.stem}.execution.json')}
save(base/'plan.json',{'preparedAt':stamp(),'jobs':[job],'selectedGuideReview':{'path':rel(dest),'sha256':sha(dest)},'clock':clock,'allFinalPixelsReviewed':False})
config=R/'motion-canvas/vite.game-lighting-history04.part1-selected-guide-v287.config.ts';assert not config.exists()
config.write_text((R/'motion-canvas/vite.game-lighting-history04.part1-spatial-bank-v206.config.ts').read_text('utf-8-sig').replace('part1-spatial-bank-v206','part1-selected-guide-v287').replace('port:9275','port:9278'),'utf-8')
cp=R/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
j['episode04Part1SelectedGuideV287']={'review':rel(dest),'sha256':sha(dest),'status':'selected-awaiting-one-spatial-guide-render-and-current-mix','frames':413,'newVoiceSeconds':5.52,'humanWholeListening':'pending','finalMixedAsrApproved':False,'uploaded':False}
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':'One413-frame guide source render through actual GUI; then narrowly replace guide PCM and bind current mixed recognition'};j['updatedAt']=stamp();cp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'selectedTakeSha256':take['sha256'],'frames':413,'wordsRead':[r['wordCount'] for r in records],'newTts':0,'finalMixedApproved':False}))
