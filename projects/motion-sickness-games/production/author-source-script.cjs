// Independent bilingual commentary authored after inspecting existing-game sources.
// This file creates no game, media, voice, render or platform upload.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,v)=>{fs.mkdirSync(path.dirname(path.join(root,p)),{recursive:true});fs.writeFileSync(path.join(root,p),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
const at=new Date().toISOString(),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const sourceBase='production/batches/sakurai-planning-game-design/preflight/proof-motion-sickness-games/game-research/';
const rows=[
 ['01','노즐만 돌리면 될까요?','Does aiming need to turn the whole view?',[
  ['파워워시 시뮬레이터의 개발 시연입니다. 물을 뿌리는 도구와, 그 뒤의 놀이터를 따로 보세요. 바닥을 따라 조준할 때 배경도 함께 움직입니다.','This is a PowerWash Simulator development demonstration. Watch the cleaning tool and the playground separately. As the aim sweeps across the floor, the background moves too.'],
  ['이번 컷에서는 달라집니다. 놀이터의 기둥과 바닥 경계는 비슷한 자리에 남아 있는데, 노즐과 조준 위치가 화면 안에서 움직입니다.','The next shot behaves differently. Posts and floor boundaries stay in roughly the same screen positions, while the nozzle and aiming point move within the image.'],
  ['이것은 개발사가 소개한 에임 모드입니다. 바라보는 방향과 도구의 조준을 나누면, 작은 목표를 따라갈 때 화면 전체를 계속 돌릴 필요가 줄어듭니다.','The developer calls this Aim Mode. Separating the viewing direction from tool aiming reduces the need to turn the whole image while following a small target.'],
  ['도구의 조준과 배경의 이동이 어떻게 연결되는지 보세요. 같은 작업에서도 화면 전체를 돌리는 정도가 달라질 수 있습니다.','Watch how tool aiming connects to background movement. The same task can involve different amounts of whole-view rotation.'],
  ['자료는 이천이십이 년 개발 중 버전입니다. 현재 설정 전체나 개인의 멀미 반응을 비교한 실험은 아닙니다.','This footage shows a development version from 2022. It is not a comparison of every current setting or individual motion-sickness responses.'],
  ['오늘은 필요한 시점 이동과 조준을 나누고, 그 선택을 플레이어에게 돌려주는 카메라 설계를 살펴보겠습니다.','We will separate necessary view movement from aiming, and examine camera design that gives players control over that relationship.']
 ]],
 ['02','화면에서 보이는 이동과 몸의 감각','Visible movement and bodily sensations',[
  ['게임의 화면은 이동하고 돌아가지만, 플레이어의 몸은 같은 자리에 있을 수 있습니다. 시각과 몸의 움직임에 관한 신호가 어긋나는 것은 멀미를 설명하는 한 가지 이론입니다.','The game image can travel and turn while the player remains seated. Conflict between visual and bodily motion signals is one explanatory theory of motion sickness.'],
  ['그렇다고 카메라가 움직이면 누구나 같은 반응을 보이는 것은 아닙니다. 다른 사람이 괜찮다고 해서 내 불편함이 사라지지도 않습니다.','People do not all respond in the same way to a moving camera. Someone else being comfortable does not make your discomfort disappear.'],
  ['여기서 우리가 다룰 것은 치료법이 아니라 개발자의 선택입니다. 조작에 필요한 움직임과 연출로 더한 움직임을 구분하면, 어떤 부분을 조절 가능하게 만들지 찾을 수 있습니다.','Our focus is a developer choice, not treatment. Separating movement needed for control from movement added for presentation helps identify what players could adjust.'],
  ['왼쪽은 목표를 향해 시점을 돌리는 동작, 오른쪽은 그 위에 얹는 흔들림이라고 생각해 보세요. 둘을 한 값으로 묶지 않는 것이 첫 번째 설계 질문입니다.','Think of the left side as turning toward a target, and the right side as extra shake layered on top. The first design question is whether these should be controlled separately.']
 ]],
 ['03','배경이 멈춰 있어도 조준은 움직인다','Aiming can move against a stable background',[
  ['다시 에임 모드의 실제 시연입니다. 노즐이 화면 왼쪽과 오른쪽을 향해 움직여도, 뒤쪽 계단과 나무는 잠시 같은 위치에 남아 있습니다.','Return to the Aim Mode demonstration. The nozzle moves toward the left and right of the image, while the stairs and trees remain in place for a time.'],
  ['바닥에서 찾는 조준 위치와, 내가 바라보고 있는 놀이터의 방향이 분리된 것입니다. 도구를 움직였다는 사실과 화면 전체가 돌아갔다는 사실은 다릅니다.','The aiming position on the floor is separated from the direction of the view. Moving the tool and rotating the whole image are different events.'],
  ['하지만 가장자리까지 움직이면 시야가 돌아가고 회전 놀이기구가 나타납니다. 에임 모드라고 해서 카메라가 언제나 완전히 고정되는 것은 아닙니다.','At the edge, the view turns and the roundabout comes into view. Aim Mode does not mean that the camera is completely fixed at all times.'],
  ['이제 놀이기구를 씻는 장면을 보세요. 배경의 나무보다 물줄기가 닿는 표면을 따라가면, 화면이 덜 돌아가는 동안에도 작업이 이어지는 것을 볼 수 있습니다.','Now watch the roundabout being cleaned. Follow the surface reached by the spray, rather than the distant trees. The task continues during stretches with less view rotation.'],
  ['조준을 독립시켜도 다른 방향을 보는 방법은 남겨야 합니다. 화면 끝으로 조준하는 일과 주변을 둘러보는 일이 어떻게 연결되는지 함께 설계해야 하죠.','Separating aim still requires a way to look elsewhere. Designers need to consider how aiming toward an edge connects to looking around the environment.'],
  ['이 시연이 보여 주는 것은 작업과 시점의 연결 방식입니다. 이런 옵션이 모두에게 같은 정도로 편안하다는 결과까지 보여 주는 것은 아닙니다.','The demonstration shows how a task connects to a viewpoint. It does not show that the option is equally comfortable for everyone.']
 ]],
 ['04','조작과 추가 연출을 따로 조절하기','Separate control from added motion',[
  ['카메라 움직임을 전부 없애면 다른 곳을 볼 수 없습니다. 대신 시점을 돌리는 입력, 도구의 조준, 걸을 때의 흔들림을 서로 다른 층으로 나누어 생각할 수 있습니다.','Removing all camera movement would prevent looking elsewhere. Instead, consider view-turning input, tool aiming and walking bob as separate layers.'],
  ['걷는 느낌을 주려고 더한 상하 움직임이나 충격을 강조하는 화면 흔들림은, 목표를 바라보는 방향과 같은 역할이 아닙니다. 조절 값도 분리할 수 있죠.','Vertical bob added to suggest walking and shake added to emphasize impact do not serve the same purpose as facing a target. Their controls can be separated too.'],
  ['접근성 가이드라인도 이런 부가 움직임을 플레이어가 조절할 수 있도록 권합니다. 다만 옵션이 있다는 사실과 개인에게 편안하다는 결과는 따로 확인해야 합니다.','Accessibility guidance recommends player control over these additional movements. Having an option and achieving comfort for an individual are separate questions.'],
  ['도식에서는 시점 회전은 남기고 추가 흔들림만 낮춥니다. 실제 구현에서도 한 스위치가 조준과 이동까지 뜻밖에 바꾸지 않도록 역할을 나누는 것이 중요합니다.','In this diagram, view rotation remains available while extra shake is reduced. In implementation, separate these responsibilities so one switch does not unexpectedly change aiming or movement.']
 ]],
 ['05','위치를 옮기는 일과 표면을 따라가는 일','Repositioning and tracking a surface',[
  ['이번에는 놀이터 구조물 주변의 다른 작업입니다. 기둥 사이를 지나 옆으로 자리를 옮기면, 가까운 기둥과 멀리 있는 나무의 위치가 함께 달라집니다.','This is another part of the playground task. When the player moves sideways between posts, the positions of nearby posts and distant trees change together.'],
  ['청소할 면이 가려져 있다면 보는 위치를 바꿔야 합니다. 이런 이동까지 없애는 것과, 그 자리에 선 뒤 조준을 독립시키는 것은 다른 선택입니다.','If the surface is hidden, the viewing position may need to change. Removing that movement and separating aim after taking a position are different choices.'],
  ['위쪽 구조물을 씻는 컷에서는 화면이 위를 향하고, 물줄기가 높은 표면으로 이동합니다. 목표가 바닥에서 위쪽으로 바뀌면 바라볼 방향도 바뀔 수 있습니다.','In the upper-structure shot, the view tilts upward and the spray reaches a higher surface. A target moving from the floor to overhead geometry can require a different viewing direction.'],
  ['이어지는 다른 면에서는 노즐이 기둥과 판자를 따라 움직입니다. 먼저 자리를 잡는 구간과, 같은 방향을 바라보며 표면을 씻는 구간을 구분해 보세요.','On another surface, the nozzle follows posts and planks. Distinguish taking a position from cleaning a surface while facing roughly the same direction.'],
  ['화면이 덜 움직이는 것을 목표로 삼더라도, 숨은 표면을 찾을 수 있어야 합니다. 조준 옵션은 게임에서 해야 하는 일을 없애는 대신 다른 조작 방법을 제공하는 쪽으로 설계할 수 있습니다.','Even if reducing screen movement is a goal, hidden surfaces must remain discoverable. An aiming option can provide another way to perform the task rather than remove the task itself.'],
  ['서로 다른 시점의 컷을 이어서 보고 있습니다. 같은 입력을 반복한 비교 실험은 아니므로, 지금 보이는 이동과 조준의 관계부터 설명해야 합니다.','These are excerpts from different moments. They are not a controlled repetition of identical inputs, so begin by describing the visible relationship between movement and aim.']
 ]],
 ['06','한 번에 한 가지를 바꾸는 옵션','Options that change one thing at a time',[
  ['화면 움직임이라는 메뉴 하나에 모든 것을 넣으면, 값을 바꿨을 때 무엇이 달라지는지 알기 어렵습니다. 시점 감도와 도구 조준, 추가 흔들림을 구분해서 설명할 수 있습니다.','A single menu item called screen movement makes it hard to know what changing it does. Explain view sensitivity, tool aiming and extra shake separately.'],
  ['감도는 같은 입력에 시점이 얼마나 돌아가는지에 관한 값입니다. 에임 모드는 조준과 시점의 연결 방식에 관한 선택입니다. 서로 바꾸어 부를 수는 없습니다.','Sensitivity concerns how much the view turns for an input. Aim Mode concerns the relationship between aim and view. Those terms are not interchangeable.'],
  ['지금 도식의 옵션 목록은 설계 제안입니다. 앞의 개발 시연에 이 메뉴가 그대로 들어 있다는 뜻은 아닙니다. 실제 게임의 메뉴와 우리가 제안하는 화면을 구분해 주세요.','This option list is a design proposal. It does not mean the development demonstration contains this exact menu. Distinguish the actual game from our proposed interface.'],
  ['짧은 설명과 되돌리기를 함께 제공하면, 플레이어가 차이를 확인하고 원래 값으로 돌아갈 수 있습니다. 만능 권장값을 하나 고르는 것보다 선택의 의미를 알게 하는 것이 먼저입니다.','A short explanation and a reset let players inspect a difference and return to the original value. Explaining the choice comes before declaring one universal recommended setting.']
 ]],
 ['07','게임 규칙이 시야의 방향을 바꿀 때','When a game mechanic changes orientation',[
  ['탈로스 프린서플 투의 공식 게임플레이입니다. 발판을 따라 이동한 뒤, 위쪽 장치를 향해 시야가 돌아가는 모습을 보세요.','This is official gameplay footage of The Talos Principle 2. Watch platform movement, then the view turning toward overhead geometry.'],
  ['다른 컷에서는 벽과 레이저가 기울어집니다. 퍼즐 공간을 보는 방향이 바뀌는 장면입니다.','In another shot, walls and lasers tilt. The orientation of the puzzle view changes.'],
  ['공간을 바꾸거나 새로운 방향을 바라보는 동작은 게임의 규칙과 연결되기도 합니다. 서로 다른 컷이므로 연속 플레이로 읽지는 마세요. 중요한 질문은 바뀐 뒤의 방향을 이해할 수 있느냐입니다.','Changing space or looking in a new direction can be connected to game rules. These separate shots are not continuous play. The important question is whether the new orientation remains understandable.'],
  ['다시 청소 게임의 다른 표면입니다. 구조물 아래에서 위를 보았다가 다른 면을 바라볼 때, 가까운 판자와 기둥이 다음 방향을 찾는 단서가 됩니다.','Return to a different surface in the cleaning game. When looking up beneath the structure and then toward another face, nearby planks and posts provide orientation cues.'],
  ['여기서는 목표를 찾기 위해 보는 방향이 바뀝니다. 앞의 퍼즐과 동일한 장치는 아니지만, 움직인 뒤 어디를 보고 있는지 읽을 수 있어야 한다는 질문은 공유합니다.','Here, the view changes to find a target. It is not the same mechanic as the puzzle, but both raise the question of reading where the view is facing after a change.'],
  ['이 영상만 보고 특정 전환이 편안하다고 판정할 수는 없습니다. 볼 방향의 변화와 그 뒤에 남는 단서를 먼저 관찰한 뒤, 전환 방식의 선택을 고민해 보세요.','This footage alone cannot establish that a particular transition is comfortable. Observe the orientation change and the remaining cues before considering choices in how the transition is presented.']
 ]],
 ['08','천천히 움직이면 언제나 편할까요?','Is slower movement always comfortable?',[
  ['전환을 부드럽게 만들면 움직임을 따라갈 시간이 생길 수 있습니다. 하지만 더 오래 움직이는 화면이 누군가에게는 더 불편할 수도 있습니다. 하나의 방식으로 모두를 대표할 수는 없죠.','A gradual transition can allow time to follow the movement. A longer-moving image can also be less comfortable for someone else. One transition cannot represent everyone.'],
  ['반대로 즉시 바꾸면 이동 과정은 짧아져도 도착한 방향을 놓칠 수 있습니다. 움직이는 시간과 바뀐 공간을 이해하는 일은 별개의 문제입니다.','An immediate change shortens the moving interval but may make the arrival orientation harder to read. Motion duration and spatial understanding are separate questions.'],
  ['이 두 경로는 설명용 도식입니다. 앞에서 본 게임에 이런 전환 옵션이 실제로 구현되어 있다고 주장하는 화면은 아닙니다.','These two paths are explanatory diagrams. They do not claim that the game footage we just watched implements these transition options.'],
  ['전환을 줄일 선택과 도착 방향을 읽을 단서를 함께 고민하세요. 편안함을 확인할 때에도 한 가지 효과만 바꾸고, 플레이어가 즉시 멈추거나 되돌릴 수 있게 해야 합니다.','Consider both a choice to reduce transition motion and cues for reading the arrival direction. When checking comfort, change one effect at a time and allow players to stop or revert immediately.']
 ]],
 ['09','작업할 목표가 계속 읽히는가','Does the task target remain readable?',[
  ['미끄럼틀 주변을 씻는 다른 구간입니다. 화면이 돌아가는 동안에도 물줄기가 닿는 면을 찾을 수 있는지 보세요. 바닥, 옆면, 가까운 구조물이 서로 다른 위치에 있습니다.','This is another cleaning interval around the slide. Can you find the surface reached by the spray while the view turns? The floor, side surface and nearby structure occupy different positions.'],
  ['청소할 곳을 새로 바라보는 순간에는 배경의 선도 이동합니다. 시점이 멈춘 뒤에는 물줄기와 깨끗해지는 면의 관계를 다시 읽을 수 있어야 합니다.','When a new area comes into view, background lines move too. After the view settles, the relationship between the spray and the surface being cleaned should be readable again.'],
  ['이제 가까운 판자와 기둥을 보겠습니다. 노즐만 크게 보여 주는 것보다, 도구가 어느 면을 향하고 있는지 함께 보이는 것이 작업을 이해하는 데 필요합니다.','Now look at the nearby planks and posts. Understanding the task requires seeing which surface the tool points at, as well as seeing the nozzle itself.'],
  ['선택형 조준 방식을 바꾼 뒤에도 이 연결이 남아야 합니다. 카메라 움직임을 줄였는데 목표를 가리거나 조준 위치를 헷갈리게 하면, 다른 조작 문제가 생길 수 있습니다.','That relationship should remain after changing the aiming mode. Reducing camera motion while obscuring the target or confusing the aiming position can introduce another control problem.'],
  ['이 장면들에서 직접 확인하는 것은 도구, 표면, 시점의 위치입니다. 플레이어의 몸 상태나 불편함을 측정한 자료와 혼동하지 마세요.','What these shots directly show is the position of tool, surface and view. Do not confuse them with measurements of a player’s symptoms or comfort.'],
  ['그래서 검토할 질문도 구체적이어야 합니다. 덜 움직이는가에 이어, 어디를 씻는지 보이는가, 다른 면으로 옮긴 뒤 다시 조준할 수 있는가를 확인할 수 있습니다.','Make the review questions specific. Beyond asking whether the image moves less, ask whether the cleaning target is visible and whether aiming remains readable after moving to another surface.']
 ]],
 ['10','선택을 숨기지 않고 되돌릴 수 있게','Make choices discoverable and reversible',[
  ['옵션이 있어도 찾기 어렵다면 필요한 순간에 쓰기 어렵습니다. 처음 설정 화면에서 카메라와 조준에 관한 선택을 알아볼 수 있게 하고, 플레이 중에도 다시 접근할 수 있게 하세요.','An option is less useful when it is hard to find. Make camera and aiming choices recognizable in initial settings and accessible again during play.'],
  ['설명에는 바뀌는 것과 남는 것을 함께 적을 수 있습니다. 예를 들어 도구의 조준은 분리하지만 다른 방향을 보는 조작은 유지된다고 알려 주는 식입니다.','Explain both what changes and what remains available. For example, tool aiming is separated while the ability to look in another direction remains.'],
  ['저장과 기본값 복원도 실제로 확인해야 합니다. 다시 실행하거나 입력 장치를 바꿨을 때 값이 달라지면, 플레이어는 같은 선택을 반복해서 찾아야 합니다.','Check saving and restoring defaults in practice. If values change after restarting or switching input devices, players may have to find the same choice repeatedly.'],
  ['이런 검수는 카메라 옵션의 동작을 확인합니다. 편안함은 사람마다 다르므로 별도의 피드백을 받아야 하며, 불편함을 참게 하는 테스트로 바꾸어서는 안 됩니다.','These checks verify how the camera options operate. Comfort requires separate individual feedback; testing should not become an exercise in enduring discomfort.']
 ]],
 ['11','같은 작업을 다른 방향에서 읽기','Read the same task from different positions',[
  ['마지막으로 구조물의 다른 면을 씻는 구간을 보겠습니다. 가까이 서서 표면을 따라가는 동안에는, 노즐과 물줄기가 어디로 향하는지 먼저 찾아보세요.','Finally, watch another face of the playground structure being cleaned. While following a nearby surface, first identify where the nozzle and spray point.'],
  ['일부를 씻은 뒤 옆으로 돌아가면 기둥과 판자의 배치가 달라집니다. 자리를 바꾸는 움직임은 새로운 면을 보여 주고, 그 뒤의 조준은 그 면에서 작업을 이어갑니다.','Moving around after cleaning part of a surface changes the arrangement of posts and planks. Repositioning reveals another face; aiming then continues the task on that face.'],
  ['위쪽 가로대를 향하는 컷에서는 카메라도 위를 봅니다. 배경 전체가 움직이는 순간과, 목표 주변에서 도구가 움직이는 순간을 나누어 읽어 보세요.','In the shot aimed at an overhead crossbar, the camera looks upward too. Distinguish moments when the whole background moves from moments when the tool moves around a target.'],
  ['앞에서 본 에임 모드의 아이디어는 이런 작업에서 조준과 보는 방향을 분리하는 것이었습니다. 그것이 모든 이동을 없애거나 모든 사람의 불편함을 없앤다는 뜻은 아닙니다.','The Aim Mode idea was to separate aiming from viewing direction during this kind of task. It does not mean eliminating every movement or everyone’s discomfort.'],
  ['예시를 검토할 때는 각각의 컷에서 무엇이 움직였는지 먼저 적어 보세요. 필요했던 이동, 조준을 위한 변화, 더해진 연출을 구분해야 어떤 선택을 제공할지 구체화됩니다.','When reviewing an example, first record what moves in each shot. Distinguishing necessary travel, aiming changes and added presentation makes the available choices more concrete.'],
  ['이 자료에서는 청소 동작이 실제로 이어지는 모습을 확인했습니다. 이제 게임을 만드는 입장에서, 같은 목표를 다른 조작 방식으로도 읽을 수 있는지 질문해 볼 수 있습니다.','Here we observed an actual cleaning task continuing across different views. As a developer, you can now ask whether the same target remains readable with another control method.']
 ]],
 ['12','효과보다 먼저 선택과 역할을 설계하기','Design the choices and responsibilities first',[
  ['오늘의 핵심은 카메라를 무조건 멈추라는 말이 아닙니다. 게임에 필요한 시점 이동과 도구의 조준, 추가 연출을 나누고 플레이어가 조절할 부분을 찾는 것입니다.','The point is not to stop the camera unconditionally. Separate necessary viewpoint movement, tool aiming and added presentation, then identify what players can control.'],
  ['실제 게임 장면에서는 무엇이 움직였는지, 설명 화면에서는 어떤 역할을 분리할지 살펴봤습니다. 옵션을 바꾼 뒤에도 목표와 현재 방향이 읽히는지 함께 확인하세요.','In actual game shots, we examined what moves; in the diagrams, what responsibilities could be separated. Check that the target and current orientation remain readable after changing an option.'],
  ['게임마다 필요한 조작은 다르고 사람마다 반응도 다릅니다. 한 가지 값을 정답으로 약속하기보다, 알아볼 수 있는 선택과 되돌리기, 실제 플레이 피드백을 준비하는 편이 좋습니다.','Games require different controls, and people respond differently. Instead of promising one correct value, provide understandable choices, a way to revert and feedback from actual play.'],
  ['내 게임에서도 카메라와 조준의 책임을 나누는 것부터 시작해 보세요. 이런 구현을 함께 배우고 싶다면 설명과 영상 마지막의 프로그래밍 과외 링크를 확인해 주세요.','In your own game, start by separating the responsibilities of the camera and aiming. To learn this kind of implementation together, see the programming coaching link in the description and ending.']
 ]]
];
const manifest=read(base+'project.json');
const ko={title:manifest.titles.ko,status:'source-matched-editorial-draft',scenes:rows.map(([id,title,_en,pairs])=>({id,title,lines:pairs.map(p=>p[0])}))};
const en={title:manifest.titles.en,status:ko.status,scenes:rows.map(([id,_ko,title,pairs])=>({id,title,lines:pairs.map(p=>p[1])}))};
write(base+'script/narration.ko.json',ko);write(base+'script/narration.en.json',en);
manifest.paths.scriptEn=base+'script/narration.en.json';
manifest.audio.backgroundMusic=read('projects/picking-sides/project.json').audio.backgroundMusic;
manifest.audio.mixStatus='pending-measured-narration-and-final-mix';
manifest.audio.musicFallbackScenes=['01','03','05','07','09','11'];
manifest.audio.sourceAudioPolicy='Official source commentary/music excluded because they compete with narration or are not independently cleared; keep original source audio locally. Continuous approved Nimbus remains.';
manifest.editing.intro={seconds:2,source:'motion-canvas/src/projects/small-window-game-design/intro-cats-v2/scene.tsx',originalCatLogo:true};
manifest.membershipOutro={...manifest.membershipOutro,kind:'original-screenshot',screenshot:'shared/assets/membership/member-list-20260929.png',cornerLogo:'shared/assets/branding/yamyamcoding-cats-original.png',displayedRows:12,title:'멤버쉽가입 감사드립니다.',truncatedHandlesReview:'pending'};
manifest.approvals={script:'pending-full-editorial-and-action-review',voiceSample:'reuse-existing-approved-Qwen3-TTS-1.7B-reference',bgm:'reuse-user-approved-continuous-Nimbus',final:'pending',publication:'private only; public release belongs to user'};
manifest.publishing={...manifest.publishing,uploadMaster:'output/motion-sickness-games/motion-sickness-games.captioned.mp4',cleanMasterLocalOnly:true,burnedCaptionsRequired:true,privacyStatus:'private',scheduledPublishAt:null};
manifest.editing.exampleInterleaving.planningPath=base+'planning/action-map.json';manifest.editing.exampleInterleaving.reviewStatus='pending-full-source-matched-script-review';
write(base+'project.json',manifest);
write(base+'production/script-authoring.json',{authoredAt:at,scriptLanguageCounts:rows.map(r=>({id:r[0],ko:r[3].length,en:r[3].length})),paragraphCount:60,sourceObservationFirst:true,rawReferenceTranscriptCopied:false,agentCreatedGameFootage:false,status:'pending-editorial-direct-review',audioCreated:false});
console.log('Independent12-scene60-paragraph bilingual draft saved; no speech approval or media completion.');
