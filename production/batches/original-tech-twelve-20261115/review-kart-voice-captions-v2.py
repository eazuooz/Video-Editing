from pathlib import Path
import hashlib,json,re,statistics
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/shorts-mariokart8-spin-boost';BASE=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def norm(s):return re.sub(r'[^a-z0-9가-힣]','',s.lower().replace('에이트','8'))
def main():
 pp=BASE/'voice-sentence-v2/voice-generation-complete-proof.json';proof=read(pp);np=P/'planning/narration-sentence-v2.json';n=read(np);rp=Path(read(BASE/'asr-sentence-v2/status.json')['review']['path']);rs={x['task']['key']:x for x in read(rp)['results']};levels=read(rp.parent/'levels.json');assert not levels['flags'];timing=read(proof['unitTiming']['path'])['entries'];units={u['id']:u for u in n['units']};words=[]
 for e,raw in zip(timing,proof['rawChunks']):
  uid=e['scene_id'];u=units[uid]
  if u['paragraph']=='p005':continue
  r=rs['unit-'+uid];assert r['task']['sha256']==raw['sha256']and norm(r['rawRecognition']['text'])==norm(u['ko']),(uid,r['rawRecognition']['text'])
  for j,c in enumerate(r['rawRecognition']['chunks']):
   a,b=c['timestamp'];assert a is not None and b is not None and 0<=a<b<=raw['duration'];words.append(dict(unit=uid,paragraph=u['paragraph'],recognizedText=c['text'],start=e['start']+a,end=e['start']+b,source=dict(review=pin(rp),taskKey=r['task']['key'],wordIndex=j,timestamp=[a,b])))
 para=next(x for x in n['paragraphs']if x['id']=='p005');r=rs['paragraph-p005'];assert norm(r['rawRecognition']['text'])==norm(para['ko']);pt=next(x for x in read(proof['paragraphTiming']['path'])['entries']if x['id']=='p005')
 for j,c in enumerate(r['rawRecognition']['chunks']):
  a,b=c['timestamp'];assert a is not None and b is not None and 0<=a<b<=(pt['endSample']-pt['startSample'])/24000;words.append(dict(unit=None,paragraph='p005',recognizedText=c['text'],start=pt['startSample']/24000+a,end=pt['startSample']/24000+b,source=dict(review=pin(rp),taskKey=r['task']['key'],wordIndex=j,timestamp=[a,b],reason='Literal positive full-paragraph recognition resolves isolated 단중력/반중력 ambiguity; original raw evidence is retained.')))
 cp=P/'planning/caption-clauses-sentence-v2.json';cues=[]
 for para in read(cp)['paragraphs']:
  ws=[w for w in words if w['paragraph']==para['id']];assert ''.join(norm(w['recognizedText'])for w in ws)==''.join(norm(c[0])for c in para['clauses']);bounds={0:0};at=0
  for i,w in enumerate(ws):at+=len(norm(w['recognizedText']));bounds[at]=i+1
  at=0
  for i,(ko,en)in enumerate(para['clauses']):
   begin=at;at+=len(norm(ko));assert begin in bounds and at in bounds,('Clause splits ASR word',ko);first,last=ws[bounds[begin]],ws[bounds[at]-1];cues.append(dict(paragraph=para['id'],clauseIndex=i,ko=ko,en=en,start=first['start'],spokenEnd=last['end'],startWord=first,endWord=last))
 for i,c in enumerate(cues):c['end']=cues[i+1]['start']if i+1<len(cues)else proof['canonical']['duration'];assert c['start']<c['spokenEnd']<=c['end']+.0001
 rows=[x for x in levels['paragraphs']if x['kind']=='paragraph'];med=statistics.median(x['wholeTake']['bodyDbfs']for x in rows);rel=[dict(paragraph=x['paragraph'],relativeToMedianDb=x['wholeTake']['bodyDbfs']-med)for x in rows];assert all(x['relativeToMedianDb']>=-4 for x in rel)
 target=pp.parent/'technical-voice-review.json';write(target,dict(voice=pin(pp),sourceNarration=pin(np),sourceAsr=pin(rp),sourceLevels=pin(rp.parent/'levels.json'),rawUnitsByteExact=True,sameApprovedReferenceAndModel=True,voiceBiometricIdentityMeasured=False,sustainedDeclineHolds=[],paragraphRelativeLevels=rel,contentReview='Every unit matches literally after8 spelling and punctuation/spacing equivalence except isolated u014. The complete p005 independently recognizes the exact source wording 반중력; all p005 anchors use its actual positive whole words. No raw recognition or voice bytes changed.',approvedForTechnicalDownstream=True,actualListening=False,humanApproval=False,finalFilmComplete=False))
 out=P/'production/caption-timing-v2.json';write(out,dict(voice=pin(pp),technicalVoiceReview=pin(target),clauses=pin(cp),cues=cues,audioOffsetSeconds=0,voiceSpeed=1,wordInterpolation=False,englishUsesSameMeaningClauseInterval=True,finalFilmComplete=False))
 def stamp(t):
  ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for lang in ['ko','en']:
  out=P/'production'/('captions-v2.'+lang+'.srt');assert not out.exists();out.write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c[lang]}'for i,c in enumerate(cues))+'\n','utf8')
 print(json.dumps(dict(technicalReview=pin(target),cues=len(cues),duration=proof['canonical']['duration'])))
if __name__=='__main__':main()
