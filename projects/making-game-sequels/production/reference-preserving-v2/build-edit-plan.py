"""Build a speech-anchored edit; estimated drafts cannot enter production."""
from pathlib import Path
import json,argparse,re,copy
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';L=P/'production/local/reference-preserving-v2';M=R/'motion-canvas/src/projects/making-game-sequels/revision-v2';N=R/'shared/output/narration/making-game-sequels/reference-preserving-v2'
ap=argparse.ArgumentParser();ap.add_argument('--estimate',action='store_true');args=ap.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf8'))
ko=read(P/'script/reference-preserving-v2/narration.ko.json');ids=[s['id'] for s in ko['scenes']]
origins={};B={};E={};cursor=0
if args.estimate:
 # Look-development only. Never render or deliver from estimated narration.
 rate=sum(len(re.sub(r'[^가-힣A-Za-z0-9]','',x)) for x in ko['scenes'][0]['lines'])/20.88
 for s in ko['scenes']:
  sid=s['id'];origins[sid]=cursor;B[sid]=[];local=0
  for line in s['lines']:B[sid].append(local);local+=len(re.sub(r'[^가-힣A-Za-z0-9]','',line))/rate
  E[sid]=local+.3;cursor+=E[sid]
else:
 timing=read(N/'game-sequels-reference-v2.timing.json');assert timing.get('alignment'),'Current whole-narration review/alignment required'
 origins={sid:next(e['start'] for e in timing['entries'] if e['scene_id']==sid) for sid in ids}
 E={sid:(origins[ids[i+1]] if i+1<len(ids) else timing['duration_seconds'])-origins[sid] for i,sid in enumerate(ids)}
 B={sid:[e['voice_start']-origins[sid] for e in timing['entries'] if e['scene_id']==sid] for sid in ids};cursor=timing['duration_seconds']
F=lambda sid,sec:120+round((origins[sid]+sec)*60)
body=round(cursor*60);target=round(body*.6)
# Concept-matched contiguous active play. Ranges were inspected in contact
# sheets and native playback; dialog, loading, maps and camera occlusion excluded.
pools={
 'pikmin-task':[['pikmin4-day2',85,115],['pikmin4-day2',40,55],['pikmin4-day2',300,326],['pikmin4-day2',440,465],['pikmin4-day2',520,565],['pikmin4-day2',145,158],['pikmin4-day2',397,406],['pikmin4-day2',487,498]],
 'pikmin-wall':[['pikmin4-day2',200,255]],
 'driving':[['gt7-sunday',2,21.5],['gt7-sunday',45,92]],
 'steering':[['gt7-sunday',22,44.5]],
 'smash-intro':[['smash-wiiu',35,85]],
 'smash-rule':[['smash-ultimate',0,34]],
 'smash-experience':[['smash-ultimate',175,205.5],['smash-wiiu',130,153]],
 'smash-summary':[['smash-wiiu',180,214]],
}
cuts=[]
def add(sid,a,b,kind,**kw):
 start,end=F(sid,a),F(sid,b)
 if end<=start:return
 c=dict(scene=sid,startFrame=start,endFrame=end,frames=end-start,kind=kind,**kw);cuts.append(c);return c
def diagram(sid,a,b,kind,cues=None):
 return add(sid,a,b,'explanation',visual=kind,renderer='Motion Canvas',implementationKind='independent explanatory diagram with independently sourced screenshots',cues=cues or [0,(b-a)*.16,(b-a)*.34,(b-a)*.53,(b-a)*.72])
def film(sid,a,b,pool,label):
 now=F(sid,a);end=F(sid,b)
 while now<end:
  assert pools[pool],('Concept-matched source capacity exhausted',sid,pool,(end-now)/60)
  source,begin,limit=pools[pool][0];available=int((limit-begin)*60+1e-6);count=min(end-now,available)
  if count<=0:pools[pool].pop(0);continue
  cuts.append(dict(scene=sid,startFrame=now,endFrame=now+count,frames=count,kind='independent-gameplay',source=source,sourceStart=begin,label=label,marks=[],playbackSpeed=1,loop=False))
  now+=count;pools[pool][0][1]=begin+count/60
  if count==available:pools[pool].pop(0)
def direct(sid,a,b,source,start,label):return add(sid,a,b,'independent-gameplay',source=source,sourceStart=start,label=label,marks=[],playbackSpeed=1,loop=False)
def cues(sid,a,indices):return [max(0,B[sid][i]-a) for i in indices]

# One adjustable boundary remains within the summary's same familiar/new-play
# explanation. It never changes audio duration or playback speed.
fixedActual=E['01']+B['02'][4]+B['03'][3]+B['04'][4]+(E['04']-B['04'][6])+B['05'][3]+B['06'][4]+B['07'][3]+B['08'][4]
oatchiStart=max(327.,334-(B['07'][4]-B['07'][3]));oatchiFirst=336.8-oatchiStart
oatchiSecond=8.;oatchiActual=min(E['07']-B['07'][3],oatchiFirst+oatchiSecond)
fixedActual+=oatchiActual
summaryActual=target/60-fixedActual
assert B['09'][1]-.1<=summaryActual<=min(34,E['09']-7),('Revisit concept allocation, never pad footage',summaryActual,B['09'])

film('01',0,E['01']/2,'pikmin-task','대원에게 일을 맡기는 익숙한 행동')
film('01',E['01']/2,E['01'],'driving','코스를 보고 조향하는 익숙한 행동')
film('02',0,B['02'][0]+3.8,'pikmin-task','작은 대원에게 작업 지시')
film('02',B['02'][0]+3.8,B['02'][1],'driving','차를 조종해 코스를 달리는 행동')
film('02',B['02'][1],B['02'][4],'pikmin-task','반복해서 알아볼 수 있는 이동과 작업')
diagram('02',B['02'][4],E['02'],'foundation',[0,1,max(2,B['02'][5]-B['02'][4]),max(3,B['02'][5]-B['02'][4]+2),max(4,B['02'][5]-B['02'][4]+4)])
film('03',0,B['03'][3],'steering','핸들의 방향과 코스, 게임 화면에서 보이는 행동')
diagram('03',B['03'][3],B['03'][5],'layers',[0,0,0,1,2])
diagram('03',B['03'][5],E['03'],'work',[0,2,B['03'][6]-B['03'][5],B['03'][6]-B['03'][5]+3,B['03'][7]-B['03'][5]])
assert 200<=261-B['04'][4]<245,'Reinspect wall sequence if voice exceeds reviewed source capacity'
direct('04',0,B['04'][4],'pikmin4-day2',261-B['04'][4],'대원에게 작업 지시 → 벽이 허물어짐 → 열린 길 확인')
diagram('04',B['04'][4],B['04'][6],'test',[0,.6,1.2,3,5])
film('04',B['04'][6],E['04'],'pikmin-task','실행 가능한 플레이에서 작업과 반응을 확인')
film('05',0,B['05'][1],'smash-intro','Wii U에서 이어지는 공격과 밀어내기')
film('05',B['05'][1],B['05'][3],'smash-rule','얼티밋의 공격과 누적 대미지 퍼센트')
diagram('05',B['05'][3],E['05'],'teams',[0,1,B['05'][4]-B['05'][3],B['05'][5]-B['05'][3],B['05'][6]-B['05'][3]])
film('06',0,B['06'][4],'smash-experience','직접 플레이하는 경험 · 만족도는 가상의 플레이어 상황')
diagram('06',B['06'][4],E['06'],'experience',[0,.6,1.2,2,max(3,B['06'][5]-B['06'][4])])
film('07',0,B['07'][3],'pikmin-task','기존 대원에게 일을 맡기는 행동에서 새로운 동료로 연결')
a=B['07'][3];b=a+oatchiFirst
direct('07',a,b,'pikmin4-day2',oatchiStart,'와치가 항아리 앞에서 돌진해 첫 항아리를 부숨')
direct('07',b,b+oatchiSecond,'pikmin4-day2',341.5,'다시 방향을 잡아 돌진 → 남은 항아리가 깨짐 → 물건 등장')
diagram('07',b+oatchiSecond,E['07'],'oatchi',[0,.7,1.4,2.2,3])
film('08',0,B['08'][3],'pikmin-task','누구에게 어떤 일을 맡길지 판단')
film('08',B['08'][3],B['08'][4],'driving','방향과 속도를 바꿀 상황을 보고 판단')
diagram('08',B['08'][4],E['08'],'value',[0,.7,1.4,2.1,B['08'][5]-B['08'][4]])
film('09',0,summaryActual,'smash-summary','익숙한 규칙 안에서 공격과 위치를 판단하는 새로운 대전')
diagram('09',summaryActual,E['09'],'conclusion',[0,.8,1.6,2.4,max(3,B['09'][4]-summaryActual)])

# Frame rounding can differ by at most one frame per independently expressed
# interval. Resolve that at the same summary boundary, without source overlap.
base=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay');delta=target-base
if delta:
 a=next(c for c in reversed(cuts) if c['kind']=='independent-gameplay');b=cuts[cuts.index(a)+1]
 assert abs(delta)<=10 and b['kind']=='explanation'
 a['frames']+=delta;a['endFrame']+=delta;b['frames']-=delta;b['startFrame']+=delta

info={s['id']:s for s in read(V/'source-selection.json')['sources']};seen=set();mc=0;parts=[]
annotations=read(V/'source-annotations.json')['marks']
for i,c in enumerate(cuts):
 c['id']=f'cut{i:02}'
 if c['kind']=='independent-gameplay':
  # Final decoded pixels exposed loading/intro transitions missed by the broad
  # source ranges. These inspected replacements preserve every edit boundary.
  correctedStarts={'cut00':520.,'cut13':45.,'cut14':5.,'cut16':179.5,'cut28':193.}
  if c['id'] in correctedStarts:
   c['sourceStart']=correctedStarts[c['id']]
   c['inpointCorrection']='final-pixel-review: active gameplay replaces loading/versus/black transition; timing unchanged'
  src=info[c['source']];game={'pikmin4-day2':'피크민 4','gt7-sunday':'그란 투리스모 7','smash-wiiu':'슈퍼 스매시브라더스 for Wii U','smash-ultimate':'슈퍼 스매시브라더스 얼티밋'}[c['source']]
  c.update(sourceFile=src['file'],sourceUrl=src['url'],sourceSha256=src['sha256'],credit=('Nintendo' if c['source']=='pikmin4-day2' else src['recorder']),game=game,classification='independent-gameplay',showGameTitle=game not in seen,clearAtSourceCut=True,coordinateSystem='Source1920x1080; aspect-preserved1600x900 at160,0; fixed captions960,970')
  if c['source']=='gt7-sunday':c.update(originalAudio='exclude',audioExclusionReason='Source broadcast-mode and third-party music rights not established; quiet approved music retained.')
  for originalMark in annotations:
   mark=copy.deepcopy(originalMark)
   if c['id']=='cut14' and mark['source']=='smash-ultimate' and mark['scene']=='05':
    # Keep the callout on the same spoken cue after moving to active combat.
    mark['from']+=5;mark['to']+=5
    for key in mark.get('keyframes',[]):key[0]+=5
   if mark['source']==c['source'] and mark['scene']==c['scene'] and mark['from']<c['sourceStart']+c['frames']/60 and mark['to']>c['sourceStart']:
    c['marks'].append({k:v for k,v in mark.items() if k not in ['source','scene']})
  seen.add(game)
 else:
  c.update(mcStartFrame=mc,mcEndFrame=mc+c['frames']);mc+=c['frames'];name='production-'+c['id'];parts.append(name)
  c['cues']=[min(max(0,x),max(0,c['frames']/60-.7)) for x in c['cues']]
  if not args.estimate:(M/(name+'.tsx')).write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view){yield* lesson(view,"+json.dumps(c['visual'])+','+json.dumps({'duration':c['frames']/60,'cues':c['cues']})+");});\n",encoding='utf8')
for a,b in zip(cuts,cuts[1:]):assert a['endFrame']==b['startFrame'],(a,b)
assert cuts[0]['startFrame']==120 and cuts[-1]['endFrame']==body+120
assert sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay')==target
for source in info:
 ranges=sorted((c['sourceStart'],c['sourceStart']+c['frames']/60,c['id']) for c in cuts if c.get('source')==source)
 for a,b in zip(ranges,ranges[1:]):assert b[0]>=a[1]-.02,('Duplicate source interval',source,a,b)
out=dict(revision='reference-preserving-v2',timing='estimated-design-only' if args.estimate else 'measured-and-asr-aligned',fps=60,width=1920,height=1080,bodyFrames=body,totalFrames=body+720,actualFrames=target,explanationFrames=body-target,ratioErrorFrames=target-body*.6,mcFrames=mc,scenes=[dict(id=sid,voiceStart=2+origins[sid],voiceDuration=E[sid]-(.3 if i<8 else 0),startFrame=F(sid,0),endFrame=F(sid,E[sid]),paragraphStarts=B[sid]) for i,sid in enumerate(ids)],cuts=cuts,noLoops=True,sourceRatePreserved=True,baselineUploadPreserved='2-IyuwcP_vQ',annotationsReview='pending source-keyframe entry and moving-output review')
dest=L/'research/estimated-edit-plan.json' if args.estimate else V/'edit-plan.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if not args.estimate:(M/'production-project.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(f"import s{i} from './{n}?scene';" for i,n in enumerate(parts))+"\nexport default makeProject({scenes:["+','.join('s'+str(i) for i in range(len(parts)))+']});\n',encoding='utf8')
print(json.dumps({'timing':out['timing'],'seconds':out['totalFrames']/60,'actual':target/60,'explanation':(body-target)/60,'summaryActual':summaryActual,'cuts':len(cuts),'sceneSeconds':E},indent=2))
