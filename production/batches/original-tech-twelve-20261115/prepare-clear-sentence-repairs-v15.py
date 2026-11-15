"""Replace two ambiguous sentences; retain every other approved-source WAV."""
from pathlib import Path
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CHANGES={
 'shorts-doom-push-forward-healing':('s6u0121','체력을 주는 규칙과 탄약을 주는 규칙은 별도로 설계합니다.','The rules for granting health and ammunition are designed separately.'),
 'shorts-botw-chemistry-rules':('s6u0031','움직임 계산과 불붙음 같은 상태 규칙은 구별됩니다.','Motion calculations and state rules such as ignition are distinct.')}
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def code(p,t):
 assert not p.exists(),p
 ast.parse(t);p.write_text(t,'utf8')
def main():
 review=[];contracts=read(HERE/'source-ordered-film-contracts-v13.json')
 for slug,(target,text,en)in CHANGES.items():
  P=ROOT/'projects'/slug;np=P/'planning/narration-repair-v6.json';n=read(np);pp=MEDIA/slug/'voice-repair-v6/voice-generation-complete-proof.json';proof=read(pp);rp=Path(read(MEDIA/slug/'asr-repair-v6/status.json')['review']['path']);lp=rp.parent/'levels.json';assert not read(lp)['flags'];oldunit=next(u for u in n['units']if u['id']==target)
  rawunit=next(x for x in read(rp)['results']if x['task']['key']=='unit-'+target);paragraph=next(x for x in read(rp)['results']if x['task']['key']=='paragraph-'+oldunit['paragraph']);units=[];new=[];reuse=[]
  for i,u in enumerate(n['units']):
   if u['id']==target:
    item=dict(id='s15'+target,paragraph=u['paragraph'],ko=text,originUnit=target);new.append(item)
   else:
    raw=proof['rawChunks'][i];assert pin(raw['path'])['sha256']==raw['sha256'];item=dict(u,sourceRaw=raw);reuse.append(item)
   units.append(item)
  paragraphs=[]
  for para in n['paragraphs']:
   selected=[u for u in units if u['paragraph']==para['id']];paragraphs.append(dict(para,ko=' '.join(u['ko']for u in selected),unitIds=[u['id']for u in selected]))
  locked=P/'planning/narration-repair-v15.json';d=dict(n,origin=pin(np),sourceVoice=pin(pp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,newEnglish={**n.get('newEnglish',{}),new[0]['id']:en},reason='A single utterance and its full paragraph share an unresolved ASR wording difference. Use clearer equivalent wording for this one sentence; preserve all other natural utterances byte for byte. No assertion that ASR alone proves a TTS error.',narrationLocked=True,approvedForTts=True,sourceOrderPreserved=True,humanApproval=False,voiceAcceptedForFilm=False)
  write(locked,d);script=P/'script/narration.repair-v15.json';write(script,dict(title=slug,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]));mf=read(P/'production/tts-manifest-repair-v6.json');mf.update(revision='one-clear-sentence-v15');mf['paths']['script']=script.relative_to(ROOT).as_posix();mf['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+slug+'/voice-repair-v15',filenameStem='targeted-voice-repair-v15');write(P/'production/tts-manifest-repair-v15.json',mf)
  oldcp=P/('planning/caption-clauses-source-ordered-v10.json'if'botw'in slug else'planning/caption-clauses-repair-v6.json');caps=read(oldcp);cp=P/'planning/caption-clauses-repair-v15.json';caps['source']=pin(locked);caps['previousUntimedClauses']=pin(oldcp);para=next(p for p in caps['paragraphs']if p['id']==oldunit['paragraph']);hits=[i for i,c in enumerate(para['clauses'])if c[0]==oldunit['ko']];assert len(hits)==1;para['clauses'][hits[0]]=[text,en];write(cp,caps)
  planp=P/'planning/film-beats-v10.json';plan=read(planp);assert plan['semanticClauses']==pin(oldcp);plan['semanticClauses']=pin(cp);newplan=P/'planning/film-beats-v15.json';write(newplan,plan);entry=next(c for c in contracts['projects']if c['slug']==slug);entry['plan']=pin(newplan)
  review.append(dict(slug=slug,narration=pin(locked),clauses=pin(cp),oneNewUnit=new[0],reusedUnits=len(reuse),previousRecognition=dict(unit=rawunit['rawRecognition']['text'],paragraph=paragraph['rawRecognition']['text']),primaryMeaningAndOrderPreserved=True,newVoiceGenerated=False))
 write(HERE/'clear-sentence-source-review-v15.json',dict(projects=review,guardAndThresholdUnchanged=True,originalWavsPreserved=True,actualListening=False,humanApproval=False));write(HERE/'source-ordered-film-contracts-v15.json',contracts)
 for src,dst in [('run-inside-voice-repair-v9.py','run-clear-sentence-voice-repair-v15.py'),('run-inside-voice-repair-asr-v9.py','run-clear-sentence-voice-repair-asr-v15.py')]:
  t=(HERE/src).read_text('utf8').replace('v9','v15').replace("SLUGS=['shorts-inside-temporal-antialiasing']",'SLUGS='+repr(list(CHANGES)));code(HERE/dst,t)
 t=(HERE/'review-corrected-voice-captions-v13.py').read_text('utf8');t=t.replace('def norm(s,slug,para):\n','def norm(s,slug,para):\n s=re.sub(r"\\s+","",s)\n');t=t.replace(" if slug=='shorts-spiderman-swing-anchor'", " if slug=='shorts-returnal-particle-tentacles'and para=='p004':s=s.replace('처음의','처음에')\n if slug=='shorts-spiderman-swing-anchor'",1)
 insertion="CONFIG.update({s:('voice-repair-v15','asr-repair-v15','v15','v15')for s in "+repr(list(CHANGES))+"});CONFIG['shorts-control-destruction-pipeline']=('voice-master-v14','asr-master-v14','v6','v14')\n"
 t=t.replace('\ndef read(p):','\n'+insertion+'\ndef read(p):',1);t=t.replace("cp=refined if refined.exists()else cp;cv='v10'if refined.exists()else cv","cp=refined if refined.exists()and nv!='v15'else cp;cv='v10'if refined.exists()and nv!='v15'else cv")
 t=t.replace("reviewAdapter=pin(__file__),", "reviewAdapter=pin(__file__),reviewV15Note={'whitespaceBeforeNamedTechnicalSpelling':True,'ReturnalP004PossessiveOnly':True,'primaryBasis':'https://www.korean.go.kr/front/mcfaq/mcfaqView.do?mcfaq_seq=5716','newLexicalAliases':False},")
 code(HERE/'review-corrected-voice-captions-v15.py',t)
 t=(HERE/'bind-ready-film-inputs-v13.py').read_text('utf8').replace('source-ordered-film-contracts-v13.json','source-ordered-film-contracts-v15.json');code(HERE/'bind-ready-film-inputs-v15.py',t)
 t=(HERE/'review-lesson-mixed-audio-v13.py').read_text('utf8').replace('review-corrected-voice-captions-v13.py','review-corrected-voice-captions-v15.py');code(HERE/'review-lesson-mixed-audio-v15.py',t)
 print(json.dumps(review,ensure_ascii=False))
if __name__=='__main__':main()
