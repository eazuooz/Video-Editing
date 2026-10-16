"""Replace only reviewed complete sentences; retain all other source samples."""
from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';N=R/'shared/output/narration/game-reward-planning/reference-preserving-v2';sys.path.insert(0,str(R/'qwen3-tts'))
from align_project_subtitles import align_characters,normalized
from build_translated_srt import split_caption,wrapped_lines,timestamp
from align_project_subtitles import partition_fixed
spec=[{'id':'bomberman','scene':'02','line':13,'slot':[48.35,53.11],'start':48.48,'ko':'한편, 봄버맨에서는 얻은 힘을 잃을 수 있다는 점도 긴장감을 줍니다.','tts':'한편, 봄버맨에서는 얻은 힘을 잃을 수 있다는 점도 긴장감을 줍니다.','en':'In Bomberman, the possibility of losing the power you have earned also creates tension.'},
{'id':'unlock','scene':'04','line':2,'slot':[4.0,10.44],'start':5.0,'ko':'해금(Unlock)은 잠긴 항목을 여는 것입니다. 조건을 달성하면 새로 사용할 수 있습니다.','tts':'해금은 잠긴 항목을 여는 것입니다. 조건을 달성하면 새로 사용할 수 있습니다.','en':'Unlocking opens a previously locked item. Once the condition is met, it becomes available to use.'},
{'id':'frequent','scene':'04','line':8,'slot':[33.24,37.9],'start':33.42,'ko':'사쿠라이는 도전자가 비교적 자주 나타나도록 구성했다고 설명합니다.','tts':'사쿠라이는 도전자가 비교적 자주 나타나도록 구성했다고 설명합니다.','en':'Sakurai says challengers were designed to appear relatively often.'}]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
backup=N/'scripts-before-pronunciation-patches';backup.mkdir(exist_ok=True)
scriptFiles={'ko':P/'script/reference-preserving-v2/narration.ko.json','en':P/'script/reference-preserving-v2/narration.en.json','tts':P/'script/reference-preserving-v2/narration.tts.ko.json'}
for k,p in scriptFiles.items():
 if not (backup/(k+'.json')).exists():shutil.copy2(p,backup/(k+'.json'))
original={k:load(backup/(k+'.json')) for k in scriptFiles};current={k:load(backup/(k+'.json')) for k in scriptFiles}
patched={};report=[];out=N/'leveled-patched';out.mkdir(exist_ok=True)
for s in spec:
 source=N/'patches/chunks'/f"{s['id']}-scene.wav";a,sr=sf.read(source,dtype='float32');asr=load(N/'patches/asr'/f"{s['id']}.json");assert asr['audio_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
 assert s['start']+len(a)/sr<=s['slot'][1],s
 if s['scene'] not in patched:patched[s['scene']]=sf.read(N/'leveled'/f"{s['scene']}-float.wav",dtype='float32')[0]
 v=patched[s['scene']];l,r=[round(x*sr) for x in s['slot']];start=round(s['start']*sr);v[l:r]=0
 w=round(sr*.4);db=np.array([20*np.log10(max(np.sqrt(np.mean(a[i:i+w]**2)),1e-9)) for i in range(0,len(a)-w,round(sr*.1))]);gain=float(-22-np.percentile(db,70));v[start:start+len(a)]=a*10**(gain/20)
 row=dict(s,sourceSha256=asr['audio_sha256'],duration=len(a)/sr,gainDb=gain,changedSamples=[l,r],speechEnd=s['start']+len(a)/sr,recognized=asr['text'],meaningReview='Complete replacement text checked against corresponding full-context ambiguity; no other phrase changed',humanListening='pending');report.append(row)
 for k in current:next(x for x in current[k]['scenes'] if x['id']==s['scene'])['lines'][s['line']-1]=s[k]
for s,a in patched.items():
 sf.write(out/f'{s}-float.wav',a,24000,subtype='FLOAT');base=sf.read(N/'leveled'/f'{s}-float.wav')[0];changed=np.zeros(len(a),bool)
 for x in spec:
  if x['scene']==s:changed[round(x['slot'][0]*24000):round(x['slot'][1]*24000)]=True
 assert np.array_equal(a[~changed],base[~changed]),'Unexpected changes outside selected sentence intervals'
for k,p in scriptFiles.items():save(p,current[k])
save(out/'patch-map.json',report)
# Reuse unchanged full-scene ASR; derive new caption times only from replacement takes.
timing=load(N/'game-reward-planning-reference-v2.timing.json');rows=[];allwords=[]
for old,now,english in zip(original['ko']['scenes'],current['ko']['scenes'],current['en']['scenes']):
 sid=old['id'];raw=load(N/'asr'/f'{sid}.json');info=sf.info(N/'chunks'/f'{sid}-scene.wav');starts,ends,_=align_characters(' '.join(old['lines']),raw['words'],info.duration);origin=next(x['start'] for x in timing['entries'] if x['scene_id']==sid);cursor=0
 for i,(before,line,en) in enumerate(zip(old['lines'],now['lines'],english['lines']),1):
  oldn=len(normalized(before));change=next((s for s in spec if s['scene']==sid and s['line']==i),None)
  if change:
   a=load(N/'patches/asr'/f"{change['id']}.json");d=sf.info(N/'patches/chunks'/f"{change['id']}-scene.wav").duration
   # Unlock is a display-only English alias, with its Korean term spoken once.
   spoken=change['tts'];aa,bb,_=align_characters(spoken,a['words'],d);localStart=origin+change['start'];n=len(normalized(line));aa=np.interp(np.linspace(0,len(aa)-1,n),np.arange(len(aa)),aa);bb=np.interp(np.linspace(0,len(bb)-1,n),np.arange(len(bb)),bb);aa[1:]=np.maximum(aa[1:],bb[:-1]);bb=np.maximum(aa,bb)
  else:aa=starts[cursor:cursor+oldn];bb=ends[cursor:cursor+oldn];localStart=origin
  count=max(len(split_caption(line,32)),len(split_caption(en,46)));kochunks=partition_fixed(line,32,count);enchunks=partition_fixed(en,46,count);offset=0
  for ko,eng in zip(kochunks,enchunks):
   n=len(normalized(ko));a=2+localStart+float(aa[offset]);b=2+localStart+float(bb[offset+n-1]);rows.append({'scene':sid,'line':i,'start':a,'end':b,'ko':'\n'.join(wrapped_lines(ko,32)),'en':'\n'.join(wrapped_lines(eng,46))});offset+=n
  cursor+=oldn
O=P/'production/local/reference-preserving-v2/edit'
for lang in ['ko','en']:
 blocks=[];previous=0
 for i,row in enumerate(rows,1):
  assert row['start']>=previous-.002 and row['end']>row['start'],(i,previous,row);previous=row['end'];blocks.append(f"{i}\n{timestamp(row['start'])} --> {timestamp(row['end'])}\n{row[lang]}")
 (O/f'captions.{lang}.srt').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
save(O/'caption-tracks.json',rows);print('Applied3 sentence repairs; all other float samples identical; captions',len(rows))
