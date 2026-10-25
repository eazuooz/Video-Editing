"""Insert narrated real-game abstract; preserve every frame/sample of old body order.

The one selected visual replacement is QG06. Prior delivery is never overwritten.
"""
from pathlib import Path
import json,sys,importlib.util,subprocess,math,re,hashlib
import numpy as np,soundfile as sf
from PIL import ImageFont
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'qwen3-tts'));from align_project_subtitles import align_characters,normalized
spec=importlib.util.spec_from_file_location('base',B.parent/'render-patches.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Keep stable workspace links when local media directories are junctions to C:.
m.rel=lambda p: Path(p).absolute().relative_to(R).as_posix()
slug='game-math-polygon-partition-v2';P=R/'projects'/slug;H=P/'production/gameplay-abstract-v5';O=P/'production/local/gameplay-abstract-v5';A=O/'intro-audio';D=R/'output'/f'{slug}-gameplay-abstract-v5';D.mkdir(parents=True,exist_ok=True)
def auth():
 a=m.read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['m14-gameplay-abstract-v5'];assert a['status']=='active' and a['renderAuthorized'] and not a['uploadAuthorized']
auth();old=R/'output'/f'{slug}-gameplay-motion-v4';base=old/f'{slug}.clean.mp4'
oldrec=m.read(P/'production/gameplay-motion-v4/outputs.json');assert m.sha(base)==oldrec['outputs'][0]['sha256']
T=m.read(A/'abstract.timing.json');speech=m.read(B/'intro.ko.json')['scenes'];introFrames=math.ceil((T['duration_seconds']+.18)*60);dur=introFrames/60;totalFrames=40231+introFrames
sources=m.read(B.parent/'motion-v4/m14-plan.json')['sources']
beats=[];endA=T['entries'][1]['start'];endB=T['entries'][2]['start']
for i,(s,start,end,key,srcin) in enumerate(zip(speech,[0,endA,endB],[endA,endB,dur],['dorf','tiny','dorf'],[21,35.6,21+endA])):
 # Audio-derived starts rounded to output frame boundaries, maximum8.34ms.
 a=round(start*60)/60;b=round(end*60)/60
 beats.append(dict(id=s['id'],start=a,end=b,seconds=b-a,source=sources[key]['path'],sourceIn=srcin,sourceKey=key,speech=s['lines'][0]))
chunks={
 'A':[('타일을 이어 붙이면','Joining tiles changes'),('땅의 모양이 바뀝니다.','the shape of the land.'),('이렇게 만든 땅을 삼각형으로 나눌 때,','When we split this land into triangles,'),('무엇을 지켜야 할까요?','what must we preserve?')],
 'B':[('호수를 그린 자리도,','The area drawn as a lake'),('땅으로 채우면 안 되겠죠.','must not be filled with land.')],
 'C':[('오늘은 조각의 개수만 세는 데서','Today we will go beyond'),('한 걸음 더 나아가겠습니다.','simply counting the pieces.'),('원래 땅은 빠짐없이 덮고,','We will cover all the original land'),('빈 공간은 그대로 남기는','while keeping the empty space intact,'),('분할을 찾아보겠습니다.','and find a partition that does both.')]
}
cues=[]
for s,entry in zip(speech,T['entries']):
 wav=A/'chunks'/f'{s["id"]}-scene.wav';samples,sr=sf.read(wav);asr=m.read(A/'asr'/f'{s["id"]}.json');assert m.sha(wav)==asr['audio_sha256']
 a,b,cov=align_characters(s['lines'][0],asr['words'],len(samples)/sr);cursor=0
 assert normalized(' '.join(k for k,e in chunks[s['id']]))==normalized(s['lines'][0])
 for ko,en in chunks[s['id']]:
  n=len(normalized(ko));begin=2+entry['start']+float(a[cursor]);end=2+entry['start']+float(b[cursor+n-1]);cursor+=n
  cues.append(dict(start=begin,end=end,ko=ko,en=en,scene=s['id']))
def srtstamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def parse_time(t):
 h,mi,s=t.replace(',','.').split(':');return int(h)*3600+int(mi)*60+float(s)
def old_srt(path):
 out=[]
 for block in path.read_text('utf-8-sig').strip().split('\n\n'):
  lines=block.splitlines();a,b=lines[1].split(' --> ');out.append(dict(start=parse_time(a),end=parse_time(b),text='\n'.join(lines[2:])))
 return out
for lang in ['ko','en']:
 body=old_srt(old/f'{slug}.{lang}.srt');assert all(r['start']>=2 for r in body)
 allc=[dict(start=c['start'],end=c['end'],text=c[lang]) for c in cues]+[dict(start=c['start']+dur,end=c['end']+dur,text=c['text']) for c in body]
 (D/f'{slug}.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{srtstamp(c["start"])} --> {srtstamp(c["end"])}\n{c["text"]}' for i,c in enumerate(allc))+'\n',encoding='utf8')
# Preserve old caption text/style/geometry; change only its absolute time.
oldass=(P/'production/local/concept-fit-v2/captions.ko.ass').read_text('utf8');head=oldass.split('Dialogue:')[0];bodyrows=[]
for line in oldass.splitlines():
 if line.startswith('Dialogue:'):
  v=line.split(',',3);v[1]=m.stamp(parse_time(v[1])+dur);v[2]=m.stamp(parse_time(v[2])+dur);bodyrows.append(','.join(v))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);introRows=[]
for c in cues:
 w=font.getlength(c['ko'])+72;assert w<1740
 x=(1920-w)/2;y=928;endY=1012
 for layer,dx,dy,color in [(10,14,14,'323C07'),(11,0,0,'FFFFFF')]:
  drawing=f'm {x+dx:.2f} {y+dy} l {x+w+dx:.2f} {y+dy} {x+w+dx:.2f} {endY+dy} {x+dx:.2f} {endY+dy}'
  style='{\\an7\\pos(0,0)'+('\\bord0' if layer==10 else '')+'\\1c&H'+color+'&\\p1}'
  introRows.append(f'Dialogue: {layer},{m.stamp(c["start"])},{m.stamp(c["end"])},Box,,0,0,0,,{style}{drawing}')
 introRows.append(f'Dialogue: 12,{m.stamp(c["start"])},{m.stamp(c["end"])},Text,,0,0,0,,{{\\an5\\pos(960,970)}}'+c['ko'])
(O/'final.ass').write_text(head+'\n'.join(introRows+bodyrows)+'\n',encoding='utf8')
# Render independent native intervals, with tracked meaning marks added below.
for beat in beats:
 file=O/f'abstract-{beat["id"]}.mp4';beat['render']=m.rel(file)
 m.ff(['-ss',beat['sourceIn'],'-i',R/beat['source'],'-vf','scale=1920:1080:flags=lanczos,setsar=1,fps=60,setpts=N/(60*TB)','-frames:v',round(beat['seconds']*60),'-an',*m.ENC,file],O/f'abstract-{beat["id"]}.log',O)
listing=O/'abstract-parts.txt';listing.write_text('\n'.join("file '"+(R/b['render']).as_posix()+"'" for b in beats)+'\n',encoding='utf8')
m.ff(['-f','concat','-safe','0','-i',listing,'-c','copy',O/'abstract-native.mp4'],O/'abstract-concat.log',O)
rows=[]
def event(a,b,s,layer=2):rows.append(f'Dialogue: {layer},{m.stamp(a)},{m.stamp(b)},Default,,0,0,0,,{s}')
def text(a,b,x,y,s,fs=46,c='EFF5F5'):event(a,b,'{\\pos('+f'{x},{y}'+')\\fs'+str(fs)+'\\1c&H'+c+'&}'+s)
def line(a,b,pts,color='A2D380',reveal=.6):
 for i in range(1,len(pts)):
  draw='m '+f'{pts[i-1][0]} {pts[i-1][1]} l {pts[i][0]} {pts[i][1]}'
  event(a+reveal*(i-1)/(len(pts)-1),b,'{\\an7\\pos(0,0)\\p1\\bord5\\shad0\\1a&HFF&\\3c&H'+color+'&}'+draw,1)
event(0,dur,'{\\an7\\pos(0,0)\\p1\\bord0\\1c&H120D09&\\1a&H15&}m 0 0 l 1920 0 1920 145 0 145',0)
text(0,dur,48,25,'나누어도, 원래 모양은 그대로',56,'73D7FF')
for beat in beats:text(beat['start'],beat['end'],48,92,('Dorfromantik' if beat['sourceKey']=='dorf' else 'Tiny Glade')+' · 실제 게임',30,'BCC0A7')
# Only show the ground outline while the inspected camera is stable.
line(1.0,min(3.4,endA),[(524,481),(550,551),(680,557),(770,507),(907,520),(951,580),(1088,587),(1153,527)])
text(1,min(3.4,endA),1200,440,'타일이 만든 땅',42,'EFF5F5')
line(1,min(3.4,endA),[(1200,495),(1160,495),(1095,548)])
text(endA+.25,endB,1270,620,'빈 공간',48,'EFF5F5')
line(endA+.35,endB,[(1340,695),(1460,760),(1460,860),(1440,825),(1460,860),(1480,825)],'EFC176')
# Return to the next, non-repeated Dorfromantik interval; hide traces during orbit.
a=endB+max(0,32.2-beats[2]['sourceIn']);b=min(dur,endB+max(0,35.4-beats[2]['sourceIn']))
if b>a:
 line(a,b,[(493,483),(639,483),(696,543),(824,543),(888,481),(1012,480),(1073,423),(1186,424),(1261,474),(1382,470)],reveal=1)
 text(a,b,1120,700,'경계 안은 빠짐없이',46,'EFF5F5')
 line(a+.4,b,[(1120,683),(1060,600),(1000,480)])
(O/'abstract-guides.ass').write_text(m.HEADER+'\n'.join(rows)+'\n',encoding='utf8')
m.ff(['-i',O/'abstract-native.mp4','-vf','ass=abstract-guides.ass','-frames:v',introFrames,'-an',*m.ENC,O/'abstract-clean.mp4'],O/'abstract-guides.log',O)
# Preserve decoded old mix samples exactly around the inserted intro.
def decode(file,dest,extra=[]):m.ff([*extra,'-i',file,'-vn','-ar',48000,'-ac',2,'-c:a','pcm_f32le',dest],Path(str(dest)+'.log'),O)
decode(base,O/'old-mix.wav')
decode(A/'abstract.wav',O/'intro-voice-48k.wav')
def loudness(file):
 p=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(file),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf8',check=True);return json.JSONDecoder().raw_decode(p.stderr[p.stderr.rfind('{'):])[0]
voice,sr=sf.read(O/'intro-voice-48k.wav',dtype='float32',always_2d=True);ref=R/m.read(P/'production/gameplay-motion-v4/audio-mix.json')['path']
oldMix=m.read(P/'production/gameplay-motion-v4/audio-mix.json');assert m.sha(ref)==oldMix['sha256'];reflevel=oldMix['levels'];vl=loudness(O/'intro-voice-48k.wav');gain=float(reflevel['input_i'])-float(vl['input_i'])
voice*=10**(gain/20);count=round(dur*48000);voice=np.pad(voice,((0,max(0,count-len(voice))),(0,0)))[:count];games=np.zeros_like(voice);tracks=[]
for entry in T['entries']:
 # Only added intro sentence tails: suppress residual hard edge without
 # time-stretching, repeating speech or changing any old narration sample.
 end=round(entry['end']*48000);voice[end-1920:end]*=np.linspace(1,0,1920,dtype=np.float32)[:,None]
for beat in beats:
 # These official trailer files contain a mixed soundtrack, not isolated
 # gameplay effects with a verified reuse basis. Keep the lecture abstract
 # narration-only; retain every sample of the previously approved body mix.
 tracks.append(dict(id=beat['id'],source=beat['source'],sourceStart=beat['sourceIn'],sourceAudioUsed=False,reason='Mixed trailer soundtrack; isolated gameplay-effects/music clearance not established. No BGM in the lecture.'))
sf.write(O/'intro-voice-matched.wav',voice,48000,subtype='FLOAT');sf.write(O/'intro-game.wav',games,48000,subtype='FLOAT')
m.ff(['-i',O/'intro-voice-matched.wav','-i',O/'intro-game.wav','-filter_complex','[0:a]asplit=2[n][key];[1:a][key]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[g];[n][g]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:attack=5:release=80:level=false:latency=true[out]','-map','[out]','-c:a','pcm_f32le',O/'intro-mix.wav'],O/'intro-mix.log',O)
body,sr=sf.read(O/'old-mix.wav',dtype='float32',always_2d=True);new,sr=sf.read(O/'intro-mix.wav',dtype='float32',always_2d=True);new=new[:count];assert len(new)==count
new[:1440]*=np.linspace(0,1,1440,dtype=np.float32)[:,None];new[-1440:]*=np.linspace(1,0,1440,dtype=np.float32)[:,None]
originalCount=40231*800;body=body[:originalCount];assert len(body)==originalCount
final=np.concatenate([body[:96000],new,body[96000:]]);sf.write(O/'final-mix.wav',final,48000,subtype='FLOAT')
assert np.array_equal(final[:96000],body[:96000]) and np.array_equal(final[96000+count:],body[96000:])
m.save(H/'audio-preservation.json',dict(oldMaster=m.rel(base),oldMasterSha256=m.sha(base),originalNarrationSha256=m.sha(P/'production/local/concept-fit-v2/audio/narration-matched.wav'),bodySamplesUnchangedBeforeEncoding=True,oldDecodedMixSha256=m.sha(O/'old-mix.wav'),introSeconds=dur,introVoiceGainDb=gain,oldMixLufs=reflevel['input_i'],introRawLufs=vl['input_i'],gameTracks=tracks,addedBgm=False,actualListening=False))
patch=m.read(H/'patch.json');start=patch['oldStart'];auth()
graph=f'[1:v]setpts=PTS-STARTPTS+{start}/TB[p];[0:v][p]overlay=eof_action=pass:repeatlast=0:enable=between(t\\,{start}\\,{start+13})[v];[v]split=2[before][after];[before]trim=end_frame=120,setpts=PTS-STARTPTS[brand];[after]trim=start_frame=120,setpts=PTS-STARTPTS[body];[brand][2:v][body]concat=n=3:v=1:a=0,fps=60,split=2[clean][c];[c]ass=final.ass[captioned]'
args=['-i',base,'-i',R/patch['path'],'-i',O/'abstract-clean.mp4','-i',O/'final-mix.wav','-filter_complex_threads',2,'-filter_complex',graph]
for label in ['clean','captioned']:args+=['-map',f'[{label}]','-map','3:a','-frames:v',totalFrames,*m.ENC,'-c:a','aac','-b:a','192k','-movflags','+faststart',D/f'{slug}.{label}.mp4']
m.save(H/'plan.json',dict(episode='M14',revision='gameplay-abstract-v5',oldSeconds=40231/60,introFrames=introFrames,introSeconds=dur,totalFrames=totalFrames,seconds=totalFrames/60,abstractThesis='Preserve the original covered region and the empty space when partitioning.',beats=beats,introCues=cues,patch=patch,bodySource=m.rel(base),bodySourceSha256=m.sha(base),bodyTextPreserved=True,bodyOrderPreserved=True,introTailBreathSeconds=dur-T['duration_seconds'],breathReason='Natural sentence-to-body breath; gameplay continues at native speed.',other17OutputsUnchanged=True,humanReview='pending',uploadAuthorized=False))
if '--prepare-only' in sys.argv:
 print('Intro, captions, final PCM and plan prepared; full encoding skipped.',flush=True)
 sys.exit(0)
m.ff(args,O/'encode.log',O)
outputs=[dict(path=m.rel(f),bytes=f.stat().st_size,sha256=m.sha(f)) for f in [D/f'{slug}.clean.mp4',D/f'{slug}.captioned.mp4',D/f'{slug}.ko.srt',D/f'{slug}.en.srt']]
m.save(H/'outputs.json',dict(status='encoded-qa-pending',outputs=outputs,frames=totalFrames,seconds=totalFrames/60,humanReview='pending',actualWholeListening=False))
print(json.dumps(dict(outputs=outputs,seconds=totalFrames/60),ensure_ascii=False),flush=True)
