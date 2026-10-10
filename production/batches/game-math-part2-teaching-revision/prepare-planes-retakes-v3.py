"""Retake only failed/overlong new lines; keep all22 supplied scenes and v2 takes.

The new footage duration is measured at1x. No gate is lowered and no original
line/audio is edited. Reused new lines keep their exact original WAV bytes.
"""
from pathlib import Path
import copy,json,hashlib,shutil,datetime

ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OLD='game-math-planes-teaching-additions-v2';NEW='game-math-planes-retakes-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

oldm=read(ROOT/f'projects/{OLD}/project.json');oldmap=read(B/'planes-addition-tts-map.json')
oldko={s['id']:s for s in read(ROOT/f'projects/{OLD}/script/narration.ko.json')['scenes']}
olden={s['id']:s for s in read(ROOT/f'projects/{OLD}/script/narration.en.json')['scenes']}
changes={
 'PB01':{1:(
  '바닥 높이를 이로 정합니다. 위쪽 법선은 영, 일, 영입니다. 내적은 같은 자리의 숫자를 곱한 뒤 더합니다. 이 법선과 점의 내적에는 와이 좌표만 남습니다. 결과가 바닥 높이 이와 같으면 점은 이 평면 위에 있습니다.',
  'Set the floor height to2 and choose the upward normal(0,1,0). A dot product multiplies matching components and adds them. Here only y remains. Matching the floor height2 places the point on this plane.')},
 'PB03':{1:(
  '바닥에 비스듬히 내려가면 옆으로 간 만큼 길이가 늘어납니다. 수직으로 내려가는 길이가 가장 짧습니다. 같은 바닥의 높이는 이입니다. 엑스와 제트는 유지하고 와이를 숫자 이로 바꿉니다. 기울어진 면에서는 단위 법선이 이 역할을 합니다.',
  'A slanted route adds sideways travel; the perpendicular route is shortest. The same floor has height2. Keep x and z and change y to2. A unit normal does this for a tilted plane.')},
 'PG04':{2:(
  '협동 플레이에서는 포털을 거쳐 끝이 있는 발판에 도착합니다. 이제 넓이로 안쪽 위치를 구합니다.',
  'In co-op, portals lead to a finite platform. Now use area to locate an interior point.')},
 'PG07':{1:(
  '다른 구간의 큐브와 이어지는 공중 이동입니다. 색을 읽으려면 먼저 표면의 어느 점인지 정해야 합니다.',
  'Another excerpt shows a cube, followed by airborne travel. To read color, first identify the point on the surface.'),2:(
  '파란 벽 접촉 뒤 튀어 오릅니다. 젤의 효과가 색 보간의 증거는 아닙니다.',
  'Contact with the blue wall leads to a bounce. The gel effect is not evidence of color interpolation.')},
}
newm=copy.deepcopy(oldm);newm.update(slug=NEW,title='평면·삼각형 신규 설명: 누락과 장면 길이 재녹음')
newm['paths']={k:v.replace(OLD,NEW) for k,v in newm['paths'].items()}
newm['tts']['outputDir']=newm['tts']['outputDir'].replace(OLD,NEW)
newm['tts']['filenameStem']=newm['tts']['filenameStem'].replace(OLD,NEW)
write(ROOT/f'projects/{NEW}/project.json',newm)
maps=[];ko=[];en=[];retained=[];changed=[]
for i,(ident,lines) in enumerate(changes.items(),1):
 ref=next(x for x in oldmap if x['additionId']==ident);a=copy.deepcopy(oldko[ref['ttsScene']]);z=copy.deepcopy(olden[ref['ttsScene']]);new_id=f'{i:02}';a['id']=z['id']=new_id
 for line in range(len(a['lines'])):
  if line in lines:
   prior=a['lines'][line];a['lines'][line],z['lines'][line]=lines[line]
   changed.append({'additionId':ident,'line':line,'previous':prior,'replacement':a['lines'][line],'reason':'Missing prerequisite/numeric phrase in raw v2 ASR' if ident.startswith('PB') else 'Measured narration longer than the clear native source group'})
  else:
   src=ROOT/oldm['tts']['outputDir']/f'chunks/{ref["ttsScene"]}-{line+1:02}.wav'
   dst=ROOT/newm['tts']['outputDir']/f'chunks/{new_id}-{line+1:02}.wav';dst.parent.mkdir(parents=True,exist_ok=True)
   assert src.exists();shutil.copyfile(src,dst);assert sha(src)==sha(dst)
   retained.append({'additionId':ident,'line':line,'source':src.relative_to(ROOT).as_posix(),'copy':dst.relative_to(ROOT).as_posix(),'sha256':sha(src),'text':a['lines'][line]})
 ko.append(a);en.append(z);maps.append({**ref,'ttsScene':new_id,'retakesV2Scene':ref['ttsScene']})
 for slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2']:
  lp=ROOT/f'projects/{slug}/production/lesson.json';lesson=read(lp)
  scene=next((s for s in lesson['scenes'] if s['id']==ident),None)
  if scene:
   scene['ko']=a['lines'];scene['en']=z['lines']
   if ident=='PG07':
    scene['intervals'][1]=[62.75,74.5];scene['maximumSeconds']=sum(y-x for x,y in scene['intervals'])
    scene['selection']['visibleBeforeActionAfter']='43–60 blue-platform contact/departure/arrival;62.75–74.5 cube followed by separately announced airborne funnel travel;78–84.5 blue wall contact and bounce'
    scene['selection']['chosenReason']='Re-reviewed all three .5s continuation sheets and full native source: cube is visible62.75–64.3, then airborne player motion is explicitly announced. This interval remains rejected for PG02 floor/normal teaching; it is relevant here to the point-versus-property question. No engine color algorithm inferred.'
   write(lp,lesson)
   for lang in ['ko','en']:
    sp=ROOT/f'projects/{slug}/script/narration.{lang}.json';script=read(sp);next(s for s in script['scenes'] if s['id']==ident)['lines']=scene[lang];write(sp,script)
for lang,scenes in [('ko',ko),('en',en)]:write(ROOT/f'projects/{NEW}/script/narration.{lang}.json',{'project':NEW,'language':lang,'status':'authorized-new-only-additive-retakes','scenes':scenes})
write(B/'planes-retakes-v3-tts-map.json',maps)
base=read(B/'baselines/game-math-planes-barycentric/lesson.json');original={s['id']:s for s in base['scenes']}
retained_originals=[s for slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2'] for s in read(ROOT/f'projects/{slug}/production/lesson.json')['scenes'] if s['id'] in original]
assert retained_originals==base['scenes']
audit={'project':NEW,'createdAt':datetime.datetime.now().astimezone().isoformat(),'original22DictionariesAndOrderExact':True,'retainedNewWavCopies':retained,'changedNewLines':changed,'existingV2WavsPreserved':True,'scriptSha256':{lang:sha(ROOT/f'projects/{NEW}/script/narration.{lang}.json') for lang in ['ko','en']},'projectManifestSha256':sha(ROOT/f'projects/{NEW}/project.json'),'voiceReferenceSha256':{key:sha(ROOT/newm['tts'][key]) for key in ['reference','referenceText']},'voiceSettingsExact':oldm['tts'],'currentHashAsrAndPixels':'pending'}
write(B/'planes-retakes-v3-pretts-audit.json',audit)
print(json.dumps({'newLines':len(changed),'reusedNewLines':len(retained),'originalsPreserved':True,'project':NEW}))
