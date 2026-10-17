from pathlib import Path
import json,subprocess,hashlib,argparse,shutil
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit'
def run(args,name):
 with (O/(name+'.log')).open('w',encoding='utf8') as f:r=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError((O/(name+'.log')).read_text(encoding='utf8',errors='replace')[-3000:])
def frames(p):
 d=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,width,height,r_frame_rate','-of','json',str(p)]))['streams'][0]
 assert (d['width'],d['height'],d['r_frame_rate'])==(1920,1080,'60/1'),(p,d)
 return int(d['nb_frames'])
enc=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['slices','pair','remux']);args=ap.parse_args();plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'))
 if args.stage=='slices':
  mc=R/'shared/output/motion-canvas/game-sequels-production-v2.mp4';assert frames(mc)==plan['mcFrames'];digest=hashlib.sha256(mc.read_bytes()).hexdigest()
  for c in plan['cuts']:
   if c['kind']!='explanation':continue
   source=R/c['renderedOverride'] if c.get('renderedOverride') else mc;start=0 if c.get('renderedOverride') else c['mcStartFrame'];sourceDigest=hashlib.sha256(source.read_bytes()).hexdigest() if c.get('renderedOverride') else digest
   out=O/(c['id']+'.mp4');receipt=O/(c['id']+'-diagram.json');signature={'sourceSha256':sourceDigest,'start':start,'frames':c['frames']}
   hold=c.get('holdAfterFrames')
   if hold:signature['holdAfterFrames']=hold
   if not(out.exists() and receipt.exists() and json.loads(receipt.read_text())==signature):
    vf='fps=60,setsar=1'
    if hold:vf+=f',trim=end_frame={hold},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop={c["frames"]-hold}'
    run(['-ss',str(start/60),'-i',str(source),'-an','-frames:v',str(c['frames']),'-vf',vf,*enc,str(out)],c['id']+'-slice');receipt.write_text(json.dumps(signature)+'\n')
   assert frames(out)==c['frames']
  for name,count in [('branding',120),('membership',600)]:
   src=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit'/(name+'.mp4');assert frames(src)==count;shutil.copy2(src,O/(name+'.mp4'))
  files=[O/'branding.mp4',*[O/(c['id']+'.mp4') for c in plan['cuts']],O/'membership.mp4']
  for c in plan['cuts']:assert frames(O/(c['id']+'.mp4'))==c['frames']
  (O/'concat.txt').write_text('\n'.join("file '"+p.as_posix()+"'" for p in files)+'\n',encoding='utf8')
  print('All cut counts match; exact branding/member clips preserved')
 else:
  mix=O/'final-mix.wav';aac=O/'final-mix.m4a';sig=hashlib.sha256(mix.read_bytes()).hexdigest();receipt=O/'aac-source.json'
  if not(aac.exists() and receipt.exists() and json.loads(receipt.read_text()).get('sha256')==sig):
   if args.stage=='remux' and aac.exists():shutil.copy2(aac,O/'rejected-adaptive-voice-mix.m4a')
   run(['-i',str(mix),'-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(aac)],'audio-encode');receipt.write_text(json.dumps({'sha256':sig,'bitrate':192000})+'\n')
  if args.stage=='remux':
   proof=[]
   def vh(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
   for suffix in ['clean','captioned']:
    source=O/f'making-game-sequels-v2-{suffix}.mp4';before=vh(source);out=O/f'voice-fixed-{suffix}.mp4'
    run(['-i',str(source),'-i',str(aac),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(plan['totalFrames']/60),'-movflags','+faststart',str(out)],'remux-'+suffix)
    assert frames(out)==plan['totalFrames'];after=vh(out);assert before==after;out.replace(source);proof.append({'output':source.name,'videoPacketsBefore':before,'videoPacketsAfter':after,'videoReencoded':False})
   (O/'voice-remux-video-preservation.json').write_text(json.dumps(proof,indent=2)+'\n');print('Repaired audio; identical encoded picture streams retained');raise SystemExit(0)
  ass=(O/'captions.ko.ass').relative_to(R).as_posix();graph=f'[0:v]fps=60,setsar=1,split=2[clean][capin];[capin]ass={ass}[captioned]'
  args=['-f','concat','-safe','0','-i',str(O/'concat.txt'),'-i',str(aac),'-filter_complex',graph]
  for branch,suffix in [('clean','clean'),('captioned','captioned')]:args+=['-map',f'[{branch}]','-map','1:a','-frames:v',str(plan['totalFrames']),'-t',str(plan['totalFrames']/60),*enc,'-c:a','copy','-movflags','+faststart',str(O/f'making-game-sequels-v2-{suffix}.mp4')]
  run(args,'pair-encode')
  for suffix in ['clean','captioned']:assert frames(O/f'making-game-sequels-v2-{suffix}.mp4')==plan['totalFrames']
  print('Both1080p60 masters encoded with identical approved AAC stream')
