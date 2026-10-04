"""Preserve all narration text; English clause timing follows directly reviewed Korean speech."""
from pathlib import Path
from datetime import datetime,timezone
import copy,difflib,hashlib,json,math,re
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'));norm=lambda s:re.sub('[^a-z0-9가-힣]','',s.lower());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (WORK/'semantic-tracks.json').exists(),'Preserve reviewed track revision.'
plan=read(WORK/'plan.json');old=read(WORK/'captions.json');ko=read(BASE.parent/'script/narration.ko.json');en=read(BASE.parent/'script/narration.en.json');mf=read(BASE.parent/'project.json');OUT=ROOT/mf['tts']['outputDir'];spec=read(BASE/'semantic-caption-boundaries.json')
contexts=read(BASE/'speech-v2/contexts.json');current=read(BASE/'speech-v3/contexts.json');ko_rows=[];en_rows=[];decisions=[]
for r in old['rows']:
 r=copy.deepcopy(r)
 if r['endSeconds']-r['startSeconds']<.45 and ko_rows and (ko_rows[-1]['scene'],ko_rows[-1]['paragraph'])==(r['scene'],r['paragraph']):
  prev=ko_rows[-1];prev['ko']+=' '+r['ko'];prev['endSample']=r['endSample'];prev['endSeconds']=r['endSeconds'];prev['sourceSpeechTo']=r['sourceSpeechTo'];prev['mergedOriginalIndices']=prev.get('mergedOriginalIndices',[prev['index']])+[r['index']];decisions.append({'kind':'merge-short-KO-tail','originalIndices':prev['mergedOriginalIndices'],'ko':prev['ko'],'duration':prev['endSeconds']-prev['startSeconds']})
 else:ko_rows.append(r)
for i,r in enumerate(ko_rows):r['index']=i+1;r.pop('en',None)
def sample(n,placement):
 for p in placement:
  if p['kind']=='preserved-current-PCM' and p['fromSample']<=n<p['toSample']:return p['outputFromSample']+n-p['fromSample']
 keep=[p for p in placement if p['kind']=='preserved-current-PCM'];assert n<=keep[-1]['toSample'];return keep[-1]['outputToSample']
def split(line,ends):
 groups=[];cursor=0
 for end in ends:
  stop=line.find(end,cursor);assert stop>=0,(line,end);stop+=len(end);groups.append(line[cursor:stop].strip());cursor=stop
 groups.append(line[cursor:].strip());assert all(groups) and ' '.join(groups)==line;return groups
for scene in plan['scenes']:
 sid=scene['id'];cache=read(OUT/'asr'/f'{sid}.json');assert cache['audio_sha256']==scene['audioSha256'];words=cache['words']
 if sid=='02':c=next(c for c in contexts['rows'] if c['id']=='02-opening');assert c['sourceSha256']==scene['audioSha256'];words=c['chunks']+[w for w in words if w['timestamp'][0]>=3.3]
 if sid=='08':c=next(c for c in current['rows'] if c['id']=='title');assert c['sourceSha256']==scene['audioSha256'];words=c['chunks']+[w for w in words if w['timestamp'][0]>=2.42]
 transcript='';times=[]
 for w in words:
  t=norm(w['text']);a,z=w['timestamp']
  for j,ch in enumerate(t):transcript+=ch;times.append((a+(z-a)*j/max(1,len(t)),a+(z-a)*(j+1)/max(1,len(t))))
 ks=next(s for s in ko['scenes'] if s['id']==sid);es=next(s for s in en['scenes'] if s['id']==sid);expected=''.join(norm(x) for x in ks['lines']);matched={}
 for tag,a,z,b,q in difflib.SequenceMatcher(None,expected,transcript,autojunk=False).get_opcodes():
  for j in range(z-a):
   if q>b:matched[a+j]=times[b+min(q-b-1,math.floor(j*(q-b)/(z-a)))]
   else:matched[a+j]=(times[max(0,b-1)][1],times[min(b,len(times)-1)][0])
 offset=0
 for pi,(k,e) in enumerate(zip(ks['lines'],es['lines'])):
  pairs=spec[sid][pi];kg=split(k,[p[0] for p in pairs]);eg=split(e,[p[1] for p in pairs]);assert len(kg)==len(eg);inside=0
  for part,translation in zip(kg,eg):
   a,z=offset+inside,offset+inside+len(norm(part))-1;t0,t1=matched[a][0],matched[z][1];s0=sample(round(t0*24000),scene['pcmPlacement'])+scene['startFrame']*400;s1=sample(round(t1*24000),scene['pcmPlacement'])+scene['startFrame']*400
   en_rows.append({'scene':sid,'paragraph':pi+1,'koSpeechSpan':part,'en':translation,'startSample':s0,'endSample':s1,'startSeconds':s0/24000,'endSeconds':s1/24000,'sourceSpeechFrom':t0,'sourceSpeechTo':t1,'manualSemanticGrouping':True,'allCurrentTextPreserved':True});inside+=len(norm(part))
  assert inside==len(norm(k));assert norm(' '.join(r['ko'] for r in ko_rows if r['scene']==sid and r['paragraph']==pi+1))==norm(k);assert ' '.join(r['en'] for r in en_rows if r['scene']==sid and r['paragraph']==pi+1)==e;offset+=len(norm(k))
for i,r in enumerate(en_rows):
 r['index']=i+1
 if i and r['startSample']<en_rows[i-1]['endSample']:
  prev=en_rows[i-1];mid=round((r['startSample']+prev['endSample'])/2);prev.update(endSample=mid,endSeconds=mid/24000);r.update(startSample=mid,startSeconds=mid/24000,asrBoundaryOverlapResolvedAtMidpoint=True)
 assert r['endSample']>r['startSample']
def tc(samples):
 ms=round(samples/24);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def english_lines(line):
 words=line.split();best=None
 for j in range(1,len(words)):
  pair=[' '.join(words[:j]),' '.join(words[j:])];cost=max(map(len,pair))+abs(len(pair[0])-len(pair[1]))*.4
  if best is None or cost<best[0]:best=cost,pair
 return line if len(line)<=62 or best is None else '\n'.join(best[1])
for lang,rows in [('ko',ko_rows),('en',en_rows)]:
 (WORK/f'captions.{lang}.srt').write_text('\n'.join(f'{r["index"]}\n{tc(r["startSample"])} --> {tc(r["endSample"])}\n{r[lang] if lang=="ko" else english_lines(r[lang])}\n' for r in rows),encoding='utf8')
record={'preparedAt':datetime.now(timezone.utc).isoformat(),'planSha256':sha(WORK/'plan.json'),'currentVoiceApproval':sha(BASE/'voice-approval-v3.json'),'originalKO279Preserved':True,'shortKoMerges':decisions,'koCueCount':len(ko_rows),'enCueCount':len(en_rows),'koreanFixedCenter':[960,970],'koRows':ko_rows,'enRows':en_rows,'all52BilingualParagraphTextsRetained':True,'wholeEnglishParagraphOrderPreserved':True,'manualSemanticReview':'paired clause boundaries directly compared; final all-cue pixels pending','allFixedCaptionPixelsApproved':False}
(WORK/'semantic-tracks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'koCues':len(ko_rows),'enCues':len(en_rows),'shortKoMerges':decisions,'finalPixelsApproved':False},ensure_ascii=False))
