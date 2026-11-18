"""FHD review copies for the connector's measured 100 MiB upload ceiling."""
from pathlib import Path
import argparse,importlib.util,json,subprocess,time
import av
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
C=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/innovation-openings-v181')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=module('phone188_render',H/'innovation-opening-render-v183.py');n=r.n;read,pin,save=n.read,n.pin,n.save
def preparation():
 rows=read(H/'innovation-opening-plan-v181.json')['rows'];chosen=[]
 for row in rows:
  out=C/row['slug'];proof=read(out/'render-proof-v183.json');source=proof['masters']['captioned'];assert pin(source['path'])==source
  if Path(source['path']).stat().st_size>104857600:chosen.append(dict(order=row['order'],slug=row['slug'],master=source,masterProof=pin(out/'render-proof-v183.json'),frames=proof['expectedTotalVideoFrames']))
 assert [x['order']for x in chosen]==[4,6,8,9,12];return chosen
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-minutes',type=float,default=0);a=ap.parse_args();assert a.project=='shorts-mario64-lakitu-camera';n.authority();base=C/'phone-copies-v188';protocol='original-tech-twelve-innovation-phone-v188';owner='original-tech-twelve-innovation-phone';n.runtime.PROTOCOL=protocol;n.runtime.OWNER=owner;n.guard.qualifier.BASE=base/'resource-observations'
 if not a.execute:print(json.dumps(dict(selected=[x['order']for x in preparation()],guardReason=n.busy(),encodeStarted=False)));return
 assert a.wait_minutes==15;bootstrap=module('phone188_bootstrap',H/'bootstrap-parent-identity-v1.py').install(n,__file__,a.project,base,protocol,owner);worker=n.runtime.SingleWorker(path=base/'worker.json');owned=None;deadline=time.monotonic()+900
 try:
  worker.acquire();worker.update(project=a.project,stage='targeted-source',**bootstrap);last=''
  while True:
   rows=preparation();reason=n.busy()
   if reason is None:
    token=worker.record['token'];lease=dict(protocol=protocol,owner=owner,token=token,**n.identity(),phase='reserved',child=None)
    try:
     with n.LEASE.open('x',encoding='utf8')as f:json.dump(lease,f)
    except FileExistsError:reason='Foreign lease preserved'
    else:
     owned=token;reason=n.busy(token)
     if reason is None:break
     if read(n.LEASE).get('token')==owned:n.LEASE.unlink()
     owned=None
   if reason!=last:print(json.dumps(dict(wait=reason,encodeStarted=False)),flush=True);last=reason
   if time.monotonic()>=deadline:print(json.dumps(dict(started=False,boundedWaitExpired=True,reason=reason)));return
   time.sleep(20)
  proofs=[]
  for row in rows:
   out=C/row['slug'];target=out/'phone-captioned-v188.mp4';proof=out/'phone-encode-v188.json';assert not target.exists()and not proof.exists();lease.update(order=row['order'],phase='FHD-phone-copy');r.command(['-threads','2','-i',row['master']['path'],'-map','0:v:0','-map','0:a:0','-c:v','h264_nvenc','-preset','p6','-rc','vbr','-cq','23','-b:v','3200k','-maxrate','4000k','-bufsize','8000k','-g','120','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','15360','-movflags','+faststart',str(target)],out/'phone-encoder-v188.log',worker,lease)
   with av.open(str(target))as c:assert (c.streams.video[0].width,c.streams.video[0].height)==(1080,1920)and c.streams.video[0].frames==row['frames']
   assert target.stat().st_size<104857600;save(proof,dict(source=row,phoneCopy=pin(target),size=target.stat().st_size,width=1080,height=1920,fps=60,profile=dict(codec='h264_nvenc',preset='p6',cq=23,bps=3200000,maxBps=4000000),audioStreamCopied=True,fullMasterUnchanged=pin(row['master']['path'])==row['master'],decodeAndVisualReviewRequired=True));proofs.append(pin(proof));print(json.dumps(dict(order=row['order'],encoded=True,bytes=target.stat().st_size)),flush=True)
  save(base/'complete.json',dict(proofs=proofs,onlyReviewCopies=True,mastersUnchanged=True));print(json.dumps(dict(completed=True,count=len(proofs))))
 finally:
  if owned and n.LEASE.exists()and read(n.LEASE).get('token')==owned:n.LEASE.unlink()
  if worker.handle is not None:worker.close()
if __name__=='__main__':main()
