"""Prepare native-speed observation inserts without replacing any baseline lesson."""
from pathlib import Path
import sys,json,importlib.util,re,hashlib,subprocess,ast,math
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent; B=H.parent; R=B.parents[2]
sys.path.insert(0,str(B/'local/pacing-v3/python-deps'))
import render as rr
read=rr.read;save=rr.save;sha=rr.sha
N=B/'local/real-clips-v2'
def rel(p):return p.absolute().relative_to(R.absolute()).as_posix()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=load('native_revision',B/'real-clips-v2/assemble_revision.py')
# The new pass is frame i -> frame i. Baseline slow-study renderers stay untouched.
src=(B/'real-clips-v2/assemble_revision.py').read_text('utf-8')
part=src[src.index('def series_images('):src.index('\ndef main(ep):')]
part=part.replace("if key in ('A04-anticipation','A11-kick'):","if False:")
part=part.replace("index,mode=state_index(f,s['frames'],study)","index,mode=f,'기본 속도'")
exec(part,native.__dict__)
part=src[src.index('def a03_images('):src.index('\ndef a02_images(')]
a=part.index('        if compare:fa=fb=');z=part.index('        identity=fa,fb',a)
part=part[:a]+'        fa=fb=f\n'+part[z:]
exec(part,native.__dict__)
def cues(row):
 out=[]
 for lang in ('ko','en'):
  p=R/next(x['path'] for x in row['files'] if x['kind']==lang+'.srt')
  for block in re.split(r'\n\s*\n',p.read_text('utf-8-sig').strip()):
   l=block.splitlines();a,b=map(rr.seconds,l[1].split(' --> '));out.append((a,b,' '.join(l[2:])))
 return out
def pause(at,cs):
 intervals=sorted((a,b) for a,b,t in cs);merged=[]
 for a,b in intervals:
  if merged and a<=merged[-1][1]+.00001:merged[-1][1]=max(merged[-1][1],b)
  else:merged.append([a,b])
 points=[]
 # Touching clause cues are still legal word boundaries; do not merge them
 # into one multi-sentence exclusion interval.
 for a,b,t in cs:
  for x in (a,b):
   if not any(aa+.00001<x<bb-.00001 for aa,bb,tt in cs):points.append(x)
 for (_,b),(a,_) in zip(merged,merged[1:]):
  if a>=b:points.append(max(b,min(a,at/60)))
 p=min(points,key=lambda p:abs(p-at/60))
 return round(p*60,5)
def fallback_overlay(ep,s,v,dest):
 im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
 def lab(x,y,t,size=35):
  f=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size);w=d.textlength(t,font=f)
  d.rectangle((x-16,y-10,x+w+18,y+size+15),fill='#14261f');d.text((x,y),t,font=f,fill='#f2d787',anchor='lt')
 lab(65,52,v.get('rendererLabel','언리얼 · 자체 동작 시연'),34)
 if ep=='A17' and s['key']=='curve':
  d.rectangle((42,37,690,104),fill='#14261f');lab(65,52,'자체 도해 · 관절 제어점',34)
 for i,t in enumerate(v['studyLabels'][s['key']]):lab(90+i*920,143,t,37)
 lab(65,817,s['focus'],35);im.save(dest)
def prepare(ep):
 assert ep in read(R/'shared/publishing/video-production-control.json')['animationPacingRevision20261107']['episodes']
 row=next(x for x in read(B/'real-clips-v2/review-manifest.json')['records'] if x['id']==ep)
 P=R/'projects'/row['slug'];slug=row['slug'];rev='unreal-kit-v2' if ep=='A01' else 'grid-v1' if ep=='A03' else 'series-v1'
 O=P/'production'/rev;L=P/'production/local'/rev;D=P/'production/local/pacing-v3';D.mkdir(parents=True,exist_ok=True)
 V=D/'previews';V.mkdir(exist_ok=True);plan=read(O/'edit-plan-final.json');cs=cues(row)
 base=R/next(x['path'] for x in row['files'] if x['kind']=='clean.mp4')
 events=[];skipped=[]
 def event(key,at,source,start,n,kind,focus,repeat=3,followingNative=False):
  if kind=='independent-gameplay':
   at+=n
   if ep=='A12' and key=='game-clock':n=min(n,300)
   if ep=='A12' and key=='game-cup':n=min(n,120)
   if ep=='A15' and key=='game-botw':n=min(n,330)
   if ep=='A18' and key=='game-goose':n=min(n,210)
   if ep=='A18' and key=='game-clock':n=min(n,150)
  audioAt=pause(at,cs);pictureAt=round(at)
  sentenceEnds={('A01','game-A01-E001'):12.88,('A01','game-A01-E010'):125.72,('A01','stop'):344.73,('A03','game-great'):19.06,('A03','attack-04'):154.49,('A03','attack-06'):288.30}
  if (ep,key) in sentenceEnds:
   audioAt=round(sentenceEnds[ep,key]*60,5)
   assert not any(a+.00001<audioAt/60<b-.00001 for a,b,t in cs)
  if abs(audioAt-at)>210:
   skipped.append(dict(key=key,reason='연속 문장을 자르지 않기 위해 가까운 문장 경계가 없는 반복 후보는 제외',desiredFrame=at,nearestPauseFrame=audioAt));return False
  events.append(dict(key=key,audioAt=audioAt,pictureAt=pictureAt,source=rel(source),sourceSHA256=sha(source),sourceStartFrame=start,sourceEndFrame=start+n,repeatCount=repeat,frames=n*repeat,kind=kind,reason=focus,speed=1,firstPassAlreadyInBaseline=kind=='independent-gameplay',followingNativePass=followingNative,originalCutStart=at,boundaryOffsetFrames=pictureAt-at,nearbyNarration=[t for a,b,t in cs[:len(cs)//2] if abs(a-at/60)<1.5][:2]))
  if (ep,key) in sentenceEnds:events[-1]['audioBoundaryReason']='Audited complete Korean sentence boundary; keep predicate and enumeration together, preserve aligned bilingual cues'
  return True
 def encode(dest,images,n):
  if not dest.exists():native.encoder(dest,images,dest.with_suffix('.log'))
  v=next(s for s in rr.probe(dest)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n
 if ep=='A01':
  sys.path.insert(0,str(O));mod=load('a01_preview',O/'render_picture.py');seen=set()
  for s in plan['segments']:
   if s['kind'] not in ('kit','added'):continue
   if s['kind']=='added':key=s['study'];head,foot=mod.newLabels[s['voice']]
   else:
    num=int(s['cut'].split('E')[-1]);key=mod.specific.get(num,mod.SOURCES[s['mode']]);head,foot=mod.labels[num]
   if key in seen or key=='strike':continue
   seen.add(key);dest=V/(key+'.mp4');q=dict(s,frames=120,mode='pacing-observation')
   encode(dest,(mod.sample(q,key,f,head,foot) for f in range(120)),120)
   event(key,s['start'],dest,0,120,'explanation',foot,2,s['frames']>=120)
  # Genuine gameplay retained in the baseline is repeated only at a complete shot.
  old=read(P/'production/grid-v1/edit-plan.json');game_ids={x['id'] for x in old['cuts'] if x.get('kind')=='independent-gameplay'}
  candidates=[s for s in plan['segments'] if s['kind']=='old' and s.get('cut') in game_ids and 150<=s['frames']<=600]
  for s in candidates[::max(1,len(candidates)//3)][:3]:event('game-'+s['cut'],s['start'],base,s['start'],s['frames'],'independent-gameplay','기존 게임 행동 전체 → 같은 예시 설명',2,True)
 elif ep=='A03':
  topics=native.a03_topics(O/'picture.py');seen=set()
  for s in plan['cuts']:
   ch=s['chapter']
   if s['kind']=='unity' and ch not in seen:
    seen.add(ch);pid=int(s['paragraph']);key='attack-'+ch;dest=V/(key+'.mp4');q=dict(s,frames=96)
    tt=dict(topics);title,legend,lt,rt=tt[pid]
    if not 13<=pid<=18:tt[pid]=(title,'준비 → 타격 → 후속 동작을 먼저 이어서 봅니다.','전체 공격 동작','같은 동작 · 단계 확인')
    encode(dest,native.a03_images(q,tt),96)
    event(key,s['startFrame'],dest,0,96,'explanation',legend)
  seen=set()
  for s in plan['cuts']:
   if s['kind']=='game' and s['source']=='great' and s['inPoint']<13.5:continue
   if s['kind']=='game' and s['source'] not in seen and s['frames']>=150:
    seen.add(s['source']);trim=180 if s['source']=='great' else 0
    event('game-'+s['source'],s['startFrame']+trim,base,s['startFrame']+trim,s['frames']-trim,'independent-gameplay','같은 카메라의 공격을 반복 관찰한 뒤 준비·타격·후속 설명',2,True)
 else:
  v=read(O/'visual-plan.json');seen=set()
  for s in plan['cuts']:
   key=s['key']
   if key not in v['studyLabels'] or key in seen:continue
   seen.add(key)
   if (ep,key) in (('A10','height'),('A13','letters'),('A15','count')):
    skipped.append(dict(key=key,reason='분류/문자/개수 도표는 실제 동작 반복 대상이 아니므로 기존 설명 유지'));continue
   retainedStudy=(ep,key) in (('A04','jab'),('A11','upper'))
   dest=V/(key+('-baseline-matched' if retainedStudy else '')+'.mp4');sp=N/'studies'/(ep+'-'+key+'.json')
   if sp.exists() and not retainedStudy:
    study=read(sp);full=study['frames'];q=dict(s,frames=full);encode(dest,native.series_images(ep,q,study,v),full)
    # Preserve the whole authored action, removing only its unchanged tail.
    delta=native.np.zeros(full-1)
    for anim in study.get('animations',[]):
     for track in anim['tracks'].values():
      for values in track.values():
       x=native.np.asarray(values)
       if len(x)==full:delta=native.np.maximum(delta,native.np.max(abs(native.np.diff(x,axis=0)),axis=1))
    moving=native.np.where(delta>.001)[0]
    n=min(full,max(60,int(moving[-1])+20)) if len(moving) else full
    native.frame.cache_clear()
    # These baseline comparisons already begin with a full native pass if long enough.
    originalFull=s['frames']>=n and (ep,key) not in (('A04','anticipation'),('A11','kick'))
   else:
    source=L/'picture'/(key+'-measured.mp4')
    if not source.exists():source=L/(key+'.mp4')
    n=int(next(x for x in rr.probe(source)['streams'] if x['codec_type']=='video')['nb_frames']);assert 60<=n<=360
    if not dest.exists():
     overlay=V/(key+'.png');fallback_overlay(ep,s,v,overlay)
     enc=rr.ENC if not retainedStudy else ['-c:v','libx264','-preset','veryfast','-crf','18','-bf','0','-g','120','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
     rr.run(['-threads','2','-filter_complex_threads','2','-i',source,'-i',overlay,'-filter_complex','[0:v][1:v]overlay=0:0','-an','-frames:v',n,*enc,dest],dest.with_suffix('.log'))
    originalFull=False
   event('demo-'+key,s['start'],dest,0,n,'explanation',s['focus'],2 if originalFull else 3,originalFull)
  seen=set()
  for s in plan['cuts']:
   if (ep,s['key']) in (('A10','great'),('A15','cup'),('A17','cup'),('A18','botw')):
    if s['key'] not in seen:skipped.append(dict(key=s['key'],reason='반복 관찰 후보에서 제외: 여러 컷의 몽타주 또는 목표 동작보다 배경/도구 소개가 중심. 기존 본편은 보존하고 직접적인 다른 게임 행동을 반복.'));seen.add(s['key'])
    continue
   if ep=='A08' and s['key']=='great':
    if s['key'] not in seen:skipped.append(dict(key=s['key'],reason='카메라가 연속 교차하는 컷은 보존하고 리리·스매시의 연속 동작을 반복 예시로 채택'));seen.add(s['key'])
    continue
   if s['key'] in ('wario','zss','bowser','dk'):
    if s['key'] not in seen:skipped.append(dict(key=s['key'],reason='기존 소개 몽타주는 보존하되 여러 컷을 한 동작처럼 3회 반복하지 않음'));seen.add(s['key'])
    continue
   if s['key'] in plan['sourceEvidence'] and s['key'] not in seen and 150<=s['frames']<=660:
    seen.add(s['key']);event('game-'+s['key'],s['start'],base,s['start'],s['frames'],'independent-gameplay',s['focus'],2,True)
 events.sort(key=lambda e:(e['pictureAt'],e['kind']!='independent-gameplay'))
 total=plan['totalFrames']+sum(e['frames'] for e in events)
 ass=L/'captions.ko.ass'
 if not ass.exists():ass=L/'edit/captions.ko.ass'
 assert ass.exists(),ass
 music=L/'music.wav' if ep not in ('A01','A03') else L/'music-stem.wav' if ep=='A03' else P/'production/local/grid-v1/edit/music-stem.wav'
 out=P/'production/local/pacing-v3/delivery/output'/slug
 p=dict(episode=ep,slug=slug,revision='pacing-v3',title=row['title'],fps=60,baseline=row,baselineFrames=plan['totalFrames'],totalFrames=total,events=events,audioMode='preserve-final-mix',audioStem=rel(L/'final-mix.wav'),music=rel(music),captionAss=rel(ass),outputDirectory=rel(out),skippedNonMotion=skipped,authoring='Retain all baseline picture frames and final PCM samples in order. Insert native-speed observation only at aligned bilingual speech boundaries. New time contains the same music bed; no regenerated or stretched voice.',humanViewed=False)
 game=plan.get('gameFrames',plan.get('independentGameFrames',0))+sum(e['frames'] for e in events if e['kind']=='independent-gameplay')
 p['measuredScreenShare']=dict(gameFrames=game,bodyFrames=total-720,actualShare=game/(total-720),reason='Explicit meaningful three-pass observation request; preserve all existing lesson frames, no quota padding')
 if ep in ('A01','A03'):p['reuseExistingPictureForSentenceBoundaryFix']=True
 save(P/'production/pacing-v3/edit-plan.json',p)
 print(ep,'PREPARED',len(events),'inserts',round(sum(e['frames'] for e in events)/60,1),'seconds added',flush=True)
 return p
if __name__=='__main__':prepare(sys.argv[1])
