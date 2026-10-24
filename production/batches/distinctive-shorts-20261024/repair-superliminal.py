"""Preserve first voice; replace two paragraphs for terminology and observable footage."""
from pathlib import Path
import json,time,subprocess,hashlib,shutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;p=R/'projects/shorts-superliminal-perspective'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
slugs=read(B/'batch.json')['authorization']['slugs']
deadline=time.monotonic()+3600
while not all((R/'projects'/s/'production/local/audio-v1/voice/narration.wav').exists() for s in slugs):
 assert time.monotonic()<deadline,'Finite audio wait expired';time.sleep(10)
auth=read(R/'shared/publishing/video-production-control.json')['shortsBatchAuthorization'];assert auth['status']=='active'
old=p/'production/local/audio-v1';new=p/'production/local/audio-v2';assert not new.exists()
archive=old/'script-snapshot';archive.mkdir()
for name in ['narration.spoken.ko.json','narration.ko.txt','clauses.json']:shutil.copy2(p/'script'/name,archive/name)
replacements={4:[('이 기법의 이름은 강제 원근입니다.','This technique is called forced perspective.'),('화면에 보이는 크기를 이용한 착시죠.','It uses apparent size to create an illusion.'),('게임은 물체의 보이는 표면에 여러 광선을 쏴,','The game casts rays across the visible surface'),('벽과 부딪히지 않는 위치를 찾습니다.','to find a position that fits without collision.')],5:[('물체를 놓으면 바뀐 크기가 실제 공간에 남습니다.','Release the object, and its changed size remains.'),('거대해진 물건을 밟고,','Step onto the enlarged object'),('높은 출구로 올라갈 수 있죠.','to reach a high exit.')]}
doc=read(p/'script/narration.spoken.ko.json');clauses=read(p/'script/clauses.json')
for i,pairs in replacements.items():doc['scenes'][0]['lines'][i]=' '.join(k for k,e in pairs)
newclauses=[]
for i in range(7):
 if i in replacements:newclauses.extend({'id':f'p{i+1}-{j}','lineIndex':i,'spoken':ko,'ko':ko,'en':en} for j,(ko,en) in enumerate(replacements[i],1))
 else:newclauses.extend(c for c in clauses['clauses'] if c['lineIndex']==i)
clauses['clauses']=newclauses
save(p/'script/narration.spoken.ko.json',doc);save(p/'script/clauses.json',clauses);(p/'script/narration.ko.txt').write_text('\n\n'.join(doc['scenes'][0]['lines'])+'\n',encoding='utf8')
reuse={};(new/'voice/chunks').mkdir(parents=True)
for i,text in enumerate(doc['scenes'][0]['lines'],1):
 if i-1 in replacements:continue
 src=old/f'voice/chunks/main-{i:02}.wav';dest=new/'voice/chunks'/src.name;shutil.copy2(src,dest);reuse[dest.name]={'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'text':text}
save(new/'reuse-takes.json',reuse)
for f in (p/'production').glob('*.py'):f.write_text(f.read_text(encoding='utf8').replace('audio-v1','audio-v2'),encoding='utf8')
m=read(p/'production/tts-manifest.json');m['tts']['outputDir']=m['tts']['outputDir'].replace('audio-v1','audio-v2');save(p/'production/tts-manifest.json',m)
plan=read(p/'planning/production-plan.json');plan['narrationRevision']={'audio':'audio-v2','reason':'Clarify canonical term after uncertain first-pass ASR, and replace broad platform/narrow-passage line with the fully inspected enlargement-to-high-exit action at source79–84s. Preserve other five raw paragraphs unchanged.','firstVoicePreserved':True};save(p/'planning/production-plan.json',plan)
py=R/'qwen3-tts/.venv/Scripts/python.exe'
with (p/'production/local/voice-repair.log').open('w',encoding='utf8') as log:
 subprocess.run([str(py),'-X','utf8',str(p/'production/render-voice.py'),'--cpu'],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
print('SUPERLIMINAL_REPAIR_DONE',flush=True)
subprocess.run([str(py),'-X','utf8',str(p/'production/transcribe.py'),'voice'],cwd=R,check=True)
