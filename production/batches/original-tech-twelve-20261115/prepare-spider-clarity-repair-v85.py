"""Resolve the beam/rain homophone with a concrete test-line description."""
from pathlib import Path
import copy,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-spiderman-swing-anchor';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 old=P/'planning/narration-repair-v84.json';n=read(old);vp=M/'voice-repair-v84/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(M/'asr-repair-v84/status.json')['review']['path']);lp=rp.parent/'levels.json';assert not any(x['kind']=='unit'and x['trend']['suspect']for x in read(lp)['paragraphs'])
 uid=next(u['id']for u in n['units']if u['ko'].startswith('가는 기둥이 빛줄기'));units=[];new=[];reuse=[]
 for u,raw in zip(n['units'],v['rawChunks']):
  if u['id']==uid:x=dict(id='c85u001',paragraph=u['paragraph'],ko='검사 선 사이에 있는 가는 기둥은 놓칠 수 있죠.',originUnit=u['id']);new.append(x)
  else:x=dict(u,sourceRaw=raw);reuse.append(x)
  units.append(x)
 paragraphs=[dict(p,ko=' '.join(u['ko']for u in units if u['paragraph']==p['id']),unitIds=[u['id']for u in units if u['paragraph']==p['id']])for p in n['paragraphs']]
 n.update(origin=pin(old),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,reason='Unprompted ASR rendered 빛줄기 as the homophone 빗줄기. A new concrete test-line sentence removes that ambiguity without adopting a lexical alias or claiming a proven TTS pronunciation error.',voiceAcceptedForFilm=False)
 np=P/'planning/narration-repair-v85.json';save(np,n);c=read(P/'planning/caption-clauses-repair-v84.json');c['source']=pin(np)
 for p in c['paragraphs']:
  if p['id']=='p002':
   cs=p['clauses'];assert cs[-2][0]=='가는 기둥이 빛줄기 사이에 있으면';p['clauses']=cs[:-2]+[['검사 선 사이에 있는 가는 기둥은','A thin post between the test lines'],['놓칠 수 있죠.','can be missed.']]
 save(P/'planning/caption-clauses-repair-v85.json',c);sp=P/'script/narration.repair-v85.json';save(sp,dict(title=P.name,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
 t=copy.deepcopy(read(P/'production/tts-manifest-repair-v84.json'));t['revision']='unambiguous-ray-gap-example-v85';t['paths']['script']=str(sp.relative_to(ROOT)).replace('\\','/');t['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+P.name+'/voice-repair-v85',filenameStem='clarity-v85');save(P/'production/tts-manifest-repair-v85.json',t)
 print(json.dumps(dict(slug=P.name,newUnits=1,reused=len(reuse),modelStarted=False)))
if __name__=='__main__':main()
