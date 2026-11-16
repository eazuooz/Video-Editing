"""Replace two ambiguous phrases; preserve all other generated utterances."""
from pathlib import Path
import copy,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
P=ROOT/'projects/shorts-journey-sand-sparkle';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 oldpath=P/'planning/narration-repair-v84.json';n=read(oldpath);vp=M/'voice-repair-v84/voice-generation-complete-proof.json';v=read(vp);status=read(M/'asr-repair-v84/status.json');rp=Path(status['review']['path']);lp=rp.parent/'levels.json';assert not any(x['kind']=='unit'and x['trend']['suspect']for x in read(lp)['paragraphs'])
 repl={'r0121':dict(id='c85u001',ko='반짝임이 움직임 속에서도 자연스럽게 보이도록 계산을 바꿨습니다.'),'c84u009':dict(id='c85u002',ko='작은 표면이 카메라를 얼마나 향하는지 살핀 겁니다.')}
 units=[];new=[];reuse=[]
 for u,raw in zip(n['units'],v['rawChunks']):
  if u['id']in repl:x=dict(repl[u['id']],paragraph=u['paragraph'],originUnit=u['id']);new.append(x)
  else:x=dict(u,sourceRaw=raw);reuse.append(x)
  units.append(x)
 paragraphs=[]
 for p in n['paragraphs']:
  us=[x for x in units if x['paragraph']==p['id']];paragraphs.append(dict(p,ko=' '.join(x['ko']for x in us),unitIds=[x['id']for x in us]))
 n.update(origin=pin(oldpath),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,reason='The independent paragraph recognized 개발지는 and inserted 의 in 작은 모래 면. Use two clearer original phrases rather than lexical ASR aliases. Raw unit trends passed; the paragraph-level join trend remains held for separate whole-utterance matching and new QA.',voiceAcceptedForFilm=False)
 np=P/'planning/narration-repair-v85.json';save(np,n)
 c=read(P/'planning/caption-clauses-repair-v84.json');c['source']=pin(np)
 for p in c['paragraphs']:
  if p['id']=='p004':
   p['clauses']=[['반짝임이 움직임 속에서도','The calculation was changed so the glints'],['자연스럽게 보이도록 계산을 바꿨습니다.','would remain natural in motion.'],['작은 표면이 카메라를','The team looked at how much'],['얼마나 향하는지 살핀 겁니다.','a small surface faces the camera.']]+p['clauses'][3:]
 save(P/'planning/caption-clauses-repair-v85.json',c)
 sp=P/'script/narration.repair-v85.json';save(sp,dict(title=P.name,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
 t=copy.deepcopy(read(P/'production/tts-manifest-repair-v84.json'));t['revision']='two-clear-phrases-v85';t['paths']['script']=str(sp.relative_to(ROOT)).replace('\\','/');t['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+P.name+'/voice-repair-v85',filenameStem='clarity-v85');save(P/'production/tts-manifest-repair-v85.json',t)
 s=(H/'run-selected-clarity-voice-v84.py').read_text('utf8').replace('v84','v85');start=s.index('SLUGS=');end=s.index('\n',start);s=s[:start]+"SLUGS=['shorts-journey-sand-sparkle']"+s[end:];target=H/'run-journey-clarity-voice-v85.py';assert not target.exists();compile(s,str(target),'exec');target.write_text(s,'utf8')
 print(json.dumps(dict(narration=pin(np),newUnits=2,reused=33,modelStarted=False)))
if __name__=='__main__':main()
