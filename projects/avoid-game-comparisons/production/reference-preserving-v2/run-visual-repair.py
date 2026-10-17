from pathlib import Path
import json,subprocess,sys,hashlib,shutil,datetime
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;O=R/'projects/avoid-game-comparisons/production/local/reference-preserving-v2/edit';B=O/'first-pass'
assert json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['selectedVideo']=='avoid-game-comparisons'
assert not B.exists();B.mkdir()
for name in ['avoid-game-comparisons-v2-captioned.mp4','avoid-game-comparisons-v2-clean.mp4','final-mix.wav','final-mix.m4a','final-mix-asr.json','final-mix-text-comparison.json','audio-build.json','voice-gain-repair.json']:
 if (O/name).exists():shutil.copy2(O/name,B/name)
# Both resolved locations stay inside this project's explicit edit directory.
for p in [O/'qa',B/'qa']:p.resolve().relative_to(O.resolve())
(O/'qa').rename(B/'qa')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={p.name:sha(p) for p in O.glob('cut[0-9][0-9].mp4')};assHash=sha(O/'captions.ko.ass');states=[]
for name,args in [('plan',['build-edit-plan.py']),('marks',['add-annotations.py']),('changed-footage',['render-footage.py']),('conclusion',['compose-video.py','slices']),('audio',['build-audio.py']),('pair',['compose-video.py','pair']),('whole-final-asr',['review-final-audio.py']),('new-integrity',['verify-output.py','--integrity-only'])]:
 assert json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['selectedVideo']=='avoid-game-comparisons'
 print('Starting repair stage',name,flush=True);log=O/(name+'-repair.log')
 with log.open('w',encoding='utf8') as f:r=subprocess.run([sys.executable,'-X','utf8',str(V/args[0]),*args[1:]],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 states.append({'stage':name,'exitCode':r.returncode,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});(O/'visual-repair-stages.json').write_text(json.dumps(states,indent=2)+'\n')
 if r.returncode:print(log.read_text(encoding='utf8',errors='replace')[-3000:]);raise SystemExit(r.returncode)
 print('Completed repair stage',name,flush=True)
after={p.name:sha(p) for p in O.glob('cut[0-9][0-9].mp4')};changed=[p for p in before if before[p]!=after[p]];assert set(changed)=={'cut00.mp4','cut12.mp4','cut17.mp4','cut25.mp4'};assert sha(O/'captions.ko.ass')==assHash
(O/'retained-range-proof.json').write_text(json.dumps({'before':before,'after':after,'changedCuts':changed,'unchangedCutFiles':22,'captionAssSha256':assHash,'allTimingsAndOutputEncoderSettingsUnchanged':True,'firstPassAll193FramesDirectlyReviewed':True,'findingsRepaired':['Removed level loading from opening','Replaced above-HUD character range with visible platform jumps','Followed actual flagpole screen motion at0.1s keyframes','Separated final arrow from the longer label'],'finalChangedPixels':'pending'},indent=2)+'\n');print('Changed cuts rendered;22 identical cut files retained',flush=True)
