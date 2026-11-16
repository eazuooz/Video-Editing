"""Make the chemistry definition unambiguous in independent recognition."""
from pathlib import Path
import copy,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-botw-chemistry-rules';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):
 if p.exists():assert read(p)==d;return
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 old=P/'planning/narration-repair-v85.json';n=read(old);vp=M/'voice-repair-v85/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(M/'asr-repair-v85/status.json')['review']['path']);lp=rp.parent/'levels.json';assert not any(x['kind']=='unit'and x['trend']['suspect']for x in read(lp)['paragraphs'])
 uid=next(u['id']for u in n['units']if u['ko']=='화학 엔진은 불이 붙거나 꺼지는 상태 변화를 다룹니다.');units=[];new=[];reuse=[]
 for u,raw in zip(n['units'],v['rawChunks']):
  if u['id']==uid:x=dict(id='c106u001',paragraph=u['paragraph'],ko='화학 엔진은 타는 상태와 불이 꺼진 상태를 다룹니다.',originUnit=u['id']);new.append(x)
  else:x=dict(u,sourceRaw=raw);reuse.append(x)
  units.append(x)
 paragraphs=[dict(p,ko=' '.join(u['ko']for u in units if u['paragraph']==p['id']),unitIds=[u['id']for u in units if u['paragraph']==p['id']])for p in n['paragraphs']]
 n.update(origin=pin(old),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,reason='Master paragraph ASR wrote 붓거나 for 붙거나 while isolated source recognition matched. This ambiguity does not prove a TTS error. Use a direct burning/extinguished-state definition rather than accepting a meaning-changing lexical alias. Preserve all other raw PCM.',voiceAcceptedForFilm=False)
 np=P/'planning/narration-repair-v106.json';save(np,n);c=read(P/'planning/caption-clauses-repair-v85.json');c['source']=pin(np)
 for para in c['paragraphs']:
  if para['id']=='p002':
   cs=para['clauses'];start=next(i for i,(k,e)in enumerate(cs)if k=='화학 엔진은 불이 붙거나 꺼지는');assert cs[start+1][0]=='상태 변화를 다룹니다.'
   para['clauses']=cs[:start]+[['화학 엔진은 타는 상태와','The chemistry engine handles burning'],['불이 꺼진 상태를 다룹니다.','and extinguished states.']]+cs[start+2:]
 save(P/'planning/caption-clauses-repair-v106.json',c);sp=P/'script/narration.repair-v106.json';save(sp,dict(title=P.name,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
 t=copy.deepcopy(read(P/'production/tts-manifest-repair-v85.json'));t['revision']='explicit-burning-extinguished-state-v106';t['paths']['script']=str(sp.relative_to(ROOT)).replace('\\','/');t['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+P.name+'/voice-repair-v106',filenameStem='clarity-v106');save(P/'production/tts-manifest-repair-v106.json',t)
 print(json.dumps(dict(slug=P.name,newUnits=len(new),reused=len(reuse),modelStarted=False)))
if __name__=='__main__':main()
