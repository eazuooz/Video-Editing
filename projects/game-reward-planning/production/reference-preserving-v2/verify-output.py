from pathlib import Path
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[4];O=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit';plan=json.loads((R/'projects/game-reward-planning/production/reference-preserving-v2/edit-plan.json').read_text(encoding='utf8'));results=[]
for name in ['clean','captioned']:
 path=O/f'game-reward-planning-v2-{name}.mp4';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',plan['totalFrames'])
 log=O/(name+'-decode.log')
 with log.open('wb') as f:p=subprocess.run(['ffmpeg','-hide_banner','-v','error','-xerror','-i',str(path),'-f','null','-'],stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0,log
 stamps=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(path)],text=True);times=[]
 for l in stamps.splitlines():
  try:times.append(float(l.split(',')[0]))
  except ValueError:pass
 assert len(times)==plan['totalFrames'];assert max(abs(b-a-1/60) for a,b in zip(times,times[1:]))<.000002
 audiohash=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a','-f','hash','-hash','sha256','-'],text=True).strip()
 results.append({'kind':name,'path':str(path.relative_to(R)).replace('\\','/'),'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'bytes':path.stat().st_size,'frames':len(times),'width':1920,'height':1080,'fps':60,'duration':float(probe['format']['duration']),'audioDuration':float(a['duration']),'fullVideoAudioDecode':'passed','uniformPts':'passed','decodedAudioSha256':audiohash})
 print(name,'decode, frame count, PTS and audio integrity passed',flush=True)
assert results[0]['decodedAudioSha256']==results[1]['decodedAudioSha256']
(O/'integrity.json').write_text(json.dumps({'outputs':results,'decodedAudioIdentical':True,'visualAndHumanReviewSeparate':True},indent=2)+'\n');print('Both outputs contain identical decoded audio.')
