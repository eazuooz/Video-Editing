"""Author five independently phrased teaching scripts and reuse verified audio tooling."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
BASE=R/'projects/shorts-interior-mapping-window/production'
DATA=[
('shorts-titanfall-time-shift',[
('game','버튼을 누르자,|불타던 복도가 멀쩡해집니다.|타이탄폴 투의 시간여행이죠.','Press the button.|The burning corridor becomes intact.|This is Titanfall 2’s time shift.'),
('reveal','그런데 이 장치는|플레이어를 위아래로 옮깁니다.','Yet this device|moves the player up and down.'),
('stack','과거와 현재의 맵을|같은 위치에 맞춰,|하나는 위에, 하나는 아래에 놓은 거예요.','The past and present maps|are aligned with each other,|one above the other.'),
('transfer','버튼을 누르면|두 맵 사이의 높이 차이만큼|위치를 순간이동시킵니다.','Press the button|and teleport by the height difference|between the two maps.'),
('numbers','우리 시연에서 두 층의 간격이 십 미터라면,|앞뒤 위치는 그대로 두고|높이에 십 미터를 더하는 겁니다.','If our demo floors are 10 metres apart,|keep the horizontal position|and add 10 metres to the height.'),
('view','카메라 방향도 이어지니|플레이어에게는 장소가 바뀐 게 아니라|시간이 바뀐 것처럼 보이죠.','The camera keeps its direction,|so the player perceives|a change of time in the same place.'),
('game2','한 시대에서 막힌 길을|다른 시대에서 지나간 뒤|다시 돌아올 수도 있습니다.','A path blocked in one era|can be crossed in the other|before switching back.'),
('close','맵 두 개와 순간이동을 맞물려,|공간 이동을 시간여행으로 느끼게 만든 거예요.','Two maps and a teleport work together|to make a spatial jump feel like time travel.')]),
('shorts-superliminal-perspective',[
('game','작은 물건을 집었는데,|내려놓으니 거대해집니다.|슈퍼리미널의 비밀은 뭘까요?','Pick up a small object.|Put it down, and it is enormous.|What is Superliminal doing?'),
('reveal','멀리 있는 물체는 작게 보이죠.|여기서는 멀리 옮길수록|물체 자체를 키웁니다.','Distant objects normally look smaller.|Here, moving an object farther away|also makes it physically larger.'),
('numbers','거리가 두 미터에서 여섯 미터로,|세 배가 되면,|물체의 크기도 세 배로 키우는 거예요.','Move it from 2 metres to 6 metres:|three times farther,|and three times larger.'),
('view','그러면 화면에서 보이는 크기는 같아도,|옆에서 보면|물체가 정말 커져 있습니다.','Its apparent size stays the same,|but viewed from the side,|the object really has grown.'),
('rays','이런 시각적 착시를 강제 원근이라고 합니다.|게임은 물체의 보이는 표면에 여러 광선을 쏴,|벽과 부딪히지 않는 위치를 찾습니다.','This illusion uses forced perspective.|The game casts rays across the visible surface|to find a position that fits without collision.'),
('game2','물체를 놓으면|바뀐 크기가 실제 공간에 남습니다.|작은 블록이 발판이 되고,|큰 물건이 작은 통로를 통과하죠.','Release the object,|and its changed size remains in the world.|A small block becomes a platform;|a large object can fit a narrow opening.'),
('close','보이는 크기를 유지한 채|거리와 실제 크기를 함께 바꾸면,|원근법이 퍼즐의 규칙이 되는 겁니다.','Keep its apparent size,|change distance and physical size together,|and perspective becomes a puzzle rule.')]),
('shorts-ghost-leaf-updraft',[
('game','고스트 오브 쓰시마의 이 낙엽들.|개발 중에는 모닥불에 떨어져도|타지 않는 문제가 있었습니다.','These leaves in Ghost of Tsushima|had a bug during development:|they could fall into campfires without burning.'),
('problem','불 속에 멀쩡한 낙엽이 남으면|아무래도 이상하죠.|개발자는 의외의 방법으로 고쳤습니다.','Intact leaves sitting in a fire|look strange.|The fix was surprisingly simple.'),
('reveal','불에 바람을 넣은 겁니다.|위로 부는 바람을 만드는|윈드 이미터를 배치했어요.','They added wind to the fire:|a wind emitter|pushing air upward.'),
('off','우리 시연에서도|바람을 끄면 낙엽이 그대로 내려갑니다.|이제 불 위의 바람만 켜 볼게요.','In our reconstruction,|leaves fall straight down with the wind off.|Now turn on just the updraft above the fire.'),
('on','같은 낙엽이 불 위에 다가가면,|상승하는 바람에 반응해서|위로 밀려나죠.','The same leaves approach the fire,|react to the upward wind|and are pushed away.'),
('compare','쓰시마에서도 이 상승기류로|대부분의 낙엽이 불에 들어가는 걸 막았습니다.|불에 반응하는 작은 디테일까지 생겼고요.','In Tsushima, the updraft|kept most leaves out of the fire.|It added a convincing little interaction too.'),
('close','낙엽을 태우는 복잡한 기능 대신,|불에 들어가는 상황부터 줄인 겁니다.|문제의 원인을 바꾸는 것도 게임 개발의 기술이죠.','Instead of adding a burning simulation,|they reduced the situation causing the bug.|Changing the conditions can solve the problem.')]),
('shorts-gears-inertialization',[
('game','달리다가 멈추는 캐릭터.|동작을 바로 바꾸면|자세가 툭 튀기 쉽습니다.','A character stops running.|Switch animations instantly,|and the pose can snap.'),
('snap','기어스 오브 워 포에 쓰인 관성화는|새 동작으로 먼저 바꾼 뒤,|튀는 차이를 부드럽게 없애요.','Inertialization, used in Gears of War 4,|switches to the new motion first,|then smoothly removes the discontinuity.'),
('difference','가령 팔의 목표 각도가 이십 도인데,|방금 전 팔은 오십 도였다면,|삼십 도의 차이를 기억합니다.','Suppose the target arm angle is 20 degrees|but the previous angle was 50.|Keep the 30-degree difference.'),
('decay','새 동작에 이 차이를 더하고,|시간이 지나며 영으로 줄입니다.|그러면 오십 도에서 끊김 없이 이어지죠.','Add that offset to the new motion,|then reduce it to zero over time.|The arm starts continuously from 50 degrees.'),
('velocity','자세만 맞추는 게 아닙니다.|직전에 움직이던 속도도 반영해서|갑자기 꺾이는 느낌을 줄여요.','It also keeps track|of the preceding motion’s velocity|to reduce abrupt changes in movement.'),
('compare','보통은 전환 중에 두 동작을 계속 계산하지만,|관성화는 새 동작과 남은 차이를 계산합니다.|이전 동작 전체를 계속 재생할 필요가 줄어들죠.','A conventional blend evaluates both motions.|Inertialization evaluates the target and residual offset.|The old motion no longer needs continued evaluation.'),
('close','관성화, 이너셜라이제이션.|움직임의 연결감은 남기고,|이전 동작을 계산하는 비용을 아끼는 겁니다.','Inertialization|preserves continuity of motion|while saving the old animation’s evaluation cost.')]),
('shorts-portal-recursion',[
('game','포털 안에 또 포털이 보입니다.|그러면 화면을|무한히 다시 그려야 할까요?','There is another portal inside this portal.|Does the renderer|have to redraw forever?'),
('reveal','먼저 포털은,|다른 출구 쪽에서 본 풍경을|입구의 구멍 안에 보여줍니다.','A portal shows|the view from the other exit|inside the entrance opening.'),
('mask','포털 게임은 스텐실 버퍼를 활용했어요.|화면에서 포털 안쪽에 표시를 해 두고,|그 영역에만 다른 풍경을 그리는 방식입니다.','Portal used a stencil buffer.|Mark the pixels inside the opening|and draw the other view only in that region.'),
('recursive','그 풍경 안에 포털이 또 보이면,|같은 작업을 한 단계 더 합니다.|이 반복을 재귀 렌더링이라고 해요.','If another portal is visible inside,|repeat the operation one level deeper.|This is recursive rendering.'),
('depth','우리 시연에서 반복을 한 번에서 세 번으로 늘리면,|안쪽 풍경은 더 깊어지지만,|그려야 하는 화면도 늘어납니다.','Increase our demo from one level to three:|the view reaches deeper,|but more views must be rendered.'),
('limit','실제로 무한 번 계산할 수는 없죠.|반복 깊이와 보이는 범위를 제한해서,|필요한 부분만 그립니다.','A renderer cannot compute infinitely many views.|Limit recursion depth and the visible region|to draw the parts that matter.'),
('close','끝없이 이어지는 것처럼 보여도,|그 뒤에는 유한한 화면과|정교한 가리개가 있는 겁니다.','It can look endless,|yet behind it are a finite set of views|and carefully restricted drawing regions.')])]

def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for slug,pars in DATA:
 p=R/'projects'/slug; clauses=[]; lines=[];sections=[]
 for i,(section,ko,en) in enumerate(pars):
  kk=ko.split('|');ee=en.split('|');assert len(kk)==len(ee),(slug,i)
  lines.append(' '.join(kk));sections.append({'id':section,'paragraph':i,'firstCue':f'p{i+1}-1','purpose':section})
  for j,(k,e) in enumerate(zip(kk,ee),1):clauses.append({'id':f'p{i+1}-{j}','lineIndex':i,'spoken':k,'ko':k,'en':e})
 doc={'slug':slug,'revision':'distinctive-v1','scenes':[{'id':'main','lines':lines}]}
 save(p/'script/narration.spoken.ko.json',doc);(p/'script/narration.ko.txt').write_text('\n\n'.join(lines)+'\n',encoding='utf8');save(p/'script/clauses.json',{'clauses':clauses,'pronunciationAliases':{}})
 save(p/'production/section-plan.json',sections)
 m=json.loads((BASE/'tts-manifest.json').read_text(encoding='utf8'));m.update(slug=slug,revision='distinctive-v1');m['paths']['script']=str((p/'script/narration.spoken.ko.json').relative_to(R)).replace('\\','/');m['tts'].update(outputDir=f'projects/{slug}/production/local/audio-v1/voice',filenameStem='narration',gpuProfileReason='CPU-only while user Unity editors remain open; approved Qwen model and voice reference retained.');save(p/'production/tts-manifest.json',m)
 for name in ['assemble-paragraphs.py','render-voice.py','transcribe.py','time-captions.py','finish-audio.py','finish-video.py']:
  text=(BASE/name).read_text(encoding='utf8').replace('shorts-interior-mapping-window',slug).replace('interior-mapping-v1','distinctive-v1').replace('audio-r2','audio-v1').replace('voice/interior.wav','voice/narration.wav')
  if name=='transcribe.py':text=text.replace("if control.get('selectedShortVideo')!=P.name or control.get('shortsDirectSelection',{}).get('selectedRevision')!=REVISION:","if P.name not in control.get('shortsBatchAuthorization',{}).get('slugs',[]):")
  if name=='finish-video.py':
   a=text.index('def guard():');b=text.index('\ndef ass_filter',a);text=text[:a]+"def guard():\n    from audio_revision import guard as current_guard\n    return current_guard()\n"+text[b:]
  if name=='finish-audio.py':text=text.replace("'musicOnlyQuietSpeechDip': [39.7, 41.5, 8.0]","'musicOnlyQuietSpeechDip': [0, 0, 0]")
  (p/'production'/name).write_text(text,encoding='utf8')
 text=(BASE/'audio_revision.py').read_text(encoding='utf8').replace('interior-mapping-v1','distinctive-v1').replace('audio-r2','audio-v1').replace('voice/interior.wav','voice/narration.wav')
 text=text[:text.index('def guard():')]+'''def guard():
    control=read(R/'shared/publishing/video-production-control.json')
    auth=control.get('shortsBatchAuthorization',{})
    project=read(P/'project.json')
    if (auth.get('id')!='explicit-five-distinctive-shorts-20261024' or auth.get('status')!='active'
        or P.name not in auth.get('slugs',[]) or not auth.get('fullProductionAuthorized')
        or project.get('currentRevision')!=REVISION):
        raise RuntimeError('Finite five-Short authorization changed; preserve work.')
    plan=read(P/'planning/production-plan.json')
    if not plan.get('independentFootageViewed') or not plan.get('scriptFinalized'):
        raise RuntimeError('Review selected footage and narration before media generation.')
    return control
'''
 (p/'production/audio_revision.py').write_text(text,encoding='utf8')
 project=json.loads((p/'project.json').read_text(encoding='utf8'));project['paths']['script']=m['paths']['script'];project['video']={'width':1080,'height':1920,'fps':60};save(p/'project.json',project)
print('Five scripts authored; source-review guards remain closed until evidence recorded.')
