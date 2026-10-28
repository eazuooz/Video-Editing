"""Build measured edit/cue drafts from verified, unchanged PCM and reviewed ASR.
No rendering, media mixing, source import, active cue overwrite or platform calls.
"""
from pathlib import Path
import json,math,copy
import audio_pipeline as a
H=Path(__file__).resolve().parent;R=H.parents[3];P=H.parents[1];L=P/'production/local/clarity-v3'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(name,d):(H/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def fr(t):return math.floor(t*60+.5)
def main():
 a.require_authorized('measured-edit-draft')
 ko,en,spoken,files=a.scripts();timing=read(L/'voice/source-scene-timings.json');planning=read(H/'production-plan.json')
 old=read(P/'production/batch-v1/edit-plan.json');sources={s['id']:s for s in planning['actualSources']}
 align,norm=a.alignment_helpers();paras={};scenes=[]
 for s,k,sp in zip(timing['scenes'],ko['scenes'],spoken['scenes']):
  origin=s['startSample']/48000+2;words=read(a.repo_path(s['wordFile']))['words'];expected=' '.join(sp['lines'])
  starts,ends,cov=align(expected,words,s['duration']);cursor=0
  scenes.append({'id':s['id'],'title':k['title'],'voiceStart':origin,'voiceDuration':s['duration'],'sourceStartSample':s['startSample'],'sourceEndSample':s['endSample'],'startFrame':120+s['startSample']//800,'endFrame':120+(s['endSample']+799)//800,'audioFile':s['path'],'audioSha256':s['sha256'],'paragraphStarts':s['paragraphStarts']})
  for i,p in enumerate(s['paragraphs']):
   pid=f"{s['id']}-p{i+1:02d}";n=len(norm(sp['lines'][i]));begin=fr(origin+(p['start'] if i else 0));end=fr(origin+(s['paragraphs'][i+1]['start'] if i+1<len(s['paragraphs']) else s['duration']))
   paras[pid]={'id':pid,'scene':s['id'],'startFrame':begin,'endFrame':end,'text':k['lines'][i],'spoken':sp['lines'][i],'starts':[origin+float(v) for v in starts[cursor:cursor+n]],'ends':[origin+float(v) for v in ends[cursor:cursor+n]]};cursor+=n
 rows=list(paras.values());body=math.ceil(timing['scenes'][-1]['endSample']/800)
 for i,p in enumerate(rows):p['startFrame']=120 if i==0 else rows[i-1]['endFrame']
 rows[-1]['endFrame']=120+body
 def at(pid,phrase,end=False):
  p=paras[pid];needle=norm(phrase);i=norm(p['spoken']).index(needle);return fr(p['ends'][i+len(needle)-1] if end else p['starts'][i])
 cuts=[];cueRows=[]
 def add(pid,begin,end,kind,key,sourceStart=None,changes=None):
  if end<=begin:raise ValueError('Invalid measured segment')
  p=paras[pid];cid=f"c{len(cuts):03d}"
  c={'id':cid,'scene':p['scene'],'paragraphIds':[pid],'startFrame':begin,'endFrame':end,'frames':end-begin,'kind':kind,'playbackSpeed':1,'loop':False,'marks':[],'captionProtectedRect':[150,892,1784,1060],'sourceRole':'independent-gameplay' if kind=='independent-gameplay' else 'self-authored-or-official-screenshot-explanation'}
  if kind=='independent-gameplay':
   src=sources[key];c.update(source=key,gameId=src['gameId'],sourceFile=src['path'],sourceSha256=src['sha256'],sourceStart=sourceStart,sourceAttribution=src['url']+' | '+src['licenseLabel'],sourceAudioEnabled=src.get('sourceAudioEnabled',True),sourceAudioReason=src.get('sourceAudioReason','Retain verified original synchronized game audio.'),viewport=[256,80,1408,792],nativeSpeed=True)
  else:
   c.update(variant=key)
   if key in {'proof-options','puyo-official-filters','mirror-still'}:
    c.update(composition='official-photo-2d',renderer='Measured2D official-photo explanation',rendererReason='No world motion is needed; preserve the inspected image and keep labels/captions outside any world color grading.')
   else:
    c.update(stageClass='D25ColorClarityStage',renderedSource=f'projects/limited-color-world/production/local/clarity-v3/render/final-v1/{cid}/unity.mp4',renderedStartFrame=0,composition='unity-world-plus-2d-ui',renderer='Native Unity world with measured2D brand UI',rendererReason='Unity performs the actual object and saturation changes; postcomposited UI preserves legibility and avoids the confirmed overlay-camera failure.')
   cues=[]
   for name,start,finish in changes or []:cues.append({'key':name,'start':(start-begin)/60,'end':(finish-begin)/60})
   cueRows.append({'cutId':cid,'variant':key,'cues':cues})
  cuts.append(c)
 def game(pid,key,start):p=paras[pid];add(pid,p['startFrame'],p['endFrame'],'independent-gameplay',key,start)
 def demo(pid,key,changes=None):p=paras[pid];add(pid,p['startFrame'],p['endFrame'],'explanation',key,changes=changes)
 def changing(pid,key,phrase,endPhrase=None):
  t=at(pid,phrase);u=at(pid,endPhrase or phrase,True);demo(pid,key,[('change',t,max(t+18,u))])
 game('01-p01','puyo-intro',1073.3)
 game('01-p02','puyo-intro',1073.3+(paras['01-p01']['endFrame']-120)/60)
 p=paras['01-p03'];b1=at(p['id'],'먼저 종류를');b2=at(p['id'],'유니티 장면을')
 add(p['id'],p['startFrame'],b1,'independent-gameplay','puyo-intro',1102)
 add(p['id'],b1,b2,'explanation','token-color');add(p['id'],b2,p['endFrame'],'explanation','forest-color')
 demo('02-p01','token-color');changing('02-p02','token-hue-loss','두 색의 차이만','줄이겠습니다')
 p=paras['02-p03'];b=at(p['id'],'테마가 바뀌어');add(p['id'],p['startFrame'],b,'independent-gameplay','puyo-intro',1110);add(p['id'],b,p['endFrame'],'explanation','token-theme',changes=[('change',b,at(p['id'],'색이 달라지면',True))])
 demo('03-p01','proof-options',[('change',paras['03-p01']['endFrame']+60,paras['03-p01']['endFrame']+90)])
 changing('03-p02','proof-options','듀테라노피아 타입')
 changing('03-p03','forest-gray','흑백은 색을 빼고','관계를 보는 검사입니다')
 changing('03-p04','puyo-official-filters','여러 필터 중에서','화면을 고를 수 있습니다')
 changing('04-p01','token-brightness','한쪽은 밝고','두 종류를 나눠 볼 수 있습니다')
 changing('04-p02','token-background-problem','어두운 조각 뒤에','배경을 놓으면 어떨까요')
 changing('04-p03','token-edge-repair','조각에 밝은 테두리를','경계가 다시 보입니다')
 demo('04-p04','token-symbols',[('change',at('04-p04','한 종류에는 동그라미'),at('04-p04','줄무늬도 사용합니다',True)),('fourth-piece',at('04-p04','동그라미 하나를'),at('04-p04','네 개라는',True))])
 p=paras['04-p05'];b=at(p['id'],'정보를 전달하는');add(p['id'],p['startFrame'],b,'explanation','token-color-restored',changes=[('change',at(p['id'],'색을 다시'),at(p['id'],'표시는 유지합니다',True))]);add(p['id'],b,p['endFrame'],'independent-gameplay','puyo-intro',1155)
 game('05-p01','wonder-before',6)
 p=paras['05-p02'];hit=at(p['id'],'블록을 두드리자');offset=7.6-(hit-p['startFrame'])/60;game(p['id'],'wonder-block-cc',offset)
 p=paras['05-p03'];start=1.368033;nativeBoundary=2.9029;b=p['startFrame']+fr(nativeBoundary-start)
 add(p['id'],p['startFrame'],b,'independent-gameplay','wonder-after',start);add(p['id'],b,p['endFrame'],'independent-gameplay','wonder-after',nativeBoundary)
 changing('06-p01','forest-gray','색만 빼겠습니다')
 demo('06-p02','forest-gray',[('change',paras['06-p02']['startFrame']-120,paras['06-p02']['startFrame']-60)])
 p=paras['06-p03'];b=at(p['id'],'다음으로');add(p['id'],p['startFrame'],b,'explanation','forest-background-repair',changes=[('change',at(p['id'],'먼저 배경'),at(p['id'],'줄여 보겠습니다',True))]);add(p['id'],b,p['endFrame'],'explanation','forest-path-repair',changes=[('change',b,at(p['id'],'주변에서 분리합니다',True))])
 changing('06-p04','forest-color-restored','이제 색을','돌려놓겠습니다')
 game('06-p05','wonder-before',19.5)
 p=paras['07-p01'];b=at(p['id'],'흑백에서는');add(p['id'],p['startFrame'],b,'explanation','proof-options');add(p['id'],b,p['endFrame'],'explanation','inspection-comparison',changes=[('change',b,b+48)])
 p=paras['07-p02'];b1=at(p['id'],'색을 잠깐');b2=at(p['id'],'마지막에는');add(p['id'],p['startFrame'],b1,'explanation','mirror-still',changes=[('change',at(p['id'],'좌우로'),at(p['id'],'뒤집으면',True))]);add(p['id'],b1,b2,'explanation','inspection-comparison',changes=[('change',b1,b1+36)]);add(p['id'],b2,p['endFrame'],'independent-gameplay','puyo-intro',1164)
 game('08-p01','puyo-intro',1180)
 # First occurrence identifies each real game without adding source credits on screen.
 seen=set()
 for c in cuts:
  if c['kind']=='independent-gameplay' and c['gameId'] not in seen:
   title='뿌요뿌요 테트리스 2' if c['gameId']=='puyo2' else '슈퍼 마리오브라더스 원더'
   c['marks'].append({'id':'game-name','shape':'rect','t0':0,'t1':min(3,c['frames']/60),'color':'#e8cf83','thickness':6,'label':title,'fontSize':42,'labelPosition':[275,7],'x':256,'y':80,'w':1408,'h':792});seen.add(c['gameId'])
  if c['kind']=='independent-gameplay' and c['source']=='puyo-intro':
   c['marks'].append({'id':'left-field','shape':'rect','t0':0,'t1':min(4,c['frames']/60),'color':'green','thickness':8,'label':'왼쪽 필드 · 같은 종류 연결','labelPosition':[430,155],'x':425,'y':220,'w':365,'h':560})
  if c['kind']=='independent-gameplay' and c['source']=='wonder-block-cc':
   prior=next(x for x in old['cuts'] if x.get('source')=='wonder-block-cc')
   delta=prior['sourceStart']-c['sourceStart']
   for rawmark in prior['marks']:
    mark=copy.deepcopy(rawmark)
    mark['t0']+=delta;mark['t1']+=delta
    for point in mark.get('keyframes',[]):point['t']+=delta
    mark['reuseEvidence']={'plan':'projects/limited-color-world/production/batch-v1/edit-plan.json','cut':prior['id'],'sameSourceSha256':c['sourceSha256'],'sameViewport':True,'sourceClockOffsetSeconds':delta,'reason':'Source-frame geometry preserved; only new cut-relative clock shifted.'}
    mark['movingPixelReview']='pending new encoded cut with new speech/captions'
    c['marks'].append(mark)
 markSpec=H/'source-marks.json'
 if markSpec.exists():
  for row in read(markSpec)['marks']:next(c for c in cuts if c['id']==row['cutId'])['marks'].append(row['mark'])
 # No repeated intervals within this new output. Source screenshots count separately as explanation.
 bysource={}
 for c in cuts:
  if c['kind']=='independent-gameplay':bysource.setdefault(c['source'],[]).append((c['sourceStart'],c['sourceStart']+c['frames']/60,c['id']))
 for key,spans in bysource.items():
  spans.sort()
  if any(x[1]>y[0]+.001 for x,y in zip(spans,spans[1:])):raise ValueError('Repeated source interval: '+str((key,spans)))
  if any(end>float(sources[key]['decoded']['duration'])+.001 for _,end,_ in spans):raise ValueError('Source exceeded')
 plan={'slug':'limited-color-world','revision':'clarity-v3','fps':60,'width':1920,'height':1080,'introFrames':120,'outroFrames':600,'bodyFrames':body,'totalFrames':body+720,'scenes':scenes,'cuts':cuts,'ratioDecision':planning['ratioDecision'],'captionAliases':read(H/'caption-aliases.json'),'brandingFile':old['brandingFile'],'membershipFile':old['membershipFile'],'outputDir':'projects/limited-color-world/production/local/clarity-v3/edit','outputStem':'limited-color-world-clarity-v3','captionsAss':'projects/limited-color-world/production/local/clarity-v3/edit/captions.ko.ass','mixFile':'projects/limited-color-world/production/local/clarity-v3/edit/final-mix.wav','audio':planning['audio'],'timingEvidence':a.artifact(L/'voice/source-scene-timings.json'),'status':'measured-draft-native-and-annotation-review-pending'}
 import video_pipeline as video
 share=video.validate_plan(plan);plan['measuredShare']=share
 save('edit-plan.draft.json',plan);save('unity-cues.draft.json',{'revision':'clarity-v3','timingLocked':True,'timingEvidence':a.artifact(L/'voice/source-scene-timings.json'),'cuts':cueRows})
 photoVariants={'proof-options','puyo-official-filters','mirror-still'}
 jobs=[]
 for c in cuts:
  if c['kind']!='explanation' or c['variant'] in photoVariants:continue
  samples={0,c['frames']//4,c['frames']//2,c['frames']*3//4,c['frames']-1}
  row=next(x for x in cueRows if x['cutId']==c['id'])
  for cue in row['cues']:
   for t in [cue['start'],(cue['start']+cue['end'])/2,cue['end']]:
    samples.update(fr(t)+d for d in [-1,0,1] if 0<=fr(t)+d<c['frames'])
  jobs.append({'slug':'limited-color-world','cutId':c['id'],'frames':c['frames'],'stageClass':'D25ColorClarityStage','sampleFrames':sorted(samples)})
 save('capture-jobs.draft.json',{'revision':'clarity-v3','timingLocked':True,'jobs':jobs})
 save('measured-layout-review.json',{'status':'draft-only','sourceSampleCount':timing['scenes'][-1]['endSample'],'durationSeconds':(body+720)/60,'bodyMeasuredDurationSeconds':body/60,'share':share,'cuts':len(cuts),'nativeExplanationCuts':len(jobs),'originalPcmReconstructed':True,'captionsAndPixels':'pending','nativeStageSourceChanged':False,'activeCueJsonChanged':False})
 print(json.dumps({'cuts':len(cuts),'native':len(jobs),'totalSeconds':(body+720)/60,'share':share},ensure_ascii=False))
if __name__=='__main__':main()
