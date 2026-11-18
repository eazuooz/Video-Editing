"""Use complete blind contexts, never lexical error aliases, for opening captions."""
from pathlib import Path
import argparse,hashlib,json,re
H=Path(__file__).resolve().parent;M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=M/'innovation-openings-v181'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def norm(s):
 s=re.sub(r'\s+','',s.lower())
 for a,b in [('삼차원','3차원'),('마리오육십사','마리오64'),('마리오카트에이트','마리오카트8'),('지피유','gpu'),('피시','pc')]:s=s.replace(a,b)
 return re.sub('[^0-9a-z가-힣]','',s)
def actual_words(record,offset,duration):
 words=[];bad=[]
 for i,w in enumerate(record['rawRecognition']['chunks']):
  x,y=w['timestamp']
  if x is None or y is None or not 0<=x<y<=duration+.00001:bad.append(w);continue
  words.append(dict(text=w['text'],start=x+offset,end=y+offset,wordIndex=i,sourceTask=record['task']['key']))
 return words,bad
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--record',action='store_true');a=ap.parse_args();n=read(H/'innovation-opening-narration-v181.json');v=read(BASE/'voice/voice-generation-complete-proof.json');status=read(BASE/'asr/status.json');rp=Path(status['review']['path']);r=read(rp);lp=Path(status['levels']['path']);l=read(lp);times=read(v['paragraphTiming']['path'])['entries'];unit_times={x['scene_id']:x for x in read(v['unitTiming']['path'])['entries']};by={x['task']['key']:x for x in r['results']};issues=[];rows=[]
 assert read(r['job']['path'])['identity']['voiceProof']==pin(BASE/'voice/voice-generation-complete-proof.json')
 for p,e in zip(n['paragraphs'],times):
  rec=by['paragraph-'+p['id']];pw,pbad=actual_words(rec,0,(e['endSample']-e['startSample'])/24000);para_ok=norm(rec['rawRecognition']['text'])==norm(p['ko'])and not pbad and ''.join(norm(w['text'])for w in pw)==norm(p['ko']);bad=[];contexts=[]
  if para_ok:words=pw;contexts=[dict(task=rec['task']['key'],kind='complete-paragraph')]
  else:
   words=[]
   for u in [u for u in n['units']if u['paragraph']==p['id']]:
    unit=by['unit-'+u['id']];ut=unit_times[u['id']];offset=ut['start']-e['start'];uw,ubad=actual_words(unit,offset,ut['end']-ut['start'])
    if norm(unit['rawRecognition']['text'])!=norm(u['ko'])or ubad or ''.join(norm(w['text'])for w in uw)!=norm(u['ko']):bad.append(dict(kind='no-exact-positive-complete-context',unit=u['id'],expected=u['ko'],recognized=unit['rawRecognition']['text'],invalidWords=ubad))
    words.extend(uw);contexts.append(dict(task=unit['task']['key'],kind='independent-complete-utterance',rawBytesUnchanged=bool(unit.get('recognitionReusedOnlyForByteExactPcm'))))
  if ''.join(norm(w['text'])for w in words)!=norm(p['ko']):bad.append(dict(kind='actual-word-coverage'))
  bounds={0:0};pos=0
  for i,w in enumerate(words):pos+=len(norm(w['text']));bounds[pos]=i+1
  cues=[];pos=0;us=[u for u in n['units']if u['paragraph']==p['id']]
  for u in us:
   for ko,en in zip(u['clausesKo'],u['clausesEn']):
    start=pos;pos+=len(norm(ko))
    if start not in bounds or pos not in bounds:bad.append(dict(kind='clause-inside-word',ko=ko));continue
    first,last=words[bounds[start]],words[bounds[pos]-1];cues.append(dict(ko=ko,en=en,start=first['start'],spokenEnd=last['end'],unitId=u['id'],startWord=first,endWord=last))
  for i,c in enumerate(cues):c['end']=cues[i+1]['start']if i+1<len(cues)else e['end']-e['start'];assert c['start']<c['spokenEnd']<=c['end']+.00001
  bad.extend(f for f in l['flags']if f.get('taskKey')in['unit-'+u['id']for u in us]);issues.extend(dict(order=p['order'],**x)for x in bad)
  rows.append(dict(order=p['order'],slug=p['slug'],paragraph=p['id'],expected=p['ko'],recognized=' '.join(by[x['task']]['rawRecognition']['text']for x in contexts),selectedCompleteContexts=contexts,alternateParagraphRecognition=rec['rawRecognition']['text']if not para_ok else None,alternateMismatchIsNotAClaimOfTtsError=True,canonicalStartSample=e['startSample'],canonicalEndSample=e['endSample'],duration=(e['endSample']-e['startSample'])/24000,cues=cues,words=words,issues=bad))
 report=dict(voice=pin(BASE/'voice/voice-generation-complete-proof.json'),narration=pin(H/'innovation-opening-narration-v181.json'),asr=pin(rp),levels=pin(lp),rows=rows,issues=issues,rawParagraphLevelFlags=l['flags'],paragraphInterTakeLevelMatchingRequired=True,positiveWholeWordCaptionCount=sum(len(x['cues'])for x in rows),approvedForConstantGainMix=not issues,standardWrittenNumericAndInitialismEquivalence=['삼차원/3차원','마리오 육십사/마리오64','마리오 카트 에이트/마리오카트8','지피유/GPU','피시/PC'],lexicalErrorAliasesAdded=False,wordInterpolation=False,rawPcmModified=False,actualListening=False,humanApproval=False)
 print(json.dumps(dict(issues=issues,rawLevelFlags=l['flags'],positiveCaptions=report['positiveWholeWordCaptionCount'],ready=not issues),ensure_ascii=False))
 if a.record:
  assert not issues;p=BASE/'voice/technical-voice-review-v182.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(pin(p)))
if __name__=='__main__':main()
