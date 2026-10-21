import os
"""Speech-led mix with retained continuous voice and synchronized game excerpts."""
from pathlib import Path
import json,sys,subprocess,hashlib,re,importlib.util
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/('production/'+os.environ.get('YAMYAM_D2_LOCAL','local'))
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard():
 c=rd(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
def ff(args,label,quiet=False):
 cmd=['ffmpeg','-hide_banner','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*map(str,args)]
 p=subprocess.run(cmd,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf8',errors='replace');(L/(label+'.log')).write_text(p.stdout,encoding='utf8');assert p.returncode==0,(label,p.stdout[-1200:]);return p.stdout
def measure(src,label,target=-16):
 cache=L/(label+'.json')
 if cache.exists() and rd(cache).get('sha256')==sha(src):return rd(cache)['measurement']
 report=ff(['-i',src,'-af',f'loudnorm=I={target}:TP=-2:LRA=11:print_format=json','-f','null','-'],label)
 q=json.loads(re.findall(r'\{\s*"input_i"[\s\S]*?\}',report)[-1]);wr(cache,{'sha256':sha(src),'measurement':q});return q
def db(x):return 20*np.log10(max(float(np.sqrt(np.mean(np.square(x,dtype=np.float64)))),1e-10))
def main():
 guard();plan=rd(L/'edit-plan.json');t=rd(L/'timing.json');total=plan['totalFrames']*800;body=plan['bodyFrames']*800
 source=L/'narration-source.wav';normal=L/'narration-normalized-v2.wav';m=measure(source,'narration-source-loudness')
 # Constant gain preserves all original sentence-to-sentence dynamics. Peak
 # headroom is reserved before the game/music sum, never duck the voice.
 gain=-16-float(m['input_i'])
 if not normal.exists():ff(['-n','-i',source,'-af',f'volume={gain}dB,aresample=48000,alimiter=limit=0.75:attack=2:release=50:level=0:latency=1','-ac','2','-c:a','pcm_f32le',normal],'normalize-continuous-voice-v2')
 a,sr=sf.read(normal,dtype='float32',always_2d=True);assert sr==48000 and np.isfinite(a).all()
 voice=np.zeros((total,2),dtype=np.float32);voice[96000:96000+len(a)]=a
 placed=L/'narration-placed.wav'
 if placed.exists():
  old,rate=sf.read(placed,dtype='float32',always_2d=True);assert rate==48000 and np.array_equal(old,voice);del old
 else:sf.write(placed,voice,48000,subtype='FLOAT')
 game=np.zeros_like(voice);game_rows=[];gains={}
 for c in plan['cuts']:
  if c['kind']!='actual' or c['audio']!='synchronized-game-mix':continue
  src=R/c['source'];key=c['sourceId']
  if key not in gains:
   q=measure(src,'source-game-'+key,-23);gains[key]=max(-20,min(12,-23-float(q['input_i'])))
  dest=L/'cuts'/(c['id']+'-game.wav');samples=c['frames']*800
  if not dest.exists():ff(['-n','-ss',c['sourceStartFrame']/60,'-i',src,'-vn','-af',f"volume={gains[key]}dB,aresample=48000,apad=whole_len={samples},atrim=end_sample={samples}",'-ac','2','-c:a','pcm_f32le',dest],'game-'+c['id'])
  x,rate=sf.read(dest,dtype='float32',always_2d=True);assert rate==48000 and len(x)==samples
  correction=plan.get('audioCorrections',{}).get(c['id'],{}).get('gainDb',0)
  if correction:x*=10**(correction/20)
  n=min(4800,len(x)//2);x[:n]*=np.linspace(0,1,n,dtype=np.float32)[:,None];x[-n:]*=np.linspace(1,0,n,dtype=np.float32)[:,None]
  at=(c['startFrame']+120)*800;game[at:at+samples]=x
  game_rows.append({'cut':c['id'],'source':c['source'],'sourceStartFrame':c['sourceStartFrame'],'targetStartFrame':c['startFrame']+120,'frames':c['frames'],'initialTargetLufs':-23,'constantSourceGainDb':gains[key],'additionalNarrationCorrectionDb':correction,'speed':1,'gameAndOriginalInseparableMusic':'critical synchronized excerpt, not isolated SFX or independently licensed soundtrack','fadeSeconds':.1})
 gamefile=L/'game-placed-v3.wav'
 if gamefile.exists():
  old,rate=sf.read(gamefile,dtype='float32',always_2d=True);assert rate==48000 and np.array_equal(old,game);del old
 else:sf.write(gamefile,game,48000,subtype='FLOAT')
 del game
 music=R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3';assert sha(music)=='06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08'
 musicnorm=L/'music-normalized.wav';mm=measure(music,'music-source-loudness',-31);mg=-31-float(mm['input_i'])
 if not musicnorm.exists():ff(['-n','-i',music,'-af',f'volume={mg}dB,aresample=48000','-ac','2','-c:a','pcm_f32le',musicnorm],'normalize-music')
 bgm,rate=sf.read(musicnorm,dtype='float32',always_2d=True);assert rate==48000;track=np.zeros_like(voice);xf=48000;step=len(bgm)-xf;ramp=np.linspace(0,1,xf,dtype=np.float32)[:,None]
 member_source=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit/membership.mp4'
 member_probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(member_source)]))
 member_has_audio=any(s['codec_type']=='audio' for s in member_probe['streams'])
 music_end=96000+body if member_has_audio else total
 for at in range(96000,music_end,step):
  count=min(len(bgm),music_end-at);part=bgm[:count].copy()
  if at>96000:part[:min(xf,count)]*=ramp[:min(xf,count)]
  if at+len(bgm)<music_end:part[-xf:]*=1-ramp
  track[at:at+count]+=part
 track[96000:96000+24000]*=np.linspace(0,1,24000,dtype=np.float32)[:,None];track[music_end-24000:music_end]*=np.linspace(1,0,24000,dtype=np.float32)[:,None]
 musicfile=L/'music-placed.wav'
 if musicfile.exists():
  old,rate=sf.read(musicfile,dtype='float32',always_2d=True);assert rate==48000 and np.array_equal(old,track);del old
 else:sf.write(musicfile,track,48000,subtype='FLOAT')
 del track,bgm
 # Preserve the approved branding/outro audio if present, without overwriting speech.
 brand=np.zeros_like(voice);base=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit'
 for key,at,n in [('branding',0,96000),('membership',96000+body,480000)]:
  src=base/(key+'.mp4');q=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(src)]))
  if not any(s['codec_type']=='audio' for s in q['streams']):continue
  dest=L/(key+'-audio.wav')
  if not dest.exists():ff(['-n','-i',src,'-vn','-af',f'aresample=48000,apad=whole_len={n},atrim=end_sample={n}','-ac','2','-c:a','pcm_f32le',dest],key+'-audio')
  x,rate=sf.read(dest,dtype='float32',always_2d=True);brand[at:at+n]=x
 brandfile=L/'brand-placed.wav';sf.write(brandfile,brand,48000,subtype='FLOAT');del brand
 graph='[0:a]asplit=3[v][scg][scm];[1:a][scg]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[g];[2:a][scm]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400:makeup=1[m];[v][g][m][3:a]amix=inputs=4:normalize=0:duration=first[p]'
 pre=L/'premix.wav'
 if not pre.exists():ff(['-n','-i',placed,'-i',gamefile,'-i',musicfile,'-i',brandfile,'-filter_complex',graph,'-map','[p]','-c:a','pcm_f32le',pre],'speech-driven-background-mix')
 pm=measure(pre,'premix-loudness');program_gain=min(0,-1.8-float(pm['input_tp']))
 final=L/'final-mix.wav'
 if not final.exists():ff(['-n','-i',pre,'-af',f'volume={program_gain}dB','-c:a','pcm_f32le',final],'constant-program-headroom')
 finalvoice=L/'narration-final-stem.wav'
 if not finalvoice.exists():ff(['-n','-i',placed,'-af',f'volume={program_gain}dB','-c:a','pcm_f32le',finalvoice],'final-voice-stem')
 mix,rate=sf.read(final,dtype='float32',always_2d=True);assert rate==48000 and len(mix)==total
 v,rate=sf.read(finalvoice,dtype='float32',always_2d=True);assert np.max(np.abs(v-voice*10**(program_gain/20)))<2e-6
 # Speech-active local measurements, not just whole-file LUFS.
 q=rd(L/'whole-source-asr.json');mask=np.zeros(total,dtype=bool)
 for w in q['words']:
  lo,hi=w['timestamp']
  if lo is not None and hi is not None:mask[round((lo+2)*48000):round((hi+2)*48000)]=True
 rows=[];flags=[]
 for p in t['paragraphs']:
  lo=round((p['start']+2)*48000);hi=round((p['end']+2)*48000);active=mask[lo:hi];vp=v[lo:hi][active];mp=mix[lo:hi][active]
  voice_db=db(vp);mixed_db=db(mp);background_db=db(mp-vp);snr=voice_db-background_db
  row={'paragraph':p['index'],'scene':p['scene'],'start':p['start']+2,'end':p['end']+2,'speechActiveVoiceDbfs':voice_db,'speechActiveMixDbfs':mixed_db,'speechActiveBackgroundDbfs':background_db,'voiceOverBackgroundDb':snr,'encodedCheck':'pending'};rows.append(row)
  if mixed_db<voice_db-1.5 or snr<7:flags.append(row)
 for x,y in zip(rows,rows[1:]):
  if y['speechActiveVoiceDbfs']<x['speechActiveVoiceDbfs']-6:flags.append({'kind':'paragraph-level-drop','previous':x['paragraph'],'current':y['paragraph'],'dropDb':y['speechActiveVoiceDbfs']-x['speechActiveVoiceDbfs']})
 report={'sourceSha256':sha(source),'normalizedSha256':sha(normal),'placedSha256':sha(placed),'finalMixSha256':sha(final),'narrationFinalStemSha256':sha(finalvoice),'originalPcmRetained':True,'sourceToNormalized':'single constant gain plus48k resampling; no local fade/duck/time stretch','narrationGainDb':gain,'programGainDb':program_gain,'voiceDucked':False,'games':game_rows,'music':{'title':'Nimbus','artist':'Eveningland','sourceSha256':sha(music),'targetLufs':-31,'license':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md'},'speechActiveParagraphs':rows,'flags':flags,'humanWholeListening':'pending','encodedContinuity':'pending'}
 wr(P/'production/audio-review.json',report);wr(L/'mix-build.json',report)
 print(json.dumps({'seconds':total/48000,'programGainDb':program_gain,'paragraphs':len(rows),'flags':len(flags),'voiceGainDb':gain}),flush=True)
if __name__=='__main__':main()
