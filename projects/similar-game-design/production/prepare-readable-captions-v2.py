from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
SOURCE=BASE/'caption-candidate-v1/captions.json';DEST=BASE/'caption-candidate-v2'
assert not DEST.exists(),'Preserve existing candidate'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
j=json.loads(SOURCE.read_text('utf-8'));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
norm=lambda s:''.join(s.split())
changes=[]
def wrap(text,lang):
 lines=[];line=''
 for word in text.split():
  trial=(line+' '+word).strip()
  fits=font.getlength(trial)<=620 if lang=='ko' else len(trial)<=78
  if line and not fits:lines.append(line);line=word
  else:line=trial
 if line:lines.append(line)
 return lines
for lang,minimum in [('ko',.65),('en',1.)]:
 rows=copy.deepcopy(j[lang]);i=0
 while i<len(rows):
  cue=rows[i]
  if cue['endSeconds']-cue['startSeconds']>=minimum-1e-6:i+=1;continue
  assert i>0,'Short opening cue requires separate review'
  prev=rows[i-1]
  assert (prev['scene'],prev['paragraph'])==(cue['scene'],cue['paragraph']),'Preserve paragraph boundary'
  assert cue['startSeconds']-prev['endSeconds']<=.4,'Do not bridge long silence'
  text=' '.join((prev[lang]+' '+cue[lang]).split());lines=wrap(text,lang)
  assert len(lines)<=2,'Excessive lines require direct rebalance'
  changes.append(dict(language=lang,scene=cue['scene'],paragraph=cue['paragraph'],originalIndices=prev.get('originalIndices',[prev['index']])+[cue['index']],previousText=prev[lang],shortText=cue[lang],shortDurationSeconds=cue['endSeconds']-cue['startSeconds'],newText='\n'.join(lines),startSeconds=prev['startSeconds'],endSeconds=cue['endSeconds']))
  prev[lang]='\n'.join(lines);prev['lines']=lines;prev['originalIndices']=changes[-1]['originalIndices'];prev['endSeconds']=cue['endSeconds']
  if lang=='ko':prev['sourceSpeechEnd']=cue['sourceSpeechEnd'];prev['textWidthPx']=max(font.getlength(t)for t in lines)
  rows.pop(i)
 for index,cue in enumerate(rows,1):cue['index']=index
 for p in j['paragraphs']:
  actual=[c for c in rows if c['scene']==p['scene'] and c['paragraph']==p['paragraph']]
  assert norm(''.join(c[lang]for c in actual))==norm(p[lang]),(lang,p['scene'],p['paragraph'])
 for a,b in zip(rows,rows[1:]):assert a['endSeconds']<=b['startSeconds']+.001
 j[lang]=rows
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
j.update(preparedAt=datetime.now(timezone.utc).isoformat(),status='current73-readable-literal-candidate-v2',previousCandidate=dict(path=rel(SOURCE),sha256=sha(SOURCE),koCueCount=437,enCueCount=155,allInitialCueTextsDirectlyRead=True),readabilityChanges=changes,koCueCount=len(j['ko']),enCueCount=len(j['en']),minimumKoCueSeconds=min(c['endSeconds']-c['startSeconds']for c in j['ko']),minimumEnCueSeconds=min(c['endSeconds']-c['startSeconds']for c in j['en']),maxLines=2,allLiteralKoEnParagraphsPreserved=True,allOriginalSpeechBoundariesPreserved=True,newTtsJobs=0,newAsrJobs=0,newMedia=0)
DEST.mkdir()
for lang in ['ko','en']:(DEST/f'candidate.{lang}.srt').write_text('\n\n'.join(f'{r["index"]}\n{stamp(r["startSeconds"])} --> {stamp(r["endSeconds"])}\n{r[lang]}'for r in j[lang])+'\n','utf-8')
(DEST/'captions.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(koCues=j['koCueCount'],enCues=j['enCueCount'],changes=len(changes),minimumKo=j['minimumKoCueSeconds'],minimumEn=j['minimumEnCueSeconds'],timingApproved=False,pixelsReviewed=False)))
