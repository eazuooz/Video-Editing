"""Use simpler color-cell wording and a direct subject in the INSIDE opening."""
from pathlib import Path
import copy,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-inside-temporal-antialiasing';M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/P.name
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 old=P/'planning/narration-repair-v84.json';n=read(old);vp=M/'voice-repair-v84/voice-generation-complete-proof.json';v=read(vp);rp=Path(read(M/'asr-repair-v84/status.json')['review']['path']);lp=rp.parent/'levels.json';assert not any(x['kind']=='unit'and x['trend']['suspect']for x in read(lp)['paragraphs'])
 specs=[('화면을 확대하면',dict(id='c85u001',ko='화면은 작은 칸들이 모인 그림입니다. 각 칸에는 색 하나가 들어 있습니다.')),('개발진은 현재 화면에',dict(id='c85u002',ko='인사이드는 현재 화면에 과거 화면 정보를 더합니다.'))]
 repl={next(u['id']for u in n['units']if u['ko'].startswith(prefix)):row for prefix,row in specs};units=[];new=[];reuse=[]
 for u,raw in zip(n['units'],v['rawChunks']):
  if u['id']in repl:x=dict(repl[u['id']],paragraph=u['paragraph'],originUnit=u['id']);new.append(x)
  else:x=dict(u,sourceRaw=raw);reuse.append(x)
  units.append(x)
 paragraphs=[dict(p,ko=' '.join(u['ko']for u in units if u['paragraph']==p['id']),unitIds=[u['id']for u in units if u['paragraph']==p['id']])for p in n['paragraphs']]
 n.update(origin=pin(old),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,newUnits=new,reuseUnits=reuse,paragraphs=paragraphs,reason='Independent paragraph ASR confused 색 칸 with 세 칸 and 개발진은 with 개발지는. Use a simpler two-sentence color-cell definition and a direct INSIDE subject; retain every other utterance and all raw evidence.',voiceAcceptedForFilm=False)
 np=P/'planning/narration-repair-v85.json';save(np,n);c=read(P/'planning/caption-clauses-repair-v84.json');c['source']=pin(np)
 for p in c['paragraphs']:
  if p['id']=='p001':
   cs=p['clauses'];out=[];i=0
   while i<len(cs):
    ko,en=cs[i]
    if ko=='화면을 확대하면':
     assert cs[i+1][0]=='작은 색 칸들이 모여 있습니다.';out += [['화면은 작은 칸들이 모인 그림입니다.','An image consists of small cells.'],['각 칸에는 색 하나가 들어 있습니다.','Each cell contains one color.']];i+=2
    elif ko=='개발진은 현재 화면에':
     assert cs[i+1][0]=='이전 화면 정보를 더합니다.';out += [['인사이드는 현재 화면에','INSIDE adds information from earlier images'],['과거 화면 정보를 더합니다.','to its current image.']];i+=2
    else:out.append([ko,en]);i+=1
   p['clauses']=out
 save(P/'planning/caption-clauses-repair-v85.json',c);sp=P/'script/narration.repair-v85.json';save(sp,dict(title=P.name,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
 t=copy.deepcopy(read(P/'production/tts-manifest-repair-v84.json'));t['revision']='clear-opening-phrases-v85';t['paths']['script']=str(sp.relative_to(ROOT)).replace('\\','/');t['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+P.name+'/voice-repair-v85',filenameStem='clarity-v85');save(P/'production/tts-manifest-repair-v85.json',t)
 print(json.dumps(dict(slug=P.name,newUnits=2,reused=len(reuse),modelStarted=False)))
if __name__=='__main__':main()
