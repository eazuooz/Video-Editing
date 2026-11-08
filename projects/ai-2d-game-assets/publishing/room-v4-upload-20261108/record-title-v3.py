"""Synchronize the user-selected 10-tool title after actual Studio save/readback."""
from pathlib import Path
import json, importlib.util, sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;R=H.parents[3]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
ko='이 도트 게임, AI로 만들었습니다 | 2D 픽셀아트부터 웹게임 완성까지, 제작 도구 10종 전부 공개!'
en='I Made This Pixel Game with AI | 10 Tools: From 2D Pixel Art to a Finished Web Game'
assert len(ko)<=100 and len(en)<=100
now=datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
record={'revision':'title-v3','userRequest':'이 도트 게임, AI로 만들었습니다 | 픽셀아트 도구부터 웹게임 완성까지 / 필요한 2D 도트 찍는 개발도구 10종 전부 공개! 이런느낌으로 제목 수정해줘','at':now,'videoId':'e7hxBpIetq4','titles':{'ko':ko,'en':en},'toolCountBasis':{'actualOutputTools':['ChatGPT image generation','ComfyUI','2dimg2motion','sprite-gen','pixelfx','PixelOE','Agent Sprite Forge','Codixel','Pixelbolt'],'introducedAndAttemptedButInferenceIncomplete':['Sprite-Sheet-Diffusion'],'count':10,'notClaimed':'All10 tools are mandatory or all10 generated successful outputs for this game.','excludedFromCount':'Alternative-only tools, Unity engine, ILXL checkpoint and style LoRA'},'sourceChecks':['production/room-v4-video/full-narration.ko.txt','publishing/room-v4-upload-20261108/description.ko.txt'],'koSavedAndReopened':True,'enSavedAndReopened':True,'thumbnailChanged':False,'videoMasterChanged':False,'adSuitabilitySubmittedByAssistant':False,'proof':'projects/ai-2d-game-assets/production/local/room-v4-video/upload-proof/title-v3-saved.jpg'}
save(H/'packaging-v3.json',record)
for lang,text in record['titles'].items():(H/f'title.{lang}.txt').write_text(text+'\n','utf-8')
p=read(H/'upload-packet.json');p['title']=record['titles'];p['titleRevision']='title-v3';save(H/'upload-packet.json',p)
p=read(H/'youtube-upload.json');p.update(updatedAt=now,titleKo=ko,titleEn=en,titleRevision='title-v3',titleRecord=str(H/'packaging-v3.json'),browserIssue=None)
p['completedSettings']=[x for x in p['completedSettings'] if not x.startswith('english-title-description')]+['english-title-v3-saved-reopened-description-preserved']
p['unfinishedSettings']=[x for x in p['unfinishedSettings'] if x!='english-title-v2-sync'];save(H/'youtube-upload.json',p)
project=R/'projects/ai-2d-game-assets/project.json';p=read(project);p['titles']=record['titles'];save(project,p)
s=read(H/'commit-spec.json');control=read(R/'shared/publishing/video-production-control.json')['ai2dLatestGameVideo20261108'];control.update(currentTitle=ko,titleRevision='title-v3',updatedAt=now);s['control']=control
s['worklistUpdate']={'title':ko,'updatedAt':now}
names=['packaging-v3.json','record-title-v3.py','title.ko.txt','title.en.txt','upload-packet.json','youtube-upload.json']
s['ownedPaths']=[str((H/n).relative_to(R)).replace('\\','/') for n in names]+['projects/ai-2d-game-assets/project.json']
save(H/'title-v3-commit-spec.json',s)
print(json.dumps({'title':ko,'count':10,'english':en},ensure_ascii=False))
