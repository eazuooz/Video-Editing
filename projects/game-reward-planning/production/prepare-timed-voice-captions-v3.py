"""Preserve current PCM, insert only planned pauses and produce review captions."""
from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,json,math,re
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();norm=lambda s:re.sub('[^a-z0-9가-힣]','',s.lower())
plan=read(WORK/'plan.json');assert not (WORK/'narration-timed.wav').exists(),'Preserve timed work.'
ko=read(BASE.parent/'script/narration.ko.json');en=read(BASE.parent/'script/narration.en.json');mf=read(BASE.parent/'project.json');out=ROOT/mf['tts']['outputDir']
contexts=read(BASE/'speech-v2/contexts.json');opening=read(BASE/'speech-v3/contexts.json')
whole=np.zeros(plan['finalFrames']*400,dtype=np.int16);rows=[];pcm_proof=[]
def map_sample(n,placement):
 for p in placement:
  if p['kind']=='preserved-current-PCM' and p['fromSample']<=n<p['toSample']:return p['outputFromSample']+n-p['fromSample']
 if n==placement[-1].get('toSample'):return placement[-1]['outputToSample']
 keep=[p for p in placement if p['kind']=='preserved-current-PCM'];assert n<=keep[-1]['toSample'];return keep[-1]['outputToSample']
def split_ko(line):
 tokens=list(re.finditer(r'\S+',line));groups=[];start=0;char_count=0
 for i,t in enumerate(tokens):
  if char_count and char_count+len(t[0])>14:groups.append((tokens[start].start(),tokens[i-1].end()));start=i;char_count=0
  char_count+=len(t[0])+1
  if t[0][-1:] in ['.', '?', '!', ','] and char_count>=7:groups.append((tokens[start].start(),t.end()));start=i+1;char_count=0
 if start<len(tokens):groups.append((tokens[start].start(),tokens[-1].end()))
 return groups
for scene in plan['scenes']:
 sid=scene['id'];wave,rate=sf.read(ROOT/scene['audio'],dtype='int16');assert rate==24000 and sha(ROOT/scene['audio'])==scene['audioSha256'];placement=scene['pcmPlacement'];timed=np.zeros(scene['frames']*400,dtype=np.int16);recovered=[]
 for p in placement:
  if p['kind']=='preserved-current-PCM':q=wave[p['fromSample']:p['toSample']];timed[p['outputFromSample']:p['outputToSample']]=q;recovered.append(q)
 assert np.array_equal(np.concatenate(recovered),wave)
 whole[scene['startFrame']*400:(scene['startFrame']+scene['frames'])*400]=timed
 pcm_proof.append({'scene':sid,'sourceSha256':scene['audioSha256'],'allSamplesExactlyRetainedInOriginalOrder':True,'sourceSamples':len(wave),'insertedSilenceSamples':len(timed)-len(wave),'waveDataSha256':hashlib.sha256(wave.tobytes()).hexdigest(),'timedWaveDataSha256':hashlib.sha256(timed.tobytes()).hexdigest()})
 cache=read(out/'asr'/f'{sid}.json');assert cache['audio_sha256']==scene['audioSha256'];words=cache['words']
 if sid=='02':c=next(x for x in contexts['rows'] if x['id']=='02-opening');words=c['chunks']+[w for w in words if w['timestamp'][0]>=3.3]
 if sid=='08':c=next(x for x in opening['rows'] if x['id']=='title');words=c['chunks']+[w for w in words if w['timestamp'][0]>=2.42]
 transcript='';times=[]
 for w in words:
  t=norm(w['text']);a,z=w['timestamp'];
  for j,ch in enumerate(t):transcript+=ch;times.append((a+(z-a)*j/max(1,len(t)),a+(z-a)*(j+1)/max(1,len(t))))
 ks=next(s for s in ko['scenes'] if s['id']==sid);es=next(s for s in en['scenes'] if s['id']==sid);expected=''.join(norm(x) for x in ks['lines']);matched={}
 for tag,a,z,b,q in difflib.SequenceMatcher(None,expected,transcript,autojunk=False).get_opcodes():
  for j in range(z-a):
   if q>b:matched[a+j]=times[b+min(q-b-1,math.floor(j*(q-b)/(z-a))) ]
   else:matched[a+j]=(times[max(0,b-1)][1],times[min(b,len(times)-1)][0])
 offset=0
 for pi,(line,english) in enumerate(zip(ks['lines'],es['lines'])):
  groups=split_ko(line);eng=english.split();weights=[len(norm(line[a:z])) for a,z in groups];cum=0;last=0
  for gi,(a,z) in enumerate(groups):
   ka=offset+len(norm(line[:a]));kz=offset+len(norm(line[:z]))-1;t0,t1=matched[ka][0],matched[kz][1];s0=map_sample(round(t0*rate),placement)+scene['startFrame']*400;s1=map_sample(round(t1*rate),placement)+scene['startFrame']*400
   cum+=weights[gi];end=len(eng) if gi==len(groups)-1 else min(len(eng)-(len(groups)-gi-1),max(last+1,round(len(eng)*cum/sum(weights))))
   assert end>last,'English translation needs fewer cue divisions';english_part=' '.join(eng[last:end]);last=end
   rows.append({'scene':sid,'paragraph':pi+1,'ko':line[a:z],'en':english_part,'startSample':s0,'endSample':s1,'startSeconds':s0/rate,'endSeconds':s1/rate,'sourceSpeechFrom':t0,'sourceSpeechTo':t1,'fixedCenter':[960,970],'fontSize':48,'maxLines':1,'pixelApproval':False})
  assert norm(' '.join(r['ko'] for r in rows if r['scene']==sid and r['paragraph']==pi+1))==norm(line);assert ' '.join(r['en'] for r in rows if r['scene']==sid and r['paragraph']==pi+1)==english
  offset+=len(norm(line))
for i,r in enumerate(rows):
 r['index']=i+1
 if i and r['startSample']<rows[i-1]['endSample']:
  prev=rows[i-1];mid=round((r['startSample']+prev['endSample'])/2);prev['endSample']=mid;prev['endSeconds']=mid/24000;r['startSample']=mid;r['startSeconds']=mid/24000;r['asrBoundaryOverlapResolvedAtMidpoint']=True
 assert r['endSample']>r['startSample'] and (not i or r['startSample']>=rows[i-1]['endSample'])
def tc(samples):
 ms=round(samples/24);h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{mi:02}:{s:02},{ms:03}'
for lang in ['ko','en']:(WORK/f'review.{lang}.srt').write_text('\n'.join(f'{r["index"]}\n{tc(r["startSample"])} --> {tc(r["endSample"])}\n{r[lang]}\n' for r in rows),encoding='utf8')
sf.write(WORK/'narration-timed.wav',whole,24000,subtype='PCM_16')
(WORK/'pcm-preservation.json').write_text(json.dumps({'recordedAt':datetime.now(timezone.utc).isoformat(),'planSha256':sha(WORK/'plan.json'),'scenes':pcm_proof,'all52ParagraphsRetained':True,'all7ExplanationSpeechPcmRetained':True,'noNewTts':True,'timedWaveSha256':sha(WORK/'narration-timed.wav'),'finalMixReview':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(WORK/'captions.json').write_text(json.dumps({'status':'all-current-text-retimed-awaiting-cue-pixels-and-context-review','planSha256':sha(WORK/'plan.json'),'rows':rows,'cueCount':len(rows),'manualBilingualTimingReview':False,'allFixedCaptionPixelsApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'currentScenes':13,'retainedParagraphs':52,'reviewCues':len(rows),'timedWaveSeconds':len(whole)/24000,'finalApproved':False}))
