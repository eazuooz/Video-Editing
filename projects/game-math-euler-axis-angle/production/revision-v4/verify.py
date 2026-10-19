"""Reuse visual evidence; measure only new mixed audio and new output integrity."""
from pathlib import Path
import importlib.util,sys,json,hashlib
H=Path(__file__).parent;P=H.parent.parent
spec=importlib.util.spec_from_file_location('v3verify',P/'production/revision-v3/verify-output.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.O=P/'production/local/revision-v4-clarity';m.Q=m.O/'qa';m.Q.mkdir(exist_ok=True)
assert m.read(m.R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
t=m.read(P/'production/revision-v3/timeline.json')
stage=sys.argv[1] if len(sys.argv)>1 else 'all'
def integrity():
 results=[];pair=m.read(m.O/'pair-source.json');reuse=m.read(H/'video-reuse-proof.json')
 assert pair['inputs']['timelineSha256']==m.sha(P/'production/revision-v3/timeline.json')
 for kind in ['clean','captioned']:
  f=m.O/f'euler-{kind}.mp4';digest=m.sha(f);receipt=m.Q/(kind+'-integrity.json');assert digest==pair['outputs'][kind]['sha256']
  if receipt.exists() and m.read(receipt).get('sha256')==digest:results.append(m.read(receipt));continue
  prior=P/f'production/local/revision-v3/euler-{kind}.mp4';previous=m.read(P/f'production/local/revision-v3/qa/{kind}-integrity.json')
  proof=next(r for r in reuse['streams'] if r['kind']==kind)
  assert previous['sha256']==m.sha(prior)==proof['previousSha256'] and proof['currentSha256']==digest and proof['exactCompressedVideoStreamEqual']
  assert previous['fullDecodePassed'] and previous['ptsMonotonicAndUniform'] and previous['frames']==t['totalFrames']
  packet_args=['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts,duration,size,flags','-of','compact']
  old_packets=m.run([*packet_args,str(prior)]);new_packets=m.run([*packet_args,str(f)]);assert old_packets==new_packets
  info=json.loads(m.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
  assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',t['totalFrames'])
  assert int(a['sample_rate'])==48000 and int(a['channels'])==2 and abs(float(info['format']['duration'])-t['totalFrames']/60)<.1
  m.run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'])
  adts=m.run(['ffmpeg','-v','error','-i',str(f),'-map','0:a','-c:a','copy','-f','adts','-'])
  r=dict(kind=kind,sha256=digest,bytes=f.stat().st_size,frames=t['totalFrames'],width=1920,height=1080,fps=60,fullDecodePassed=True,ptsMonotonicAndUniform=True,ptsEvidence='Every compressed video packet and its PTS/DTS/duration is identical to the authenticated prior full93100-frame timing pass. Current whole output decoded successfully.',packetTimingSha256=hashlib.sha256(new_packets).hexdigest(),aacSha256=hashlib.sha256(adts).hexdigest(),sampleRate=a['sample_rate'],channels=2,duration=float(info['format']['duration']))
  m.save(receipt,r);results.append(r)
 assert results[0]['aacSha256']==results[1]['aacSha256'] and t['actualFrames']*3==t['explanationFrames']*2
 m.save(m.Q/'integrity.json',dict(outputs=results,bodyFrames=t['bodyFrames'],actualFrames=t['actualFrames'],explanationFrames=t['explanationFrames'],ratioErrorFrames=0,sourceIntervalsUnique=t['sourceIntervalsUnique'],sourceSpeed=t['sourceSpeed'],noGameplayFreezeOrLoop=True,humanWholeListening='pending'))
if stage in ['integrity','all']:integrity()
if stage in ['audio','all']:m.audio(t)
print('Current v4 output checks:',stage,'; visual/caption evidence reused only through exact video-stream equality.')
