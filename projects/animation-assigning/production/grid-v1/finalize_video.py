"""Assemble this exact completed A01 revision; never generates TTS or publishes."""
from pathlib import Path
import subprocess,sys
import audio_pipeline as ap
import video_pipeline as vp
H=Path(__file__).resolve().parent
R=H.parents[3]
L=H.parent/'local/grid-v1'
def run(name,*args):subprocess.run([sys.executable,'-X','utf8',str(H/name),*args],cwd=R,check=True)
def main():
 ap.require_authorized('video-pair')
 run('assemble_edit_plan.py')
 plan=ap.read(H/'edit-plan.json');audio=ap.read(H/'audio-plan.json');build=ap.read(L/'edit/audio-build.json')
 assert not plan['pendingBeforeRender']['nativeCaptures']
 assert not plan['pendingBeforeRender']['actualAnnotations']
 assert ap.audio_plan_contract(plan)==ap.audio_plan_contract(audio)==build['inputs']['audioPlanContract']
 assert build['inputs']['plan']==ap.artifact(H/'audio-plan.json')
 run('video_pipeline.py','cuts')
 run('video_pipeline.py','pair')
 run('video_pipeline.py','verify')
 structure=ap.read(L/'edit/structural-verification.json')
 digest=vp.stream_hash(L/'edit/final-mix.m4a','0:a:0')
 assert all(record['audioPacketsSha256']==digest for record in structure['outputs'].values())
 ap.save(H/'final-assembly-binding.json',{'status':'structural-pass-visual-listening-review-separate','plan':ap.artifact(H/'edit-plan.json'),'audioPlan':ap.artifact(H/'audio-plan.json'),'audioBuild':ap.artifact(L/'edit/audio-build.json'),'sameAudioDependencyContract':True,'identicalFinalAacPackets':True,'audioPacketsSha256':digest,'structuralVerification':ap.artifact(L/'edit/structural-verification.json'),'outputs':structure['outputs'],'humanReviewRecorded':False,'platformMutation':False})
 print('Both full masters complete and structurally verified; sampled visual/audio review still separate',flush=True)
if __name__=='__main__':main()
