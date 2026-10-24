from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
slug='game-math-orientation-matrices';P=R/'projects'/slug/'production/concept-fit-v2'
sources=read(P/'composition.json')['sources']
sources['besiege']['audioPath']='projects/game-math-orientation-matrices/production/local/concept-fit-v2/audio/besiege-source.m4a'
sources['totk']['rightsEvidence']='production/batches/private-math-concept-fit-20261023/m03-narration-edits.json#rights'
sources['besiege']['rightsEvidence']='production/batches/private-math-concept-fit-20261023/m03-narration-edits.json#rights'
def patch(scene,src,start,duration,title,phases,meaning,notes,tracks=[]):
 return dict(scene=scene,source=src,offset=0,duration=duration,title=title,meaning='',segments=[dict(kind='motion',**{'in':start},seconds=duration)],guides=[],phases=phases,tracks=tracks,modelCrop=[80,210,850,750],sourceReview=notes,speechMapping=meaning)
patches=[
 patch('02','totk',995,15,'위치와 자세를 따로 조절하기',[(0,4,'바닥에 놓인 돛'),(4,8,'들어 올리기 → 위치 변화'),(8,12,'돛 세우기 → 자세 변화'),(12,15,'통나무에 붙인 결과')],
 '0–4.56s game introduction;4.74–9.7s lying sail/pickup/stand;9.88–15.4s position versus orientation. The full source action is shown, then the unchanged explanation continues.',
 'Source995–1010 inspected at1fps; uninterrupted pickup→upright rotation→attachment→release. End before the new whole-raft pickup.',[dict(points=[[0,.60,.66,90],[2,.60,.64,90],[3,.61,.63,90]])]),
 patch('05','besiege',53,16,'선택한 부품과 고정된 주변 비교',[(0,6,'주황색: 선택한 부품'),(6,10,'주변은 고정 · 회전 도구 선택'),(10,16,'선택한 부품만 기울이기')],
 '0–4s selecting assembly;4.18–8.5s selected orange versus surroundings;8.68–13.08s body up rotates with the part;13.26s world/screen-up contrast. Own model retains explicit axes.',
 'Source53–69 inspected at1fps. Selection shown before rotation; actual ring rotation63–68. Camera changes58 and63; our marks clear at source cuts. No numeric game angles inferred.'),
 patch('08','totk',232,24,'고리의 앞쪽과 이동 방향 구분',[(0,5,'누워 있는 고리를 선택'),(5,11,'고리를 들어 세우기'),(11,15,'세운 고리를 판에 붙이기'),(15,22,'방향을 유지하며 레일로 이동'),(22,24,'레일에 걸린 결과')],
 '0–4.48s lying hook;4.66–10.5s opening follows rotation;10.72–14.92s fixed world comparison;15.27–20.31s local versus world movement. This preserves selection, rotation, attachment and placement instead of a9s insert.',
 'Source232–256 inspected at2fps; separate pickup237,rotation239–242,attachment244,whole-platform translation247–253,release254. Native in-game axes/highlight carry the moving target; no guessed3D ring.',[dict(points=[[0,.57,.46,55],[2,.57,.46,55],[4,.57,.46,55]])]),
 patch('11','besiege',33,8,'물체는 그대로 · 보는 위치만 변경',[(0,3.5,'정면에서 본 조립 물체'),(3.5,6.5,'위쪽으로 시점 이동'),(6.5,8,'같은 물체를 다른 방향에서 관찰')],
 '0–4.48s object fixed and camera changes;4.66–9.46s front versus top appearance. Cut back to preserved camera/coordinate model before subsequent source object-editing.',
 'Source33–41 inspected at1fps: front→top camera motion37–38,selection39–40, then cut out before selected assembly manipulation.8s includes complete change; no loop.'),
 patch('14','totk',1008,12,'돛의 화면 폭과 실제 모양 구분',[(0,3,'세워진 돛을 정면에서 보기'),(3,8,'시점이 달라지며 좁아 보이는 돛'),(8,12,'형태는 그대로 · 화면 모습만 변화')],
 '0–5.36s front versus oblique visible width;5.60–9.70s not physical scaling;9.98–13.30s camera/distance affects appearance. Previously narration referred to the sail with no game at all; now the real attached sail remains visible.',
 'Source1008–1020 inspected at1fps; raft pickup then camera yaw with near edge-on sail; no artificially held frame.1008–1010 overlaps prior end as explicit same-object return; only one teaching example counted for this new camera claim.')]
out=dict(episode='M03-original',slug=slug,revision='gameplay-motion-v4',patchSet='reviewed-native-2',status='source-sequence-reviewed',newTts=False,sources=sources,patches=patches,sourceReview={'method':'Ordered decoded source frames at1fps and2fps; not a claim of continuous listening','sheets':['totk-sail/sheet-0.jpg','totk-sail/sheet-1.jpg','totk-ring/sheet-0.jpg','besiege/sheet-0.jpg','besiege/sheet-1.jpg','besiege/sheet-2.jpg'],'folder':'shared/output/private-math-gameplay-20261024/motion-v4/source-review','nativeSpeed':1,'analyticalFreeze':0},preservation={'narration':'unchanged PCM','duration':'unchanged','explanation':'Original model during comparison; full original explanation outside patches'},coverage={'previousNativeSeconds':39,'newNativeSeconds':75,'examples':5,'notAQuotaPass':True,'remaining':'Encoded source/voice alignment and caption/mobile QA pending'})
(B/'m03-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('M03:5 native action examples,75seconds; render QA pending')
