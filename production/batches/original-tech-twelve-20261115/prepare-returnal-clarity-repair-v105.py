"""Short concrete comparisons replace three long additions, old approved PCM retained."""
from pathlib import Path
import copy,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-returnal-particle-tentacles';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 old=P/'planning/narration-repair-v85.json';n=read(old);vp=M/'voice-repair-v85/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(M/'asr-repair-v85/status.json')['review']['path']);lp=rp.parent/'levels.json';assert not any(x['kind']=='unit'and x['trend']['suspect']for x in read(lp)['paragraphs'])
 replacements={
 'c84u008':('c105u001','리본을 옆으로 돌려 보세요. 얇은 옆면만 보이죠.',['리본을 옆으로 돌려 보세요.','얇은 옆면만 보이죠.'],['Turn the ribbon sideways.','Only its thin edge is visible.']),
 'c84u009':('c105u002','원통은 어느 쪽에서 봐도 둥근 두께가 남습니다.',['원통은 어느 쪽에서 봐도','둥근 두께가 남습니다.'],['A cylinder keeps its round thickness','when viewed from different sides.']),
 'c84u011':('c105u003','이 방향을 부드럽게 이으면 빛의 변화도 자연스러워집니다.',['이 방향을 부드럽게 이으면','빛의 변화도 자연스러워집니다.'],['Smoothly connecting these orientations','also makes changes in lighting smoother.'])}
 units=[];new=[];reuse=[]
 for u,raw in zip(n['units'],v['rawChunks']):
  if u['id']in replacements:
   uid,text,_,_=replacements[u['id']];x=dict(id=uid,paragraph=u['paragraph'],ko=text,originUnit=u['id']);new.append(x)
  else:x=dict(u,sourceRaw=raw);reuse.append(x)
  units.append(x)
 paragraphs=[dict(p,ko=' '.join(u['ko']for u in units if u['paragraph']==p['id']),unitIds=[u['id']for u in units if u['paragraph']==p['id']])for p in n['paragraphs']]
 n.update(origin=pin(old),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,reason='User requests easier interleaved examples. Use a direct sideways-ribbon/cylinder comparison and a simpler lighting conclusion. The prior master has cross-utterance level holds under its safe peak cap; preserve it and all approved old PCM. New raw words and levels must be independently checked, with no internal DSP or relaxed thresholds.',voiceAcceptedForFilm=False)
 np=P/'planning/narration-repair-v105.json';save(np,n);c=read(P/'planning/caption-clauses-repair-v85.json');c['source']=pin(np)
 for para in c['paragraphs']:
  for oldid,(uid,text,ko,en)in replacements.items():
   oldunit=next(u for u in read(old)['units']if u['id']==oldid)
   if para['id']!=oldunit['paragraph']:continue
   cs=para['clauses'];joined='';start=None;end=None
   for i,(k,e)in enumerate(cs):
    if start is None and oldunit['ko'].startswith(k):start=i
    if start is not None:
     joined+=' '+k
     if ''.join(joined.split())==''.join(oldunit['ko'].split()):end=i+1;break
   assert start is not None and end is not None,(oldid,cs)
   para['clauses']=cs[:start]+[[k,e]for k,e in zip(ko,en)]+cs[end:]
 save(P/'planning/caption-clauses-repair-v105.json',c);sp=P/'script/narration.repair-v105.json';save(sp,dict(title=P.name,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
 t=copy.deepcopy(read(P/'production/tts-manifest-repair-v85.json'));t['revision']='concrete-ribbon-cylinder-lighting-v105';t['paths']['script']=str(sp.relative_to(ROOT)).replace('\\','/');t['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+P.name+'/voice-repair-v105',filenameStem='clarity-v105');save(P/'production/tts-manifest-repair-v105.json',t)
 print(json.dumps(dict(slug=P.name,newUnits=len(new),reused=len(reuse),modelStarted=False)))
if __name__=='__main__':main()
