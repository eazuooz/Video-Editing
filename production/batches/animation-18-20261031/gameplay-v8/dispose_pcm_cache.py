"""Dispose only this revision's reproducible working PCM after verified AAC creation."""
from common import *
import shutil

def main():
 records=[]
 for ep in SCOPE:
  receipt=OUTPUT/ep/'delivery.json';folder=WORK/ep;p=folder/'final-mix.wav'
  if not receipt.is_file() or not p.is_file():continue
  assert p.resolve().is_relative_to(WORK.resolve()) and p.parent==folder and p.name=='final-mix.wav'
  d=read(receipt);m=read(folder/'audio.json');aac=read(folder/'aac.json');audio=folder/'final-audio.m4a'
  assert d['fourOutputs'] and all(Path(f['path']).is_file() for f in d['files'])
  assert aac['pcmSha256']==m['audioSha256'] and sha(audio)==aac['aacSha256'] and sha(p)==m['audioSha256']
  assert m['originalPcmUnchangedOutsideReplacements']
  source=Path('C:/Users/1/Videos/YamyamProduction/animation-native-clips-v6')/ep/'assembly/final-mix.wav'
  assert source.is_file() and not source.resolve().is_relative_to(WORK.resolve())
  r=dict(episode=ep,path=str(p),sha256=m['audioSha256'],bytes=p.stat().st_size,
   verifiedAac=str(audio),aacSha256=aac['aacSha256'],originalApprovedPcm=str(source),
   reason='Disposable derived working mix only. Final AAC/MP4, original approved PCM, voice chunks, music sources and actual-mix ASR snippets remain. Rebuild only if new voice editing is authorized.')
  records.append(r)
  m['workingPcmCache']=dict(status='disposed-after-verified-aac',path=str(p),historicalSha256=m['audioSha256'],aacRetained=str(audio),reproducibleFrom='Original M6 PCM + retained individual replacement/guidance chunks + source music; exact unchanged ranges already verified.')
  save(folder/'audio.json',m);p.unlink()
 p=HERE/'pcm-cache-cleanup.json';old=read(p) if p.exists() else dict(records=[])
 old['records']+=records;old.update(totalFreedBytes=sum(r['bytes'] for r in old['records']),scope='Only gameplay-v8 derived final-mix.wav caches; no original media or delivered masters deleted.',updatedAt=stamp());save(p,old)
 print('Freed',round(sum(r['bytes'] for r in records)/1024**3,2),'GiB from',len(records),'derived caches; free',round(shutil.disk_usage(WORK).free/1024**3,2),'GiB',flush=True)
if __name__=='__main__':main()
