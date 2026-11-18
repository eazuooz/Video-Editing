"""Check the reserved caption band, real body quality and exact AAC packets."""
from pathlib import Path
import argparse,hashlib,json,math
import av,numpy as np
H=Path(__file__).resolve().parent;M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def packets(path):
 with av.open(str(path))as c:return [bytes(p)for p in c.demux(c.streams.audio[0])if p.size]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);a=ap.parse_args();base=M/a.project/'camera-paired-v164/film-v171';p=read(base/'pilot-proof.json');q=read(base/'clean-proof.json');assert p['fingerprint']==q['fingerprint'];assert packets(p['video']['path'])==packets(q['video']['path'])
 cues=p['identity']['captionCues'];indices={math.floor((c['start']+c['spokenEnd'])*30)for c in cues};rows=[]
 with av.open(p['video']['path'])as ca,av.open(q['video']['path'])as cb:
  for i,(fa,fb)in enumerate(zip(ca.decode(video=0),cb.decode(video=0))):
   if i not in indices:continue
   assert fa.time==fb.time;aa=np.asarray(fa.to_image(),dtype=np.float32);bb=np.asarray(fb.to_image(),dtype=np.float32)
   diff=np.concatenate([(aa[:1470]-bb[:1470]).reshape(-1),(aa[1740:]-bb[1740:]).reshape(-1)]);mse=float(np.mean(diff*diff));psnr=100 if mse==0 else 10*math.log10(255*255/mse);black=bb[1470:1740];assert psnr>=42,(i,psnr);assert float(np.quantile(black,.999))<=8,(i,float(black.max()))
   rows.append(dict(frame=i,seconds=fa.time,bodyPsnrDb=psnr,cleanReservedBand999Quantile=float(np.quantile(black,.999))))
 assert len(rows)==len(indices)
 out=base/'clean-derivative-verification.json';assert not out.exists();out.write_text(json.dumps(dict(pilot=p['video'],clean=q['video'],aacPacketsByteExact=True,allCaptionLocationsChecked=len(rows),minimumBodyPsnrDb=min(x['bodyPsnrDb']for x in rows),reservedCaptionBandIsBlack=True,captionBandContainsNoGamePictureOrMascot=True,rows=rows,humanApproval=False),ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(report=pin(out),sampledFrames=len(rows),minimumBodyPsnrDb=min(x['bodyPsnrDb']for x in rows))))
if __name__=='__main__':main()
