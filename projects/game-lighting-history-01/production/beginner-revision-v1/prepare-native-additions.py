"""Narrow, directly inspected native actions and their independent beginner guides."""
import pathlib,json,datetime,hashlib
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[
 ('x02',2,'epic-robo-performance-2017',[(1442,1452)],'after','반사 진단 보기 / 최종 화면과 구별',None),
 ('x01',1,'epic-lighting-techniques-2017',[(3790,3794)],'after','삼각형으로 나눈 실제 메시',None),
 ('x07',7,'steam-quake-enhanced-2021',[(8,10),(13,14),(69,71),(59,60)],'before','벽 무늬와 밝기를 구별해서 보기',None),
 ('x09',9,'epic-lighting-techniques-2017',[(3812,3820)],'after','UV: 표면에 붙일 그림을 읽는 주소',None),
 ('x10',10,'bethesda-quake2-enhanced-2023',[(43,44),(46.5,48),(57,58)],'before','퀘이크 II · 최신판 실제 환경',None),
 ('x14',14,'epic-lighting-techniques-2017',[(1108,1114),(1126,1140)],'after','벽 조각의 경계 · 원인은 화면만으로 단정하지 않음',None),
 ('x16',16,'epic-robo-performance-2017',[(2616,2626)],'before','카메라가 다가가면 표면 무늬의 화면 크기가 변함',None),
 ('x29',29,'epic-lighting-techniques-2017',[(1062,1068),(1078,1089)],'after','벽에 붙인 그림 / 공간에 놓인 정보 지점',None),
 ('xsh',None,'epic-lighting-techniques-2017',[(2344,2362),(2364,2382)],'after-key','조명 전체 끄기 ≠ 그림자 설정 끄기','09-p2'),
 ('x37',37,'epic-lighting-techniques-2017',[(1918,1928),(1934,1942)],'after','먼 그림자 범위와 단계 설정 · 성능 향상 수치 아님',None),
 ('x36',36,'epic-lighting-techniques-2017',[(2258,2266+5/60)],'after','카메라 이동으로 가까운 모형과 먼 지형 구별',None),
 ('x44',44,'epic-post-processing-2017',[(3078,3085)],'before','구석의 주변 가림 · 카메라 접근',None),
]
guides=[
 ('x02','반사를 살피는 보기로 바꾸면, 같은 표면도 다르게 표시됩니다. 최종 게임 화면과 진단 화면을 구별하세요.','Switching to a reflection diagnostic changes how the same surfaces appear. Distinguish the final game view from a diagnostic view.'),
 ('x14','이 예에서는 벽의 넓은 면보다 조각 사이 경계가 먼저 눈에 띕니다. 저장한 빛이 이웃 면에서 자연스럽게 이어지는지도 확인해야 합니다. 화면의 경계만으로 원인을 하나로 단정할 수는 없습니다.','In this example, the seams between wall pieces stand out. Check whether stored lighting joins smoothly across neighboring surfaces. The visible seam alone does not establish a single cause.'),
 ('x29','카메라가 방 안으로 돌아오면 벽과 공간의 점이 함께 보입니다. 벽에 붙인 빛 그림과 공간에서 읽어 오는 빛 정보를 구별하세요. 점은 실제로 빛을 내는 전구가 아닙니다.','As the camera turns into the room, walls and spatial points appear together. Distinguish the lighting image attached to a wall from lighting information sampled in space. The points are not light-emitting bulbs.'),
 ('xsh','조명을 끄는 것과 그림자를 끄는 것은 다릅니다. 먼저 조명 전체의 영향을 빼니 지형이 어두워집니다. 다시 켠 뒤 그림자 관련 설정만 바꿉니다. 표면 방향 때문에 남는 명암과, 다른 면이 빛을 막아서 생기는 그림자를 구별해서 보세요.','Disabling a light differs from disabling shadows. Removing the whole light contribution first darkens the terrain. After restoring it, shadow settings are changed. Distinguish shading caused by surface orientation from shadows cast when another surface blocks light.'),
 ('x37','가까운 범위만 살핀 뒤에는 먼 지형도 확인합니다. 이 설정은 멀리 있는 그림자 범위와 단계 수를 다룹니다. 숫자만 읽지 말고 화면의 어느 범위를 담당하는지 함께 보세요.','After the nearby region, inspect distant terrain too. These settings control distant shadow coverage and cascade count. Read the settings together with the region of the view they cover.'),
 ('x36','카메라를 뒤로 빼면, 앞의 모형과 먼 지형이 어떻게 떨어져 있는지 보입니다.','Pulling the camera back reveals the spatial separation between the nearby objects and distant terrain.'),
]
registry=rd(P/'production/local/final-edit-v1/recipe.json')['sourceRegistry']
base=rd(P/'production/local/threejs-revision-v1/pair-caption-decoder-v3/plan.json')
native=[]
for key,packet,sid,intervals,where,label,anchor in rows:
 source=registry[sid];ranges=[{'startFrame':round(a*60),'endFrame':round(z*60)} for a,z in intervals]
 for r in ranges:
  assert all(n.get('sourceId')!=sid or n['role']!='actual' or min(r['endFrame'],n['sourceStartFrame']+n['frames'])<=max(r['startFrame'],n['sourceStartFrame']) for n in base['nodes']),(key,'overlap')
 native.append(dict(id=key,packetIndex=packet,sourceId=sid,path=source['localFile'],sourceSha256=source['sha256'],intervals=ranges,frames=sum(r['endFrame']-r['startFrame'] for r in ranges),where=where,anchor=anchor,focusKo=label,sourceClass='engine-demo' if sid.startswith('epic-') else 'independent-gameplay',sourceAudio=False,loop=False,slowdown=False,directFrameReview=True,exactBoundaryAndCropReview=False))
# Book-demo p3 remains a native/material graph explanation; its whole new
# narration fits the retained packet plus the retained10.433s graph. No3D
# asset is substituted for an actual material-export operation.
expDelta=6000-97
assert abs(sum(n['frames'] for n in native)-expDelta*1.5)<=1
wr(H/'native-additions.json',dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=native,additionalActualFrames=sum(n['frames'] for n in native),additionalExplanationFrames=expDelta,ratioRoundingErrorFrames=sum(n['frames'] for n in native)-expDelta*1.5,wholeOutputApproved=False,allNativeFinalPixelsApproved=False,guideTextDirectlyReviewed=True,guideRows=[dict(id=k,ko=ko,en=en) for k,ko,en in guides],observations={'inspection5':'Quake title cards and stationary shadow-camera tail excluded; only actual environmental views kept.','inspection6':'Far-shadow camera2258–2265.583 is camera movement; checkbox/FPS claims excluded. AO3078–3085 approaches crevices. Quake2opening14–28 title/logo rejected.'}))
for lang,idx in [('ko',1),('en',2)]:wr(H/f'native-additions.{lang}.json',dict(project='game-lighting-history-01',language=lang,title='Additional native prerequisite guidance',scenes=[dict(id=r[0],title=r[0],lines=[r[idx]]) for r in guides]))
m=rd(H/'terminology-r1.project.json');m['paths']={k:f'projects/game-lighting-history-01/production/beginner-revision-v1/native-additions.{lang}.json' for k,lang in [('script','ko'),('scriptEn','en')]};m['tts'].update(outputDir='shared/output/narration/game-lighting-history-01/beginner-native-additions',filenameStem='game-lighting-history-01-beginner-native-additions');m['voiceRepair']['scope']='Six independently authored guides for directly inspected added native actions; all prior PCM retained.';wr(H/'native-additions.project.json',m)
print(json.dumps(dict(nativeFrames=sum(n['frames'] for n in native),guides=len(guides),explanationDelta=expDelta)))
