"""Bind independently recognized full paragraphs to actual whole-word cues."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,statistics
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CONFIG={'shorts-horizon-gpu-placement':('voice-master-v8','asr-master-v8','v6','v8'),'shorts-spiderman-swing-anchor':('voice-master-v8','asr-master-v8','v6','v8'),'shorts-inside-temporal-antialiasing':('voice-repair-v9','asr-repair-v9','v9','v9')}
CONFIG.update({s:('voice-repair-v15','asr-repair-v15','v15','v15')for s in ['shorts-doom-push-forward-healing', 'shorts-botw-chemistry-rules']});CONFIG['shorts-control-destruction-pipeline']=('voice-master-v14','asr-master-v14','v6','v14')

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def norm(s,slug,para):
 s=re.sub(r"\s+","",s)
 for x,y in [('씨피유','cpu'),('지피유','gpu'),('에스에스디','ssd'),('피시','pc'),('다이렉트스토리지','directstorage')]:s=s.lower().replace(x,y)
 if slug=='shorts-journey-sand-sparkle'and para=='p001':s=s.replace('모래의','모래에')
 if slug=='shorts-horizon-gpu-placement'and para=='p004':s=s.replace('사이의','사이에')
 if slug=='shorts-returnal-particle-tentacles'and para=='p004':s=s.replace('처음의','처음에')
 if slug=='shorts-spiderman-swing-anchor'and para=='p004':s=s.replace('면의','면에')
 return re.sub(r'[^0-9a-z가-힣]','',s.lower())
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--record',action='store_true');a=p.parse_args();allowed=[x['slug']for x in read(HERE/'bounded-semantic-corrections-source-review-v6.json')['projects']];assert a.project in allowed;P=ROOT/'projects'/a.project;BASE=MEDIA/P.name;vv,av,nv,cv=CONFIG.get(P.name,('voice-repair-v6','asr-repair-v6','v6','v6'));np=P/('planning/narration-repair-'+nv+'.json');n=read(np);pp=BASE/vv/'voice-generation-complete-proof.json';proof=read(pp);assert 'master'not in vv or(read(pp.parent/'constant-gain-proof.json')['sourceUnitsUnmodified']and not read(pp.parent/'constant-gain-proof.json')['masterFlags']);rp=Path(read(BASE/av/'status.json')['review']['path']);r=read(rp);lp=rp.parent/'levels.json';l=read(lp);assert not l['flags'],l['flags'];cp=P/('planning/caption-clauses-repair-'+nv+'.json');refined=P/'planning/caption-clauses-source-ordered-v10.json';cp=refined if refined.exists()and nv!='v15'else cp;cv='v10'if refined.exists()and nv!='v15'else cv;caps=read(cp);pt=read(proof['paragraphTiming']['path'])['entries'];cues=[];unit_discrepancies=[]
 for u in n['units']:
  unit=next(x for x in r['results']if x['task']['key']=='unit-'+u['id']);
  if norm(unit['rawRecognition']['text'],P.name,u['paragraph'])!=norm(u['ko'],P.name,u['paragraph']):unit_discrepancies.append(dict(unit=u['id'],expected=u['ko'],isolatedRecognition=unit['rawRecognition']['text'],review='Full independent paragraph must match literally before acceptance; isolated record preserved.'))
 for para,entry in zip(n['paragraphs'],pt):
  rec=next(x for x in r['results']if x['task']['key']=='paragraph-'+para['id']);assert rec['task']['expected']==para['ko']and rec['task']['startSample']==entry['startSample'];normp=lambda s:norm(s,P.name,para['id']);assert normp(rec['rawRecognition']['text'])==normp(para['ko']),(para['id'],para['ko'],rec['rawRecognition']['text']);words=[]
  for j,w in enumerate(rec['rawRecognition']['chunks']):
   x,y=w['timestamp'];assert x is not None and y is not None and 0<=x<y<=(entry['endSample']-entry['startSample'])/24000
   words.append(dict(unit=None,paragraph=para['id'],recognizedText=w['text'],start=entry['startSample']/24000+x,end=entry['startSample']/24000+y,source=dict(review=pin(rp),taskKey=rec['task']['key'],wordIndex=j,timestamp=[x,y])))
  cs=next(x['clauses']for x in caps['paragraphs']if x['id']==para['id']);assert ''.join(normp(w['recognizedText'])for w in words)==''.join(normp(x[0])for x in cs);bounds={0:0};at=0
  for i,w in enumerate(words):at+=len(normp(w['recognizedText']));bounds[at]=i+1
  at=0
  for i,(ko,en)in enumerate(cs):
   begin=at;at+=len(normp(ko));assert begin in bounds and at in bounds,('Clause splits actual ASR word',para['id'],ko);first,last=words[bounds[begin]],words[bounds[at]-1];cues.append(dict(paragraph=para['id'],clauseIndex=i,ko=ko,en=en,start=first['start'],spokenEnd=last['end'],startWord=first,endWord=last))
 for i,c in enumerate(cues):c['end']=cues[i+1]['start']if i+1<len(cues)else proof['canonical']['duration'];assert c['start']<c['spokenEnd']<=c['end']+.0001
 rows=[x for x in l['paragraphs']if x['kind']=='paragraph'];med=statistics.median(x['wholeTake']['bodyDbfs']for x in rows);rel=[dict(paragraph=x['paragraph'],relativeToMedianDb=x['wholeTake']['bodyDbfs']-med)for x in rows];assert all(x['relativeToMedianDb']>=-4 for x in rel),rel
 spec=importlib.util.spec_from_file_location('caption_fit_only',HERE/'shorts-layout-v3.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout);composer=layout.Composer(P.name)
 for c in cues:composer.captioned(composer.base('해설용 모형'),c['ko'])
 print(json.dumps(dict(project=P.name,paragraphsLiteralMatch=True,numericFlags=[],positiveWholeWordCues=len(cues),duration=proof['canonical']['duration'],isolatedContextDifferences=unit_discrepancies),ensure_ascii=False))
 if not a.record:return
 target=pp.parent/'technical-voice-review.json';write(target,dict(voice=pin(pp),sourceNarration=pin(np),sourceAsr=pin(rp),sourceLevels=pin(lp),rawUnitsByteExact=('master'not in vv),wholeSentenceMasterProof=(pin(pp.parent/'constant-gain-proof.json')if'master'in vv else None),sameApprovedReferenceAndModel=True,voiceBiometricIdentityMeasured=False,sustainedDeclineHolds=[],paragraphRelativeLevels=rel,isolatedContextDifferences=unit_discrepancies,contentReview='All full paragraphs recognize the exact revised source after spacing/punctuation, named technical spelling and explicitly scoped standard possessive-pronunciation equivalence. Caption edges use actual positive whole words from those independent unprompted paragraph recognitions. Original isolated discrepancies remain unchanged.',possessiveParticleNote=({'scope':'p001 actual whole word 모래에 versus written 모래의 only','basis':'National Institute of Korean Language permits possessive 의 pronounced 에. This does not permit lexical substitutions.','source':'https://www.korean.go.kr/front/mcfaq/mcfaqView.do?mcfaq_seq=5716'}if'journey'in P.name else None),reviewAdapter=pin(__file__),reviewV15Note={'whitespaceBeforeNamedTechnicalSpelling':True,'ReturnalP004PossessiveOnly':True,'primaryBasis':'https://www.korean.go.kr/front/mcfaq/mcfaqView.do?mcfaq_seq=5716','newLexicalAliases':False},additionalPossessivePronunciation=({'scope':'Spider-Man p004 written 면의 versus recognized 면에 only','basis':'Standard Korean allows possessive 의 pronounced 에; no lexical substitution is permitted.','source':'https://www.korean.go.kr/front/mcfaq/mcfaqView.do?mcfaq_seq=5716'}if'spiderman'in P.name else None),approvedForTechnicalDownstream=True,actualListening=False,humanApproval=False,finalFilmComplete=False));out=P/('production/caption-timing-'+cv+'.json');write(out,dict(voice=pin(pp),technicalVoiceReview=pin(target),clauses=pin(cp),cues=cues,audioOffsetSeconds=0,voiceSpeed=1,wordInterpolation=False,englishUsesSameMeaningClauseInterval=True,finalFilmComplete=False))
 def stamp(t):
  ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 selection=P/'production/accepted-voice-selection-v10.json';write(selection,dict(voice=pin(pp),technicalVoiceReview=pin(target),captionTiming=pin(out),narration=pin(np),asr=pin(rp),clauses=pin(cp),sourceMasterProcessing=('constant whole-utterance level matching'if'master'in vv else None),humanApproval=False))
 for lang in ['ko','en']:
  out=P/'production'/('captions-'+cv+'.'+lang+'.srt');assert not out.exists();out.write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c[lang]}'for i,c in enumerate(cues))+'\n','utf8')
if __name__=='__main__':main()
