"""Use one clearer recap sentence; keep the corrected history and20 raw takes."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/shorts-inside-temporal-antialiasing';MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def code(p,t):
 assert not p.exists(),p
 ast.parse(t);p.write_text(t,'utf8')
def main():
 np=P/'planning/narration-repair-v9.json';n=read(np);pp=MEDIA/P.name/'voice-repair-v9/voice-generation-complete-proof.json';v=read(pp);rp=Path(read(MEDIA/P.name/'asr-repair-v9/status.json')['review']['path']);lp=rp.parent/'levels.json';assert not read(lp)['flags'];units=[];reuse=[];new=[]
 for i,u in enumerate(n['units']):
  if u['id']=='s7out04':item=dict(id='s21recap01',paragraph='p006',ko='현재 화면과 맞는 정보만 골라 쓰는 겁니다.',originUnit=u['id']);new.append(item)
  else:
   raw=v['rawChunks'][i];assert pin(raw['path'])['sha256']==raw['sha256'];item=dict(u,sourceRaw=raw);reuse.append(item)
  units.append(item)
 assert len(new)==1 and len(reuse)==20
 paras=[]
 for para in n['paragraphs']:
  us=[u for u in units if u['paragraph']==para['id']];paras.append(dict(para,ko=' '.join(u['ko']for u in us),unitIds=[u['id']for u in us]))
 locked=P/'planning/narration-repair-v21.json';write(locked,dict(n,origin=pin(np),sourceVoice=pin(pp),sourceAsr=pin(rp),sourceLevels=pin(lp),units=units,reuseUnits=reuse,newUnits=new,paragraphs=paras,newEnglish={**n['newEnglish'],'s21recap01':'Choose only information that fits the current image.'},reason='Both independent V7 and V9 full-paragraph recognitions omit 지금 in the unchanged last take. Preserve that ambiguity and every old original; replace only this final sentence with clearer 현재 wording. All other20 raw WAV/PCM units, including the corrected V9 history sentence, remain byte exact.',voiceAcceptedForFilm=False))
 script=P/'script/narration.repair-v21.json';write(script,dict(title=P.name,scenes=[dict(id=new[0]['id'],title='p006',lines=[new[0]['ko']])]));mf=read(P/'production/tts-manifest-repair-v9.json');mf.update(revision='inside-one-clear-recap-v21');mf['paths']['script']=script.relative_to(ROOT).as_posix();mf['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/'+P.name+'/voice-repair-v21',filenameStem='targeted-voice-repair-v21');write(P/'production/tts-manifest-repair-v21.json',mf)
 cp=P/'planning/caption-clauses-repair-v9.json';caps=read(cp);caps['source']=pin(locked);caps['previousUntimedClauses']=pin(cp);next(x for x in caps['paragraphs']if x['id']=='p006')['clauses'][-1]=[new[0]['ko'],'Choose only information that fits the current image.'];cp=P/'planning/caption-clauses-repair-v21.json';write(cp,caps)
 plan=read(P/'planning/film-beats-v13.json');plan['semanticClauses']=pin(cp);planp=P/'planning/film-beats-v21.json';write(planp,plan);contracts=read(HERE/'source-ordered-film-contracts-v15.json');next(x for x in contracts['projects']if x['slug']==P.name)['plan']=pin(planp);write(HERE/'source-ordered-film-contracts-v21.json',contracts)
 for old in ['run-inside-voice-repair-v9-cooperative-v19.py','run-inside-voice-repair-asr-v9-cooperative-v19.py']:
  code(HERE/old.replace('v9-','v21-'),(HERE/old).read_text('utf8').replace('v9','v21'))
 t=(HERE/'review-corrected-voice-captions-v16.py').read_text('utf8').replace("('voice-repair-v9','asr-repair-v9','v9','v9')","('voice-repair-v21','asr-repair-v21','v21','v21')");code(HERE/'review-corrected-voice-captions-v21.py',t)
 t=(HERE/'bind-ready-film-inputs-v15.py').read_text('utf8').replace('source-ordered-film-contracts-v15.json','source-ordered-film-contracts-v21.json');code(HERE/'bind-ready-film-inputs-v21.py',t)
 t=(HERE/'review-lesson-mixed-audio-v16.py').read_text('utf8').replace('review-corrected-voice-captions-v16.py','review-corrected-voice-captions-v21.py').replace('mixed-peer-review-v13.json','mixed-peer-review-v21.json');code(HERE/'review-lesson-mixed-audio-v21.py',t)
 t=(HERE/'run-finite-cooperative-completion-v19.py').read_text('utf8');a=t.index('JOBS=');b=t.index('\ndef read(p):',a);t=t[:a]+"JOBS=[('shorts-inside-temporal-antialiasing','run-inside-voice-repair-v21-cooperative-v19.py','run-inside-voice-repair-asr-v21-cooperative-v19.py','voice-repair-v21','asr-repair-v21')]\n"+t[b:];t=t.replace('finite-cooperative-completion-v19','finite-inside-completion-v21').replace('review-corrected-voice-captions-v16.py','review-corrected-voice-captions-v21.py').replace('bind-ready-film-inputs-v15.py','bind-ready-film-inputs-v21.py');code(HERE/'run-finite-inside-completion-v21.py',t)
 write(HERE/'inside-recap-source-review-v21.json',dict(narration=pin(locked),clauses=pin(cp),newUnits=1,reusedUnits=20,primaryTeachingSequencePreserved=True,oldAsrAmbiguityPreserved=True,newVoiceGenerated=False))
 print('Prepared one clearer recap sentence; all20 other raw WAVs verified.')
if __name__=='__main__':main()
