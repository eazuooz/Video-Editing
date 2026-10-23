"""Create this explicitly selected Short's editable inputs, preserving other work."""
from pathlib import Path
import json,datetime,hashlib,shutil,re
R=Path(__file__).resolve().parents[3]; P=Path(__file__).resolve().parents[1]; S=P.name
REV='flow-map-v1'; now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
paragraphs=[
 [
 ('이 물결, 바위를 피해 돌아가죠.','These ripples bend around the rock.'),
 ('물을 전부 시뮬레이션한 걸까요?','Did we simulate all that water?'),
 ('이 장면은 물결 그림을 움직여 만든 겁니다.','Here, we move a ripple texture instead.')],
 [
 ('그냥 한쪽으로 밀면,','Slide it in just one direction,'),
 ('무늬가 바위도 그대로 통과합니다.','and the pattern runs straight through the rock.'),
 ('그래서 위치마다 움직일 방향을','So, at each position, we store a direction'),
 ('화살표로 따로 정해 두죠.','represented here by an arrow.')],
 [
 ('이 방향 지도가 플로 맵입니다.','That direction texture is a flow map.'),
 ('우리 지도는 빨강에 가로,','Our map stores horizontal motion in red'),
 ('초록에 세로 방향을 담아요.','and vertical motion in green.'),
 ('두 값이 절반이면 정지,','Both at one half means no motion.'),
 ('빨강만 최대로 올리면 오른쪽입니다.','Raise red to its maximum, and it points right.')],
 [
 ('셰이더는 이 값을 읽고,','The shader reads these values'),
 ('물결 그림을 가져올 위치를 조금씩 옮깁니다.','and shifts where it samples the ripple texture.'),
 ('바위 주변의 화살표를 휘게 그렸으니,','We bent the arrows around the rock,'),
 ('무늬도 갈라져 돌아가는 거죠.','so the pattern appears to flow around it.')],
 [
 ('그런데 계속 늘리면 무늬가 찌그러집니다.','But continuous distortion stretches the pattern.'),
 ('그래서 짧게 움직이고 되감되,','We use short motions, then reset them.'),
 ('엇갈린 두 무늬를 번갈아 섞어서','Blending two offset cycles'),
 ('되감는 순간을 감춰요.','hides the moment each one resets.')],
 [
 ('바위를 옮겨도 새 길이 저절로 생기진 않아요.','Moving the rock does not automatically make a new path.'),
 ('방향 지도도 바꿔 줘야 합니다.','We have to update the flow map too.'),
 ('물의 모든 움직임 대신,','Instead of solving all the motion of water,'),
 ('보이는 흐름을 설계한 겁니다.','we design the flow that you see.')]
]
for name in ['script','planning','sources','publishing','production/local/audio','production/local/final']: (P/name).mkdir(parents=True,exist_ok=True)
auth={'selectedOn':now,'userEvidence':'플로맵 좋다. 이걸로 제작해줘','selectedRevision':REV,'slug':S,'fullProductionAuthorized':True,'scope':'ONE flow-map technical Short through complete local review, four files and selective Git. No upload/publication/Drive/next video.','finalUserReviewRequired':True,'automaticNextVideo':False}
controlPath=R/'shared/publishing/video-production-control.json'; control=read(controlPath)
control['selectedShortVideo']=S;control['shortsDirectSelection']=auth;control['updatedAt']=now;save(controlPath,control)
project={'schemaVersion':2,'slug':S,'status':'production','currentRevision':REV,'titles':{'ko':'게임 속 강물은 어떻게 바위를 피해 흐를까? | 플로 맵','en':'How Game Water Flows Around Rocks | Flow Maps'},'authorization':auth,'format':{'type':'youtube-shorts','width':1080,'height':1920,'fps':60},'video':{'width':1080,'height':1920,'fps':60},'paths':{'script':f'projects/{S}/script/narration.ko.json','scriptEn':f'projects/{S}/script/narration.en.json','productionPlan':f'projects/{S}/planning/production-plan.json','sources':f'projects/{S}/sources/sources.json','voiceNarration':f'projects/{S}/production/local/audio/voice/flow-map.wav','videoClean':f'projects/{S}/production/local/final/clean.mp4','videoBurnedCaptions':f'projects/{S}/production/local/final/captioned.mp4','captionsKo':f'projects/{S}/production/local/audio/captions.ko.srt','captionsEn':f'projects/{S}/production/local/audio/captions.en.srt','audioMix':f'projects/{S}/production/local/audio/final-mix.m4a','publishingKo':f'projects/{S}/publishing/description.ko.txt','publishingEn':f'projects/{S}/publishing/description.en.txt'},'membershipOutro':{'enabled':False,'reason':'Shorts integrated branding'},'publishReady':False,'delivery':{'directory':f'output/{S}'}}
save(P/'project.json',project)
for lang in ['ko','en']:
 lines=[' '.join(c[0 if lang=='ko' else 1] for c in para) for para in paragraphs]
 save(P/f'script/narration.{lang}.json',{'title':project['titles'][lang],'scenes':[{'id':'01','title':'Flow Map','lines':lines}]})
 (P/f'script/narration.{lang}.txt').write_text('\n\n'.join(lines)+'\n',encoding='utf8')
clauses=[]
for i,para in enumerate(paragraphs):
 for j,(ko,en) in enumerate(para):
  row={'id':f'p{i+1}-{j+1}','lineIndex':i,'spoken':ko,'ko':ko,'en':en}
  for term,role in [('플로 맵','term'),('그대로 통과','problem'),('오른쪽','result'),('되감는 순간','problem'),('방향 지도','term')]:
   if term in ko: row['emphasis']={'text':term,'role':role}; break
  clauses.append(row)
save(P/'script/clauses.json',{'pronunciationAliases':{},'clauses':clauses})
raw=read(P/'script/narration.ko.json');save(P/'script/narration.spoken.ko.json',{**raw,'derivation':{'displayScriptSha256':hashlib.sha256((P/'script/narration.ko.json').read_bytes()).hexdigest(),'clausesSha256':hashlib.sha256((P/'script/clauses.json').read_bytes()).hexdigest(),'speechSpeed':1,'renderUnit':'concept-paragraph'}})
base=R/'projects/shorts-normal-map-illusion/production'
for name in ['assemble-paragraphs.py','transcribe.py','time-captions.py','finish-audio.py']:
 text=(base/name).read_text(encoding='utf8').replace('shorts-normal-map-illusion',S).replace('normal-map-v2-grid-rgb-deadcells',REV).replace('normal-map-v2','flow-map').replace('production/local/audio-v2','production/local/audio')
 (P/'production'/name).write_text(text,encoding='utf8')
text=(base/'audio_revision.py').read_text(encoding='utf8').replace('normal-map-v2-grid-rgb-deadcells',REV).replace('production/local/audio-v2','production/local/audio').replace('normal-map-v2.wav','flow-map.wav')
(P/'production/audio_revision.py').write_text(text,encoding='utf8')
manifest=read(base/'tts-manifest.json');manifest['slug']=S;manifest['revision']=REV;manifest['paths']['script']=f'projects/{S}/script/narration.spoken.ko.json';manifest['tts']['outputDir']=f'projects/{S}/production/local/audio/voice';manifest['tts']['filenameStem']='flow-map';manifest['tts']['gpuProfileReason']='Same approved model/reference/paragraphs; GPU talker, CPU codec to preserve live Unity memory. Validate one paragraph before continuing.';manifest['tts']['gpuMinimumFreeMiB']=4800
save(P/'production/tts-manifest.json',manifest)
plan={'schemaVersion':1,'slug':S,'revision':REV,'status':'ready-for-native-preview','authorization':auth,'centralQuestion':'게임 속 물결은 어떻게 장애물 주변에서 방향을 바꿔 보일까?','sourceReference':{'url':'https://cdn.fastly.steamstatic.com/apps/valve/2010/siggraph2010_vlachos_waterflow.pdf','kind':'research-reference-only','fullTextRead':True,'selectedScope':'Flow vector texture → short UV distortion → two phases → limits. Not a full reproduction of the lecture.','omissions':'Historical hardware budgets, 17% playtest statistic, Houdini authoring and advanced noise/debris variants are outside this single Short mechanism.'},'tools':{'Unity':'Actual custom flow-map shader, sampled linear RG texture, persistent editable river test bed and native frames','Motion Canvas':'Labels, RGB decode example, moving field guides, mascot and compositing'},'sceneSaveStatus':'pending','scenes':[{'id':str(i+1),'narrationParagraph':i,'renderer':'Unity + Motion Canvas','beforeActionResult':x,'sourceKind':'our-implementation','hold':0} for i,x in enumerate(['Flowing river around stationary rock; reveal texture-based effect','Uniform scrolling crosses obstacle; switch to authored field arrows','Show sampled RG texture, decode signed vector; neutral→right worked example','Same map drives water shader around rock; arrows track same map samples','One stretching phase versus two staggered reset phases','Move rock without changing map, then update map; visible correction'])],'continuity':'Same river, same rock and camera; gradually reveal field/map and return to rendered water. Two-layer problem inherits texture distortion from preceding explanation. Closing changes rock location and then map, explicitly proving the limit.','technicalLimits':['Illustrates artist-authored local UV distortion, not Navier–Stokes or particle advection','Arrow lattice shows representative sampled texels, not every pixel','RG=0.5 decodes to 0 with linear float data; 8-bit PNG neutral has quantization error','Map channels are a chosen UV convention; not material colour and not the same quantity as normal direction','Flows must be updated when obstacles change; no claim every game water uses this technique'],'screenShare':{'contract':'Technical Short focused on explicitly selected engine demonstration; ordinary longform60:40 not imposed','independentGameplay':0,'explanation':1,'reason':'No actual commercial-game claim requires a gameplay insert; available Portal2 source is720p and rejected. Our implemented effect is visibly labeled.'},'assetRecords':[{'kind':'self-authored','asset':'procedural irregular rock, river mesh, flow texture and ripple texture','reason':'One mathematically controlled obstacle and shader source are the teaching subject; imported rock library consulted but unverified terms and asset complexity unnecessary.'},{'kind':'owned-brand','path':'shared/assets/branding/cat-reactions-v1'},{'kind':'licensed-music','path':'shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.mp3','license':'CC BY4.0; description credit'}],'duplicateReview':'Local shorts-worklist checked: hitbox, zombie pacing, normal map. Flow maps move texture coordinates; normal maps change shading direction. Distinct central mechanism.','recommendedChoices':[{'choice':'~60–80seconds, one river test bed','reason':'Allows first-view understanding, signed RG worked example, hidden-reset comparison and honest limit at natural speech speed.'},{'choice':'Same approved Qwen voice with CPU codec/GPU talker','reason':'Live Unity retains GPU memory; do not close or pause foreign apps. Validate local finite offload and stop own job if insufficient.'}],'humanFinalReview':'pending','platformActionsAuthorized':False}
save(P/'planning/production-plan.json',plan)
(P/'planning/outline.md').write_text('# 게임 속 강물은 어떻게 바위를 피해 흐를까?\n\n'+ '\n\n'.join(f'## {i+1}. {s["beforeActionResult"]}\n\n'+raw['scenes'][0]['lines'][i] for i,s in enumerate(plan['scenes']))+'\n',encoding='utf8')
save(P/'production/checkpoint.json',{'slug':S,'revision':REV,'stage':'native-preview-and-voice-preparation','authorization':auth,'nextAction':'Validate actual shader preview and finite paragraph TTS; keep live Unity intact.','humanFinalReview':'pending','updatedAt':now})
save(P/'production/review-ledger.json',{'slug':S,'revision':REV,'checks':[{'id':'source-reading','status':'pass','scope':'Complete Valve2010 water-flow slide text; sources research-only'},{'id':'duplicate-review','status':'pass','scope':plan['duplicateReview']},{'id':'human-full-listening','status':'pending'}]})
save(P/'sources/sources.json',{'sources':[plan['sourceReference'],{'url':'https://store.steampowered.com/video_policy','kind':'policy-research','productionClips':False}],'assets':plan['assetRecords']})
(P/'.gitignore').write_text('production/local/\nproduction/__pycache__/\n',encoding='utf8')
wpath=R/'shared/publishing/shorts-worklist.json';w=read(wpath);w['updatedAt']=now;w['rows'].append({'slug':S,'title':project['titles']['ko'],'status':'production','authorization':auth,'production':'Unity flow-map test bed and Motion Canvas selected','review':'pending','youtube':'not-uploaded','drive':'not-requested'});save(wpath,w)
print('Created',S,'Hangul syllables',len(re.findall('[가-힣]',''.join(raw['scenes'][0]['lines']))))
if __name__=='__main__':pass
