from pathlib import Path
import shutil,json,hashlib,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3];OLD=H.parent/'grid-v1';L=H.parent/'local/fighters-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 records=[]
 for name in ('audio_pipeline.py','video_pipeline.py','caption_pipeline.py','storage_paths.py'):
  src=OLD/name;dst=H/name;text=src.read_text(encoding='utf-8')
  if name=='storage_paths.py':text=text.replace('local/grid-v1','local/fighters-v2')
  if not dst.exists():dst.write_text(text,encoding='utf-8')
  records.append({'source':src.relative_to(R).as_posix(),'sha256':sha(src),'target':dst.relative_to(R).as_posix(),'targetSha256':sha(dst)})
 save(H/'helper-provenance.json',{'helpers':records,'originalHelpersUnchanged':True,'nativeAndStillReceiptsReuseOriginalGridV1':True})
 save(H/'execution-grant.json',{'episode':'A02','revision':'fighters-v2','stages':['recognize','video-cuts','video-pair','video-verify','mix','captions'],'platformMutation':False})
 source=Path('C:/Users/1/Downloads/ElevenLabs_2026-11-04T13_29_07_얌얌코딩 - 내 목소리 샘플_ivc_s50_sim75_v4.mp3')
 voice=L/'voice/additional-sample-b.mp3';voice.parent.mkdir(parents=True,exist_ok=True)
 if not voice.exists():shutil.copy2(source,voice)
 assert sha(voice)==sha(source)
 save(H/'voice-generation-record.json',{'provider':'ElevenLabs','voiceId':'jIRSnF8OWAsWEChVwCuK','model':'Eleven v4','sample':'B','settings':{'stability':0.5,'similarity':0.75,'speed':1,'effects':[]},'uiReadback':True,'creditsBefore':80206,'creditsAfter':79568,'creditsConsumed':638,'source':{'path':voice.relative_to(R).as_posix(),'sha256':sha(voice)},'scriptSha256':sha(H/'additional-narration.ko.txt'),'oldAudioPreserved':True,'humanListening':False})
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(voice),'-ar','48000','-ac','1','-c:a','pcm_s24le',str(voice.with_suffix('.wav'))],check=True)
 print('Isolated revision helpers and additional voice prepared.')
if __name__=='__main__':main()
