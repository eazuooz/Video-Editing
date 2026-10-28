"""Measured word-cue proposal, then explicitly reviewed edit/native job lock.

--proposal never invents final timing. --lock requires the internal full text /
screen review and exact60/40 measured contract; no narration truncation or loops.
"""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,math,re
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;P=HERE.parents[1];LOCAL=P/'production/local/clarity-v3'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def norm(t):return re.sub(r'[^0-9a-z가-힣]','',t.lower())
def locate(scene,needle):
 words=read(ROOT/scene['wordFile'])['words'];chars='';times=[]
 for word in words:
  w=norm(word.get('text',word.get('word','')));stamp=word.get('timestamp',[word.get('start'),word.get('end')]);chars+=w;times.extend([stamp[0]]*len(w))
 text=''.join(norm(p['spokenText'])for p in scene['paragraphs']);needle=norm(needle);at=text.find(needle)
 if at<0:raise ValueError('Anchor absent from locked script: '+needle)
 match=difflib.SequenceMatcher(None,text,chars,autojunk=False);mapping={}
 for b in match.get_matching_blocks():
  for j in range(b.size):mapping[b.a+j]=b.b+j
 mapped=[mapping[i]for i in range(at,min(at+len(needle),len(text)))if i in mapping]
 if len(mapped)<max(3,len(needle)*.65):raise ValueError('Weak measured word anchor: '+needle)
 return round(times[mapped[0]]*60)
def proposal():
 plan=read(HERE/'production-plan.json');timing=read(LOCAL/'voice/source-scene-timings.json');rows=[]
 for scene in timing['scenes']:
  cuts=[c for c in plan['cuts']if c['scene']==scene['id']];starts=[0]+[locate(scene,c['speechAnchor'])for c in cuts[1:]];ends=starts[1:]+[round(scene['duration']*60)]
  for c,start,end in zip(cuts,starts,ends):
   r=copy.deepcopy(c);r.update(localStartFrame=start,localEndFrame=end,frames=end-start,reviewedWithNarration=False,phaseSeconds=None);rows.append(r)
 save(HERE/'timing-proposal.json',{'revision':'clarity-v3','timingSource':rel(LOCAL/'voice/source-scene-timings.json'),'timingSha256':sha(LOCAL/'voice/source-scene-timings.json'),'status':'measured-anchor-proposal-needs-edit-review','reviewedWithFullNarration':False,'cuts':rows})
 print('Measured proposal written; review source ranges, meaningful transitions and actual ratio before lock.')
def lock():
 authored=read(HERE/'timing-lock.json');timing=read(LOCAL/'voice/source-scene-timings.json');original=read(P/'production/batch-v1/edit-plan.json');sourcebank={s['id']:s for s in read(HERE/'sources.json')['sources']};titles=read(HERE/'unity-cues.json');bytitle={s['mode']:s['title']for s in titles['cuts']}
 assert authored['reviewedWithFullNarration']is True and authored['timingSha256']==sha(LOCAL/'voice/source-scene-timings.json')
 body=math.ceil((timing['scenes'][-1]['sourceOrigin']+timing['scenes'][-1]['duration'])*60);out=copy.deepcopy(original)
 out.update(revision='clarity-v3',bodyFrames=body,totalFrames=body+720,scenes=[],cuts=[],outputDir=rel(LOCAL/'edit'),outputStem=P.name)
 out['captionAliases']=read(P/'script/clarity-v3/caption-aliases.json')
 out['audio']['sourceReviewPath']=rel(HERE/'audio-source-review.json');out['audio']['sourceReviewSha256']=sha(HERE/'audio-source-review.json')
 out['notes']=['All previous outputs preserved. Full new continuous SampleB narration, same approved Nimbus BGM.','MK8, Unpacking and A Short Hike: three distinct meaningfully taught examples, one Nintendo.','Self-authored Unity is explanation footage. Source1x/native aspect, no looping, no source lesson footage.']
 jobs=[];cues=[];cursor=120
 for scene in timing['scenes']:
  base=120+round(scene['sourceOrigin']*60);end=120+round((scene['sourceOrigin']+scene['duration'])*60)
  if scene==timing['scenes'][-1]:end=120+body
  out['scenes'].append({'id':scene['id'],'title':scene['title'],'voiceStart':2+scene['sourceOrigin'],'startFrame':base,'endFrame':end})
  group=[r for r in authored['cuts']if r['scene']==scene['id']]
  for n,r in enumerate(group):
   assert r['reviewedWithNarration']and r['frames']>0
   a=base+r['localStartFrame'];b=base+r['localEndFrame']
   if n==len(group)-1:b=end
   assert a==cursor,(r['id'],a,cursor)
   c={k:r[k]for k in ['id','scene','kind','normalSpeed','loop','playbackSpeed']};c.update(startFrame=a,endFrame=b,frames=b-a)
   if r['kind']=='independent-gameplay':
    src=sourcebank[r['source']];c.update(source=r['source'],game=r['source'],sourceFile=src['file'],sourceSha256=src['sha256'],sourceStart=r['sourceStart'],sourceAttribution=f"{src['creator']} | {src['url']}",sourceAudioEnabled=True,sourceAudioReviewStatus='source-specific-retain',audioRightsReview=rel(HERE/'audio-source-review.json'),onScreenAttributionRequired=False,viewport=[0,0,1920,880],marks=r.get('marks',[]))
    limit=r.get('reviewedSourceEnd')
    if limit is None:raise ValueError('Exact inspected source end required: '+c['id'])
    assert c['sourceStart']+c['frames']/60<=limit+.02,(c['id'],'source range exceeds inspection')
   else:
    phase=r.get('phaseSeconds');assert phase and len(phase)==3 and 0<phase[0]<phase[1]<phase[2]<=c['frames']/60
    c.update(purpose=r['mode'],renderedSource=rel(LOCAL/f"render/v1/{r['id']}/unity.mp4"),renderedStartFrame=0)
    cues.append({'id':r['id'],'mode':r['mode'],'title':bytitle[r['mode']],'phaseSeconds':phase,'speechCueEvidence':r['speechCueEvidence']})
    jobs.append({'slug':P.name,'cutId':r['id'],'frames':c['frames'],'stageClass':'D29ClarityStage','sampleFrames':sorted(set([0]+[min(c['frames']-1,round(t*60))for t in phase]+[c['frames']-1]))})
   out['cuts'].append(c);cursor=b
 actual=sum(c['frames']for c in out['cuts']if c['kind']=='independent-gameplay')
 assert abs(actual-round(body*.6))<=1,('Meaningful allocation must meet agreed60:40',actual,body,actual/body)
 assert cursor==120+body
 save(HERE/'edit-plan.json',out);save(HERE/'unity-cues.json',{'revision':'clarity-v3','timingLocked':True,'timingSha256':sha(LOCAL/'voice/source-scene-timings.json'),'cuts':cues});save(HERE/'capture-jobs.json',{'revision':'clarity-v3','timingLocked':True,'jobs':jobs})
 save(HERE/'timing-lock-receipt.json',{'status':'measured-internal-timing-review-locked','editPlanSha256':sha(HERE/'edit-plan.json'),'unityCuesSha256':sha(HERE/'unity-cues.json'),'bodyFrames':body,'gameplayFrames':actual,'share':actual/body,'humanReview':False})
 print('Locked measured edit and native cues; parent freeze required before capture.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--proposal',action='store_true');group.add_argument('--lock',action='store_true');args=parser.parse_args();proposal()if args.proposal else lock()
