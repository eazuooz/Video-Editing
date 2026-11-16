"""Make the Chemistry Engine definition and closing summary unambiguous."""
from pathlib import Path
import copy,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-botw-chemistry-rules';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 old=P/'planning/narration-repair-v84.json';n=read(old);vp=M/'voice-repair-v84/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(M/'asr-repair-v84/status.json')['review']['path']);lp=rp.parent/'levels.json';assert not any(x['kind']=='unit'and x['trend']['suspect']for x in read(lp)['paragraphs'])
 replacements={
 '불이 닿기 전과':[('c85u001','이 풀밭에 불이 붙는 과정을 보세요.')],
 '물리 엔진이 물체가':[('c85u002','물리 엔진은 물체의 움직임을 계산합니다.'),('c85u003','화학 엔진은 불이 붙거나 꺼지는 상태 변화를 다룹니다.')],
 '물리 엔진이 움직임을,':[('c85u004','정리하면 물리 엔진은 움직임, 화학 엔진은 상태 변화입니다.')]
 };ids={next(u['id']for u in n['units']if u['ko'].startswith(prefix)):spec for prefix,spec in replacements.items()};units=[];new=[];reuse=[]
 for u,raw in zip(n['units'],v['rawChunks']):
  if u['id']in ids:
   for uid,ko in ids[u['id']]:x=dict(id=uid,paragraph=u['paragraph'],ko=ko,originUnit=u['id']);units.append(x);new.append(x)
  else:x=dict(u,sourceRaw=raw);units.append(x);reuse.append(x)
 paragraphs=[dict(p,ko=' '.join(u['ko']for u in units if u['paragraph']==p['id']),unitIds=[u['id']for u in units if u['paragraph']==p['id']])for p in n['paragraphs']]
 n.update(origin=pin(old),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,reason='Independent ASR made 젖는 into 전능 and 맡습니다 into 맞습니다. Use two short plain engine definitions, a direct ignition example, and an explicit motion/state recap. No lexical alias or threshold relaxation.',voiceAcceptedForFilm=False)
 np=P/'planning/narration-repair-v85.json';save(np,n);c=read(P/'planning/caption-clauses-repair-v84.json');c['source']=pin(np)
 for para in c['paragraphs']:
  cs=para['clauses'];out=[];i=0
  while i<len(cs):
   ko,en=cs[i]
   if ko=='불이 닿기 전과 후의 풀밭을':
    assert cs[i+1][0]=='나란히 비교해 보세요.';out += [['이 풀밭에 불이 붙는 과정을 보세요.','Watch this patch of grass catch fire.']];i+=2
   elif ko=='물리 엔진이 물체가 어디로 움직이는지 계산한다면,':
    assert cs[i+1][0]=='화학 엔진은 불붙거나 젖는 관계를 다룹니다.';out += [['물리 엔진은 물체의 움직임을 계산합니다.','Physics calculates the motion of objects.'],['화학 엔진은 불이 붙거나 꺼지는','Chemistry handles state changes'],['상태 변화를 다룹니다.','such as fire starting or going out.']];i+=2
   elif ko=='물리 엔진이 움직임을,':
    assert cs[i+1][0]=='화학 엔진이 상태의 연결을 맡습니다.';out += [['정리하면 물리 엔진은 움직임,','In short, physics handles motion;'],['화학 엔진은 상태 변화입니다.','chemistry handles state changes.']];i+=2
   else:out.append([ko,en]);i+=1
  para['clauses']=out
 save(P/'planning/caption-clauses-repair-v85.json',c);sp=P/'script/narration.repair-v85.json';save(sp,dict(title=P.name,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
 t=copy.deepcopy(read(P/'production/tts-manifest-repair-v84.json'));t['revision']='plain-chemistry-engine-definition-v85';t['paths']['script']=str(sp.relative_to(ROOT)).replace('\\','/');t['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+P.name+'/voice-repair-v85',filenameStem='clarity-v85');save(P/'production/tts-manifest-repair-v85.json',t)
 print(json.dumps(dict(slug=P.name,newUnits=len(new),reused=len(reuse),modelStarted=False)))
if __name__=='__main__':main()
