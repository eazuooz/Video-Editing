"""D30 one final source/diagram correction bundle plus authorized native game-audio mix."""
from pathlib import Path
import subprocess,json,sys,hashlib
HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1];ROOT=HERE.parents[3]
plan_file=HERE/'edit-plan.json';plan=json.loads(plan_file.read_text('utf-8'));edit=ROOT/plan['outputDir'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/plan['audio']['sourceReviewPath'])==plan['audio']['sourceReviewSha256'],'Audio source decision record changed after freeze'
subprocess.run([sys.executable,str(HERE/'prepare-final-v3.py')],cwd=ROOT,check=True)
reuse=json.loads((edit/'visual-reuse.json').read_text('utf-8'))
commands=[
 [sys.executable,str(HERE/'audio_pipeline.py'),'mix','--plan',str(plan_file),'--output-dir',str(edit)],
 [sys.executable,str(HERE/'video_pipeline.py'),'cuts','--plan',str(plan_file),*[arg for cid in reuse['needsRender'] for arg in ['--only-cut',cid]]],
 [sys.executable,str(HERE/'video_pipeline.py'),'pair','--plan',str(plan_file)],
 [sys.executable,str(HERE/'video_pipeline.py'),'verify','--plan',str(plan_file)],
 [sys.executable,str(HERE/'review_audio.py'),'--plan',str(plan_file),'--encoded',str(edit/(plan['outputStem']+'-captioned.mp4'))],
 [sys.executable,str(HERE/'extract-final-review.py')],
]
for i,cmd in enumerate(commands,1):
 print(f'D30 FINAL v3 {i}/{len(commands)} '+Path(cmd[1]).name+' '+(cmd[2] if len(cmd)>2 else ''),flush=True);subprocess.run(cmd,cwd=ROOT,check=True)
 if Path(cmd[1]).name=='video_pipeline.py' and cmd[2]=='pair':print(json.dumps({'notification':'new-encoded-master-ready-for-root-asr','asrOutputDir':plan['outputDir'],'encoded':plan['outputDir']+'/'+plan['outputStem']+'-captioned.mp4','sha256':sha(edit/(plan['outputStem']+'-captioned.mp4'))},ensure_ascii=False),flush=True)
p=PROJECT/'project.json';m=json.loads(p.read_text('utf-8'));m['paths']['videoBurnedCaptions']=plan['outputDir']+'/'+plan['outputStem']+'-captioned.mp4';m['paths']['videoClean']=plan['outputDir']+'/'+plan['outputStem']+'-clean.mp4';m['paths']['captionsKo']=plan['outputDir']+'/captions.ko.srt';m['paths']['captionsEn']=plan['outputDir']+'/captions.en.srt';m['membershipOutro']['appliedToFinal']=True;m['status']='final-audio-asr-pending';m['finalRender']={'status':'encoded-final-audio-asr-pending','knownIssues':[],'openItems':['전체 영상의 실제 시청·청취와 최종 사용자 검수는 대기 중입니다.']};p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf-8')
subprocess.run(['node',str(ROOT/'scripts/collect-video-output.cjs'),PROJECT.name],cwd=ROOT,check=True)
print(json.dumps({'slug':PROJECT.name,'stage':'final-encoded-audio-asr-and-changed-pixel-review-pending','asrOutputDir':plan['outputDir'],'captioned':m['paths']['videoBurnedCaptions'],'sha256':sha(ROOT/m['paths']['videoBurnedCaptions'])},ensure_ascii=False),flush=True)
