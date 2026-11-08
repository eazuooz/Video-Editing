"""Encode four local final-review outputs from one approved17 episode assembly."""
from pathlib import Path
import argparse,hashlib,json,subprocess,shutil,sys,os
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';OUT=Path('C:/Users/1/Videos/YamyamCoding/animation-contrast-v5-review')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,log):
 with Path(log).open('wb')as f:subprocess.run(['ffmpeg','-nostdin','-hide_banner','-y',*map(str,args)],stdout=f,stderr=f,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],creationflags=subprocess.CREATE_NO_WINDOW))
def audio_payload(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--episode',required=True);ap.add_argument('--assembly',required=True);ap.add_argument('--mix');a=ap.parse_args()
 control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert a.episode in control['episodes']and a.episode!='A03'and control['fullLocalProductionAuthorized']
 edl=read(a.assembly);assert edl['id']==a.episode
 base=next(x for x in read(H/'baseline-review-manifest.json')['records']if x['id']==a.episode)
 source=L/'explanation-assembly'/a.episode/'captionless';receipt=read(source/'receipt.json');assert receipt['wholeVideoRendered']and receipt['frames']==edl['frames']
 captions=L/'final-audio'/a.episode/'captions';review=read(captions/'review.json');assert not review['fallbackPassages'],'Resolve changed clause ASR alignment before final encode'
 folder=OUT/a.episode;folder.mkdir(parents=True,exist_ok=True);work=L/'final-encode'/a.episode;work.mkdir(parents=True,exist_ok=True)
 if a.mix:mix=Path(a.mix)
 else:
  # Matching, inspected native source sound only; the helper passes through
  # the inherited voice+BGM when no eligible source window is present.
  result=subprocess.check_output([sys.executable,'-X','utf8',str(H/'mix_verified_game_audio.py'),'--episode',a.episode,'--assembly',str(a.assembly)],cwd=R,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
  mix=Path(result.strip());assert mix.is_file()
 voice_proof={'source':str(mix),'sha256':sha(mix)}
 picture=source/'picture.mp4';v=next(x for x in probe(picture)['streams']if x['codec_type']=='video');assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',edl['frames'])
 slug=base['slug'];aac=work/'audio.m4a';clean=folder/(slug+'.clean.mp4');captioned=folder/(slug+'.captioned.mp4')
 signature={'pictureSha256':sha(picture),'mixSha256':sha(mix),'assSha256':sha(captions/'captions.provisional.ko.ass'),'frames':edl['frames'],'encoder':'libx264 veryfast crf18 4threads bt709','audio':'AAC192k48kstereo-single-shared-payload'}
 previous=read(work/'signature.json')if(work/'signature.json').exists()else{}
 if previous!=signature or not all(p.is_file()for p in [clean,captioned,aac]):
  videoKeys=['pictureSha256','assSha256','frames','encoder']
  reuseVideo=captioned.is_file()and all(previous.get(k)==signature[k]for k in videoKeys)
  oldDelivery=read(work/'delivery.json')if(work/'delivery.json').exists()else{}
  priorCaption=next((f for f in oldDelivery.get('files',[])if f['kind']=='captioned.mp4'),None)
  reuseVideo=reuseVideo and priorCaption is not None and sha(captioned)==priorCaption['sha256']
  run(['-i',mix,'-c:a','aac','-b:a','192k','-ar','48000','-ac','2',aac],work/'aac.log')
  run(['-i',picture,'-i',aac,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',clean],work/'clean.log')
  ass=str((captions/'captions.provisional.ko.ass').absolute()).replace('\\','/').replace(':','\\:').replace("'","\\'")
  if reuseVideo:
   remux=folder/(slug+'.captioned.remux.mp4');run(['-i',captioned,'-i',aac,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',remux],work/'captioned-audio-update.log');os.replace(remux,captioned)
  else:
   run(['-threads','4','-filter_threads','1','-i',picture,'-i',aac,'-map','0:v:0','-map','1:a:0','-vf',"ass='"+ass+"'",'-frames:v',edl['frames'],'-r','60','-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart',captioned],work/'captioned.log')
  save(work/'signature.json',signature)
 facts={}
 for kind,p in [('clean.mp4',clean),('captioned.mp4',captioned)]:
  pr=probe(p);v=next(x for x in pr['streams']if x['codec_type']=='video');au=next(x for x in pr['streams']if x['codec_type']=='audio')
  assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',edl['frames'])
  assert(au['codec_name'],au['sample_rate'],au['channels'])==('aac','48000',2)
  run(['-v','error','-threads','4','-i',p,'-f','null','-'],work/(kind+'.decode.log'))
  facts[kind]={'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'kind':kind,'wholeDecode':'passed'}
 assert audio_payload(clean)==audio_payload(captioned)==audio_payload(aac),'Clean/captioned AAC must be identical'
 for lang in ['ko','en']:
  p=folder/(slug+'.'+lang+'.srt');shutil.copyfile(captions/('captions.provisional.'+lang+'.srt'),p);facts[lang+'.srt']={'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'kind':lang+'.srt'}
 report={'id':a.episode,'slug':slug,'title':base['title'],'description':'주제별 게임 예시·비교 시연·동작 단계 보강. 정상 속도 관찰 뒤 자세와 차이를 분석합니다.','revision':'contrast-v5','durationSeconds':edl['frames']/60,'frames':edl['frames'],'files':list(facts.values()),'localFinalFilesReady':True,'humanReviewed':False,'humanListened':False,'platformChanged':False,'technicalQa':{'wholeDecodeBothMasters':'passed','identicalSharedAacPayload':True,'fhd60':True,'scriptSource':str(R/'projects'/slug/'production/contrast-v5'),'captionAlignment':review['status'],'audioInput':voice_proof},'remainingReview':['Integrated visual/mobile boundary review','Actual full human viewing/listening','Source publication conditions in source ledger']}
 save(folder/'delivery.json',report);save(work/'delivery.json',report);print(json.dumps({'id':a.episode,'captioned':str(captioned),'sha256':facts['captioned.mp4']['sha256']}))
if __name__=='__main__':main()
