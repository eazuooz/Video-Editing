"""Resolve the read/lose homophone with a clearer attack-state conclusion."""
from pathlib import Path
import copy,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-returnal-particle-tentacles';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 old=P/'planning/narration-repair-v84.json';n=read(old);vp=M/'voice-repair-v84/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(M/'asr-repair-v84/status.json')['review']['path']);lp=rp.parent/'levels.json';assert not any(x['kind']=='unit'and x['trend']['suspect']for x in read(lp)['paragraphs'])
 uid=next(u['id']for u in n['units']if u['ko'].startswith('생물 같은 움직임을 만들면서'));units=[];new=[];reuse=[]
 for u,raw in zip(n['units'],v['rawChunks']):
  if u['id']==uid:x=dict(id='c85u001',paragraph=u['paragraph'],ko='이런 움직임은 적의 공격 준비를 알아채는 데도 도움이 됩니다.',originUnit=u['id']);new.append(x)
  else:x=dict(u,sourceRaw=raw);reuse.append(x)
  units.append(x)
 paragraphs=[dict(p,ko=' '.join(u['ko']for u in units if u['paragraph']==p['id']),unitIds=[u['id']for u in units if u['paragraph']==p['id']])for p in n['paragraphs']]
 n.update(origin=pin(old),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,reason='Unprompted ASR rendered 읽게 as the homophone 잃게. Rephrase the same source-supported enemy-state benefit with 알아채다 rather than accepting a meaning-changing ASR alias or declaring a proven pronunciation failure.',voiceAcceptedForFilm=False)
 np=P/'planning/narration-repair-v85.json';save(np,n);c=read(P/'planning/caption-clauses-repair-v84.json');c['source']=pin(np)
 for p in c['paragraphs']:
  if p['id']=='p006':
   cs=p['clauses'];assert cs[-2][0]=='생물 같은 움직임을 만들면서';p['clauses']=cs[:-2]+[['이런 움직임은','This motion also helps players'],['적의 공격 준비를 알아채는 데도 도움이 됩니다.','notice an enemy preparing an attack.']]
 save(P/'planning/caption-clauses-repair-v85.json',c);sp=P/'script/narration.repair-v85.json';save(sp,dict(title=P.name,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
 t=copy.deepcopy(read(P/'production/tts-manifest-repair-v84.json'));t['revision']='unambiguous-enemy-state-conclusion-v85';t['paths']['script']=str(sp.relative_to(ROOT)).replace('\\','/');t['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+P.name+'/voice-repair-v85',filenameStem='clarity-v85');save(P/'production/tts-manifest-repair-v85.json',t)
 print(json.dumps(dict(slug=P.name,newUnits=1,reused=len(reuse),modelStarted=False)))
if __name__=='__main__':main()
