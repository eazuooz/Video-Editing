"""Speech-anchored unique gameplay excerpts and exact60:40 body classification."""
from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';V=P/'production/reference-preserving-v2';M=R/'motion-canvas/src/projects/avoid-game-comparisons/revision-v2';L=P/'production/local/reference-preserving-v2'
N=R/'shared/output/narration/avoid-game-comparisons/reference-preserving-v2'
t=json.loads((N/'avoid-comparisons-reference-v2.timing.json').read_text(encoding='utf8'));assert t.get('alignment')
ko=json.loads((P/'script/reference-preserving-v2/narration.ko.json').read_text(encoding='utf8'))
ids=[s['id'] for s in ko['scenes']];origins={sid:next(e['start'] for e in t['entries'] if e['scene_id']==sid) for sid in ids}
E={sid:(origins[ids[i+1]] if i+1<len(ids) else t['duration_seconds'])-origins[sid] for i,sid in enumerate(ids)}
B={sid:[e['voice_start']-origins[sid] for e in t['entries'] if e['scene_id']==sid] for sid in ids}
kinds=['overview','familiar','pitch','difference','exception','nes','odyssey','conditions','rewrite','retell','shared','conclusion'];cuts=[];mc=0;pool=65.
def add(s,a,b,kind,**kwargs):
 start=120+round((origins[s]+a)*60);end=120+round((origins[s]+b)*60);assert end>start,(s,a,b)
 c=dict(id=f'cut{len(cuts):02}',scene=s,startFrame=start,endFrame=end,frames=end-start,kind=kind,**kwargs);cuts.append(c);return c
def film(s,a,b,source,start,label):return add(s,a,b,'independent-gameplay',source=source,sourceStart=start,playbackSpeed=1,loop=False,label=label,marks=[])
def nes(s,a,b,label):
 global pool
 c=film(s,a,b,'nes-gameplay-project',pool,label);pool+=c['frames']/60+1;assert pool<138,'Inspect another relevant source range, never pad';return c
def diagram(s,a,b,kind,cues=None):return add(s,a,b,'explanation',visual=kind,cues=cues or [0,(b-a)*.18,(b-a)*.38,(b-a)*.58,(b-a)*.78],renderer='Motion Canvas',implementationKind='independent conceptual diagram')

nes('01',0,10.5,'같은 이름이 떠올리는 횡스크롤 플레이')
film('01',10.5,E['01'],'odyssey-switch2-180-360',60,'같은 마리오, 다른 공간과 모자 행동')
film('02',0,E['02'],'nes-gameplay-project',10,'오른쪽으로 이동 · 점프로 장애물과 적을 통과')
# Scene03 is first built entirely as a diagram. Its last concrete-play passage
# can inherit the real cap/bridge example, within the inspected source capacity.
diagram('03',0,E['03'],'pitch',[0,B['03'][1],B['03'][2],B['03'][3],B['03'][4]])
nes('04',0,B['04'][2],'이미 존재하는 재미만 말하면 새 게임의 이유가 남지 않음')
film('04',B['04'][2],B['04'][3],'odyssey-switch2-180-360',152-(B['04'][3]-B['04'][2]),'점프하는 모습만으로 설명하면 빠지는 능력')
film('04',B['04'][3],B['04'][3]+5.5,'odyssey-switch2-180-360',152,'모자를 던져 개구리로 조종 대상 전환')
film('04',B['04'][3]+5.5,E['04'],'odyssey-switch2-360-440',15.5,'개구리의 높은 점프로 위쪽 발판에 도착')
nes('05',0,14,'비교가 불러오는 익숙한 조작과 진행')
film('05',14,E['05'],'odyssey-switch2-180-360',108.5,'익숙한 이동 위에 모자 행동이 더해짐 · 후속작 일반론의 참고 사례')
film('06',0,B['06'][3],'nes-gameplay-project',150,'발판 높이와 사이의 빈 공간을 보고 점프')
film('06',B['06'][3],B['06'][4],'nes-gameplay-project',194,'깃대 도착으로 구간 완료')
film('06',B['06'][4],B['06'][5],'nes-gameplay-project',178,'기억으로 남는 횡스크롤 이동과 점프')
film('06',B['06'][5],E['06'],'odyssey-switch2-705-820',29,'평면 점프의 기억에서 입체 공간 탐색으로 연결')
film('07',0,B['07'][2],'odyssey-switch2-705-820',68-B['07'][2],'공간에서 이동 경로와 캡처 대상을 탐색').update(labels=[{'from':B['07'][1]+3,'to':B['07'][2]-.1,'text':'캡처 (Capture) · 특정 대상을 조종하는 기능','position':[470,70]}])
film('07',B['07'][2],B['07'][4],'odyssey-switch2-705-820',68,'티라노사우루스 캡처 → 돌 부수기')
nes('07',B['07'][4],B['07'][5],'같은 단어가 불러오는 첫 번째 경험: 횡스크롤 점프')
film('07',B['07'][5],E['07'],'odyssey-switch2-705-820',68+B['07'][4]-B['07'][2],'다른 경험: 조종 대상의 능력으로 길 열기')
actual08=B['08'][4]  # Keep the actual Moon collection through goal/action/condition; diagram begins when the condition is varied.
source08=94-(B['08'][2]+4.0)
film('08',0,actual08,'odyssey-switch2-555-705',source08,'멍멍이에게 접근 → 캡처 → 당겨 발사 → 벽 파괴 → 파워문')
diagram('08',actual08,E['08'],'conditions',[0,max(.5,B['08'][4]-actual08),max(1,B['08'][4]-actual08+3),max(2,B['08'][5]-actual08),max(3,B['08'][6]-actual08)])
diagram('09',0,E['09'],'rewrite',[B['09'][1],B['09'][2],B['09'][3],B['09'][4],B['09'][5]])
diagram('10',0,E['10'],'retell',[0,B['10'][1],B['10'][2],B['10'][3],B['10'][4]])
nes('11',0,B['11'][2],'같은 구간을 봤다면 시점과 조작을 함께 가리킬 수 있음')
diagram('11',B['11'][2],E['11'],'shared',[0,1,max(2,B['11'][3]-B['11'][2]),max(4,B['11'][3]-B['11'][2]+3),max(6,B['11'][4]-B['11'][2])])
diagram('12',0,E['12'],'conclusion',[0,B['12'][1],B['12'][2],B['12'][2]+2,B['12'][3]])
body=round(t['duration_seconds']*60);target=round(body*.6);base=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay');need=target-base
# The tail demonstrates the concrete existing play that a pitch must explain.
# No idle footage, loops, speed changes or extra duration are introduced.
assert 0<=need<=round(18*60),('Source/design allocation needs review',body,target,base,need)
c=next(c for c in cuts if c['scene']=='03');oldEnd=c['endFrame'];c['endFrame']-=need;c['frames']-=need
if need:
 tail=dict(id='pitch-play',scene='03',startFrame=oldEnd-need,endFrame=oldEnd,frames=need,kind='independent-gameplay',source='odyssey-switch2-180-360',sourceStart=108-need/60,playbackSpeed=1,loop=False,label='전달할 플레이를 실제 장면에서 확인: 모자 행동과 장치 작동',marks=[])
 cuts.insert(cuts.index(c)+1,tail)
sourceInfo={
 'nes-gameplay-project':('HGmyQS09VGQ','Gameplay Project · CC BY','슈퍼 마리오 브라더스'),
 'odyssey-switch2-180-360':('FJgSiI-Fols','LongplayArchive / Spazbo4','슈퍼 마리오 오디세이'),
 'odyssey-switch2-360-440':('FJgSiI-Fols','LongplayArchive / Spazbo4','슈퍼 마리오 오디세이'),
 'odyssey-switch2-555-705':('FJgSiI-Fols','LongplayArchive / Spazbo4','슈퍼 마리오 오디세이'),
 'odyssey-switch2-705-820':('FJgSiI-Fols','LongplayArchive / Spazbo4','슈퍼 마리오 오디세이')}
parts=[];seen=set()
for i,c in enumerate(cuts):
 c['id']=f'cut{i:02}'
 if c['kind']=='independent-gameplay':
  video,credit,game=sourceInfo[c['source']];c.update(sourceFile=(L/(c['source']+'.mp4')).relative_to(R).as_posix(),sourceUrl='https://www.youtube.com/watch?v='+video,credit=credit,game=game,classification='independent-gameplay',showGameTitle=game not in seen,coordinateSystem='Source1920x1080; aspect-preserved1600x900 at160,0; fixed captions960,970',clearAtSourceCut=True);seen.add(game)
 else:
  c.update(mcStartFrame=mc,mcEndFrame=mc+c['frames']);mc+=c['frames'];name='production-'+c['id'];parts.append(name)
  (M/(name+'.tsx')).write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view){yield* lesson(view,"+json.dumps(c['visual'])+','+json.dumps({'duration':c['frames']/60,'cues':c['cues']})+");});\n",encoding='utf8')
for a,b in zip(cuts,cuts[1:]):assert a['endFrame']==b['startFrame'],(a,b)
assert cuts[0]['startFrame']==120 and cuts[-1]['endFrame']==body+120
for source in sourceInfo:
 intervals=sorted([(c['sourceStart'],c['sourceStart']+c['frames']/60,c['id']) for c in cuts if c.get('source')==source])
 for a,b in zip(intervals,intervals[1:]):assert b[0]>=a[1]-.02,('Duplicate source range',source,a,b)
(M/'production-project.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(f"import s{i} from './{name}?scene';" for i,name in enumerate(parts))+"\nexport default makeProject({scenes:["+','.join('s'+str(i) for i in range(len(parts)))+']});\n',encoding='utf8')
scenes=[{'id':sid,'kind':kinds[i],'voiceStart':2+origins[sid],'voiceDuration':E[sid]-(.3 if i<11 else 0),'startFrame':120+round(origins[sid]*60),'endFrame':120+round((origins[sid]+E[sid])*60),'paragraphStarts':B[sid]} for i,sid in enumerate(ids)]
out={'revision':'reference-preserving-v2','fps':60,'width':1920,'height':1080,'bodyFrames':body,'totalFrames':body+720,'actualFrames':target,'explanationFrames':body-target,'ratioErrorFrames':target-body*.6,'mcFrames':mc,'scenes':scenes,'cuts':cuts,'noLoops':True,'sourceRatePreserved':True,'baselineUploadPreserved':'cQE7_ygx_XM','currentFinalReview':'pending','notes':'Gameplay is unique, concept-matched native-speed action; diagram/retelling passages classified as explanation. Scene03 final concrete-play passage inherits the actual cap interaction; exact screen-role boundary falls within the same spoken explanation.'}
(V/'edit-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'seconds':out['totalFrames']/60,'bodyFrames':body,'actualFrames':target,'explanationFrames':body-target,'scene03ActualSeconds':need/60,'cuts':len(cuts),'mcFrames':mc,'source08':[source08,source08+actual08],'nesPoolEnd':pool},indent=2))
