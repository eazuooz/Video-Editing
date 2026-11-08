"""Add narrated maps while preserving every previous PCM sample and subtitle cue."""
from pathlib import Path
import json,re,sys,subprocess,hashlib,math,html,difflib,os
import numpy as np
import soundfile as sf
from PIL import ImageFont
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=H/'local'
sys.path.insert(0,str(H/'planning'))
from opening_edit import make_edit,reconstruct_pcm,retime_cues,retime_ass
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def rel(p):return p.absolute().relative_to(R.absolute()).as_posix()
def run(args,log):
 with log.open('wb') as f:subprocess.run([str(x) for x in args],stdout=f,stderr=f,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def ff(args,log):return run(['ffmpeg','-nostdin','-hide_banner','-v','error','-y',*args],log)

def baseline_pcm_proof(P,O,base):
 old=P/'production/local/pacing-v3/mix.wav';fingerprint=sha(old);receipt=O/'baseline-audio-verified.json'
 expected=base.get('identicalAAC',{}).get('clean.mp4')
 if expected is None:
  baseline=R/next(f['path'] for f in base['files'] if f['kind']=='clean.mp4')
  expected=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(baseline),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],capture_output=True,check=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW).stdout.strip()
 if receipt.exists():
  cached=read(receipt)
  if cached.get('pcmSha256')==fingerprint and cached.get('expectedAacHash')==expected:return cached
 got=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(old),'-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-f','hash','-hash','sha256','-'],capture_output=True,check=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW).stdout.strip()
 assert got==expected,(P.name,'Stored PCM does not reproduce baseline AAC',got,expected)
 evidence={'pcmSha256':fingerprint,'expectedAacHash':expected,'reencodedAacHash':got,'exactAACPacketsReproduced':True};save(receipt,evidence);return evidence

def measured_share(P,id,allFrames,repairs):
 pacing=read(P/'production/pacing-v3/edit-plan.json')
 if id=='A02':
  source=read(P/'production/fighters-v4-kula-lili/edit-plan.json');game=sum(c['frames'] for c in source['cuts'] if c['kind']=='independent-gameplay')+sum(e['frames'] for e in pacing['events'] if e['kind']=='independent-gameplay')
 else:game=pacing['measuredScreenShare']['gameFrames']
 replaced=0
 if repairs:
  source=read(P/'production/series-v1/edit-plan-final.json');mask=np.zeros(source['totalFrames'],dtype=bool)
  for c in source['cuts']:
   if c['key'] in source['sourceEvidence']:mask[c['start']:c['start']+c['frames']]=True
  pieces=[];cursor=0
  for e in pacing['events']:pieces.extend([mask[cursor:e['pictureAt']],np.full(e['frames'],e['kind']=='independent-gameplay',bool)]);cursor=e['pictureAt']
  pieces.append(mask[cursor:]);mask=np.concatenate(pieces);assert int(mask.sum())==game
  replaced=sum(int(mask[r['start']:r['end']].sum()) for r in repairs)
 return {'actualGameplayFrames':game-replaced,'explanationReplacedGameplayFrames':replaced,'bodyFrames':allFrames-720,'actualGameplayShare':(game-replaced)/(allFrames-720),'classification':'Source scene classifications, unchanged baseline plus added explanatory maps and music-only study relocation.','ratioChoice':'User-requested relationship explanations and meaningful native-speed repeats; preserve useful lesson and do not pad to a quota.'}
def sec(s):
 h,m,s=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
def stamp(t,srt=True):
 scale=1000 if srt else 100;n=round(t*scale);s,n=divmod(n,scale);h,s=divmod(s,3600);m,s=divmod(s,60)
 return f'{h:02d}:{m:02d}:{s:02d},{n:03d}' if srt else f'{h}:{m:02d}:{s:02d}.{n:02d}'
def cues(p):
 out=[]
 for b in re.split(r'\n\s*\n',p.read_text('utf-8-sig').strip()):
  x=b.splitlines();a,z=map(sec,x[1].split(' --> '));out.append({'start':a,'end':z,'text':'\n'.join(x[2:])})
 return out
def srt_write(p,rows):p.write_text('\n\n'.join(f'{i+1}\n{stamp(x["start"])} --> {stamp(x["end"])}\n{x["text"]}' for i,x in enumerate(rows))+'\n','utf-8')
def split_text(s,maxlen=28):
 out=[];row=''
 for w in s.split():
  if row and len(row+' '+w)>maxlen:out.append(row);row=w
  else:row+=((' ' if row else '')+w)
 if row:out.append(row)
 return out
def engsplit(s,n,weights):
 w=s.split();out=[];at=0;cum=np.cumsum(weights)/sum(weights)
 for i in range(n):
  end=len(w) if i==n-1 else max(at+1,min(len(w)-(n-i-1),round(len(w)*cum[i])))
  out.append(' '.join(w[at:end]));at=end
 return out
def new_cues(ep,timing,at):
 asr=read(L/'asr'/(ep['id']+'.json'));out={'ko':[],'en':[]}
 clauses=read(H/'planning/caption-clauses.json');assert clauses['sourceSha256']==sha(H/'planning/relations-plan.json')
 entries={e['id']:e['parts'] for e in clauses['entries']};norm=lambda x:''.join(c.lower() for c in x if c.isalnum())
 for s in timing['sentences']:
  parts=[x['ko'] for x in entries[s['id']]];eng=[x['en'] for x in entries[s['id']]];assert norm(''.join(parts))==norm(s['ko']) and norm(''.join(eng))==norm(s['en'])
  ws=[w for w in asr['chunks'] if None not in w['timestamp'] and w['timestamp'][1]>s['start'] and w['timestamp'][0]<s['end']]
  text='';times=[]
  for w in ws:
   word=norm(w['text']);a,b=w['timestamp'];text+=word;times.extend([(a+(b-a)*i/max(1,len(word)),a+(b-a)*(i+1)/max(1,len(word))) for i in range(len(word))])
  source=''.join(norm(x) for x in parts);mapping={}
  for a,b,n in difflib.SequenceMatcher(None,source,text,autojunk=False).get_matching_blocks():
   for k in range(n):mapping[a+k]=times[b+k]
  bounds=[s['start']]
  cursor=0
  for part in parts[:-1]:
   end=cursor+len(norm(part));found=[mapping[i] for i in range(cursor,end) if i in mapping];assert found,(ep['id'],s['id'],part,'No independently heard clause')
   bounds.append(min(s['end'],max(bounds[-1]+.08,found[-1][1])));cursor=end
  bounds.append(s['end'])
  assert all(a<b for a,b in zip(bounds,bounds[1:])),(ep['id'],s)
  for i in range(len(parts)):
   for lang,txt in [('ko',parts[i]),('en',eng[i])]:out[lang].append({'start':at+bounds[i],'end':at+bounds[i+1],'text':txt})
 return out
CPU=os.environ.get('YAMYAM_RELATIONS_CPU')=='1'
ENC=(['-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-x264-params','scenecut=0'] if CPU else ['-c:v','h264_nvenc','-preset','p4','-cq','18','-b:v','0'])+['-bf','0','-g','120','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
def main(id):
 control=read(R/'shared/publishing/video-production-control.json')['animationRelationsRevision20261108'];assert id in control['episodes'] and control['renderAuthorized']
 plan=read(H/'planning/relations-plan.json');ep=next(x for x in plan['episodes'] if x['id']==id);tm=next(x for x in read(L/'timing.json')['episodes'] if x['id']==id)
 review=read(L/'text-review.json');assert next(x for x in review if x['id']==id)['directReview']=='complete-current-text'
 base=next(x for x in read(B/'pacing-v3/review-manifest.json')['records'] if x['id']==id);P=R/'projects'/ep['slug'];O=P/'production/local/relations-v4';V=O/'rendered';V.mkdir(exist_ok=True);parts=O/'parts';parts.mkdir(exist_ok=True)
 clean=R/next(x['path'] for x in base['files'] if x['kind']=='clean.mp4');assert sha(clean)==next(x['sha256'] for x in base['files'] if x['kind']=='clean.mp4')
 baselineAudio=baseline_pcm_proof(P,O,base)
 oldFrames=round(base['durationSeconds']*60);at=float(ep['insertion']['atSeconds']);duration=tm['frames']/60
 oldcaptions={lang:cues(R/next(x['path'] for x in base['files'] if x['kind']==lang+'.srt')) for lang in ['ko','en']}
 for lang,cs in oldcaptions.items():assert not any(c['start']+.001<at<c['end']-.001 for c in cs),(id,lang,'Insertion splits a caption',at)
 prev=[c for c in oldcaptions['ko'] if c['end']<=at+.001];assert not prev or re.search(r'[.!?][”"’\']?$',prev[-1]['text']),(id,'Insertion interrupts sentence',prev[-1] if prev else None)
 # Remove only proven old music-only observation inserts; replay their native pictures after the map.
 repairs=read(L/'body-repairs.json').get(id,[]) if (L/'body-repairs.json').exists() else []
 edit=make_edit(id,oldFrames,tm['frames'],repairs,O/'relation.mp4');save(O/'opening-edl.json',edit)
 allFrames=edit['totalFrames'];at=edit['mapStartSeconds'];atFrame=edit['mapStartFrame'];seq=[]
 escape=lambda p:str(p.absolute()).replace('\\','/').replace(':','\\:').replace("'","\\'")
 for i,part in enumerate(edit['pictureEdl']):
  source=Path(part['source']);assert source.exists();dest=parts/f'part-{i:02d}.mp4';receipt=dest.with_suffix('.json')
  metadata=dict(part,sourceSha256=part.get('sourceSha256') or sha(source),encoder=ENC)
  if 'passIndex' in part:metadata['counterLayout']=id.lower()+'-right-footer-v2' if id in {'A01','A16'} else 'full-width-v1'
  cached=dest.exists() and receipt.exists() and read(receipt)==metadata
  if not cached:
   active=read(R/'shared/publishing/video-production-control.json')['animationRelationsRevision20261108'];assert active['renderAuthorized'] and id in active['episodes']
   vf='settb=1/60,setpts=N'
   if 'passIndex' in part:
    label=dest.with_suffix('.txt')
    if id in {'A01','A16'}:
     label.write_text(f"{part['passIndex']}/3 · 1×",'utf-8')
     vf+=f",drawbox=x=1620:y=839:w=240:h=83:color=0x101713:t=fill,drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':text='기본 속도':fontsize=27:fontcolor=0xF2D787:x=1663:y=844,drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':textfile='{escape(label)}':fontsize=37:fontcolor=0xF2D787:x=1658:y=878"
    else:
     label.write_text(f"기본 속도 · {part['passIndex']}/3    ─    관계도에서 본 움직임을 확인하세요",'utf-8')
     vf+=f",drawbox=x=58:y=878:w=1804:h=42:color=0x101713:t=fill,drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':textfile='{escape(label)}':fontsize=31:fontcolor=0xF2D787:x=(w-text_w)/2:y=884"
   ff(['-threads','4','-filter_threads','2','-ss',part['sourceStartFrame']/60,'-i',source,'-vf',vf,'-frames:v',part['frames'],'-an',*ENC,dest],dest.with_suffix('.log'))
   save(receipt,metadata)
  seq.append(dest)
 concat=O/'concat.txt';concat.write_text(''.join("file '"+p.as_posix().replace("'","'\\''")+"'\n" for p in seq),'utf-8')
 ff(['-f','concat','-safe','0','-i',concat,'-c:v','copy','-an','-video_track_timescale','60000',O/'picture.mp4'],O/'picture.log')
 old=P/'production/local/pacing-v3/mix.wav';mix=O/'mix.wav';proof=reconstruct_pcm(edit,old,Path(tm['audio']),mix);proof['baselineAudioReproduction']=baselineAudio
 save(O/'audio-proof.json',proof)
 ff(['-i',mix,'-c:a','aac','-b:a','192k','-ar','48000','-ac','2',O/'pair-audio.m4a'],O/'aac.log')
 addition=new_cues(ep,tm,at);finals={}
 for lang,cs in oldcaptions.items():
  shifted=retime_cues(cs,edit)
  final=sorted(shifted+addition[lang],key=lambda x:x['start']);assert all(a['end']<=b['start']+.002 for a,b in zip(final,final[1:])),(id,lang,'caption overlap')
  srt_write(V/(ep['slug']+'.'+lang+'.srt'),final);finals[lang]=final
 ass=retime_ass((P/'production/local/pacing-v3/captions.ass').read_text('utf-8-sig'),edit).splitlines()
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
 for c in addition['ko']:
  a,z=stamp(c['start'],False),stamp(c['end'],False);txt=c['text'];width=math.ceil(font.getlength(txt))+100;assert width<1780,(id,txt,width);x=960-width/2
  for layer,xx,yy,color,border in [(0,x+14,942,'323C07',0),(1,x,928,'FFFFFF',3)]:
   ass.append(f'Dialogue: {layer},{a},{z},Default,,0,0,0,,{{\\an7\\pos({xx:.0f},{yy})\\p1\\bord{border}\\shad0\\1c&H{color}&\\3c&H181B16&}}m 0 0 l {width} 0 {width} 84 0 84')
  ass.append(f'Dialogue: 2,{a},{z},Default,,0,0,0,,{{\\an5\\pos(960,970)\\bord0\\shad0\\b500}}{txt}')
 captions=O/'captions.ass';captions.write_text('\n'.join(ass)+'\n','utf-8');escape=lambda p:str(p.absolute()).replace('\\','/').replace(':','\\:').replace("'","\\'")
 cleanOut=V/(ep['slug']+'.clean.mp4');capOut=V/(ep['slug']+'.captioned.mp4')
 ff(['-i',O/'picture.mp4','-i',O/'pair-audio.m4a','-map','0:v','-map','1:a','-c','copy','-movflags','+faststart',cleanOut],O/'clean.log')
 ff(['-threads','4','-filter_threads','2','-i',O/'picture.mp4','-i',O/'pair-audio.m4a','-vf',f"ass='{escape(captions)}'",'-map','0:v','-map','1:a','-frames:v',allFrames,*ENC,'-c:a','copy','-movflags','+faststart',capOut],O/'captioned.log')
 for repair,part in zip(repairs,[p for p in edit['pictureEdl'] if p['kind']=='repair']):repair.update(finalStartFrame=part['outputStartFrame'],finalEndFrame=part['outputEndFrame'])
 save(O/'assembly.json',{'id':id,'slug':ep['slug'],'title':base['title'],'revision':'relations-v4','baseline':base['files'],'addedFrames':tm['frames'],'totalFrames':allFrames,'duration':allFrames/60,'insertion':{'audioSeconds':at,'pictureFrame':atFrame,'duration':duration,'reason':ep['insertion']['reason']},'openingEdl':rel(O/'opening-edl.json'),'bodyRepairs':repairs,'measuredScreenShare':measured_share(P,id,allFrames,repairs),'oldCueCounts':{k:len(v) for k,v in oldcaptions.items()},'newCueCounts':{k:len(v) for k,v in finals.items()},'audioProof':proof,'addedNarrationAudio':{k:tm.get(k) for k in ['rawAudioSha256','voiceSha256','audioSha256','constantGainDb','newMixAttenuation','voiceLevelCorrection']},'renderedDirectory':rel(V),'humanReview':'pending','platformChanged':False})
 print(id,'assembled',allFrames/60,'seconds',flush=True)
if __name__=='__main__':main(sys.argv[1])
