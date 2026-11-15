"""Bind reviewed camera v5 voice to literal positive whole-word cues."""
from pathlib import Path
import hashlib,json,re,statistics
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/shorts-mario64-lakitu-camera';BASE=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def norm(s):
 for a,b in [('육십사','64'),('씨','c'),('에이','a'),('비','b')]:s=s.replace(a,b)
 return re.sub(r'[^0-9A-Za-z가-힣]','',s).lower()
def main():
 pp=BASE/'voice-edit-v5/voice-generation-complete-proof.json';proof=read(pp);n=read(P/'planning/narration-camera-v5.json');a4=Path(n['sourceAsr']['path']);a2=Path(n['earlierAsr']['path']);a5=Path(read(BASE/'asr-edit-v5/status.json')['review']['path']);r4=read(a4);r2=read(a2);r5=read(a5);l4=read(a4.parent/'levels.json');l5=read(a5.parent/'levels.json');assert not l4['flags'] and not l5['flags']
 for row in r5['results']:
  assert '나눠'in row['rawRecognition']['text']
 expected={u['id']:u for u in n['units']};timing=read(proof['unitTiming']['path'])['entries'];words=[]
 for e,raw in zip(timing,proof['rawChunks']):
  uid=e['scene_id'];rp=a2 if uid=='u011'else a4;r=next(x for x in (r2 if uid=='u011'else r4)['results']if x['task']['key']=='unit-'+uid);assert r['task']['sha256']==raw['sha256'];assert norm(r['rawRecognition']['text'])==norm(expected[uid]['ko']),(uid,r['rawRecognition']['text'])
  for j,c in enumerate(r['rawRecognition']['chunks']):
   a,b=c['timestamp'];assert a is not None and b is not None and 0<=a<b<=raw['duration']
   words.append(dict(unit=uid,paragraph=expected[uid]['paragraph'],recognizedText=c['text'],start=e['start']+a,end=e['start']+b,source=dict(review=pin(rp),taskKey=r['task']['key'],wordIndex=j,timestamp=[a,b])))
 cp=P/'planning/caption-clauses-camera-v5.json';clauses=read(cp);cues=[]
 for para in clauses['paragraphs']:
  ws=[w for w in words if w['paragraph']==para['id']];text=''.join(norm(w['recognizedText'])for w in ws);assert text==''.join(norm(c[0])for c in para['clauses'])
  bounds={0:0};at=0
  for i,w in enumerate(ws):at+=len(norm(w['recognizedText']));bounds[at]=i+1
  at=0
  for i,(ko,en)in enumerate(para['clauses']):
   begin=at;at+=len(norm(ko));assert begin in bounds and at in bounds,('Clause splits ASR word',para['id'],ko);first,last=ws[bounds[begin]],ws[bounds[at]-1];cues.append(dict(paragraph=para['id'],clauseIndex=i,ko=ko,en=en,start=first['start'],spokenEnd=last['end'],startWord=first,endWord=last))
 for i,c in enumerate(cues):c['end']=cues[i+1]['start']if i+1<len(cues)else proof['canonical']['duration'];assert c['start']<c['spokenEnd']<=c['end']+.0001
 rows=[x for x in l4['paragraphs']if x['kind']=='paragraph'and x['paragraph']not in ['p003','p002+p003']]+[x for x in l5['paragraphs']if x['paragraph']=='p003'];assert len(rows)==len(n['paragraphs'])
 med=statistics.median(x['wholeTake']['bodyDbfs']for x in rows);relative=[dict(paragraph=x['paragraph'],relativeToMedianDb=x['wholeTake']['bodyDbfs']-med)for x in rows];assert all(x['relativeToMedianDb']>=-4 for x in relative)
 target=pp.parent/'technical-voice-review.json';write(target,dict(voice=pin(pp),sourceAsr=pin(a4),earlierAsr=pin(a2),assembledAsr=pin(a5),sourceLevels=pin(a4.parent/'levels.json'),assembledLevels=pin(a5.parent/'levels.json'),contentReview='Every retained sentence matches independent recognition after punctuation/spacing and64/C/A/B orthographic equivalence only. The replacement 나눠 sentence is recognized literally in both new joins, full p003 and combined p002+p003. Rejected 나노 and removed proper-name ambiguity remain in previous evidence.',rawUnitsByteExact=True,sameApprovedReferenceAndModel=True,voiceBiometricIdentityMeasured=False,sustainedDeclineHolds=[],paragraphRelativeLevels=relative,approvedForTechnicalDownstream=True,actualListening=False,humanApproval=False,finalFilmComplete=False))
 out=P/'production/caption-timing-v5.json';write(out,dict(voice=pin(pp),technicalVoiceReview=pin(target),clauses=pin(cp),cues=cues,audioOffsetSeconds=0,voiceSpeed=1,wordInterpolation=False,englishUsesSameMeaningClauseInterval=True,finalFilmComplete=False))
 def stamp(t):
  ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for lang in ['ko','en']:
  out=P/'production'/('captions-v5.'+lang+'.srt');assert not out.exists();out.write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c[lang]}'for i,c in enumerate(cues))+'\n','utf8')
 print(json.dumps(dict(technicalReview=pin(target),cues=len(cues),duration=proof['canonical']['duration'])))
if __name__=='__main__':main()
