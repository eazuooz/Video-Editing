"""Finalize the verified title-only local bundle; retain all existing versions."""
from pathlib import Path
import av,copy,hashlib,json,shutil
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
SLUG='shorts-mario64-lakitu-camera';R=M/SLUG/'title-revision-v83';F=R/'film-v83';OUT=R/'local-review-v2'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def packets(p):
 with av.open(str(p))as c:return [bytes(x)for x in c.demux(c.streams.audio[0])if x.size]
def main():
 old=read(M/SLUG/'final-review-v1/bundle.json');baseline=read(H/'local-final-review-manifest-v2.json');row=copy.deepcopy(baseline['projects'][1]);artifacts={}
 original=Path(old['artifacts']['captioned']['path'])
 for mode,key in [('pilot','captioned'),('clean','clean')]:
  proof=read(F/(mode+'-proof.json'));qa=read(F/(mode+'-encoded-qa.json'));assert qa['allAutomaticChecksPassed'];video=Path(proof['video']['path']);assert packets(video)==packets(original);artifacts[key]=pin(video)
 for lang,title in [('ko','3D 게임 카메라를 바꾼 게임, 마리오64 #게임개발'),('en','Mario 64 Changed the Way We Control 3D Game Cameras #GameDev')]:
  key='metadataKo'if lang=='ko'else'metadataEn';source=Path(old['artifacts'][key]['path']);text=source.read_text('utf8');text=title+'\n'+text.split('\n',1)[1];dest=OUT/('metadata-'+lang+'.txt');assert not dest.exists();dest.write_text(text,'utf8');artifacts[key]=pin(dest)
  key='subtitlesKo'if lang=='ko'else'subtitlesEn';source=Path(old['artifacts'][key]['path']);dest=OUT/('captions.'+lang+'.srt');assert not dest.exists();shutil.copyfile(source,dest);assert pin(dest)['sha256']==pin(source)['sha256'];artifacts[key]=pin(dest)
 bundle=OUT/'bundle-v2.json';save(bundle,dict(slug=SLUG,version='mario-title-v83',titleKo='3D 게임 카메라를 바꾼 게임, 마리오64 #게임개발',originalBundle=pin(M/SLUG/'final-review-v1/bundle.json'),request=pin(H/'selected-clarity-request-v83.json'),artifacts=artifacts,durationSeconds=65.2,unchangedSpeechAndAacPackets=True,unchangedSubtitles=True,technicalChecksPassed=True,actualFullListening=False,actualRealtimePlayback=False,humanApproval=False,localFinalBundleComplete=True,platformActions=[]))
 save(ROOT/'projects'/SLUG/'publishing/metadata-title-v83.json',dict(titleKo='3D 게임 카메라를 바꾼 게임, 마리오64 #게임개발',titleEn='Mario 64 Changed the Way We Control 3D Game Cameras #GameDev',titleCorrection=read(H/'selected-clarity-request-v83.json')['titleCorrection'],bundle=pin(bundle),uploaded=False,humanApproval=False))
 print(json.dumps(dict(bundle=pin(bundle),duration=65.2,artifacts=6,titleOnly=True)))
if __name__=='__main__':main()
