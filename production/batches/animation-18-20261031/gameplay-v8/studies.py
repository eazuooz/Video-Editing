"""Inspected independent game actions and topic-specific, explicitly editorial studies."""
from common import *
import sys
sys.path.insert(0,str(BATCH/'footage-substitution-audit-20261115'))
from audit_pictures import source_catalog

# All times are in the cached independent recording, not in the edited lesson.
# A crop is a detail view; the complete, unflipped recording remains in its inset.
SOURCES={
 'great':('great',17.8,20.6,[0,1,1.9,2.7],(400,100,1400,1060)),
 'axe':('hades-training',39.1,41.9,[0,.6,1.5,2.6],(630,230,1320,940)),
 'jab':('zss-retained',2.8,4.8,[0,.45,.7,1.8],None),
 'peach':('peach-sword',17.5,20.7,[0,.8,2,3.1],(500,100,1470,1060)),
 'luigi':('luigi-run',8,11,[0,.7,1.5,2.9],None),
 'hug':('spiritfarer-embrace',7,10,[0,.6,1.9,2.9],(700,150,1500,1000)),
 'ring':('ringfit-warrior1',14,17,[0,.8,1.7,2.9],(0,50,530,1040)),
 'ring-flow':('ringfit-warrior1',15,17.8,[0,.7,1.7,2.7],(0,50,530,1040)),
 'ring-feet':('ringfit-warrior1',40,43,[0,.7,1.7,2.9],(550,150,1230,1080)),
 'maelle':('maelle-no-commentary',55.5,58,[0,.6,1.3,2.4],(720,110,1800,1060)),
 'goopy':('cup-goopy',22.1,25.1,[0,1.15,1.7,2.9],(90,100,1200,1060)),
 'juri':('juri-hit-b',30.65,32.1,[0,.3,.7,1.4],(700,100,1770,1060)),
 'lili':('lili-practice',20.43,22.47,[0,.45,.8,1.9],(480,180,1420,940)),
 'punch':('marisa-follow',10.5,13,[0,.6,1.2,2.4],(300,130,1500,1060)),
 'paper':('paper-mario',25.4,28.4,[0,.8,1.4,2.9],None),
 'lune':('lune-clean-camp',21,24,[0,.8,1.7,2.9],(1050,150,1660,790)),
 'animal':('acnh-catch-expression',11.25,14.25,[0,.8,1.7,2.9],(580,160,1220,820)),
 'dee-right':('sf2-deejay',15.5,16.2,[0,.2,.4,.65],(100,220,800,1050)),
 'dee-left':('sf2-deejay',29.4,30.1,[0,.2,.4,.65],(950,220,1490,1050)),
 'horizon':('hzd-aim-move',8.5,11.5,[0,.6,1.7,2.9],None),
 'splatoon':('splatoon-moving-fire',21.5,24.5,[0,.8,1.7,2.9],None),
 'bottle-neck':('alyx-grip',19,20.4,[0,.4,.8,1.3],(620,180,1880,1080)),
 'bottle-body':('alyx-grip',25.4,26.3,[0,.2,.5,.8],(0,100,820,1080)),
 'hands':('ghostwire-cast',7,10,[0,.8,1.7,2.9],None),
 'lance':('mhw-lance',13.5,16.5,[0,.8,1.7,2.9],(500,120,1810,1050)),
 'ribbon':('arms-ribbon',4,7,[0,.8,1.7,2.9],None),
 'luigi-head':('luigi-lobby',29.5,32.5,[0,.8,1.7,2.9],(420,240,1000,850)),
 'goose':('goose-basket-start',5,8,[0,.8,1.7,2.9],(650,270,1720,1060)),
 'trico':('trico-look',18.5,21,[0,.7,1.4,2.4],(500,200,1400,1080)),
}

# key -> bank, visual grammar, focus, ordered observed phases.
STUDIES={'A03': {'attack': ('great', 'phases')},
 'A04': {'anticipation': ('axe', 'timing'),
         'charge': ('axe', 'phases'),
         'jab': ('jab', 'startup'),
         'weight': ('axe', 'phases')},
 'A05': {'impact': ('peach', 'pose'),
         'size': ('peach', 'pose'),
         'plane': ('peach', 'space'),
         'top': ('peach', 'space'),
         'twist': ('peach', 'pose'),
         'outline': ('peach', 'pose'),
         'camera': ('peach', 'space')},
 'A07': {'near': ('luigi-head', 'size'), 'far': ('luigi-head', 'size'), 'gesture': ('peach', 'size')},
 'A08': {'overview': ('ring', 'pose'),
         'flow': ('ring-flow', 'pose'),
         'edge': ('ring', 'pose'),
         'stance': ('ring-feet', 'weightbase')},
 'A09': {'fist': ('goopy', 'squash')},
 'A10': {'recoil': ('juri', 'phases'),
         'height': ('juri', 'pose'),
         'root': ('juri', 'displacement'),
         'turn': ('juri', 'space')},
 'A11': {'kick': ('lili', 'timing'), 'upper': ('punch', 'timing'), 'returning': ('punch', 'return')},
 'A12': {'expression': ('lune', 'face'),
         'eyes': ('animal', 'face'),
         'mouth': ('lune', 'face'),
         'distance': ('animal', 'size')},
 'A13': {'mirror': ('dee-right', 'direction'), 'direction': ('dee-right', 'space'), 'tool': ('dee-right', 'prop')},
 'A14': {'blend': ('horizon', 'blend'),
         'duration': ('horizon', 'blend'),
         'guard': ('splatoon', 'weights'),
         'slope': ('horizon', 'slope')},
 'A15': {'grip': ('bottle-neck', 'hand'), 'keys': ('hands', 'hand'), 'scale': ('hands', 'size')},
 'A16': {'range': ('lance', 'collision'), 'path': ('lance', 'space'), 'active': ('lance', 'active')},
 'A17': {'fkik': ('ribbon', 'fkik'), 'hint': ('ribbon', 'hint')},
 'A18': {'head': ('luigi-head', 'rotation'),
         'tilt': ('luigi-head', 'rotation'),
         'wrist': ('trico', 'wrist'),
         'curves': ('goose', 'curves'),
         'gaze': ('luigi-head', 'gaze')}}

# Display language is Korean; the source-spec shorthand is kept independent of speech.
FOCUS={('A04', 'anticipation'): '첫 변화가 보여야 공격을 예상할 수 있습니다',
 ('A04', 'charge'): '힘을 모으는 자세 → 힘을 푸는 움직임',
 ('A04', 'jab'): '준비 동작이 거의 없는 빠른 잽',
 ('A04', 'weight'): '큰 무기를 들고 내리는 몸의 방향',
 ('A05', 'size'): '접힌 몸과 펼쳐진 몸의 차이',
 ('A05', 'plane'): '상대를 향하는 기준 평면',
 ('A05', 'top'): '화면의 겹침과 공간의 깊이',
 ('A05', 'twist'): '공격하는 팔 · 균형을 잡는 몸',
 ('A05', 'outline'): '팔과 몸통 사이에 남는 빈 공간',
 ('A05', 'camera'): '보는 방향이 바뀌면 겹침도 달라집니다',
 ('A08', 'flow'): '머리 → 몸통 → 골반으로 이어지는 흐름',
 ('A08', 'edge'): '팔과 몸 사이 빈 공간을 확인',
 ('A08', 'stance'): '발의 배치와 앞무릎을 함께 관찰',
 ('A10', 'height'): '어디에 닿았고, 어느 부위가 반응했나',
 ('A10', 'root'): '몸의 자세와 전체 위치 이동을 분리',
 ('A11', 'returning'): '공격과 복귀가 똑같은 길을 돌아오지 않게',
 ('A12', 'eyes'): '눈을 뜬 순간과 감은 순간',
 ('A12', 'mouth'): '입 · 눈 · 눈썹의 관계',
 ('A13', 'mirror'): '실제로 양쪽을 향한 두 장면 · 영상 좌우 반전 아님',
 ('A13', 'tool'): '손과 소품이 함께 바뀌는 관계',
 ('A14', 'duration'): '같은 두 자세 · 전환 시간만 변경',
 ('A14', 'guard'): '입력 방향과 혼합 비중',
 ('A14', 'slope'): '지면에 맞춘 발 목표',
 ('A15', 'grip'): '병의 목과 몸통을 쥔 서로 다른 손 모양',
 ('A15', 'keys'): '연속 움직임과 미리 준비한 손 모양',
 ('A16', 'range'): '같은 무기 경로 · 다른 판정 범위',
 ('A16', 'active'): '같은 무기 경로 · 다른 활성 시간',
 ('A17', 'fkik'): '관절에서 손으로 / 손 목표에서 관절로',
 ('A17', 'hint'): '같은 손 목표 · 다른 팔꿈치 방향',
 ('A18', 'curves'): '축별 곡선과 같은 시각의 회전을 연결',
 ('A18', 'gaze'): '머리 방향과 눈동자 방향이 합쳐진 시선',
 ('A18', 'wrist'): '손의 위치와 손목의 회전을 따로 관찰'}

KOREAN={
 'A03':('준비 → 타격 → 후속 동작',['대기','준비','타격','후속 동작']),
 'A04':('첫 변화를 읽힌 뒤 빠르게 공격',['시작 자세','첫 변화','공격','다음 자세']),
 'A05':('공격하는 팔과 몸의 지지 방향',['준비 자세','힘 모으기','공격 자세','후속 자세']),
 'A07':('화면 크기에 따라 남는 동작 정보',['처음','몸짓 시작','큰 반응','다음 자세']),
 'A08':('몸의 흐름 · 팔 사이 빈 공간 · 디딤발',['처음 자세','팔 올리기','기울인 자세','다음 자세']),
 'A09':('힘의 방향과 눌리고 늘어나는 형태',['기본 형태','눌림','펼쳐짐','다음 형태']),
 'A10':('닿는 순간과 몸의 반응을 연결',['맞기 전','접촉','몸의 반응','회복']),
 'A11':('주요 자세와 전체 길이 · 시간 배분만 비교',['준비 자세','회전 시작','발차기','복귀']),
 'A12':('눈썹 · 눈 · 입이 함께 만드는 표정',['첫 표정','변화 시작','주요 표정','다음 표정']),
 'A13':('방향 · 포즈 반전 · 손과 소품의 관계',['오른쪽 보기','앞쪽 손','왼쪽 보기','앞쪽 손']),
 'A14':('이전 자세 → 혼합 비중 → 다음 자세',['이전 자세','전환 시작','혼합 중','다음 자세']),
 'A15':('손가락과 닿는 물체를 함께 관찰',['펼친 손','굽히기','접촉','쥔 손']),
 'A16':('무기 경로 · 판정 범위 · 활성 시간',['준비','판정 시작','접촉','판정 종료']),
 'A17':('관절의 회전과 손 목표를 나누어 제어',['어깨','팔꿈치','손 목표','중간 형태']),
 'A18':('같은 끝 방향 · 다른 회전 경로와 시간차',['처음','변화 시작','중간 경로','끝 방향'])}

def catalog():
 c=source_catalog()
 prior=read(ROOT/'projects/animation-exaggeration/production/local/fighters-v4-kula-lili/edit/A02-F21-render.json')['signature']['cut']
 c['lili-practice']=dict(file=str(ROOT/prior['sourceFile']),game='TEKKEN 8 CNT · 리리',sourceUrl=prior['sourceUrl'],rights=prior['sourceAttribution'],sha256=prior['sourceSha256'])
 return c

def prepare():
 cat=catalog();plan=read(HERE/'plan.json');rows=[]
 for ep,studies in STUDIES.items():
  e=next(x for x in plan['episodes'] if x['id']==ep)
  masks=e['candidateIntervals']
  if ep=='A03':
   p=read(ROOT/'projects/animation-breaking-down-attack-animations/production/contrast-v5/edit-plan.json')
   masks=[dict(start=x['start'],end=x['end'],reference=dict(key='attack',mode=x['mode'],passIndex=x.get('passIndex'))) for x in p['rows']]
  spans=[];a=e['opening']['startFrame'];b=e['opening']['endFrame']
  for x in masks:
   for start,end in [(x['start'],min(x['end'],a)),(max(x['start'],b),x['end'])]:
    if end<=start:continue
    key=x['reference']['key'];assert key in studies,(ep,key)
    mode=x['reference'].get('mode','analysis')
    if spans and spans[-1]['end']==start and spans[-1]['key']==key and spans[-1]['mode']==mode:
     spans[-1]['end']=end
    else:spans.append(dict(start=start,end=end,key=key,mode=mode))
  spans.sort(key=lambda x:x['start']);assert all(x['end']<=y['start'] for x,y in zip(spans,spans[1:])),ep
  e['replacementSpans']=spans
  e['studyDefinitions']={}
  for key,(bank,grammar) in studies.items():
   source,lo,hi,phases,crop=SOURCES[bank];s=cat[source]
   record=dict(key=key,bank=bank,sourceKey=source,grammar=grammar,focus=FOCUS.get((ep,key),KOREAN[ep][0]),phaseLabels=KOREAN[ep][1],
    sourceFile=s['file'],sourceUrl=s.get('sourceUrl',s.get('url')),game=s.get('game',source),
    localIn=lo,localOut=hi,phaseSeconds=phases,detailCrop=crop,
    provenance='independent-gameplay; existing decoded FHD source and rights evidence retained',
    evidence=str(BATCH/'footage-substitution-audit-20261115/evidence.json'),
    limitations='Only visible game actions are observations. Edited timing, vectors, collision volumes, blend weights and rig controls are labeled principle illustrations, not retail-game telemetry.',
    visualRole='explanation; slow motion, detail crop or principle drawing in the same original explanation slots',
    audioTreatment='New analytic windows retain the approved speech/music bed; their source-recording music is muted. Untouched native game/audio segments remain unchanged.',
    nativeLead='Original-speed observed action repeated before detail study in existing native-pass slots; no optical-flow frames.')
   if grammar in ('startup','squash','wrist'):
    record['sourceKind']='principle-diagram-only' if grammar!='startup' else 'primary-frame-data-with-character-still'
    record['performanceVideoUsedInStudy']=False
    record['selectionReason']='Show the unobservable or configured property directly in a diagram; do not claim unrelated footage performs the illustrated change.'
    record['nativeLead']='Not applicable to this data/illustration-only study; do not label it a recorded game-animation performance.'
   if grammar=='startup':
    record['primaryData']='projects/animation-making-lead-ins-instant-and-impactful/production/series-v1/source-selection.json'
    record['primaryDataUrl']='https://ultimateframedata.com/zero_suit_samus'
    record['sourceLimit']='Retained official showcase does not verify Jab1. Use only a character still, and show Jab1 start-up1F as separately sourced data; exclude the earlier laser segment as a jab performance.'
   if ep=='A18' and key=='wrist':
    record.update(sourceKind='hybrid-game-contact-and-principle-diagram',performanceVideoUsedInStudy=True,
      selectionReason='Show the inspected boy/hand/body contact crop for the named Trico passage (old192.4–202.27s); use the calculated hand-axis diagram for the following hypothetical wrist explanation.')
   e['studyDefinitions'][key]=record;rows.append(dict(episode=ep,**record))
  e['openingGameBank']=next(iter(studies.values()))[0]
  e['summaryGameBank']=e['openingGameBank'];e['timing']='Preserve baseline clock except natural-duration speech insertions; carry original ordering/overview/recap speech through the same map.'
  # Three complete native-speed actions before detailed analysis. One action
  # bank is introduced once; several later principles can reuse that observation.
  groups=[]
  for span in spans:
   bank=studies[span['key']][0]
   if groups and groups[-1]['end']==span['start'] and groups[-1]['bank']==bank:groups[-1]['end']=span['end']
   else:groups.append(dict(start=span['start'],end=span['end'],bank=bank))
  leads=[]
  for bank in dict.fromkeys(s[0] for s in studies.values()):
   if all(s[1] in ('startup','squash','wrist') for s in studies.values() if s[0]==bank):continue
   length=round((SOURCES[bank][2]-SOURCES[bank][1])*60)
   candidates=[]
   for g in groups:
    start=max(g['start'],round(247.5*60)) if ep=='A07' and bank=='peach' else g['start']
    if g['bank']==bank and start>=120 and g['end']-start>=3*length:candidates.append(dict(g,start=start))
   if candidates:leads.append(dict(bank=bank,start=candidates[0]['start'],end=candidates[0]['start']+3*length,framesPerPass=length,passes=3))
  if ep=='A18':
   start=min(s['start'] for s in spans if s['key']=='wrist');length=round((SOURCES['trico'][2]-SOURCES['trico'][1])*60)
   leads.append(dict(bank='trico',start=start,end=start+3*length,framesPerPass=length,passes=3,role='named boy climbing/contact passage only'))
  e['nativeLeads']=leads
 index=read(BATCH/'research/research-index.json')
 for e in plan['episodes']:
  research=next(r for r in index['episodes'] if r['episode']==e['id']);path=BATCH/research['map'];assert path.exists()
  e['sourceReferenceMap']=str(path);e['referenceMapSha256']=sha(path)
  e['preservation']='Retain all baseline teaching cues/order; only explicitly mapped demonstration-specific wording is rewritten. Reuse unchanged source research evidence.'
 save(HERE/'plan.json',plan);save(HERE/'source-studies.json',dict(studies=rows,sourceCatalogEvidence=str(BATCH/'footage-substitution-audit-20261115/evidence.json')))
 print('Prepared',len(rows),'topic studies and',sum(len(e.get('replacementSpans',[])) for e in plan['episodes']),'replacement spans')

if __name__=='__main__':prepare()
