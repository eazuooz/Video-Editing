"""Record exactly completed CPU work; keep final video/audio QA pending."""
from pathlib import Path
import json,hashlib,subprocess,shutil
ROOT=Path(__file__).resolve().parents[3]
DATA={
'shorts-d2r-ultrawide-ai-range':{
 'file':'shorts-d2r-ultrawide-ai-range-preview-300-1792895603358.mp4',
 'description':'디아블로 II: 레저렉션의 2021년 기술 알파에서 초광각 화면과 몬스터 AI 반응 범위가 맞지 않았던 개발 사례입니다. 21:9에서 드러난 문제와 출시 당시 19:9로 제한한 이유를, 위치를 고정한 설명도로 보여 줍니다.',
 'en':'A 2021 Diablo II: Resurrected technical-alpha case: a wider view exposed enemies beyond their AI reaction range. An original diagram explains the 21:9 issue and the release-era 19:9 limit.',
 'candidates':['모니터를 넓혔더니 몬스터가 반격을 못 했다? | 디아블로2 개발 이야기','초광각 화면이 디아블로2의 전투를 바꾼 이유 | AI 반응 범위','디아2는 왜 화면 양옆을 가렸을까? | 2021년 개발 이야기'],
 'change':'Viewport widens with player/enemy fixed; the previously hidden target becomes visible.'},
'shorts-d2r-loot-grass-clearance':{
 'file':'shorts-d2r-loot-grass-clearance-preview-725-1792895575514.mp4',
 'description':'디아블로 II: 레저렉션 개발진은 입체적인 풀이 전리품을 가리는 문제를 해결해야 했습니다. 직접 개발자 인터뷰에 공개된 해결책과, 아이템 주변의 풀만 비켜 주는 식생 변위의 원리를 자체 2D 설명으로 살펴봅니다.',
 'en':'Physical grass could obscure loot in Diablo II: Resurrected. A direct developer interview describes moving grass out of the way. Our original 2D illustration explains the visibility principle without claiming the exact game shader.',
 'candidates':['아이템이 풀에 가려지자, 개발자는 풀을 비켜 줬다 | 디아블로2','디아2의 풀은 전리품을 위해 비켜 준다? | 게임 그래픽','그래픽을 좋아지게 했더니 아이템이 사라졌다? | 디아블로2 개발 이야기'],
 'change':'A fixed gem is initially obscured by foreground tufts; tips bend outward while roots stay fixed.'},
'shorts-d2-modular-sprite-equipment':{
 'file':'shorts-d2-modular-sprite-equipment-preview-709-1792895607912.mp4',
 'description':'2000년 원작 디아블로 II는 머리·몸통·다리·팔·무기·방패를 따로 렌더링했습니다. 개발 회고를 바탕으로, 부위별 그림을 조합해 장비 외형을 만드는 스프라이트 방식을 자체 캐릭터로 설명합니다.',
 'en':'The original 2000 Diablo II rendered the head, torso, legs, arms, weapon and shield separately. Based on the original development postmortem, an independently drawn character demonstrates modular sprite composition.',
 'candidates':['디아2는 갑옷을 갈아입을 때 그림 조각을 바꿨다? | 스프라이트의 비밀','디아블로2 캐릭터는 한 장의 그림이 아니었다?','갑옷마다 캐릭터를 다시 그리지 않는 방법 | 원작 디아블로2'],
 'change':'Separate components remain fixed while only the torso image changes armor color; parts later recombine.'}
}
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for slug,row in DATA.items():
 p=ROOT/'projects'/slug;out=p/'production/local/mechanism-preview';out.mkdir(exist_ok=True)
 preview=out/'silent-3s-v2.mp4';shutil.copy2(ROOT/'shared/output/motion-canvas'/row['file'],preview)
 subprocess.run(['ffmpeg','-v','error','-n','-i',str(preview),'-vf','select=eq(n\\,0)+eq(n\\,150),scale=375:667,tile=2x1','-frames:v','1',str(out/'mobile-before-after-v2.jpg')],check=True)
 sha=hashlib.sha256(preview.read_bytes()).hexdigest()
 save(out/'v2-scope.json',{'kind':'silent-three-second-mechanism-sample','path':str(preview),'sha256':sha,'nativeDimensions':[1080,1920],'fps':60,'frames':180,'mechanism':row['change'],'timing':'provisional; not PCM aligned','audio':False,'finalCaptions':False,'finalMaster':False})
 plan=read(p/'planning/production-plan.json')
 plan['visualReview']={'native1080':'selected frames directly inspected','mobile375':'selected sample contact sheets directly inspected; final captions absent','movingPlayback':'sampled3-second exported sequences only; no full playback claim','finalAudioCaptionReview':False}
 plan['previewArtifact']='production/local/mechanism-preview/silent-3s-v2.mp4'
 save(p/'planning/production-plan.json',plan)
 checkpoint=read(p/'production/checkpoint.json');checkpoint['preview']={'path':plan['previewArtifact'],'sha256':sha,'durationSeconds':3,'audio':False,'isFinal':False};checkpoint['nextCommands']=[f'python projects/shorts-d2r-ultrawide-ai-range/production/prepare-exact-visuals.py '+{'shorts-d2r-ultrawide-ai-range':'ultrawide','shorts-d2r-loot-grass-clearance':'grass','shorts-d2-modular-sprite-equipment':'sprites'}[slug],'Coordinate full renderer and parent finish-audio/finish-video after real voice, ASR and captions exist.'];save(p/'production/checkpoint.json',checkpoint)
 meta=read(p/'publishing/metadata-draft.json');source=read(p/'sources/selected-footage.json')['sources'][0]['source']['sourceUrl'];primary=plan['primarySource']['url']
 meta.update(descriptionKo=row['description']+'\n\n#디아블로2 #게임개발 #게임그래픽 #쇼츠\n\n자료\n'+primary+'\n게임 화면: Blizzard Entertainment 공식 게임플레이 자료\n'+source,descriptionEn=row['en']+'\n\n#Diablo2 #GameDevelopment #Shorts\n\nSources\n'+primary+'\nGameplay: Blizzard Entertainment\n'+source,titleCandidates=row['candidates'],titleChoiceReason='Lead with the visible surprising result, then identify the actual game/technical topic. The selected title is supported by the scoped primary-source claim.',status='title-and-description-ready; final music credit and human review pending')
 save(p/'publishing/metadata-draft.json',meta)
 print(json.dumps({'slug':slug,'preview':str(preview),'sha256':sha}))
