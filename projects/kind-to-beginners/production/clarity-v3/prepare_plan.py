"""Isolated evidence/teaching plan. Measured edit frames are assigned after TTS."""
from pathlib import Path
import hashlib,json,subprocess,urllib.request
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'projects/kind-to-beginners';OUT=Path(__file__).resolve().parent;LOCAL=P/'production/local/clarity-v3'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
SPECS={
'01':[
 ('G','mk8',2,10,'카트가 코너를 지나','첫 코너 진입 → 방향 변화 → 다음 길을 계속 달림'),
 ('E','intent',None,8,'오늘은 처음 게임을 켠 친구가','숙련자는 결승, 첫 사용자는 첫 코너에 관심'),
 ('G','mk8',20,11,'함께 하는 목표를 맞추고','하나의 레이스 안에서 이동·회전·다음 길을 계속 확인'),
 ('E','goal',None,None,'초보자에게 친절하다는 건','차가 한 코너를 돌아 다음 갈림길 앞에 서고 선택을 돌려줌')],
'02':[
 ('G','mk8',40,9,'게임을 처음 해 보는 친구와','실제 레이스 코스/이동으로 규칙 소개; 친구 상황은 가정'),
 ('E','intent',None,8,'익숙한 사람은 출발하자마자','두 사람의 목표 칩: 순위 / 첫 코너'),
 ('G','mk8',60,9,'그런데 친구는 어느 버튼을 누르면','실제 카트 이동과 코너만 보여줌; 실제 녹화자의 숙련도 추정 금지'),
 ('E','intent',None,8,'친구에게는 카트가 벽을 따라','가상 차가 벽 앞에서 멈춤→방향 입력→회복'),
 ('G','mk8',75,10,'한쪽이 결승선에 도착했어도','현재 카트와 다음 코스 주목; 승패/마음의 실제 측정인 양 표시 금지'),
 ('E','intent',None,7,'한 사람은 실력을 겨루러 왔고','같은 출발선, 다른 목적 두 대조'),
 ('G','mk8',105,None,'친구가 앞으로 나아가는 것부터','다음 코너를 만나는 실제 이동으로 목표 확인 필요 연결')],
'03':[
 ('G','mk8',117,9,'친구가 제대로 겨뤄 보자고 했다면','실제 레이스 경쟁: 합의한 경우 전력 승부'),
 ('E','goal',None,8,'가볍게 처음 해 보는 자리라면','결승순위 표시 접기→첫 코너 하나를 선택'),
 ('G','mk8',155,10,'이번에는 순위보다 첫 코너를','한 코너의 진입·회전·이탈 확인'),
 ('E','goal',None,8,'방향 조작을 알려 준 뒤에는','왼쪽 입력 누름→차량이 실제 회전→입력 놓음'),
 ('G','mk8',180,9,'카트가 돌아가고, 코너를 지나','다음 길을 실제 주행하며 결과 확인'),
 ('E','goal',None,None,'다음 코너는 스스로 시도해','보조 안내 손을 내리고 두 갈래 중 차가 한 길을 택함')],
'04':[
 ('G','mk8',230,9,'게임을 켠 사람에게는','운전 중 코스/아이템/HUD를 필요한 순서로만 짚음'),
 ('E','onboarding',None,8,'첫 접촉부터 재미를 느끼기까지','세 입력 중 이동 하나만 켜서 실제 캐릭터 이동'),
 ('G','mk8',250,10,'여럿이 겨루는 게임에서도','카트가 움직이는 결과를 확인'),
 ('E','onboarding',None,8,'우선 하나를 해 볼 수 있게','가속 하나→차 전진→방향 입력 추가→코너 통과'),
 ('G','mk8',270,10,'마리오 카트 에이트 디럭스는','레이스의 카트·코너·아이템 표시는 용어와 동시에'),
 ('E','onboarding',None,None,'이 부담 중 일부를 선택해서','입력 세 개 중 가속 지속만 보조가 맡음')],
'05':[
 ('E','steering',None,10,'핸들 어시스트, 영어로','실제 공식 안테나 스틸 + 원리 시연, 외곽 진입→안쪽 보정'),
 ('E','acceleration',None,8,'오토 액셀러레이트는','누르던 버튼을 놓은 뒤에도 카트가 계속 이동'),
 ('G','mk8',290,12,'가속을 유지하는 손의 부담을','일반 실제 주행; 이 녹화의 보조 ON 상태는 주장하지 않음'),
 ('E','turbo',None,10,'이 게임에는 코너에서 차체를','드리프트 곡선→모은 힘 단계→미니 터보 출발'),
 ('G','mk8',310,None,'처음 들어오는 길을 넓히면서','일반 코너 통과로 귀환; 3단 부스트 실측 표기 없음')],
'06':[
 ('G','unpacking-launch',33,9,'언패킹은 이삿짐 상자에서','상자→물건 꺼내기→주방 수납 배치: 현재 출시 게임 화면'),
 ('E','placement',None,8,'우리가 이미 아는 정리 행동이','인식 가능한 컵/테이블: 고름→올림→놓음. 추상 큐브대신 도구'),
 ('G','unpacking-launch',64,7.2,'방금 놓은 물건을 다시 옮겨','침대 위 물건→집음→다른 수납 위치. 현재 물건 및 결과를 추적'),
 ('E','placement',None,8,'그래도 어디에 무엇을 놓을지는','책상 위 두 위치가 가능, 플레이어가 하나를 고르고 컵을 옮김'),
 ('G','unpacking-launch',71.2,4.2,'자기 취향과 판단이 남아','바로 앞 침실의 정리를 이어받음: 가방/마지막 옷을 정리하고 완성 표시를 확인. 사진 편집 UI/다른 방 전환은 제외'),
 ('E','placement',None,None,'그런데 옆 사람이 그 자리까지','두 자리에 선택 여지가 있다가 명령 화살표가 한곳을 강요→화살표 지움')],
'07':[
 ('G','hike-climbing',0,6,'옆에서 다음 버튼, 다음 길','직접 오르는 움직임'),
 ('E','choice',None,8,'플레이어가 직접 선택할 순간도','두 길 중 지시 화살표가 우측을 강요; 캐릭터 망설임'),
 ('G','hike-walk',1,9,'어 쇼트 하이크에서는','새의 걷기와 실제 섬 지형'),
 ('E','choice',None,6,'어디로 가 볼지 정하고','원하는 목적지 표식 고르기→직접 이동'),
 ('G','hike-glide',0,9,'이런 순간에 옆 사람이','선택한 장소를 향하는 활공 실제 결과'),
 ('E','choice',None,5,'다음 행동은 본인이 골라','길 안내가 사라지고 캐릭터가 고른 길로 전진'),
 ('G','hike-glide',11,None,'도움의 양만큼','활공 후 다음 장소 확인으로 물러남의 의미 연결')],
'08':[
 ('G','hike-glide',18,9,'처음 게임을 해 보겠다는','전편 선택의 결과를 이어받는 활공'),
 ('E','summary',None,8,'한 번 해 볼 마음이 생긴 순간을','차량/컵/갈림길 세 장면에서 각 작은 행동의 결과를 연결'),
 ('G','mk8',365,9,'함께 하는 목표를 맞추고','첫 시도부터 다음 길로 이어지는 실제 주행'),
 ('E','summary',None,7,'게임은 결국 즐기려고','목표 일치→하나 성공→자기 다음 행동'),
 ('G','mk8',385,None,'초보자에게 친절한 설계는','카트가 다음 코너를 이어 가며 본문 종료')]
}
def main():
 old=read(P/'planning/production-plan.json');bank=read(P/'planning/sources.json')['sources']
 sources=[s for s in bank if s['id'] in ['mk8','hike-climbing','hike-walk','hike-glide']]
 probe=read(LOCAL/'sources/unpacking-launch.probe.json');v=next(x for x in probe['streams']if x['codec_type']=='video')
 assert v['width']>=1920 and v['height']>=1080
 sources.append({'id':'unpacking-launch','creator':'Witch Beam','url':'https://www.youtube.com/watch?v=vPcoMltTVXE','sourceKind':'independent-gameplay','file':rel(LOCAL/'sources/unpacking-launch.mp4'),'sha256':sha(LOCAL/'sources/unpacking-launch.mp4'),'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'duration':float(probe['format']['duration']),'rightsBasis':'Official developer launch trailer distributed through official press kit for editorial coverage of the game. No third-party narration or finished teaching material. Use short game-screen passages with original-source credit in description; no standalone asset redistribution.','rightsEvidence':'https://unpackinggame.com/presskit/','nativeSourceSpeed':'Use1x downloaded source. Publisher trailer editing/timing is retained; do not call this a new raw capture.','audio':'Original linked trailer audio retained only beneath corresponding gameplay after direct audition and low constant gain/voice ducking. Contains promotional music; do not extract as standalone BGM. Listening and mix QA pending.','notUsed':['Award cards','end promotion','photo editor frames','2019 development footage','narrated third-party guide','official control explainer'],'inspection':[{'range':[33,42],'object':'Unpacked kitchen objects','before':'objects in carton','action':'cursor selects and puts objects on cupboard/fridge','result':'objects remain at chosen room positions','proof':rel(LOCAL/'inspection/placement-31-45.jpg')},{'range':[64,73],'object':'Clothes and other items lying on bed','before':'items on bed, placement outlines visible','action':'pick up items and move them to appropriate places','result':'bed becomes clear and completion icon appears','proof':rel(LOCAL/'inspection/relocation-63-76.jpg')}],'settingToggleObserved':False,'noClaimOfObservedButtonHold':True})
 save(OUT/'sources.json',{'schemaVersion':1,'slug':'kind-to-beginners','revision':'clarity-v3','sources':sources})
 assets=read(ROOT/'unity/VideoEditing/Assets/VideoScenes/design-25-30-unity-v2/asset-map.json')
 selected=[a for a in assets['assets']if a['key']in ['hero','heroAlt','car','table','chair','cup','tree']]
 rows=[]
 for sid,items in SPECS.items():
  for i,(kind,key,start,seconds,anchor,purpose)in enumerate(items):
   rows.append({'id':f'{sid}-{i+1:02d}','scene':sid,'kind':'independent-gameplay'if kind=='G'else'explanation','source':key if kind=='G'else None,'mode':key if kind=='E'else None,'sourceStart':start,'provisionalDurationSeconds':seconds,'speechAnchor':anchor,'visual':purpose,'hold':0,'timingState':'not-measured-until-new-voice-alignment','normalSpeed':True,'loop':False,'playbackSpeed':1,'captionProtectedRect':[150,892,1784,1060],'annotations':'Target-linked editorial guides, clear at every original camera/source cut; actual coordinates assigned after final timing.'})
 links=[('01','02','같은 레이스의 다른 기대','친구와 첫 레이스 가정으로 구체화'),('02','03','목적이 다르므로 먼저 확인','전력 승부도 합의했을 때 의미가 있음'),('03','04','내 조작이 작은 성공으로 연결됨','같은 성공을 게임 첫 경험에 내장하는 온보딩'),('04','05','동시에 많은 입력이 부담','가속 유지와 방향 보조를 각각 분리'),('05','06','배우려는 행동에 집중할 공간','보조 메뉴 없이도 단순한 정리 조작으로 진입 부담 낮추기'),('06','07','배치의 결정은 플레이어에게 남음','옆 사람이 모든 결정을 가져갈 때 발견이 줄어듦'),('07','08','조작 정보 뒤에는 스스로 고를 공간','처음 생긴 관심이 본인의 다음 시도로 이어지게 마무리')]
 plan={'schemaVersion':1,'slug':'kind-to-beginners','revision':'clarity-v3','status':'script-locked-native-timing-pending','authorization':'production/clarity-v3/authorization.json','preservedBaseline':{'projectManifestSha256AtStart':sha(P/'project.json'),'planningPlanSha256':sha(P/'planning/production-plan.json'),'v2ReviewStatusSha256':sha(P/'production/unity-visual-v2/review-status.json')},'reference':old['reference'],'coreClaimOrderPreserved':True,'referenceMediaInProduction':False,'sourceToScriptMap':[{'reference':'0:04–1:43','scenes':['01','02'],'retain':'Unseen/unknown other player intent; expert action can remove newcomer participation','substitution':'First kart race imagined friend situation, not the reference creator personal arcade story','added':'State race goal and visible steering success; do not infer real recorder emotions'},{'reference':'1:44–1:55','scenes':['03'],'retain':'Full effort is respectful if both participants want it','substitution':'Agree whether to race seriously or try a first corner','added':'Input→corner→next choice worked noncombat example'},{'reference':'1:56–2:15','scenes':['04','05','06'],'retain':'Games are for enjoyment; gently lower the first-contact burden in competitive and solo games','substitution':'MK8 assistance retained; SF6 Dynamic replaced by familiar Unpacking actions','added':'Precise assistance scope, drift prerequisite, one object placed and moved'},{'reference':'2:16–2:32','scenes':['07'],'retain':'Dragging the newcomer through every decision removes interest and freedom','substitution':'Retain A Short Hike independently recorded exploration','added':'Show instructions disappear before actor selects path'},{'reference':'2:35–2:46','scenes':['08'],'retain':'Initial interest is fragile; protect enjoyment and the next self-directed attempt','substitution':'Return to kart movement and selected path','added':'Conclude with same thesis rather than generic accessibility summary'}],'omittedNoninstructional':old.get('omittedNoninstructional',[]),'gameExamples':[{'title':'Mario Kart 8 Deluxe','genre':'kart racing','role':'Different first-session goals; first corner feedback; Smart Steering and Auto-Accelerate','nintendo':True,'ownership':'https://mariokart8.nintendo.com/','selectionReason':'Existing verified FHD race and officially documented specific assists; newer Mario Kart World is not substituted merely for recency. Same necessary mechanics and known constraints preserved.','necessaryRules':'Follow a course to finish; accelerate, steer, use items. Define drift then Mini-Turbo before third-stage constraint.','limits':'General race recording does not prove assistance state, novice skill, emotions or a measured assist force.'},{'title':'Unpacking','genre':'domestic organization puzzle','role':'Familiar action plus low physical input burden leaves personal placement choice','nintendo':False,'ownership':'https://www.unpackinggame.com/','selectionReason':'Cross-genre replacement of complex fighting inputs with a recognizable physical task and directly visible item placement; official no-hold/no-multiple-button/no-timer facts.','necessaryRules':'Take possessions from boxes and find a place in each new room; can pick an item up again and rearrange.','limits':'Removing input burden is not the same implementation as SF6 automatic attack selection. We retain the higher-level first-touch lesson, not a false one-to-one mechanics claim. Optional Allow items anywhere omitted as unnecessary; no imaginary settings screen.'},{'title':'A Short Hike','genre':'exploration adventure','role':'Self-selected path and discovery; know when to stop instructing','nintendo':False,'ownership':'https://ashorthike.com/press/','selectionReason':'Retain the approved independent developer B-roll that directly shows walking/climbing/gliding.','necessaryRules':'Move the bird, climb and glide toward visible places.','limits':'Our marked routes are editorial possibilities, not measured player attention or AI-generated paths.'}],'previousCompletedEpisodeComparison':{'slug':'start-with-climax','actualKnownExamples':['DOOM(2016): FPS action','Super Mario Galaxy2: platforming','Phoenix Wright Ace Attorney Trilogy: courtroom deduction'],'evidence':'projects/start-with-climax/planning/batch-v1-plan.json and shared/publishing/video-worklist.json D28 verified2026-10-29.','newGenres':['kart racing','organization puzzle','exploration']},'nintendo':{'numerator':1,'denominator':3,'fraction':1/3,'counting':'Distinct meaningfully taught games only; no Unity illustration, repeat cut or menu variant counted','rounding':'exact one third'},'sourceRecords':'sources.json','fhdMinimum':[1920,1080],'output':[1920,1080,60],'bodyRatio':{'actual':.6,'explanation':.4,'excludes':['branding2s','membership10s'],'rule':'Measured after speech alignment. Never loop, slow, use unrelated footage or shorten useful reasoning to hit quota. If no meaningful allocation satisfies it, escalate concrete mismatch to root.'},'script':{'ko':rel(P/'script/clarity-v3/narration.ko.json'),'en':rel(P/'script/clarity-v3/narration.en.json'),'spokenKo':rel(P/'script/clarity-v3/narration.spoken-ko.json'),'delta':'script-delta.json'},'chapterLinks':[{'from':a,'to':b,'inheritedResult':c,'nextNeed':d}for a,b,c,d in links],'glossary':[{'ko':'온보딩','en':'Onboarding','meaning':'첫 접촉부터 재미를 느끼기까지 낯선 조작과 규칙의 부담을 낮추는 과정'},{'ko':'핸들 어시스트','en':'Smart Steering','meaning':'코스를 벗어나려 할 때 방향 조절 보조'},{'ko':'오토 액셀러레이트','en':'Auto-Accelerate','meaning':'가속 버튼을 계속 누르지 않아도 가속 유지'},{'ko':'드리프트','en':'Drift','meaning':'코너에서 차체를 옆으로 미끄러뜨리는 조작'},{'ko':'미니 터보','en':'Mini-Turbo','meaning':'드리프트로 모은 힘을 놓으며 얻는 짧은 가속'},{'ko':'울트라 미니 터보','en':'Ultra Mini-Turbo','meaning':'드리프트 부스트의 세 번째 단계; Smart Steering ON일 때 사용 불가'}],'primaryFacts':[{'url':'https://www.nintendo.com/jp/ichikara/aabpa/index_en.html','claims':['Smart Steering/antenna','Auto-Accelerate','Ultra Mini-Turbo condition'],'seen':'2026-10-29'},{'url':'https://www.unpackinggame.com/','claims':['No click-drag, button holding or simultaneous presses required','No time limits or penalties for missteps','Optional Allow items anywhere (not narrated)'],'snapshot':rel(LOCAL/'research/unpacking-official.html'),'sha256':sha(LOCAL/'research/unpacking-official.html'),'seen':'2026-10-29'},{'url':'https://ashorthike.com/press/','claims':['Own pace and path','walk/climb/glide','developer B-roll distribution'],'seen':'2026-10-29'}],'unity':{'project':'unity/VideoEditing','version':'6000.6.0f1','pipeline':'URP17.6.0','stageClass':'D29ClarityStage','baseClass':'DesignClarityLessonStage','namespace':'Yamyam.DesignVisualV2','source':'production/clarity-v3/unity-source/D29ClarityStage.cs','installTarget':'Assets/VideoScenes/design-25-29-clarity-v3/D29ClarityStage.cs','savedScenePaths':[],'sceneSaveStatus':'pending-parent-capture; do not claim saved until files exist','assetRecords':selected,'reuse':'Shared prefabs and animations, no vendor originals changed','capture':[1920,1080,60],'illustration':'All self-authored scenes explicitly labeled explanatory demonstrations; no commercial measurements fabricated'},'cuts':rows,'quality':{'storyAndOrder':'preserved','noFightingExamples':True,'noCreatorFraming':True,'audio':'SampleB same own voice, continuous phrasing preferred, BGM preserved','ui':'Black, warm yellow headings, white body, meaningful teal/red/green; detailed imported objects, no decorative paragraphs','mobile':'Inspect final375px and1080p with actual captions','humanWholeReview':'pending','technicalReview':'not-rendered'},'delivery':'Local four outputs only, root handles shared ledger/Git. No upload without review of same SHA.'}
 save(OUT/'production-plan.json',plan)
 save(OUT/'storage-routing.json',{'slug':'kind-to-beginners','revision':'clarity-v3','logicalRoot':rel(LOCAL),'physicalRoot':str(LOCAL.resolve()).replace('\\','/')})
 save(OUT/'checkpoint.json',{'revision':'clarity-v3','status':'script-locked-plan-and-runtime-preparing','scriptReady':True,'newSourceDownloaded':True,'nativeRenderStarted':False,'ttsStarted':False,'parentOwnsCostlySlots':True,'lastUpdateKst':'2026-10-29','next':['Root SampleB continuous voice','Align ASR and lock source/visual cue frames','Parent native capture slot','Single-sequence composition and full QA','Local review delivery'],'preserved':'All batch-v1 and unity-visual-v2 media/metadata remain untouched.'})
 print('Wrote source records, exact asset provenance, lesson mapping and provisional speech-anchored cut plan.')
if __name__=='__main__':main()
