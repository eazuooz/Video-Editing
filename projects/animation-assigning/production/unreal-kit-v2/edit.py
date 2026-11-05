"""Splice four local narration passages into A01; retain the original game cuts and audio elsewhere."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib,sys,math,shutil
import numpy as np,soundfile as sf
from PIL import ImageFont
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/unreal-kit-v2';B=P/'production/local/grid-v1';E=B/'edit'
read=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
def save(f,data):f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(f):return f.relative_to(R).as_posix()
def sha(f):
 with f.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def ff(args,log):
 with (L/(log+'.log')).open('wb') as f:
  rc=subprocess.call(['ffmpeg','-v','error','-nostdin','-y',*map(str,args)],stdout=f,stderr=f)
 if rc:raise RuntimeError((L/(log+'.log')).read_text('utf-8',errors='replace')[-1800:])
def build():
 sys.path.insert(0,str(R/'projects/animation-breaking-down-attack-animations/production/grid-v1'))
 import caption_pipeline as cp
 old=read(P/'production/grid-v1/edit-plan.json');orig=read(E/'captions.json')['cues']
 groups=[[(a.strip(),b.strip()) for a,b in (line.split(' | ') for line in block.splitlines())] for block in (H/'commentary-pairs.txt').read_text('utf-8').strip().split('\n\n')]
 origFrameCount=old['totalFrames'];segments=[];changes=[]
 changes=[(2877,2877,'01','walk'),(round(137.20*60),9791,'02','pose'),(round(325.62*60),round(325.62*60),'03','stop'),(round(373.74*60),round(373.74*60),'04','turn')]
 cuts=old['cuts'];oldCursor=0;newCursor=0;cueRows=[]
 def preserve(a,b):
  nonlocal newCursor
  points=sorted({a,b}|{c['startFrame'] for c in cuts if a<c['startFrame']<b}|{c['endFrame'] for c in cuts if a<c['endFrame']<b})
  for start,end in zip(points,points[1:]):
   cut=next((v for v in cuts if v['startFrame']<=start<v['endFrame']),None)
   native=bool(cut and 'Unity' in cut.get('renderer',''))
   segments.append({'kind':'kit' if native else 'old','mode':cut.get('explanationMode') if native else None,'oldStart':start,'oldEnd':end,'start':newCursor,'frames':end-start,'cut':cut['id'] if cut else 'brand-member','chapter':cut['scene'] if cut else None});newCursor+=end-start
 def attach_kept(a,b,newStart):
  for row in orig:
   if row['start']>=a/60-.012 and row['start']<b/60-.012:
    assert row['end']<=b/60+.05,(row['paragraph'],row['end'],b/60)
    x=dict(row);x['start']=round(newStart/60+max(0,row['start']-a/60),2);x['end']=round(newStart/60+min(b/60,row['end'])-a/60,2);cueRows.append(x)
 for a,b,sid,study in changes:
  dest=newCursor;preserve(oldCursor,a);attach_kept(oldCursor,a,dest)
  q=read(L/'voice/asr'/f'{sid}.json');wav=L/'voice/chunks'/f'{sid}-scene.wav';assert q['audio_sha256']==sha(wav)
  dur=sf.info(wav).duration;count=math.ceil((.12+dur+.18)*60)
  pairs=groups[int(sid)-1];text=' '.join(k for k,e in pairs);words=[];last=0.
  for w in q['words']:
   m,n=w['timestamp'];m=max(last,m or 0);n=min(dur,n if n is not None else dur)
   if n>m+.0001:words.append({'text':w['text'],'timestamp':[m,n]});last=n
  aliases={'얼리얼':'언리얼','early':'언리얼'};begin,ends,qa=cp.align_characters(text,words,dur,aliases,.93);ix=0
  for ko,en in pairs:
   length=len(cp.normalized(ko,aliases));s=.12+newCursor/60+begin[ix];e=.12+newCursor/60+ends[ix+length-1];ix+=length
   cueRows.append({'start':round(s,2),'end':round(e,2),'ko':ko,'en':en,'paragraph':'kit-'+sid,'emphasis':{'ko':None,'en':None}})
  segments.append({'kind':'added','voice':sid,'study':study,'start':newCursor,'frames':count,'oldStart':a,'oldEnd':b,'sourceCoverage':qa['matchingCharacterCoverage']})
  newCursor+=count;oldCursor=b
 dest=newCursor;preserve(oldCursor,origFrameCount);attach_kept(oldCursor,origFrameCount,dest)
 plan={'totalFrames':newCursor,'bodyFrames':newCursor-720,'originalTotalFrames':origFrameCount,'changes':changes,'segments':segments,'addedVoiceCueCount':sum(c['paragraph'].startswith('kit-') for c in cueRows),'originalSRTCount':len(orig)}
 fontPath=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')
 if not fontPath.exists():fontPath=Path('C:/Windows/Fonts/malgun.ttf')
 font=cp.measured_font(fontPath,500);bold=cp.measured_font(fontPath if 'Noto' in fontPath.name else Path('C:/Windows/Fonts/malgunbd.ttf'),700)
 for i,c in enumerate(cueRows):
  c['cue']=i+1;assert c['end']>c['start'] and (not i or c['start']>=cueRows[i-1]['end']-.001),(i,c)
  if c['paragraph'].startswith('kit-'):
   for language in ('ko','en'):
    parts=cp.wrap(c[language],font);assert parts;c[language]='\n'.join(parts)
 for lang in ('ko','en'):
  (L/f'captions.{lang}.srt').write_text(''.join(f"{c['cue']}\n{cp.srt_stamp(c['start'])} --> {cp.srt_stamp(c['end'])}\n{c[lang]}\n\n" for c in cueRows),encoding='utf-8')
  events=[cp.ass_events(c,cp.geometry(c[lang],font,bold,c['emphasis'][lang]),lang) for c in cueRows]
  (L/f'captions.{lang}.ass').write_text(cp.ass_header('Noto Sans KR' if 'Noto' in fontPath.name else 'Malgun Gothic')+''.join(events),encoding='utf-8')
 save(L/'captions.json',{'cues':cueRows});save(L/'timeline.json',plan);print('Frames',newCursor,'cues',len(cueRows),flush=True)
def audio():
 plan=read(L/'timeline.json');source,sr=sf.read(E/'final-mix.wav',dtype='float32');music,r=sf.read(E/'music-stem.wav',dtype='float32')
 assert sr==r==48000
 dest=np.empty((plan['totalFrames']*800,2),np.float32);gains=[]
 for cut in plan['segments']:
  start=cut['start']*800;size=cut['frames']*800;old=cut['oldStart']*800
  if cut['kind']!='added':
   dest[start:start+size]=source[old:old+size];continue
  sid=cut['voice'];a,rate=sf.read(L/'voice/chunks'/f'{sid}-scene.wav',dtype='float32');assert rate==24000
  stem=L/f'added-{sid}.wav'
  ff(['-i',L/'voice/chunks'/f'{sid}-scene.wav','-af','acompressor=threshold=0.2:ratio=4:attack=2:release=80:makeup=1,pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-2.5:LRA=9','-ar','48000','-c:a','pcm_s24le',stem],'normalize-'+sid)
  vo,vr=sf.read(stem,dtype='float32');voice=np.zeros((size,2),np.float32);offset=round(.12*sr);limit=min(len(vo),size-offset);voice[offset:offset+limit]=vo[:limit]
  # Retain the old BGM phase at both splice boundaries. Crossfade the actual
  # music bed through the middle of the addition without touching retained PCM.
  stop=cut['oldEnd']*800; left=music[old:old+size].copy();right=music[stop-size:stop].copy()
  assert len(left)==len(right)==size
  ramp=np.clip((np.arange(size)/size-.35)/.30,0,1)[:,None];bed=(left*(1-ramp)+right*ramp)*.6
  mixed=voice+bed;gains.append({'id':sid,'peak':float(np.max(np.abs(mixed)))})
  # The splice occurs inside an actual voice pause on either side.
  blend=round(.03*sr);tail=np.linspace(1.,0.,blend)[:,None]
  mixed[:blend]=source[old:old+blend]*tail+mixed[:blend]*(1-tail)
  mixed[-blend:]=mixed[-blend:]*tail+source[stop-blend:stop]*(1-tail)
  dest[start:start+size]=mixed
 sf.write(L/'final-mix.wav',dest,sr,subtype='PCM_24')
 ff(['-i',L/'final-mix.wav','-ar','48000','-ac','2','-c:a','aac','-b:a','192k',L/'audio.m4a'],'encode-audio')
 save(L/'audio-receipt.json',{'retainedPcm':sha(E/'final-mix.wav'),'addedVoices':gains,'aacSha256':sha(L/'audio.m4a')})
if __name__=='__main__':build();audio()
