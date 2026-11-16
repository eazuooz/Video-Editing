"""CPU review of exact recognized words, unchanged levels and meaning captions."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,statistics
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def norm(s,slug='',para=''):
 s=re.sub(r'\s+','',s.lower())
 for x,y in [('씨피유','cpu'),('지피유','gpu'),('에스에스디','ssd'),('피시','pc'),('directstorage','다이렉트스토리지')]:s=s.replace(x,y)
 # Retain only the already evidenced, standard possessive pronunciation scopes.
 if 'journey'in slug and para=='p001':s=s.replace('모래의','모래에')
 if 'spiderman'in slug and para=='p004':s=s.replace('면의','면에')
 if 'returnal'in slug and para=='p004':s=s.replace('처음의','처음에')
 if 'control'in slug and para=='p002':s=s.replace('그옆의작은','그옆에작은')
 if 'mariokart8'in slug and para in['p001','p005']:s=s.replace('마리오카트에이트','마리오카트8')
 if 'mariokart8'in slug and para=='p004':s=s.replace('옆의평범한','옆에평범한')
 return re.sub('[^0-9a-z가-힣]','',s)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--record',action='store_true');a=ap.parse_args()
 p=ROOT/'projects'/a.project;np=p/'planning/narration-master-v110.json';n=read(np);vp=M/p.name/'voice-master-v110/voice-generation-complete-proof.json';v=read(vp)
 status=read(M/p.name/'asr-master-v110/status.json');rp=Path(status['review']['path']);r=read(rp);lp=rp.parent/'levels.json';l=read(lp);cp=p/'planning/caption-clauses-master-v110.json';caps=read(cp)
 assert pin(vp)==r['job']or read(r['job']['path'])['identity']['voiceProof']==pin(vp)
 holds=list(l['flags']);cues=[];mismatches=[]
 for para,entry in zip(n['paragraphs'],read(v['paragraphTiming']['path'])['entries']):
  rec=next(x for x in r['results']if x['task']['key']=='paragraph-'+para['id']);clean=lambda s:norm(s,p.name,para['id'])
  if clean(rec['rawRecognition']['text'])!=clean(para['ko']):mismatches.append(dict(paragraph=para['id'],expected=para['ko'],recognized=rec['rawRecognition']['text']));continue
  words=[];bad=[]
  for j,w in enumerate(rec['rawRecognition']['chunks']):
   x,y=w['timestamp']
   if x is None or y is None or not 0<=x<y<=(entry['endSample']-entry['startSample'])/24000:bad.append(w);continue
   words.append(dict(paragraph=para['id'],recognizedText=w['text'],start=entry['startSample']/24000+x,end=entry['startSample']/24000+y,source=dict(review=pin(rp),taskKey=rec['task']['key'],wordIndex=j,timestamp=[x,y])))
  if bad:holds.append(dict(kind='invalid-paragraph-whole-word',paragraph=para['id'],words=bad));continue
  cs=next(x['clauses']for x in caps['paragraphs']if x['id']==para['id']);at=0;bounds={0:0}
  for i,w in enumerate(words):at+=len(clean(w['recognizedText']));bounds[at]=i+1
  if ''.join(clean(w['recognizedText'])for w in words)!=clean(para['ko']):holds.append(dict(kind='word-text-discrepancy',paragraph=para['id']));continue
  unitbounds=[];pos=0
  for u in [u for u in n['units']if u['paragraph']==para['id']]:
   unitbounds.append((pos,pos+len(clean(u['ko'])),u['id']));pos+=len(clean(u['ko']))
  pos=0
  for i,(ko,en)in enumerate(cs):
   start=pos;pos+=len(clean(ko))
   if start not in bounds or pos not in bounds:holds.append(dict(kind='caption-splits-actual-word',paragraph=para['id'],ko=ko));continue
   first,last=words[bounds[start]],words[bounds[pos]-1];uid=next((uid for x,y,uid in unitbounds if x<=start<y),None)
   cues.append(dict(paragraph=para['id'],clauseIndex=i,unitId=uid,ko=ko,en=en,start=first['start'],spokenEnd=last['end'],startWord=first,endWord=last))
 rows=[x for x in l['paragraphs']if x['kind']=='paragraph'];median=statistics.median(x['wholeTake']['bodyDbfs']for x in rows);relative=[dict(paragraph=x['paragraph'],relativeToMedianDb=x['wholeTake']['bodyDbfs']-median)for x in rows]
 for x in relative:
  if x['relativeToMedianDb']< -4:holds.append(dict(kind='paragraph-relative-body-level',**x))
 result=dict(slug=p.name,paragraphMismatches=mismatches,holds=holds,relativeLevels=relative,positiveWholeWordCaptionCount=len(cues),approvedForTechnicalDownstream=not holds and not mismatches,actualListening=False,humanApproval=False,standardPossessivePronunciationScope=({'text':'그 옆의 작은 / 그 옆에 작은','paragraph':'p002','source':'https://www.korean.go.kr/front/mcfaq/mcfaqView.do?mcfaq_seq=5716','newLexicalAlias':False}if'control'in p.name else {'text':'옆의 평범한 / 옆에 평범한','paragraph':'p004','source':'https://www.korean.go.kr/front/mcfaq/mcfaqView.do?mcfaq_seq=5716','newLexicalAlias':False}if'mariokart8'in p.name else None),canonicalNamedSpelling=({'scope':'p001/p005 Mario Kart8 title only','spoken':'마리오 카트 에이트','canonicalAsr':'마리오 카트8','source':'https://www.nintendo.com/en-gb/News/2014/April/New-items-characters-and-courses-make-for-gravity-defying-fun-in-Mario-Kart-8-launching-May-30th-on-Wii-U-870260.html','lexicalSubstitution':False}if'mariokart8'in p.name else None))
 print(json.dumps(result,ensure_ascii=False),flush=True)
 if not a.record:return
 assert result['approvedForTechnicalDownstream'],'Preserve source and inspect exact holds before a separate repair version'
 for i,c in enumerate(cues):c['end']=cues[i+1]['start']if i+1<len(cues)else v['canonical']['duration'];assert c['start']<c['spokenEnd']<=c['end']+.0001
 spec=importlib.util.spec_from_file_location('clarity_caption_fit',H/'clarity-layout-v88.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout);composer=layout.Composer(p.name)
 for c in cues:composer.captioned(composer.base('해설용 비교 모형'),c['ko'])
 review=vp.parent/'technical-voice-review.json';save(review,dict(**result,voice=pin(vp),sourceNarration=pin(np),sourceAsr=pin(rp),sourceLevels=pin(lp),unchangedSelectedPcmByteExact=True,newRawPcmUnmodified=False,wholeUtteranceGainProof=v['wholeUtteranceGainProof'],rawInternalDeclineHoldsPreserved=True,voiceBiometricIdentityMeasured=False))
 target=p/'production/caption-timing-v95.json';save(target,dict(voice=pin(vp),technicalVoiceReview=pin(review),clauses=pin(cp),cues=cues,audioOffsetSeconds=0,voiceSpeed=1,wordInterpolation=False,englishUsesSameMeaningClauseInterval=True,finalFilmComplete=False))
 save(p/'production/accepted-voice-selection-v95.json',dict(selectedMasterVersion=110,voice=pin(vp),technicalVoiceReview=pin(review),captionTiming=pin(target),narration=pin(np),asr=pin(rp),clauses=pin(cp),humanApproval=False))
 def stamp(t):
  ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for lang in ['ko','en']:
  target=p/'production'/('captions-v95.'+lang+'.srt');assert not target.exists();target.write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c[lang]}'for i,c in enumerate(cues))+'\n','utf8')
if __name__=='__main__':main()
