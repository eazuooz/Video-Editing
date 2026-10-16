"""Lock the selected revision to measured speech; no ratio-padding cuts."""
from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';M=R/'motion-canvas/src/projects/game-reward-planning/revision-v2'
T=R/'shared/output/narration/game-reward-planning/reference-preserving-v2/game-reward-planning-reference-v2.timing.json'
t=json.loads(T.read_text(encoding='utf8'));assert t.get('alignment'),'Align current speech first'
origins={s:next(e['start'] for e in t['entries'] if e['scene_id']==s) for s in [f'{i:02}' for i in range(1,12)]}
end={s:origins[f'{int(s)+1:02}']-o if int(s)<11 else t['duration_seconds']-o for s,o in origins.items()}
cuts=[];parts=[];mcFrame=0
def add(s,a,b,kind,**k):
 start=120+round((origins[s]+a)*60);stop=120+round((origins[s]+b)*60)
 assert stop>start
 cuts.append(dict(id=f'cut{len(cuts):02}',scene=s,startFrame=start,endFrame=stop,frames=stop-start,kind=kind,**k))
def diagram(s,a,b,visual,cues):add(s,a,b,'explanation',visual=visual,cues=cues,renderer='Motion Canvas',reason='Progressive causal diagram or official still analysis aligned to narration; not measured game data')
def film(s,a,b,source,sourceStart,label,mark=None,freeze=False):
 add(s,a,b,'explanation' if freeze else 'independent-gameplay',source=source,sourceStart=sourceStart,freeze=freeze,label=label,marks=mark or [],renderer='FFmpeg source-preserving composite',reason='Verified independent recording; editorial marks identify the narrated target',clearAtSourceCut=True)
def box(x,y,w,h,begin,finish,color,label,lx=None,ly=None):return dict(shape='rectangle',x=x,y=y,w=w,h=h,start=begin,end=finish,color=color,label=label,labelX=lx if lx is not None else x,labelY=ly if ly is not None else max(30,y-58),lineWidth=7,meaning=label,tracking='fixed UI or verified stationary interval',occlusion='clear at interval and source cut')
Y='ffd15c';G='79d4a1';B='69c9df'
diagram('01',0,end['01'],'overview',[0,7.12,15.4,18.5,21])
diagram('02',0,28.9,'growth',[0,13,16.38,21.04,25.72])
film('02',28.9,41.3,'kirby-adventure-first',192.2,'Kirby’s Adventure · 카피 능력',[
 box(1040,682,170,151,5.6,12.4,Y,'능력 표시: NORMAL → BEAM',700,620)])
film('02',41.3,48.48,'kirby-adventure-first',216,'Kirby’s Adventure · 다른 능력으로 전환',[
 box(1040,682,170,151,1.7,7.18,G,'능력 표시: FIRE',800,620)])
diagram('02',48.48,end['02'],'powerLoss',[0,7.34,10.0,12.8,16])
diagram('03',0,18.78,'training',[0,0.8,2.88,8.66,15])
film('03',18.78,end['03'],'melee-classic',103.5,'실제 녹화: 클래식 모드의 파이터·난이도 선택',[
 box(456,40,1008,430,0,6.0,Y,'사용할 파이터 선택',460,500)])
diagram('04',0,10.6,'unlock',[0,4.14,7.2,4.14,9])
film('04',10.6,20,'brawl-challenger',51.2,'새 도전자 · 툰 링크',[
 box(410,100,1100,580,0.4,3.1,Y,'도전자로 등장',580,40)])
cuts[-1]['sourceSegments']=[{'start':51.2,'frames':216},{'start':59,'frames':348}]
film('04',20,23,'brawl-challenger',133,'전투 승리 → 참가 알림')
film('04',23,26,'brawl-challenger',147,'전투 승리 → 툰 링크 참가',[
 box(390,130,1150,550,.9,1.55,G,'새 파이터 합류',660,60)])
film('04',26,30.72,'brawl-challenger',159,'선택 화면에서 사용할 수 있는 파이터가 늘어남',[
 box(370,50,1170,500,.3,4.5,G,'선택지 확인',690,590)])
diagram('04',30.72,41.32,'unlock',[0,0,0,0,0])
film('04',41.32,45.94,'ultimate-lucina',57,'빛의 세계 · 지도에서 파이터 구출',[
 box(610,250,650,390,.2,3.8,B,'지도 위 파이터에게 접근',600,170)])
film('04',45.94,48.2,'ultimate-lucina',100,'빛의 세계 · 구출을 위한 전투')
film('04',48.2,end['04'],'ultimate-lucina',106,'승리 → 루키나 합류 · 도전자 난입과 다른 획득 경로',[
 box(235,70,1460,720,2.4,6.2,G,'루키나 합류',1100,800)])
cuts[-1]['analysisTail']={'startFrame':526,'label':'정지 화면 분석 · 획득한 보상','reason':'Hold the verified source114.75s reward-result frame while narration links new choices to collectible rewards; remove unrelated loading screen. Original quiet background audio retained.'}
film('05',0,16.24,'melee-classic',813.7,'클래식 모드 완료 → 사용한 파이터의 피규어',[
 box(590,140,740,620,10.2,15.2,Y,'파이터가 피규어로 전시',570,70)])
diagram('05',16.24,end['05'],'trophyCost',[0,2,11.56,16.0,20])
diagram('06',0,20.48,'stickers',[0,4.44,10,7.3,17])
diagram('06',20.48,40.46,'costMath',[0,4.88,10.26,16.1,18])
diagram('06',40.46,57.62,'spiritRules',[0,8.54,12.2,14.0,15])
film('06',57.62,66.2,'ultimate-first-spirits-usable',301.5,'서포터 장착 → 추가 효과 확인',[
 box(967,220,670,190,.2,1.7,B,'서포터를 넣는 슬롯',930,425),
 box(225,735,540,100,5.5,7.4,G,'Unira Equipped · 유니라 장비',850,750)])
film('06',66.2,end['06'],'ultimate-first-spirits-usable',321.2,'장착 효과를 실제 전투에서 확인 · 유니라를 들고 시작',[
 box(310,455,180,125,.1,1.3,G,'장비하고 시작',530,455)])
diagram('07',0,end['07'],'coins',[0,8.38,15.62,20.56,29.44])
film('08',0,6.74,'brawl-challenger',137.5,'결과 화면의 보상마다 조건은 다릅니다')
film('08',6.74,16.52,'brawl-challenger',142.4,'결과 화면 정지 분석 · 음악의 획득 조건',[
 box(500,685,940,70,0,9.78,Y,'조건: 노멀 난이도 클래식 모드 완료',400,790)],freeze=True)
diagram('08',16.52,end['08'],'music',[0,5.4,9.58,15.56,21.58])
diagram('09',0,19.32,'checklist',[0,13.84,15.7,17.1,18])
film('09',19.32,27.8,'kirby-air-riders-first-race',47.5,'카트에 탄 웨이들 디 두 마리 동시 처치',[
 box(1255,10,470,110,4.5,8.45,Y,'조건 달성 알림',1000,160)])
film('09',27.8,35.2166666667,'kirby-air-riders-first-race',121.5,'과제 완료 47 → 48 · 새 음악 획득',[
 box(408,10,180,66,2.9,5.4,Y,'완료 수',630,80),
 box(1197,122,470,480,5.8,7.4,G,'음악 보상',1110,660)])
film('09',35.2166666667,37.58,'kirby-air-riders-first-race',128.5,'결과 화면 정지 분석 · 완주 자체가 이 음악의 조건은 아닙니다',[
 box(1197,122,470,480,0,2.37,G,'음악 보상',1110,660)],freeze=True)
diagram('09',37.58,end['09'],'checklist',[0,7.82,11.42,14.58,19.3])
diagram('10',0,end['10'],'progress',[0,10.0,24.0,26.5,29])
diagram('11',0,end['11'],'worksheet',[2.34,14.3,16.7,19,22.42])
# Quantized boundaries are contiguous across source cuts and chapter joins.
assert cuts[0]['startFrame']==120
for a,b in zip(cuts,cuts[1:]):assert a['endFrame']==b['startFrame'],(a,b)
bodyFrames=round(t['duration_seconds']*60)
assert cuts[-1]['endFrame']==120+bodyFrames
sourceInfo={
 'kirby-adventure-first':('NU7-hWGV5G0','LongplayArchive','Kirby’s Adventure'),
 'melee-classic':('pPpkIitFjvk','longplays.org · World of Longplays / Tsunao','Super Smash Bros. Melee'),
 'brawl-challenger':('GdTZ8UKlA78','LongplayArchive','Super Smash Bros. Brawl'),
 'ultimate-lucina':('zNeBk3e3f50','LongplayArchive / Spazbo4','Super Smash Bros. Ultimate'),
 'ultimate-first-spirits-usable':('663UvTXbzbM','LongplayArchive / Spazbo4','Super Smash Bros. Ultimate'),
 'kirby-air-riders-first-race':('HjA-J3yKJ2I','LongplayArchive / SpectreBull','Kirby Air Riders')}
for c in cuts:
 if 'source' in c:
  video,credit,game=sourceInfo[c['source']];c.update(sourceUrl='https://www.youtube.com/watch?v='+video,credit=credit,game=game,sourceFile=f'projects/game-reward-planning/production/local/reference-preserving-v2/media/{c["source"]}.mp4',classification='independent-gameplay' if not c['freeze'] else 'independent-gameplay-still-analysis',nativeRatePreserved=True,playbackSpeed=1,coordinateSystem='final1920x1080; source fitted within1536x864 at top; fixed captions centered960,970')
  continue
 name='production-'+c['id'];c['mcStartFrame']=mcFrame;c['mcEndFrame']=mcFrame+c['frames'];mcFrame+=c['frames'];parts.append(name)
 (M/(name+'.tsx')).write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './lesson-visuals';\nexport default makeScene2D(function*(view){yield* lesson(view,"+json.dumps(c['visual'])+','+json.dumps({'duration':c['frames']/60,'cues':c['cues']})+");});\n",encoding='utf8')
actual=sum(c.get('analysisTail',{}).get('startFrame',c['frames']) for c in cuts if c['kind']=='independent-gameplay')
plan=dict(schemaVersion=1,revision='reference-preserving-v2',fps=60,width=1920,height=1080,bodyFrames=bodyFrames,totalFrames=bodyFrames+720,ratioPolicy='reward-planning-content-led-ratio-v2',actualFrames=actual,explanationFrames=bodyFrames-actual,actualShare=actual/bodyFrames,narrationTiming=str(T.relative_to(R)).replace('\\','/'),sourceReview='sources/game-candidates.json#currentRevision',cuts=cuts,mcFrames=mcFrame,brandingFrames=120,membershipFrames=600,qaStatus='exact cuts planned; annotations must be verified in moving encoded output')
(P/'production/reference-preserving-v2/edit-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
imports='\n'.join(f"import s{i} from './{name}?scene';" for i,name in enumerate(parts))
(M/'production-project.ts').write_text("import {makeProject} from '@motion-canvas/core';\nimport branding from '../scenes/branding-intro?scene';\nimport membership from '../scenes/membership-outro?scene';\n"+imports+"\nexport default makeProject({name:'game-reward-planning-v2-production-explanations',scenes:["+','.join('s'+str(i) for i in range(len(parts)))+",branding,membership]});\n",encoding='utf8')
# In the intermediate MC render the12s branding assets are last, for simple slicing.
(M/'production-project.meta').write_text((M/'lesson-project.meta').read_text(encoding='utf8'),encoding='utf8')
print(json.dumps({'cuts':len(cuts),'diagramParts':len(parts),'actualShare':actual/bodyFrames,'duration':plan['totalFrames']/60,'mcDuration':mcFrame/60+12}))
