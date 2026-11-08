"""Eight changed/additional paragraphs; earlier takes and every baseline PCM stay intact."""
from pathlib import Path
import json,copy
H=Path(__file__).resolve().parent; H2=H.parent/'room-v2'; P=H.parents[1]; R=P.parents[1]
brief=json.loads((H/'additional-narration-brief.json').read_text('utf8'))
base=json.loads((H2/'revision-plan.json').read_text('utf8'))
translations={
'V31': 'In the small game view, the character edges looked blurred. Rather than enlarge the source, we clean it for the number of pixels it actually occupies on screen: ninety-six by one hundred thirty-two. PixelOE refines the shape, then every pose receives the same thirty-two-color palette and binary edge transparency. The game draws this image at its native size. When enlarging the whole view, Nearest Neighbor sampling avoids blending adjacent pixels. We also avoid shrinking it so far that the face and hands disappear.',
'V32': 'Even with eight poses, feet that move too fast make the character appear to slide. While a foot supports the body on the floor, it should move backward relative to the body by the distance the body travels forward. We checked both leg length and the supporting foot’s displacement. In the cleaned sprites, one complete walking cycle corresponds to about eighty-three game pixels. The previous setting was thirty-eight, so the cycle repeated more than twice over the same distance. Now the actual distance traveled advances the pose. When movement stops, the feet stop too.',
'V33': 'Next, we add writing at the central worktable. The room-wide framing and character scale stay the same; the desk moves to the center. We create the approach, lowering, hand-on-ledger, and pen-down poses in sequence. The ledger is a separate Pixelbolt prop, fixed on the tabletop. During the writing loop, small pen and arm movements connect without rocking the whole body. The table front draws ahead of the legs, while the hands and pen draw above the table, making the seated writing contact clear.',
'V34': 'Flame effects also need the correct placement. The bottom of the flame meets the wick inside the hanging lantern, and the tabletop candle uses the same rule. The flames switch off during the day. At night, the room darkens and warm light appears around these two points. The light and flame use the same position values so that they cannot drift apart. This makes nightfall clearer than changing the background color alone.',
'V35': 'In the finished room, you can choose five actions and four weather states. The workshop radio includes twenty lo-fi tracks that their creator released under CC0. Press play to hear them in sequence; after the last track, playback returns to the first. You can also skip, shuffle, and change the volume. Open the game link in the description to sit, write, and listen while seeing how the results from these tools work together.'
}
insert_after={'V31':'R21','V32':'R17','V33':'R23','V34':'R20','V35':'30'}
new={}
for row in brief['passages']:
 ident=row['id']; new[ident]={'id':ident,'title':row['title'],'ko':' '.join(row['lines']),'en':translations[ident],'evidence':'room-v3 actual tool/game execution records','screenPlan':row['visual'],'audio':'new Qwen same approved voice','originalPcmPreserved':False}
changes={
'R04':('이번 캐릭터 원화에는 챗 지피티의 이미지 생성 기능을 사용했습니다.', '이번 캐릭터 원화에는 챗지피티 이미지 생성을 사용했습니다.'),
'R16':('실제 게임에 배치하자 의자와 캐릭터가 맞지 않는 부분이 보였습니다.', '실제 게임에 놓으니 의자와 캐릭터가 맞지 않는 부분이 보였습니다.'),
'R20':('방에는 불꽃, 비, 눈', '방에는 횃불, 비, 눈')
}
scenes=[]; retakes=[]
for original in base['scenes']:
 row=copy.deepcopy(original)
 if row['id'] in changes:
  replacement,old=changes[row['id']]; assert old in row['ko'],(row['id'],row['ko']); row['ko']=row['ko'].replace(old,replacement)
  if row['id']=='R04':row['en']=row['en'].replace('We used ChatGPT image generation','We used ChatGPT’s image-generation feature')
  if row['id']=='R20':row['en']=row['en'].replace('torch, rain, and snow','flame, rain, and snow')
  retakes.append(row)
 scenes.append(row)
 for ident,after in insert_after.items():
  if after==row['id']:scenes.append(new[ident])
plan={**base,'revision':'room-v3','scenes':scenes,'currentState':'new game assets integrated; five adjacent explanations and three narrow retakes; final mix waits for final game capture'}
(H/'revision-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),'utf8')
(H/'full-narration.ko.txt').write_text('\n\n'.join(s['ko'] for s in scenes),'utf8')
changed=[s for s in scenes if s['id'] in new or s['id'] in changes]
(H/'narration-additions.ko-en.json').write_text(json.dumps({'scenes':changed,'preservation':'all baseline30 and unchanged13 room-v2 chunks preserved; earlier3 takes retained for audit'},ensure_ascii=False,indent=2),'utf8')
(H/'added.ko.json').write_text(json.dumps({'scenes':[{'id':s['id'],'title':s['title'],'lines':[s['ko']]} for s in changed]},ensure_ascii=False,indent=2),'utf8')
m=json.loads((H2/'tts-manifest.json').read_text('utf8'));m['paths']['script']=(H/'added.ko.json').relative_to(R).as_posix();m['tts'].update(outputDir=(P/'production/local/room-v3/voice').relative_to(R).as_posix(),filenameStem='room-v3-additions')
(H/'tts-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
for name in ['run_audio.py','asr_additions.py']:
 text=(H2/name).read_text('utf8').replace("production/local/room-v2","production/local/room-v3")
 (H/name).write_text(text,'utf8')
print('Prepared',len(scenes),'total scenes;',len(changed),'voice passages; baseline files unchanged.')
