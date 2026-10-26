"""D29 native game-audio restoration; reuse exact current video packets."""
from pathlib import Path
import json,sys,subprocess,hashlib
HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1];ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import video_pipeline as v
plan_file=HERE/'edit-plan.json';plan=json.loads(plan_file.read_text('utf-8'));edit=PROJECT/'production/local/batch-v1/edit';audio=PROJECT/'production/local/batch-v1/audio-v3';audio.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base={kind:edit/f'kind-to-beginners-batch-v1-r-focus-v2-{kind}.mp4' for kind in ['clean','captioned']}
base_hash={k:sha(p) for k,p in base.items()}
assert sha(ROOT/plan['audio']['sourceReviewPath'])==plan['audio']['sourceReviewSha256'],'Audio source decision record changed after freeze'
subprocess.run([sys.executable,str(HERE/'audio_pipeline.py'),'mix','--plan',str(plan_file),'--output-dir',str(audio)],cwd=ROOT,check=True)
proof={'kind':'audio-restoration-with-exact-video-copy','planSha256':sha(plan_file),'newTtsRuns':0,'baseMasters':[],'outputs':[],'earlierAllMuteDecision':'superseded','sourceChoices':'projects/kind-to-beginners/planning/audio-source-review.json','wholeHumanListening':'pending'}
for kind,src in base.items():
 assert sha(src)==base_hash[kind]
 dst=edit/(plan['outputStem']+'-'+kind+'.mp4')
 if dst.exists():raise RuntimeError('Preserve existing v3 master; do not overwrite '+str(dst))
 tmp=dst.with_suffix('.partial.mp4')
 subprocess.run(['ffmpeg','-n','-v','error','-threads','2','-i',str(src),'-i',str(audio/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(tmp)],check=True)
 assert v.stream_hash(src,'0:v:0')==v.stream_hash(tmp,'0:v:0')
 assert v.stream_hash(audio/'final-mix.m4a','0:a:0')==v.stream_hash(tmp,'0:a:0')
 tmp.replace(dst)
 proof['baseMasters'].append({'kind':kind,'path':v.routed_relative(src),'sha256':base_hash[kind]})
 proof['outputs'].append({'kind':kind,'path':v.routed_relative(dst),'sha256':sha(dst),'videoPacketsExactEqualToBase':True,'audioPacketsSha256':v.stream_hash(dst,'0:a:0')})
print(json.dumps({'notification':'new-encoded-master-ready-for-root-asr','asrOutputDir':v.routed_relative(audio),'encoded':v.routed_relative(edit/(plan['outputStem']+'-captioned.mp4')),'sha256':sha(edit/(plan['outputStem']+'-captioned.mp4'))},ensure_ascii=False),flush=True)
subprocess.run([sys.executable,str(HERE/'video_pipeline.py'),'verify','--plan',str(plan_file)],cwd=ROOT,check=True)
current=edit/(plan['outputStem']+'-captioned.mp4')
subprocess.run([sys.executable,str(HERE/'review_audio.py'),'--plan',str(plan_file),'--encoded',str(current),'--edit-dir',str(audio),'--output-dir',str(audio/'qa')],cwd=ROOT,check=True)
(audio/'video-copy-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
p=PROJECT/'project.json';m=json.loads(p.read_text('utf-8'));m['paths']['videoBurnedCaptions']=v.routed_relative(current);m['paths']['videoClean']=v.routed_relative(edit/(plan['outputStem']+'-clean.mp4'));m['membershipOutro']['appliedToFinal']=True;m['status']='final-audio-asr-pending';m['finalRender']={'status':'encoded-final-audio-asr-pending','knownIssues':[],'openItems':['전체 영상의 실제 시청·청취와 최종 사용자 검수는 대기 중입니다.']};p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf-8')
subprocess.run(['node',str(ROOT/'scripts/collect-video-output.cjs'),PROJECT.name],cwd=ROOT,check=True)
print(json.dumps({'slug':PROJECT.name,'stage':'new-game-audio-final-encoded-asr-pending','asrOutputDir':v.routed_relative(audio),'captioned':v.routed_relative(current),'sha256':sha(current),'audioPacketsSha256':v.stream_hash(current,'0:a:0')},ensure_ascii=False),flush=True)
