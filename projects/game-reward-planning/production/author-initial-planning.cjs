const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.dirname(__dirname);process.chdir(root);
const write=(f,v)=>fs.writeFileSync(path.join(base,f),JSON.stringify(v,null,2)+'\n');
const proof='production/batches/sakurai-planning-game-design/proof-game-reward-planning';
const bankFile=proof+'/source-research/action-bank-planning-v1.json';
const bank=JSON.parse(fs.readFileSync(bankFile,'utf8'));
if(!bank.sourceIntervalsApproved)throw Error('Inspect actual actions first.');
const m=JSON.parse(fs.readFileSync(path.join(base,'project.json'),'utf8'));
if(m.status!=='planning')throw Error('Preserve a progressed project.');
const previous=JSON.parse(fs.readFileSync('projects/hierarchical-game-outlines/project.json','utf8'));
m.status='independent-script-and-action-planning';m.tts={...previous.tts,outputDir:'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v1',filenameStem:'game-reward-planning-qwen3-1.7b-balanced-v1'};
m.audio.backgroundMusic=previous.audio.backgroundMusic;m.audio.mixStatus='approved-existing-voice-and-Nimbus-awaiting-measured-production';m.audio.sourceAudioPolicy='All original game-source audio is preserved locally and excluded from the final mix. The approved Nimbus is continuous.';
m.paths.scriptEn='projects/game-reward-planning/script/narration.en.json';m.paths.footageCuts='projects/game-reward-planning/sources/action-map.json';
m.membershipOutro={...m.membershipOutro,kind:'original-screenshot-rows',title:'멤버쉽가입 감사드립니다.',identityReview:'pending-original-rows-render-review',appliedToFinal:false};
m.editing.exampleSeconds=0;m.editing.timingStatus='awaiting-measured-speech-and-supplementary-action-review';
m.editing.openingOverview={required:true,scene:'01',afterBrandingSeconds:2,plannedSeconds:[20,30],classification:'explanation',languages:['ko','en'],question:'보상을 많이 넣기 전에 무엇을 정해야 성장 구조가 흔들리지 않을까?',outcome:'보상 한 줄에 기능·조건·필요한 제작 작업을 함께 적기',orderedSteps:['Wizard 탄약의 행동 역할과 연구/제작 조건','강화와 조합의 제한을 정하는 질문','Cult 목장/꾸미기 및 배치 사례에서 범위와 제작 작업 나누기'],firstCaseBridge:'적을 얼리는 탄약과 길을 만드는 탄약 비교',reviewedBeforeTts:false,measuredSeconds:null};
m.editing.exampleInterleaving.reviewStatus='native-source-bank-approved-for-independent-planning; supplementary-source-and-script-review-pending';
m.approvals={production:'User authorized the full private batch and per-video Git. Reuse the already approved voice and Nimbus; thumbnail caps are a nonblocking follow-up.',humanWholeListening:'pending',finalPublicRights:'pending',originalNimbusBytes:'pending',truncatedMemberHandles:'pending',externalBackup:'pending'};m.publishReady=false;
write('project.json',m);
const scenes=[
 ['01','많은 보상보다 먼저 정할 것','What to decide before adding rewards','explanation',[
 '보상을 많이 넣기 전에, 무엇을 먼저 정해야 성장 구조가 흔들리지 않을까요?',
 '위저드 위드 어 건의 탄약과 연구로 기능과 조건, 강화의 한계를 나눈 다음, 컬트 오브 더 램의 목장 행동에서 제작 범위를 살펴보겠습니다.',
 '보고 나면 보상 한 줄에 기능, 조건, 필요한 작업을 함께 적을 수 있을 겁니다.',
 '먼저 적을 얼리는 탄약과 길을 만드는 탄약을 비교해 보죠.'
 ],[
 'Before adding lots of rewards, what should we decide to keep progression coherent?',
 'We will use the ammunition and research in Wizard with a Gun to separate functions, conditions and limits on power, then examine production scope through ranching actions in Cult of the Lamb.',
 'By the end, you will be able to record a reward\'s function, conditions and required work together in one catalogue row.',
 'Let us begin with ammunition that freezes enemies and ammunition that creates a path.'
 ]],
 ['02','실제 행동 · 얼리기와 길 만들기','Actions · freezing and making a path','actual',[
 '위저드 위드 어 건의 공식 시연입니다. 발사 뒤 적이 얼어붙고, 다른 전투 컷에서는 얼음이 깨지는 모습을 보세요.',
 '이어서 캐릭터가 빈틈 위에 생긴 땅을 이용해 건너갑니다. 공격 수치만이 아니라 이동할 방법이 달라진 거죠.',
 '탄약 선택 화면에는 살아 있는 대상의 회복과 언데드 공격을 구분한 설명도 있습니다.',
 '서로 다른 편집 컷이라 위력을 숫자로 비교할 수는 없습니다. 여기서는 각 탄약이 어떤 행동을 바꾸는지 구별해 봅시다.'
 ],[
 'This is an official Wizard with a Gun demonstration. Watch an enemy freeze after a shot, then ice shatter in a separate combat cut.',
 'Next, the character crosses a gap using created ground. The change concerns a way to move, beyond a damage number.',
 'The ammunition selection also describes healing living targets and attacking undead targets differently.',
 'These are separately edited shots, so they cannot establish a numerical power comparison. We are distinguishing the actions each ammunition type changes.'
 ]],
 ['03','기능부터 나누는 보상 목록','A catalogue organized by function','explanation',[
 '첫 목록에는 아이템 이름보다, 얻은 뒤 달라지는 행동을 먼저 적어 보세요.',
 '더 강해지는 보상, 새 선택을 여는 보상, 표현하거나 모으는 보상을 나누면 빠진 역할이 보입니다.',
 '아직 없는 장식이나 기념품을 적었다면 그것은 우리 기획의 후보입니다. 실제 게임에 있다고 단정하지 말고, 왜 필요한지부터 확인하세요.'
 ],[
 'In the initial catalogue, record the action that changes after acquisition before naming the item.',
 'Separate power increases, new options, and rewards for expression or collecting. This reveals missing roles.',
 'A proposed decoration or keepsake is a candidate in our own design, not a claim that it exists in the shown game. First establish why it is needed.'
 ]],
 ['04','실제 행동 · 재료와 연구와 제작','Actions · materials, research and crafting','actual',[
 '이번 시연은 적 주변에서 재료를 줍는 장면과, 연구대에서 가지를 선택하는 장면을 따로 보여 줍니다.',
 '이어서 용광로의 투입 재료와 결과, 탄약 제작에 필요한 항목을 확인할 수 있습니다.',
 '회복 물약 화면도 약한 물약에서 다음 항목으로 선택이 바뀝니다. 그런데 완료 표시와 함께 재료가 부족하다는 문구가 남아 있죠.',
 '이 홍보 편집을 정상적인 결제나 획득 과정의 증거로 삼을 수는 없습니다. 연구, 제작, 실제 사용을 따로 기록해야 한다는 관찰로 연결해 봅시다.'
 ],[
 'The demonstration separately shows picking up materials near enemies and selecting branches at a research station.',
 'It then shows furnace inputs and outputs, and the listed requirements for crafting ammunition.',
 'The potion interface changes selection from the weaker potion to the next entry. Yet a missing-ingredients message remains alongside a completed state.',
 'This promotional edit cannot prove a normal payment or acquisition process. Use the observation to record research, crafting and actual use as separate steps.'
 ]],
 ['05','획득 조건은 한 줄씩 연결하기','Connect acquisition conditions explicitly','explanation',[
 '보상 목록에는 언제 얻는지, 무엇이 먼저 필요한지, 사용하려면 다시 무엇을 만드는지 함께 적습니다.',
 '설계할 때는 앞 단계가 없어도 다음 항목을 얻는 경로가 있는지, 필요한 재료를 그 시점에 구할 수 있는지 확인하세요.',
 '영상에서 확인하지 못한 획득 조건은 미확인으로 남깁니다. 그 빈칸을 가정으로 메우는 대신, 우리 게임에서 결정할 질문으로 바꾸는 겁니다.'
 ],[
 'For each reward, record when it becomes available, what must precede it, and what must still be crafted before use.',
 'Check whether another route can bypass the previous step, and whether the required materials are available at that point.',
 'Leave acquisition conditions not established by the footage unverified. Turn the gap into a question for our own design instead of filling it with assumptions.'
 ]],
 ['06','실제 행동 · 효과가 함께 일어날 때','Actions · effects occurring together','actual',[
 '물과 전기 효과가 이어지는 전투, 얼음 관련 재료를 줍는 장면, 번개 연구 항목을 선택하는 장면입니다.',
 '다음 컷에서는 여러 효과와 여러 플레이어의 공격이 같은 공간에 겹칩니다. 한 기능을 추가해도 확인할 상황은 하나로 끝나지 않죠.',
 '회복을 주는 탄약처럼 대상에 따라 역할이 바뀌는 항목도 있으니, 피해량 하나만으로 목록을 정렬하기는 어렵습니다.',
 '이 화면으로 밸런스가 나쁘다고 판단하는 것은 아닙니다. 어떤 조합과 대상을 검토할지, 우리 기획의 질문을 뽑아 보는 겁니다.'
 ],[
 'These shots show water and electrical combat effects, collecting an ice-related material, and selecting a lightning research entry.',
 'In the next cuts, several effects and several players\' attacks overlap in one space. One added function can require more than one test situation.',
 'Some ammunition changes role depending on its target, as with healing, so a single damage ranking is insufficient for the catalogue.',
 'The footage does not establish poor balance. We are extracting questions about combinations and targets for our own design.'
 ]],
 ['07','강화의 끝과 허용할 조합','Limits on power and combinations','explanation',[
 '성장이 핵심이라면 강해지는 폭을 계획하고, 대등한 경쟁이 핵심이라면 누적 강화가 그 목표를 깨지 않는지 검토합니다.',
 '지금 본 협동 게임이 대전 게임이라는 뜻은 아닙니다. 장르와 목표에 맞춰 상한, 동시 사용, 교체 조건을 정하자는 설계 제안입니다.',
 '새 보상 한 개를 적을 때는 기존 항목과 함께 쓸 상황도 적어 두세요. 수치 조정으로 해결할지, 선택의 교환으로 남길지 결정하기 쉬워집니다.'
 ],[
 'If growth is central, plan the range of power increases. If equal competition is central, examine whether accumulated upgrades undermine that goal.',
 'The cooperative game we just saw is not being presented as a competitive game. This is a proposal to set caps, simultaneous-use rules and replacement conditions for the intended experience.',
 'For each new reward, list situations where it combines with existing entries. Then decide whether to adjust numbers or preserve a trade-off between choices.'
 ]],
 ['08','실제 행동 · 목장 안의 여러 역할','Actions · different roles in the ranch','actual',[
 '컬트 오브 더 램의 목장 시연으로 바꿔 보죠. 동물을 쓰다듬는 장면, 우유를 얻는 동작, 먹이 메뉴를 고르는 장면이 이어집니다.',
 '다른 컷에서는 동물을 탄 캐릭터가 움직이고 내립니다. 여기서 보이는 것은 상호작용과 생산, 이동의 서로 다른 역할입니다.',
 '동물마다 어떤 조건으로 열리는지, 능력치가 같은지까지 이 짧은 시연이 알려 주지는 않습니다.',
 '그러니 전투 강화와 별개의 역할을 기록하되, 동물 전체를 순수한 외형 보상이라고 부르지는 맙시다.'
 ],[
 'Now turn to the Cult of the Lamb ranching demonstration. Separate shots show petting an animal, a milking action, and selecting a feeding option.',
 'Other shots show a mounted character moving and dismounting. The visible roles concern interaction, production and movement.',
 'This short demonstration does not establish each animal\'s unlock conditions or equal statistics.',
 'Record roles beyond combat power, while avoiding a claim that all these animals are purely cosmetic rewards.'
 ]],
 ['09','수치 밖의 보상도 목적이 필요하다','Rewards beyond numbers need a purpose','explanation',[
 '꾸미기, 기록, 수집을 보상 후보에 넣을 수도 있습니다. 다만 많다는 이유만으로 필요한 보상이 되는 것은 아닙니다.',
 '개성을 표현하게 할지, 플레이의 기억을 남기게 할지, 새로운 생산이나 이동을 열지 목적을 나누어 보세요.',
 '겉모양이 다른 두 항목도 기능이 다를 수 있습니다. 외형과 기능을 별도 칸에 적으면, 순수한 꾸미기와 능력 확장을 혼동하지 않게 됩니다.'
 ],[
 'Customization, records and collectibles can be reward candidates. Quantity alone does not make them necessary.',
 'Separate purposes such as expression, commemorating play, and enabling new production or movement.',
 'Two visually different entries may also differ functionally. Separate appearance from function to avoid confusing pure customization with added capabilities.'
 ]],
 ['10','실제 행동 · 배치와 서로 다른 효과','Actions · placement and distinct effects','actual',[
 '다시 위저드 위드 어 건을 보면 바닥 칸을 추가하고, 서로 다른 작업대와 물건을 배치하는 동작이 보입니다.',
 '배치된 모습을 지나 전투로 가면, 얼음과 불, 전기 효과가 다른 동작과 겹칩니다.',
 '플레이어가 쓰는 재료 비용은 게임 안의 조건이고, 이런 모습과 동작을 만드는 일은 개발 쪽의 작업입니다.',
 '개발사의 실제 예산이나 코드를 아는 것은 아닙니다. 보이는 차이를 토대로, 우리 항목에 필요한 이미지와 동작, 확인할 조합을 생각해 봅시다.'
 ],[
 'Back in Wizard with a Gun, watch floor cells being added and distinct workstations and objects being placed.',
 'After the placement shots, combat shows ice, fire and electrical effects overlapping different actions.',
 'Player material costs are conditions inside the game. Creating those appearances and behaviors is development work.',
 'We do not know the developer\'s actual budget or code. Use the visible differences to consider the images, behaviors and combinations our own entries require.'
 ]],
 ['11','게임 속 비용과 제작 비용을 나누기','Separate player costs from production work','explanation',[
 '보상 한 줄 옆에 아이콘, 모델이나 그림, 동작, 효과, 화면 안내, 검수할 상황을 붙여 보세요.',
 '기존 자료를 쓸 수 있는 항목과 새로 만들어야 하는 항목을 구분하면, 목록이 작업 범위로 바뀝니다.',
 '이 표는 우리의 계획 도구입니다. 비용을 숫자로 단정하기보다 담당 작업과 빠진 조건을 먼저 적고, 감당할 수 있는 묶음부터 제작하세요.'
 ],[
 'Next to each catalogue row, list icons, models or drawings, animation, effects, interface guidance and test situations.',
 'Distinguishing reusable assets from new work turns the catalogue into a production scope.',
 'This table is our planning tool. Record responsibilities and missing conditions before inventing precise costs, then produce manageable groups of entries.'
 ]],
 ['12','실제 행동 · 후보를 다시 점검하기','Actions · reviewing the candidates','actual',[
 '서로 다른 전투 컷을 보면서, 효과가 나타날 대상과 주변 환경을 하나씩 골라 보세요.',
 '새 탄약이 어떤 적과 지형에서 쓰일지, 재료를 얻고 돌아오는 흐름과 어디에서 연결할지 질문할 수 있습니다.',
 '협동 장면에서는 다른 플레이어의 행동이 함께 일어납니다. 보상 하나의 검수 목록도 혼자 쓰는 상황과 함께 쓰는 상황으로 나눌 수 있죠.',
 '이것은 화면에서 확정되지 않은 규칙을 추측하는 일이 아닙니다. 실제로 보인 행동을 우리 보상 목록의 확인 질문으로 바꾸는 과정입니다.'
 ],[
 'Across these distinct combat shots, pick a target and surrounding environment in which an effect appears.',
 'Ask which enemies and terrain a new ammunition type should address, and where it connects to collecting materials and returning.',
 'The cooperative shot includes other players\' actions. A reward\'s checklist can distinguish solo use from use alongside others.',
 'We are not guessing rules the footage fails to establish. We are turning observed actions into review questions for our own catalogue.'
 ]],
 ['13','한 줄을 완성한 뒤 목록을 늘리기','Complete one row before expanding the catalogue','explanation',[
 '보상 하나를 골라, 바뀌는 행동과 획득 조건, 제한할 조합, 필요한 제작 작업을 한 줄로 연결해 보세요.',
 '빈칸이 많다면 아이템 수를 늘리기 전에 그 조건부터 결정합니다. 같은 역할만 반복된다면 다른 목적의 후보를 검토하고요.',
 '좋은 출발점은 긴 아이템 목록보다 설명할 수 있는 보상 한 줄입니다. 그 한 줄을 실제 플레이와 제작 범위 양쪽에서 확인해 보세요.'
 ],[
 'Pick one reward and connect its changed action, acquisition conditions, constrained combinations and required production work in one row.',
 'If many fields are empty, decide those conditions before adding more items. If one role repeats, consider candidates serving another purpose.',
 'A useful starting point is one explainable reward row. Check that row against both actual play and the work needed to produce it.'
 ]]
 ];
const allocations={
 '02':['ammo-01','ammo-06','ammo-11','overview-03','shatter-03','overview-04'],
 '04':['ammo-02','ammo-03','ammo-04','ammo-05','ammo-09','ammo-10','shatter-04','shatter-01'],
 '06':['ammo-12','ammo-13','ammo-14','coop-01','shatter-02'],
 '08':['ranch-02','ranch-03','ranch-05','ranch-05b'],
 '10':['base-01','base-02','overview-05','shatter-06','shatter-07','ammo-08'],
 '12':['overview-01','overview-02','overview-06','overview-07','ammo-15','shatter-08','coop-02']};
const ko={title:m.titles.ko,scenes:scenes.map(s=>({id:s[0],title:s[1],lines:s[4]}))};
const en={title:m.titles.en,scenes:scenes.map(s=>({id:s[0],title:s[2],lines:s[5]}))};
write('script/narration.ko.json',ko);write('script/narration.en.json',en);
const actionMap={schemaVersion:1,slug:m.slug,createdAt:new Date().toISOString(),status:'independent-script-draft-awaiting-full-review-and-measured-timing',bank:bankFile,bankSha256:crypto.createHash('sha256').update(fs.readFileSync(bankFile)).digest('hex'),sourceAudioStreamsForFinal:0,agentCreatedGames:0,sourceIntervalsApprovedForPlanning:true,final60_40Measured:false,fixedCaptionApproval:false,
 chapters:scenes.map(s=>({sceneId:s[0],title:s[1],classification:s[3],claim:s[4].join(' '),cuts:(allocations[s[0]]||[]).map(id=>{const c=bank.cuts.find(c=>c.id===id);if(!c)throw Error('Missing reviewed interval '+id);return {...c,scriptScene:s[0]};}),diagram:s[3]==='explanation'?'Independent white2.5D comparison and animated catalogue/prerequisite arrows; see outline.':null})),selectedCandidateSeconds:bank.uniqueCandidateSeconds};
if(actionMap.chapters.flatMap(c=>c.cuts).length!==bank.cuts.length)throw Error('Every cut must be allocated exactly once.');
write('sources/action-map.json',actionMap);
const research=JSON.parse(fs.readFileSync(proof+'/source-research.json','utf8'));
write('sources/game-candidates.json',{schemaVersion:1,reviewedAt:actionMap.createdAt,recentUse:research.recentUse,candidates:research.candidates,acquiredSources:research.acquiredSources,selectedBank:research.selectedBank,firstHandSourceReview:research.directActionReview,additionalCandidate:proof+'/source-research/request-customization.json',additionalCandidateApproved:false,sourceAudioForFinal:'exclude-all',finalPublicRights:'pending'});
process.stdout.write(JSON.stringify({sceneCount:ko.scenes.length,koParagraphs:ko.scenes.reduce((n,s)=>n+s.lines.length,0),enParagraphs:en.scenes.reduce((n,s)=>n+s.lines.length,0),uniqueActionCandidates:bank.cutCount,seconds:bank.uniqueCandidateSeconds,status:m.status})+'\n');
