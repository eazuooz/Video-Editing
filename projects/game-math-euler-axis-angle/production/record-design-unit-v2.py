"""Record selected revision design without changing active speech inputs."""
from pathlib import Path
import json,datetime,hashlib,ast,subprocess
R=Path(__file__).resolve().parents[3];P=R/'projects/game-math-euler-axis-angle'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
m=read(P/'sources/media-revision-v2.json')
m['additionalSource']=read(P/'production/local/revision-v2/second-source-acquisition.json')
m['availableNonrepeatingSeconds']=467+165
m['finalSelectedMovingReview']='pending exact measured cut selection'
save(P/'sources/media-revision-v2.json',m)
save(P/'sources/annotation-plan-v2.json',read(P/'production/local/revision-v2/annotation-plan.json'))
p=read(P/'project.json')
baseline=json.loads(subprocess.check_output(['git','show','acebcb0437af6d523230b58196dbf27fa57f0ccd:projects/game-math-euler-axis-angle/project.json'],cwd=R))
p['revision']['baselineManifestState']=dict(durationSeconds=baseline['video']['durationSeconds'],finalRender=baseline['finalRender'],audio=baseline['audio'],engines=baseline['engines'],approvals=baseline['approvals'],publishing=dict(videoId='iv9esV7vv_g',visibility='private',settingsVerifiedAt=baseline['publishing']['verifiedAtUtc']))
p['editing']['timingStatus']='revision-v2 measured timing pending; historical totals in baselineManifestState'
p['editing']['explanationStyle']='Detailed Unity spatial aircraft and fixed/body axes; Manim arithmetic/code; timed labels and independent-gameplay annotations'
p['engines']=['Unity6000.6.0f1','Manim Community0.20.1','FFmpeg compositing']
p['approvals']['visualPixelReview']='revision-v2 representative sample only; full output pending'
p['audio'].update(mixStatus='revision-v2 voice generation in progress',bgmTargetLufs=-31,bgmPlacement='quiet instrumental under body, voice-driven ducking',backgroundMusic=dict(enabled=True,required=True,policy='lecture-lofi-game-audio-v1',track='shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3',sampleListening='pending'),sourceAudioPolicy='Both independent gameplay sources are video-only. No unverified soundtrack or effects. Narration plus rights-recorded instrumental music.')
p['lecture']['backgroundMusic']=True
p['finalRender']=dict(status='revision-v2-not-rendered',currentRevisionComplete=False,baselineVideoId='iv9esV7vv_g',baselinePreserved=True)
save(P/'project.json',p)
l=read(P/'production/review-ledger.json');l['updatedAt']=now
new_checks=[dict(name='revised source coverage, full KOEN and chapter joins',status='pass-with-scope',evidence='production/content-review-v2.json',scope='26scenes/157pairedparagraphs, original8.3–8.4 order, primary math verification, all25boundary links; actual TTS and pixels remain pending'),dict(name='detailed Unity aircraft representative sample',status='pass-with-scope',evidence='production/local/revision-v2/unity-preview/sample-qa.json',scope='Three-second FHD60 sample directly inspected. Updated layout and whole moving sequence not yet rendered.'),dict(name='actual-footage annotation keyframes',status='prepared-pixel-keyframes-reviewed-by-footage-agent',evidence='sources/annotation-plan-v2.json',scope='23seconds sparsewindows and seven verified2Dtrailpoints; newASRcue binding and final moving pixels pending')]
l['checks']=[c for c in l['checks'] if c['name'] not in {v['name'] for v in new_checks}]+new_checks
save(P/'production/review-ledger.json',l)
paths=['planning/outline.md','planning/production-plan.json','project.json','script/revision-v2/narration.ko.json','script/revision-v2/narration.en.json','production/revision-v2/lesson.json','production/revision-v2/tts-manifest.json','production/content-review-v2.json','production/finalize-script-design-v2.py','production/render-voice-v2.py','production/review-voice-v2.py','production/align-voice-v2.py','production/serve-review-v2.cjs','production/record-design-unit-v2.py','production/review-ledger.json','production/checkpoint.json','sources/media-revision-v2.json','sources/annotation-plan-v2.json','publishing/studio-revision-selection.json']
owned=['projects/'+P.name+'/'+s for s in paths]+['production/preflight/game-math-euler-axis-angle.json','production/preflight/game-math-euler-axis-angle/candidate.json']
for rel in owned:
 f=R/rel
 if f.suffix=='.json':read(f)
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf8'))
out=P/'production/local/revision-v2/design-commit-spec.json'
save(out,dict(message='Revise M04 teaching script, source evidence and continuous narration design',paths=owned))
print(json.dumps(dict(validatedPaths=len(owned),spec=str(out))))
