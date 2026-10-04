// Independent commentary written after official existing-game actions were reviewed.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../..');
const slug = 'hierarchical-game-outlines';
if (fs.existsSync(path.join(root,`projects/${slug}/production/script-source-review.json`))) throw Error('Reviewed inputs are locked. Preserve the approved script/manifest and use a versioned reviewed repair if needed.');
const research = 'production/batches/sakurai-planning-game-design/proof-hierarchical-game-outlines/source-research/';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const write = (p, value) => {fs.mkdirSync(path.dirname(path.join(root,p)),{recursive:true});fs.writeFileSync(path.join(root,p),JSON.stringify(value,null,2)+'\n');};
const bank = read(research+'action-bank.json');
if (bank.status !== 'source-action-bank-reviewed-before-independent-narration') throw Error('Review actual source actions first');
const chapters = [
  {
    id:'01', kind:'actual', group:'overview', ko:'놀이기구와 메모의 크기', en:'A ride and the scale of a note',
    pairs:[
      ['투 포인트 뮤지엄의 공식 시연입니다. 둥근 놀이기구를 놓고, 가까이에서 입구를 살펴봅니다. 같은 화면에도 서로 다른 결정이 들어 있습니다.', 'This is an official Two Point Museum demonstration. A circular ride is positioned, then its entrance is inspected up close. One image contains several different decisions.'],
      ['다른 발췌에서는 새 놀이기구의 위치를 옮깁니다. 설치할 대상과 놓을 자리를 정하는 일은, 작은 장식의 색을 고르는 일보다 큰 질문입니다.', 'Another excerpt moves a new ride placement preview. Choosing the attraction and its location is a broader question than choosing the color of a small decoration.'],
      ['이 자료는 이천이십육 년 공개 시연과 추가 콘텐츠 미리보기입니다. 화면을 관찰해 우리만의 기획 메모를 정리해 보겠습니다.', 'This footage comes from a public demonstration and additional-content preview in 2026. We will organize our own design notes from the visible actions.'],
      ['놀이기구 하나, 입구 하나, 세부 조절값 하나를 모두 같은 크기의 항목으로 적으면 무엇부터 읽어야 할까요? 오늘은 그 순서를 계층형 아웃라인으로 만듭니다.', 'If a ride, an entrance, and one adjustment value are all listed at the same level, where should a reader start? We will build that reading order with a hierarchical outline.'],
    ],
    cutIds:['museum-28','museum-29','museum-26','museum-27','museum-02'],
    claim:'Mixed observations need an explicit reading hierarchy; the outline is our proposal, not a recovered developer document.',
    focus:'Ride placement and entrance inspection are separate observed actions. The drop preview does not prove a newly operating ride.',
    diagram:'Flat notes → player goal → features → concrete rules.',
  },
  {
    id:'02', kind:'explanation', group:'overview', ko:'부모 항목은 읽는 질문', en:'A parent defines the reading question',
    pairs:[
      ['아웃라인은 긴 목록에 들여쓰기만 더한 것이 아닙니다. 상위 항목이 먼저 질문을 정하고, 하위 항목이 그 질문에 필요한 내용을 펼쳐 줍니다.', 'An outline does more than indent a long list. A parent first defines a question, and its children expand the information needed to answer it.'],
      ['예를 들어 관람객이 놀이기구를 이용한다는 목표 아래에 배치, 선로 설계, 입구 연결을 둡니다. 이것은 우리가 화면을 보고 만든 설명용 구성입니다.', 'For example, put placement, track design, and entrance connection under the goal of visitors using a ride. This is our explanatory structure based on the footage.'],
      ['높이 조절값은 선로 설계 아래로 내려갑니다. 목표와 기능과 조절값을 같은 줄에 섞지 않으면, 읽는 사람은 먼저 전체를 이해할 수 있습니다.', 'A height adjustment belongs beneath track design. Separating goals, features, and values lets the reader understand the whole before individual details.'],
      ['먼저 이 가지가 무엇을 설명하는지 한 문장으로 써 보세요. 그 문장에 답하지 않는 항목이 보이면, 부모의 이름이나 항목의 위치를 다시 살펴봅니다.', 'First write one sentence describing what this branch explains. When an item does not answer that question, reconsider the parent label or the item’s location.'],
    ],
  },
  {
    id:'03', kind:'actual', group:'levels', ko:'전체 놀이기구와 선로 한 조각', en:'The whole attraction and one track section',
    pairs:[
      ['이제 선로 편집을 보겠습니다. 처음에는 끝부분의 미리보기가 보이고, 다음 발췌에서는 굽은 부분이 주변 놀이기구를 향해 길어집니다.', 'Now watch track editing. An endpoint preview appears first; in another excerpt, a curved section grows toward a neighboring attraction.'],
      ['화면에서 바뀌는 것은 선로의 일부입니다. 놀이기구 전체를 어디에 놓을지 결정하는 질문과, 이 조각을 어떻게 굽힐지 결정하는 질문을 나눌 수 있죠.', 'Only part of the track changes on screen. We can separate deciding where the whole attraction belongs from deciding how this particular section should bend.'],
      ['카메라가 가까워지면 선택한 끝부분과 조절 지점이 보입니다. 이 장면에 관한 메모라면 선로 설계 아래에 연결 위치와 곡선 조절을 넣을 수 있습니다.', 'As the camera approaches, the selected endpoint and adjustment points become visible. Notes about this action could place connection position and curve adjustment under track design.'],
      ['다음 조절에서는 굽은 선로와 지지점의 위치가 달라집니다. 큰 기능 이름만 적으면, 실제로 무엇을 바꿀 수 있는지 설명이 빠집니다.', 'Another adjustment changes the curve and support position. A feature name alone would leave out what the player can actually change.'],
      ['반대로 모든 조절값을 맨 위에 올리면 전체 계획이 묻힙니다. 지금 보이는 조각의 규칙은 아래에, 그 조각을 사용하는 기능은 위에 두는 이유입니다.', 'Listing every value at the top would bury the overall plan. That is why rules for this visible section belong below the feature that uses it.'],
    ],
    cutIds:['museum-01','museum-03','museum-04','museum-05'],
    claim:'Siblings should answer comparable questions; concrete adjustments belong beneath their feature.',
    focus:'Selected curve, endpoint and support changes. Do not equate a preview with a completed attraction.',
    diagram:'Comparable feature siblings with height/curve properties as children.',
  },
  {
    id:'04', kind:'explanation', group:'levels', ko:'형제 항목의 크기를 맞추기', en:'Keep sibling items at a comparable scale',
    pairs:[
      ['같은 부모 아래의 항목들은 비슷한 크기의 질문에 답하도록 만듭니다. 놀이기구 배치 옆에 높이 숫자 하나를 놓으면, 기능과 세부값이 섞입니다.', 'Children of one parent should answer questions of a comparable scale. Putting a single height value beside attraction placement mixes a feature with a detail.'],
      ['배치, 선로 설계, 입구 연결을 나란히 놓고, 높이와 회전은 선로 설계 아래에 둡니다. 들여쓰기는 글자의 장식이 아니라 포함 관계를 보여 줍니다.', 'Put placement, track design, and entrance connection beside one another, with height and rotation under track design. Indentation communicates containment, not decoration.'],
      ['항상 세 단계만 써야 한다는 규칙은 없습니다. 아직 정하지 않은 값은 질문으로 남겨도 됩니다. 중요한 것은 자세한 항목이 어느 기능에 속하는지 찾을 수 있다는 점입니다.', 'There is no requirement to use exactly three levels. An undecided value can remain a question. What matters is being able to find the feature that owns each detail.'],
      ['같은 줄의 항목들을 읽고, 서로 바꿔 읽어도 질문의 크기가 비슷한지 확인해 보세요. 다르면 아래로 내리거나, 그 항목을 담을 부모를 추가합니다.', 'Read the sibling items and check whether they ask similarly sized questions. If one does not, move it deeper or add a parent that properly contains it.'],
    ],
  },
  {
    id:'05', kind:'actual', group:'fold', ko:'전체를 볼 때와 조각을 볼 때', en:'Overview and detail serve different questions',
    pairs:[
      ['다른 각도에서 보면 출발 지점과 선로가 함께 보입니다. 전체를 읽을 때 필요한 정보는, 지금 선택한 조절값 하나보다 넓습니다.', 'From another angle, the station and track appear together. Reading the whole requires more context than the single value currently selected.'],
      ['이어서 굽은 선로를 여러 번 조절하는 발췌를 보세요. 카메라와 선택 지점이 달라질 때마다, 작은 부분을 확인하는 질문도 바뀝니다.', 'Watch separate excerpts of successive curve adjustments. As the camera and selection point change, the question being checked at the detail level changes too.'],
      ['모든 세부 규칙을 항상 펼쳐 놓으면, 출발 지점과 선로 설계라는 큰 항목을 훑기 어려워집니다. 지금 확인할 가지를 골라야 합니다.', 'If every detailed rule stays expanded, it becomes harder to scan the main branches for the station and track design. Choose the branch needed for the current review.'],
      ['다음 발췌에서는 큰 고리 모양의 선로가 달라집니다. 높이와 기울기를 따로 읽는 순간에는, 이 부분에 관한 메모를 펼칠 수 있겠죠.', 'In the next excerpt, a large loop changes shape. When reviewing height and tilt, we can expand the notes about that part.'],
      ['하지만 카메라가 멀어졌다고 해서 세부 규칙이 없어지는 것은 아닙니다. 화면의 거리 변화처럼, 문서에서도 전체와 세부를 오가며 읽습니다.', 'The detailed rules do not disappear when the camera moves farther away. As with this change of viewpoint, a document lets us move between the whole and its details.'],
      ['여기서 화면 조작과 문서의 접기 기능이 같은 시스템이라는 뜻은 아닙니다. 관찰할 크기를 바꾼다는 점을 빌려, 읽기 순서를 설계하는 것입니다.', 'Camera controls and document folding are not the same system. We are borrowing the change in observation scale to design a useful reading order.'],
    ],
    cutIds:['museum-06','museum-07','museum-08'],
    claim:'Folding selects a level of detail without deleting information; camera-scale comparison is an analogy, not footage of an outline tool.',
    focus:'Station/track context, then curve/loop adjustment; both remain parts of the same analytical branch.',
    diagram:'Fold children → three feature headings remain → expand the branch relevant to the reviewer.',
  },
  {
    id:'06', kind:'explanation', group:'fold', ko:'접기는 삭제가 아닙니다', en:'Folding hides detail without deleting it',
    pairs:[
      ['접기는 하위 항목을 잠시 숨기는 기능입니다. 세부 내용을 지우지 않고도, 상위 항목만 남겨 기획의 큰 흐름을 읽을 수 있습니다.', 'Folding temporarily hides child items. It preserves the details while leaving parent headings visible for reading the broad structure of a design.'],
      ['전체 구성을 검토할 때는 기능들을 접고, 선로 규칙을 검토할 때는 그 가지만 펼칩니다. 모든 사람에게 같은 화면을 강요할 필요는 없습니다.', 'Collapse feature details for an overview, then expand the track branch when reviewing its rules. Different readers do not need to see the same level of detail.'],
      ['다만 접힌 제목만으로도 내용의 범위를 알 수 있어야 합니다. 기타 사항처럼 모호한 제목은, 접는 순간 안에 무엇이 있는지 감춥니다.', 'A collapsed heading must still communicate its scope. A vague label such as “miscellaneous” hides what belongs inside as soon as the branch is folded.'],
      ['접힌 상태로 문서를 훑어 보고, 원하는 규칙이 어느 가지에 있을지 예상해 보세요. 예상한 곳에서 찾을 수 있으면 제목과 구조가 읽는 사람을 돕고 있는 것입니다.', 'Scan the collapsed outline and predict where a needed rule belongs. Finding it where expected shows that the headings and structure are helping the reader.'],
    ],
  },
  {
    id:'07', kind:'actual', group:'move', ko:'조각과 그 조각의 설명을 함께', en:'Keep a section together with its description',
    pairs:[
      ['이번에는 고리 주변의 지지점을 선택합니다. 선택된 선로 모양이 달라져도, 옆의 다른 선로와 출발 지점은 여전히 함께 보입니다.', 'A support near the loop is selected. As the selected track changes, neighboring rails and the station remain visible together.'],
      ['다른 발췌에서는 붉은 미리보기의 기울기와 바닥에 닿는 모양이 달라집니다. 이 조각을 설명하는 메모에는 조절 대상과 확인할 조건을 함께 적을 수 있습니다.', 'Another excerpt changes a red preview’s tilt and footprint near the ground. Notes about this section can keep the adjustable object and its check conditions together.'],
      ['화면에 보이는 여러 조각은 서로 떨어진 단어 목록이 아닙니다. 어느 선로의 끝을 바꾸는지 알아야, 지지점에 관한 설명도 이해할 수 있죠.', 'The visible sections are not an unrelated list of words. Knowing which track endpoint is being edited provides context for the support description.'],
      ['이어서 카메라가 옆의 고리를 돌아보는 발췌입니다. 전체가 어디에 이어지는지 확인하고, 다시 선택한 부분으로 돌아옵니다.', 'The next excerpt moves around a neighboring loop. It checks how the larger arrangement connects before returning to the selected part.'],
      ['우리 문서에서 이 조각을 다른 기능 아래로 옮겨야 한다면, 높이와 연결 조건 같은 하위 메모도 함께 옮기는 편이 자연스럽습니다.', 'If we move this section beneath another feature in our document, its notes about height and connection conditions should normally move with it.'],
      ['마지막 발췌에서도 지지점 조절에 따라 주변 곡선이 바뀝니다. 설명의 부모만 옮기고 관련 규칙을 남겨 두면, 무엇에 관한 규칙인지 잃어버릴 수 있습니다.', 'The last excerpt again changes a nearby curve through a support adjustment. Moving only the heading and leaving its rules behind can remove the context those rules need.'],
      ['이 비교는 문서에서 가지를 옮길 때의 주의점입니다. 게임에서 선로를 움직이면 모든 관련 규칙이 자동으로 따라온다고 주장하는 것은 아닙니다.', 'This comparison concerns moving branches in a document. It does not claim that every related game rule automatically follows a moved track section.'],
    ],
    cutIds:['museum-09','museum-10','museum-11','museum-12','museum-18'],
    claim:'Move a branch with its children; review semantic fit under the new parent. Do not infer automatic game dependencies.',
    focus:'Selected segment/support retains context in neighboring rails; separate source attempts remain separate.',
    diagram:'Move a parent plus children; contrast a stranded detail and a correctly moved branch.',
  },
  {
    id:'08', kind:'explanation', group:'move', ko:'가지 이동 뒤에는 뜻도 확인하기', en:'Check meaning after moving a branch',
    pairs:[
      ['계층형 아웃라인의 가지를 옮길 때는, 제목과 하위 내용을 하나의 묶음으로 봅니다. 제목만 이동하면 세부 규칙이 옛 위치에 남을 수 있습니다.', 'Treat a heading and its children as one branch when moving an outline. Moving only the heading can leave the detailed rules in their old location.'],
      ['접어서 큰 가지를 이동한 뒤 다시 펼쳐 보세요. 항목 수가 그대로인지 확인하는 것과, 새 부모 아래에서 의미가 맞는지 확인하는 것은 다른 작업입니다.', 'Fold the branch, move it, and expand it again. Checking that the item count is unchanged differs from checking whether the contents still fit their new parent.'],
      ['예를 들어 높이 조절 규칙을 입구 연결 아래로 옮기면 글자는 보존돼도 관계는 어색해집니다. 새 위치가 그 규칙을 설명하는 질문인지 다시 읽어야 합니다.', 'A height rule placed under entrance connection keeps its words but gains an awkward relationship. Read the new parent again to see whether it asks the question that rule answers.'],
      ['순서를 바꾸는 것은 생각을 다시 검토하는 기회입니다. 자동 정렬이 끝났다는 이유로 구조까지 맞다고 판단하지 말고, 묶인 내용의 뜻을 확인합니다.', 'Reordering is a chance to reconsider the design. Finishing a move does not prove the structure is correct; review the meaning of the grouped contents.'],
    ],
  },
  {
    id:'09', kind:'actual', group:'exceptions', ko:'포함 관계와 다른 가지의 연결', en:'Containment and relationships across branches',
    pairs:[
      ['다른 선로 편집 발췌입니다. 새 곡선의 미리보기가 이미 놓인 선로 옆에서 바뀝니다. 한 조각을 설명하더라도 주변과의 관계를 빼놓을 수 없습니다.', 'In another track-editing excerpt, a new curve preview changes beside existing rails. Describing one section still requires considering its relationship to its surroundings.'],
      ['선택한 조각의 길이나 모양에 관한 메모는 그 조각 아래에 둡니다. 다른 선로와 만날 때 확인할 조건은, 두 가지를 이어 주는 참고 항목으로 만들 수 있죠.', 'Notes about the selected section’s length or shape can live beneath it. Conditions to check where it meets another track can be cross-references between the two branches.'],
      ['이어서 붉은 선로와 지지점이 주변 고리 옆에서 움직입니다. 색과 미리보기만으로, 모든 연결 조건이 해결됐다고 말할 수는 없습니다.', 'A red track and support then move beside neighboring loops. The preview and its color do not show that every connection condition has been resolved.'],
      ['다음 발췌에는 충돌 항목도 나타납니다. 우리 메모에는 확인되지 않은 조건을 남겨야 합니다. 구조를 깔끔하게 만든 것과 실제 문제를 해결한 것은 다릅니다.', 'A later excerpt also shows collision entries. Our notes should retain unresolved checks. Organizing a clean structure and solving the actual problem are different tasks.'],
      ['이제 별도의 놀이기구 입구를 가까이 봅니다. 입구에 관한 메모는 선로 조절값과 같은 항목이 아니지만, 이용하려는 목표와는 연결됩니다.', 'Now inspect the entrance of a separate attraction up close. Entrance notes are different from track adjustment values, but both relate to the goal of using a ride.'],
      ['금색 꽃 장식을 옮기는 다른 발췌도 보세요. 장식의 위치를 확인할 수는 있지만, 이 장면만으로 관람객의 만족도가 좋아졌다고 결론 내리지는 않습니다.', 'Watch another excerpt repositioning a golden flower decoration. Its location is visible, but this shot does not establish an improvement in visitor satisfaction.'],
      ['장식과 입구가 서로 영향을 줄 수 있다는 질문은 별도 연결로 남깁니다. 같은 내용을 두 가지에 복사해 놓기보다, 기준이 되는 항목을 가리키는 편이 수정하기 쉽습니다.', 'Keep questions about possible relationships between decoration and access as separate links. Pointing to one authoritative item is easier to maintain than copying the same rule into two branches.'],
    ],
    cutIds:['museum-13','museum-14','museum-15','museum-16','museum-17','museum-30','museum-31','museum-32'],
    claim:'A hierarchy expresses containment, not every causal relationship. Record unresolved checks and use explicit cross-references.',
    focus:'Changed previews, collision feedback, existing entrance and flower placement. No inferred success, newly built queue or happiness result.',
    diagram:'Contains tree versus cross-reference arrow; one authoritative rule with unresolved question marker.',
  },
  {
    id:'10', kind:'explanation', group:'exceptions', ko:'모든 관계를 나무 하나에 넣지 않기', en:'A tree does not describe every relationship',
    pairs:[
      ['부모 아래에 놓였다는 것은, 그 설명에 포함된다는 뜻입니다. 반드시 그것을 먼저 만들어야 한다거나, 그것 때문에 다른 기능이 작동한다는 뜻은 아닙니다.', 'Being under a parent means belonging in its explanation. It does not necessarily mean it must be built first or that it causes another feature to work.'],
      ['입구 연결과 장식 배치가 같은 규칙을 참고해야 한다면, 규칙은 한 곳에 두고 서로 가리키게 합니다. 복사본 둘을 따로 고치면 내용이 달라질 수 있습니다.', 'If entrance connection and decoration placement refer to one shared rule, store it once and link to it. Separate copies can drift when edited independently.'],
      ['우리 구성에서는 포함 관계를 세로 가지로, 다른 항목을 참고하는 관계를 옆 화살표로 표시합니다. 실제 게임의 모든 의존성을 분석한 도식은 아닙니다.', 'Our proposed structure uses vertical branches for containment and side arrows for references. It is not a complete dependency analysis of the game.'],
      ['한 곳에 넣기 어려운 항목은 억지로 숨기지 마세요. 어떤 질문에 답하는지 다시 정하고, 확인이 필요한 관계는 질문으로 드러내면 됩니다.', 'Do not hide an item merely because it is hard to place. Reconsider the question it answers and make relationships needing verification visible as questions.'],
    ],
  },
  {
    id:'11', kind:'actual', group:'review', ko:'한 조절 뒤에 전체를 다시 읽기', en:'Read the whole after checking one detail',
    pairs:[
      ['카메라가 굽은 선로를 따라 움직이다가 출발 지점까지 돌아봅니다. 한 조각의 값만 확인하고 끝내면, 전체가 어떻게 이어지는지 놓칠 수 있습니다.', 'The camera moves along the curved track and looks back toward the station. Checking only one section’s value can miss how the entire arrangement connects.'],
      ['다른 발췌에서는 선로로 돌아와 새 지지점을 선택합니다. 우리 메모를 검토하는 사람도 전체 제목을 읽다가, 확인할 세부 항목 하나로 내려갈 수 있어야 합니다.', 'Another excerpt returns to the track and selects a different support. A reader of our notes should likewise be able to move from a broad heading to the particular detail needing review.'],
      ['지지점을 조절하면 고리 모양이 바뀌고, 옆의 선로가 함께 보입니다. 이 규칙이 어느 기능을 위한 것인지 문서 안에서 찾을 수 있는지 확인해 보세요.', 'Adjusting a support changes the loop while neighboring track remains visible. Check whether the document lets a reader find which feature this rule serves.'],
      ['이어지는 발췌에서도 선택한 선로가 여러 모양을 거칩니다. 우리가 적을 것은 멋있어 보인다는 평가만이 아니라, 무엇을 조절하고 무엇을 확인해야 하는지입니다.', 'The selected track passes through several shapes in the following excerpt. Our notes should describe what is adjustable and what needs checking, rather than only judging whether it looks impressive.'],
      ['일부 장면에는 충돌 목록이 보이고, 또 다른 순간에는 확인 표시가 달라집니다. 표시 하나가 달라졌다고 해서 모든 검토 항목을 완료로 바꾸지는 않습니다.', 'Some shots show collision entries, and another moment changes the confirmation indicator. One changed indicator does not justify marking every review item complete.'],
      ['마지막으로 다른 지지점을 조절하고 전체 선로를 다시 살펴봅니다. 이 자료의 여러 발췌를 하나의 성공한 연속 플레이로 묶지 않고, 관찰한 동작별로 읽습니다.', 'Finally, another support is adjusted and the track is inspected again. We read these separate excerpts by their observed actions rather than presenting them as one continuous successful session.'],
      ['기획서도 같은 순서로 점검할 수 있습니다. 전체 목표를 읽고, 구체적인 확인 조건을 찾고, 그 조건이 목표와 연결되는지 다시 올라가 보는 것입니다.', 'A design document can be reviewed in the same order: read the overall goal, find a concrete check condition, then return upward to see how the condition connects to that goal.'],
    ],
    cutIds:['museum-19','museum-20','museum-21','museum-22','museum-23','museum-24','museum-25'],
    claim:'A useful outline enables goal→detail→goal review and preserves unresolved conditions. Indicator changes are not complete validation.',
    focus:'Track overview, newly selected support, geometry change, collision feedback and return to overview in separate excerpts.',
    diagram:'Reader path from folded goal to leaf check and back; explicit unanswered condition.',
  },
  {
    id:'12', kind:'explanation', group:'review', ko:'읽는 사람이 찾을 수 있는 기획서', en:'A design document readers can navigate',
    pairs:[
      ['좋은 아웃라인의 기준은 단계가 많거나 모양이 반듯하다는 데 있지 않습니다. 읽는 사람이 필요한 질문을 찾고, 그 답이 어느 목표에 속하는지 이해할 수 있어야 합니다.', 'A good outline is not defined by many levels or a tidy appearance. Readers must be able to find the question they need and understand which goal its answer serves.'],
      ['자기 기획서에서 기능 하나를 골라 보세요. 같은 크기의 항목을 나란히 놓고, 세부 규칙은 아래로 내리고, 다른 가지의 관계는 참고 표시로 남깁니다.', 'Choose one feature from your design. Put comparable items beside one another, move detailed rules below them, and mark references to other branches explicitly.'],
      ['한 번 접어서 전체를 읽고, 필요한 가지를 펼친 뒤 옮겨 보세요. 마지막에는 아직 답하지 못한 질문도 보이도록 남깁니다. 정리한 문서와 검증한 설계를 구분하는 것입니다.', 'Fold the outline for an overview, expand the relevant branch, and try moving it. Keep unanswered questions visible afterward. An organized document and a verified design remain distinct.'],
      ['기획을 실제 구현과 연결하는 연습이 필요하다면 설명란의 프로그래밍 과외 링크를 참고해 주세요. 오늘의 목표는 더 긴 목록이 아니라, 다음에 확인할 내용을 찾을 수 있는 구조입니다.', 'If you want practice connecting a design to implementation, see the programming coaching link in the description. The goal is a structure that reveals what to check next, rather than a longer list.'],
    ],
  },
];
const titles = read(`projects/${slug}/project.json`).titles;
for(const language of ['ko','en'])write(`projects/${slug}/script/narration.${language}.json`,{title:titles[language],scenes:chapters.map(c=>({id:c.id,title:c[language],lines:c.pairs.map(p=>p[language==='ko'?0:1])}))});
const actionChapters=chapters.filter(c=>c.kind==='actual').map(c=>({id:c.id,group:c.group,claim:c.claim,focus:c.focus,diagramConnection:c.diagram,insertionPoint:`Before explanation ${String(Number(c.id)+1).padStart(2,'0')}`,paragraphCount:c.pairs.length,cuts:c.cutIds.map(id=>{const found=bank.cuts.find(x=>x.id===id);if(!found)throw Error('Unreviewed source cut '+id);return {...found,classification:'actual-existing-game-action',loop:false,finalApproved:false};}),timingStatus:'source-bank-only; paragraph/action fit, measured final60:40 and every caption remain pending'}));
const usedIds=actionChapters.flatMap(c=>c.cuts.map(x=>x.id));if(new Set(usedIds).size!==usedIds.length)throw Error('Source cut reused across chapters');
write(`projects/${slug}/planning/action-map.json`,{schemaVersion:1,reviewedSourceBank:research+'action-bank.json',sourceObservationBeforeScript:true,actualSelfCreatedGameFootage:false,chapters:actionChapters,explanations:chapters.filter(c=>c.kind==='explanation').map(c=>({id:c.id,group:c.group,title:c.ko,paragraphCount:c.pairs.length,preserveClaimsAndDuration:true})),uniqueCandidateSeconds:bank.uniqueCandidateSeconds,final60_40Measured:false,captionCueApproval:false,allFootageSpeed:1,sourceAudio:'exclude; preserve original locally',versionLabel:bank.source.versionLabel});
write(`projects/${slug}/sources/game-candidates.json`,{...read(research+'candidate-review.json'),selectedSourceBank:research+'action-bank.json',chosenForNarration:['I-ccSZ5J1Bo'],supplementalSource:'5rgASbqkeTI has only a short unambiguous placement preview; deferred rather than using condensed construction or cinematic panels for quota.',newProjectCreated:true,narrationWritten:true,finalMeasuredShare:null,finalPublicRights:'pending'});
write(`projects/${slug}/sources/source-action-bank.json`,bank);
const m=read(`projects/${slug}/project.json`), approved=read('projects/motion-sickness-games/project.json');
m.status='source-first-independent-bilingual-script-written-awaiting-direct-review';
m.membershipOutro={...approved.membershipOutro,appliedToFinal:false};
m.audio.backgroundMusic={...approved.audio.backgroundMusic};
m.audio.mixStatus='awaiting-current-narration-and-measured-timeline';m.audio.sourceAudioPolicy=approved.audio.sourceAudioPolicy;m.audio.musicFallbackScenes=actionChapters.map(c=>c.id);
m.editing.exampleInterleaving.planningPath=`projects/${slug}/planning/action-map.json`;
m.editing.exampleInterleaving.reviewStatus='source-native-action-reviewed; bilingual-script-direct-review-and-final-cut-timing-pending';
m.editing.sourceBankSeconds=bank.uniqueCandidateSeconds;
m.approvals={script:'pending-direct-review-of60-bilingual-paragraphs',voiceSample:'reuse-existing-approved-Qwen3-TTS-1.7B-reference',bgm:'reuse-user-approved-continuous-Nimbus',final:'pending-current-ASR-and-all-final-QA',publication:'private only; public release belongs to user'};
m.publishReady=false;
write(`projects/${slug}/project.json`,m);
console.log(JSON.stringify({scenes:chapters.length,paragraphs:chapters.reduce((s,c)=>s+c.pairs.length,0),koChars:chapters.map(c=>({id:c.id,kind:c.kind,chars:c.pairs.reduce((s,p)=>s+p[0].length,0)})),sourceCuts:usedIds.length,candidateSeconds:bank.uniqueCandidateSeconds,finalApproval:false}));
