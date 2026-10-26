"""Apply the isolated R-setting picture correction, retaining the original master/audio evidence."""
from pathlib import Path
import sys,json,hashlib,subprocess
import soundfile as sf
HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1];ROOT=HERE.parents[3]
plan=HERE/'edit-plan.json';data=json.loads(plan.read_text('utf-8'));edit=PROJECT/'production/local/batch-v1/edit';qa=edit/'qa/visual-v2';qa.mkdir(exist_ok=True)
for command in [
 [sys.executable,str(HERE/'video_pipeline.py'),'cuts','--plan',str(plan),'--only-cut','05-02'],
 [sys.executable,str(HERE/'video_pipeline.py'),'pair','--plan',str(plan)],
 [sys.executable,str(HERE/'video_pipeline.py'),'verify','--plan',str(plan)],
]:
 print('VISUAL PATCH: '+Path(command[1]).name+' '+command[2],flush=True);subprocess.run(command,cwd=ROOT,check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((edit/'qa/final-v1/inputs/structural-verification.json').read_text('utf-8'));new=json.loads((edit/'structural-verification.json').read_text('utf-8'))
old_master=edit/'kind-to-beginners-batch-v1-captioned.mp4';new_master=edit/(data['outputStem']+'-captioned.mp4')
assert sha(old_master)==old['outputs']['captioned']['sha256']
assert old['outputs']['captioned']['audioPacketsSha256']==new['outputs']['captioned']['audioPacketsSha256']
old_wav=edit/'encoded-audio-for-asr.wav';new_wav=qa/'encoded-audio-for-asr.wav'
if not new_wav.exists():subprocess.run(['ffmpeg','-n','-v','error','-threads','2','-i',str(new_master),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(new_wav)],check=True)
a,ar=sf.read(old_wav,dtype='int16');b,br=sf.read(new_wav,dtype='int16');assert ar==br==16000 and a.shape==b.shape and (a==b).all()
proof={'kind':'visual-only-revision-identical-audio','baseMaster':str(old_master.relative_to(ROOT)).replace('\\','/'),'baseMasterSha256':sha(old_master),'currentMaster':str(new_master.relative_to(ROOT)).replace('\\','/'),'currentMasterSha256':sha(new_master),'audioPacketsSha256':new['outputs']['captioned']['audioPacketsSha256'],'decodedMono16000PcmSha256':hashlib.sha256(b.tobytes()).hexdigest(),'oldAsrWavSha256':sha(old_wav),'currentEquivalentAsrWavSha256':sha(new_wav),'samples':len(b),'pcmExactEqual':True,'newAsrRuns':0,'preservedBaseReview':'qa/final-v1','changedCut':'05-02','voiceScriptsCaptionClockAndMusicChanged':False,'sourceAsrFinalAsrAndContinuityEvidenceReused':'Existing current base-master audio evidence, tied by exact AAC packets and decoded PCM. Human listening remains pending.'}
(qa/'audio-equivalence.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
mf=PROJECT/'project.json';m=json.loads(mf.read_text('utf-8'));m['paths']['videoBurnedCaptions']=str(new_master.relative_to(ROOT)).replace('\\','/');m['paths']['videoClean']=str((edit/(data['outputStem']+'-clean.mp4')).relative_to(ROOT)).replace('\\','/');m['membershipOutro']['appliedToFinal']=True;mf.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf-8')
subprocess.run(['node',str(ROOT/'scripts/collect-video-output.cjs'),PROJECT.name],cwd=ROOT,check=True)
print(json.dumps(proof,ensure_ascii=False),flush=True)
