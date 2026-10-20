"""V6 changed-range caption/visual QA; default is CPU planning, never decoding.

Full old/new yuv420p framemd5 records must come from the one integrity decode
already performed for each master. Only byte-identical decoded global frames
reuse the prior RGB rasters. Fresh rasters use bounded scene seeks, preserved
global PTS and a selected-yuv framemd5 branch in the same decoder invocation.
No offsets are inferred. No audio extraction, ASR, render or platform action.
"""
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
import argparse, ast, bisect, hashlib, importlib.util, json, math, os, shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6';Q=O/'qa';FPS=60
FLAGS=(subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS) if os.name=='nt' else 0

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,file);out=importlib.util.module_from_spec(spec);spec.loader.exec_module(out);return out

qa=module('v6_caption_reuse_base',H/'caption-output-qa.py')
verify=module('v6_caption_reuse_integrity',H/'verify-output.py')
read=qa.read;save=qa.save;sha=qa.sha;rel=qa.rel;proof=qa.proof

def now():return datetime.now(timezone.utc).isoformat()

def selected():
 c=read(R/'shared/publishing/video-production-control.json')
 assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']

def balanced_select(values,field='pts'):
 values=list(values);assert values and values==sorted(set(values))
 assert field in ['n','pts']
 def node(a,b):
  if b-a==1:return f'eq({field}\\,{values[a]})'
  mid=(a+b)//2;return '('+node(a,mid)+'+'+node(mid,b)+')'
 return node(0,len(values))

def ranges(values):
 out=[]
 for value in values:
  if out and value==out[-1][1]:out[-1][1]+=1
  else:out.append([value,value+1])
 return out

def output_row(integrity,kind):
 row=next(x for x in integrity['outputs'] if x['kind']==kind)
 assert row['fullDecodePassed'] and row['ptsMonotonicAndUniform'] and row['exactAACStreamEqual']
 assert (row['frames'],row['width'],row['height'],row['fps'])==(217544,1920,1080,60)
 return row

def load_framehash(integrity,kind,folder):
 item=output_row(integrity,kind);file=folder/Path(item['frameHashFile']).name
 assert sha(file)==item['frameHashSha256'],('Integrity/framehash binding',kind,file)
 rows,tb=verify.parse_decoded_frames(file.read_text('utf8'),217544)
 return rows,dict(**proof(file),masterSha256=item['sha256'],timeBase=tb,frames=len(rows),pixelFormat='yuv420p')

def scene_at(timeline,frame):
 return next((s['id'] for s in timeline['scenes'] if s['startFrame']<=frame<s['endFrame']),None)

def plan(args):
 """Reads existing JSON/hash/text only. Never opens the video decoder."""
 selected();old=read(args.prior_integrity);new=read(args.integrity)
 old_report=read(args.prior_qa/'caption-output-review.json');reviewed=read(args.prior_qa/'caption-output-reviewed.json')
 old_plan=read(args.prior_qa/'sample-plan.json');old_actual=read(args.prior_qa/'actual-extraction.json')
 old_expected=read(args.prior_qa/'expected-extraction.json')
 old_caption=output_row(old,'captioned');new_caption=output_row(new,'captioned')
 archive_root=args.prior_integrity.parent.parent
 prior_sceneplan=getattr(args,'prior_scene_plan',None) or archive_root/'edit/scene-plan.json'
 prior_master=getattr(args,'prior_master',None) or archive_root/'euler-captioned.mp4'
 assert sha(prior_sceneplan)==old_report['inputs']['scenePlan']['sha256'],'Preserved prior scene plan differs'
 assert sha(prior_master)==old_caption['sha256'],'Preserved prior master differs from its integrity identity'
 assert old_report['inputs']['master']['sha256']==old_caption['sha256']==old_actual['inputs']['masterSha256']
 assert sha(args.prior_qa/'actual-extraction.json')==old_report['actualExtraction']['sha256']
 assert sha(args.prior_qa/'expected-extraction.json')==old_report['expectedExtraction']['sha256']
 assert sha(H/'caption-output-qa.py')==old_report['inputs']['implementation']['sha256'],'Comparison implementation changed; re-audit the strict comparison instead of reusing silently'
 assert reviewed['inputs']==old_report['inputs'] and reviewed['unresolvedFailureCount']==0
 assert reviewed['strictPixelThresholdsChanged'] is False
 assert sha(args.prior_qa/'caption-output-review.json')==reviewed['rawAutomatedReport']['sha256']
 assert reviewed['rawAutomatedFailureFrames']==[50547,103449,212868]
 t=read(H/'timeline.json');s=read(O/'edit/scene-plan.json');c=read(O/'captions/captions.json');layout=read(O/'captions/caption-layout.json')
 checked=qa.input_contract(t,s,c,layout,O/'captions.ko.ass',O/'captions.ko.srt')
 current=qa.sample_plan(t,s,c,layout)
 assert current['samples']==old_plan['samples'] and current['nativeFrames']==old_plan['nativeFrames'],'Current sample timing/tags changed; bounded reuse needs a new audit'
 assert current['totalFrames']==old_plan['totalFrames']==217544
 assert len(current['samples'])==2269 and len(current['nativeFrames'])==1813
 assert old_actual['frameMapping']['roi']==[x['frame'] for x in current['samples']] and old_actual['frameMapping']['native']==current['nativeFrames']
 stable={'timeline':H/'timeline.json','captions':O/'captions/captions.json','canonicalAliasMap':H/'caption-aliases.json','captionLayout':O/'captions/caption-layout.json',
         'assKo':O/'captions.ko.ass','srtKo':O/'captions.ko.srt','assEn':O/'captions.en.ass','srtEn':O/'captions.en.srt',
         'sourceKo':P/'script/revision-v6-article-flow/narration.ko.json','sourceEn':P/'script/revision-v6-article-flow/narration.en.json'}
 for key,file in stable.items():assert sha(file)==old_report['inputs'][key]['sha256'],(key,'Expected pixels/text/timing changed')
 assert old_expected['inputs']['assSha256']==sha(O/'captions.ko.ass')
 assert old_expected['globalPts']==[x['frame']*1000 for x in current['samples']]
 assert old_expected['inputs']['fontSha256']==sha(qa.FONT)
 assert old_expected['inputs']['captionWorkingFormat']=='TV BT709 yuv420p before ASS, full-range RGB PNG after ASS'
 old_hashes={};new_hashes={};hash_inputs={};diff={}
 for kind in ['clean','captioned']:
  old_hashes[kind],oldproof=load_framehash(old,kind,args.prior_framehash_directory or args.prior_integrity.parent)
  new_hashes[kind],newproof=load_framehash(new,kind,args.framehash_directory or args.integrity.parent)
  changed=[i for i,(a,b) in enumerate(zip(old_hashes[kind],new_hashes[kind])) if a['md5']!=b['md5']]
  outside=[f for f in changed if scene_at(t,f) not in args.changed_scene]
  assert not outside,('Decoded changes outside the explicitly selected repair scenes',ranges(outside))
  diff[kind]={'framesChanged':len(changed),'ranges':ranges(changed),'all217544FramesCompared':True}
  hash_inputs[kind]={'prior':oldproof,'current':newproof}
 assert new_caption['aacSha256']==old_caption['aacSha256'],'Audio changed; existing audio evidence is not reusable'
 equal=lambda frame:old_hashes['captioned'][frame]['md5']==new_hashes['captioned'][frame]['md5']
 samples=[dict(frame=x['frame'],mode='reused' if equal(x['frame']) else 'fresh',oldMd5=old_hashes['captioned'][x['frame']]['md5'],newMd5=new_hashes['captioned'][x['frame']]['md5']) for x in current['samples']]
 natives=[dict(frame=f,mode='reused' if equal(f) else 'fresh',oldMd5=old_hashes['captioned'][f]['md5'],newMd5=new_hashes['captioned'][f]['md5']) for f in current['nativeFrames']]
 joins=[]
 for sid in ['v6-09','v6-27']:
  sc=next(x for x in t['scenes'] if x['id']==sid)
  joins.append({'id':sid+'-first12','scene':sid,'frames':list(range(sc['startFrame'],sc['startFrame']+12)),'purpose':'Direct native/375px re-review of the repaired first12-frame join; generation is not viewing'})
 clock=read(args.prior_qa/'clock-boundary-reproduction/clock-boundary-review.json')
 assert sha(args.prior_qa/'clock-boundary-reproduction/clock-boundary-review.json')==reviewed['reviewedEvidence']['sha256']
 assert clock['currentCaptionedMaster']['sha256']==old_caption['sha256'] and clock['sourceAss']['sha256']==sha(O/'captions.ko.ass')
 assert clock['timeline']['sha256']==sha(H/'timeline.json') and clock['unresolvedCount']==0 and clock['preservesStrictPixelThresholds']
 clock_rows=[]
 for row in clock['rows']:
  f=row['originalFailure']['frame'];sid=row['cue']['scene'];sc=next(x for x in t['scenes'] if x['id']==sid)
  assert sid in ['v6-12','v6-22','v6-41'] and row['unresolved'] is False and row['maximumObservedFrameDifference']==1
  assert all(old_hashes[k][i]['md5']==new_hashes[k][i]['md5'] for k in ['clean','captioned'] for i in range(sc['startFrame'],sc['endFrame'])),('Clock boundary scene changed',sid)
  clock_rows.append({'frame':f,'scene':sid,'priorClockRow':row,'entireSceneDecodedEqualCleanAndCaptioned':True,'oldMd5':old_hashes['captioned'][f]['md5'],'newMd5':new_hashes['captioned'][f]['md5'],'clockExceptionReusedOnlyForThisFrame':True})
 temporal=[]
 assert len(current['visualReview']['targets'])==107
 for target in current['visualReview']['targets']:
  frames=target['motionFrames'];identities=[{'frame':f,'oldMd5':old_hashes['captioned'][f]['md5'],'newMd5':new_hashes['captioned'][f]['md5'],'decodedEqual':equal(f)} for f in frames]
  temporal.append({'id':target['id'],'scene':target['scene'],'motionFrames':frames,'samples':identities,'allFiveFramesDecodedEqual':all(x['decodedEqual'] for x in identities),'disposition':'prior sampled pixel evidence reusable if its original direct-review record covers this target' if all(x['decodedEqual'] for x in identities) else 'fresh sampled native/mobile review required','realTimePlaybackNotEstablishedByFiveSamples':True})
 inputs={'priorMaster':proof(prior_master),'priorMasterOriginalFile':old_caption['file'],'currentMaster':{'sha256':new_caption['sha256'],'file':rel(args.master)},'priorIntegrity':proof(args.prior_integrity),'currentIntegrity':proof(args.integrity),'framehash':hash_inputs,'priorQa':rel(args.prior_qa),'priorRawCaptionReport':proof(args.prior_qa/'caption-output-review.json'),'priorReviewedCaptionReport':proof(args.prior_qa/'caption-output-reviewed.json'),'priorSamplePlan':proof(args.prior_qa/'sample-plan.json'),'priorActualExtraction':proof(args.prior_qa/'actual-extraction.json'),'priorExpectedExtraction':proof(args.prior_qa/'expected-extraction.json'),'priorClockProof':proof(args.prior_qa/'clock-boundary-reproduction/clock-boundary-review.json'),'priorScenePlan':proof(prior_sceneplan),'currentScenePlan':proof(O/'edit/scene-plan.json'),'stableInputs':{key:proof(file) for key,file in stable.items()},'implementation':proof(Path(__file__))}
 report={'schemaVersion':1,'revision':'article-flow-v6','status':'CPU-plan-only; no master decode performed','createdAt':now(),'inputs':inputs,'frameChanges':diff,'allowedChangedScenes':args.changed_scene,'roiSamples':samples,'nativeSamples':natives,'temporalTargets':temporal,'repairJoinTargets':joins,'reusedClockBoundaries':clock_rows,'counts':{'roi':len(samples),'roiReused':sum(x['mode']=='reused' for x in samples),'roiFresh':sum(x['mode']=='fresh' for x in samples),'native':len(natives),'nativeReused':sum(x['mode']=='reused' for x in natives),'nativeFresh':sum(x['mode']=='fresh' for x in natives),'temporalTargets':107,'temporalUnchanged':sum(x['allFiveFramesDecodedEqual'] for x in temporal),'temporalFresh':sum(not x['allFiveFramesDecodedEqual'] for x in temporal)},'scope':{'newFullMasterDecodePasses':0,'wholeHourCaptionDecodeRepeated':False,'newAudioExtraction':False,'newAsr':False,'newRender':False,'humanWholeListening':'pending','realTimeMotionReview':'pending'}}
 return report,dict(t=t,s=s,c=c,layout=layout,checked=checked,plan=current,oldReport=old_report,oldActual=old_actual,oldExpected=old_expected,newHashes=new_hashes['captioned'])

def archived_files(receipt,logical_root,archive_root):
 out={}
 for row in receipt['files']:
  tail=Path(row['file']).relative_to(logical_root);file=archive_root/tail
  assert file.is_file() and sha(file)==row['sha256'],('Missing/mutated prior raster',file)
  out[tail.as_posix()]=file
 return out

def link_verified(source,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert sha(source)==sha(dest);return
 try:os.link(source,dest)
 except OSError:shutil.copy2(source,dest)
 assert sha(source)==sha(dest)

def cached_completion(report,inputs):
 assert report['inputs']==inputs,'Existing completed report belongs to different inputs'
 assert report.get('completionState')=='all-required-artifacts-written-and-hashed','Incomplete prior output is not a successful cache'
 assert report.get('completedFiles'),'Missing required artifact hash bindings'
 for row in report['completedFiles']:
  file=R/row['file'];assert file.is_file() and sha(file)==row['sha256'],('Completed QA artifact changed',file)
 assert report['unresolvedFailureCount']==len(report['unresolvedFailures'])
 return 2 if report['unresolvedFailureCount'] else 0

def parse_selected_hashes(file,expected_frames,hashes):
 text=file.read_text('utf8');tbline=next(x for x in text.splitlines() if x.startswith('#tb 0: '));tb=Fraction(tbline.split(': ',1)[1]);rows=[]
 for line in text.splitlines():
  if not line or line.startswith('#'):continue
  p=[x.strip() for x in line.split(',')];assert len(p)==6
  exact=Fraction(int(p[2]))*tb*FPS;assert exact.denominator==1,'Selected timestamp is not an exact global frame'
  f=int(exact);assert int(p[4])==1920*1080*3//2 and p[5]==hashes[f]['md5'],('Bounded seek MD5 does not identify the requested current frame',f,p[5],hashes[f]['md5'])
  rows.append({'frame':f,'pts':int(p[2]),'timeBase':str(tb),'md5':p[5],'matchesCurrentIntegrityDecodedFrame':True})
 assert [x['frame'] for x in rows]==expected_frames,('Wrong/missing/reordered seek frames',expected_frames,[x['frame'] for x in rows])
 return rows

def extract_bounded(master,scene,roi_frames,native_frames,folder,hashes,master_sha):
 selected();union=sorted(set(roi_frames)|set(native_frames));assert union
 folder.mkdir(parents=True,exist_ok=True);receipt=folder/'extraction.json'
 seek=scene['startFrame']//FPS;duration=(union[-1]+1)/FPS-seek+.05
 assert duration>0 and all(scene['startFrame']<=f<scene['endFrame'] for f in union)
 identity={'masterSha256':master_sha,'scene':scene['id'],'floorSecondInputSeek':seek,'inputDurationLimitSeconds':duration,'selectedGlobalFrames':union,'roiFrames':roi_frames,'nativeFrames':native_frames,'colorConversion':'original yuv420p -> RGB PNG; TV BT709 metadata verified; no scaling','implementationSha256':sha(Path(__file__))}
 if receipt.exists():
  old=read(receipt);assert old['inputs']==identity and old['returnCode']==0 and all((R/x['file']).is_file() and sha(R/x['file'])==x['sha256'] for x in old['files']),'Different or failed prior bounded extraction; preserve and investigate'
  parse_selected_hashes(folder/'selected-framehash.txt',union,hashes);return old
 assert not list(folder.rglob('*.png')) and not (folder/'selected-framehash.txt').exists(),'Unreceipted partial range exists; preserve and investigate before retry'
 branches=['hash']+(['roi'] if roi_frames else [])+(['native'] if native_frames else [])
 graph=f'[0:v]settb=1/60000,select={balanced_select([f*1000 for f in union])},split={len(branches)}'+''.join('['+b+']' for b in branches)+';[hash]format=yuv420p[hashout]'
 args=['ffmpeg','-nostdin','-hide_banner','-loglevel','warning','-threads','2','-filter_complex_threads','1','-copyts','-ss',str(seek),'-t',f'{duration:.9f}','-i',str(master)]
 if roi_frames:graph+=f';[roi]select={balanced_select([f*1000 for f in roi_frames])},crop=1920:200:0:880,format=rgb24[roiout]'
 if native_frames:graph+=f';[native]select={balanced_select([f*1000 for f in native_frames])},format=rgb24[nativeout]'
 graphfile=folder/'range.ffgraph';graphfile.write_text(graph,'utf8');args+=['-/filter_complex',str(graphfile),'-map','[hashout]','-an','-c:v','rawvideo','-pix_fmt','yuv420p','-threads:v','1','-fps_mode','passthrough','-enc_time_base:v','1:60000','-frames:v',str(len(union)),'-f','framemd5',str(folder/'selected-framehash.txt')]
 for name,frames in [('roi',roi_frames),('native',native_frames)]:
  if not frames:continue
  (folder/name).mkdir(exist_ok=True);args+=['-map',f'[{name}out]','-an','-fps_mode','passthrough','-enc_time_base:v','1:60000','-frames:v',str(len(frames)),'-start_number','0','-compression_level','1',str(folder/name/'%06d.png')]
 with (folder/'range.log').open('wb') as log:proc=subprocess.run(args,cwd=R,stdout=subprocess.DEVNULL,stderr=log,creationflags=FLAGS)
 save(folder/'process.json',{'command':args,'returnCode':proc.returncode,'scope':'One bounded input decode for this scene. Same decoder split yields PNGs and selected full-YUV MD5; no offset estimation.'})
 assert proc.returncode==0,(folder/'range.log').read_text('utf8',errors='replace')[-1800:]
 identities=parse_selected_hashes(folder/'selected-framehash.txt',union,hashes);files=[]
 for name,frames in [('roi',roi_frames),('native',native_frames)]:
  if not frames:continue
  got=sorted((folder/name).glob('*.png'));assert len(got)==len(frames)
  for file in got:
   with Image.open(file) as im:assert im.size==((1920,200) if name=='roi' else (1920,1080))
   files.append(proof(file))
 data={'inputs':identity,'returnCode':0,'files':files,'selectedYuvFrames':identities,'selectedFramehash':proof(folder/'selected-framehash.txt'),'videoDecodePasses':1,'fullMasterDecode':False,'audioDecoded':False};save(receipt,data);return data

def execute(args,report,data):
 out=args.output_directory;prior=args.prior_qa;master_sha=report['inputs']['currentMaster']['sha256'];selected()
 assert sha(args.master)==master_sha,'Current master differs from its complete integrity receipt'
 done=out/'caption-range-reuse.json'
 if done.exists():
  prior_done=read(done);code=cached_completion(prior_done,report['inputs']);print('Cached same current changed-range report',rel(done),'unresolved',prior_done['unresolvedFailureCount'])
  if code:raise SystemExit(code)
  return
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_frames,pix_fmt,color_range,color_space','-of','json',str(args.master)],creationflags=FLAGS))['streams'][0]
 assert (probe['width'],probe['height'],Fraction(probe['avg_frame_rate']),int(probe['nb_frames']),probe['pix_fmt'],probe['color_range'],probe['color_space'])==(1920,1080,Fraction(60),217544,'yuv420p','tv','bt709')
 stat=(args.master.stat().st_size,args.master.stat().st_mtime_ns)
 out.mkdir(parents=True,exist_ok=True);save(out/'sample-plan.json',data['plan'])
 logical_root=Path(data['oldReport']['actualExtraction']['file']).parent
 actual_files=archived_files(data['oldActual'],logical_root,prior);expected_files=archived_files(data['oldExpected'],logical_root,prior)
 roi_lookup={x['frame']:i for i,x in enumerate(data['plan']['samples'])};native_lookup={f:i for i,f in enumerate(data['plan']['nativeFrames'])};paths={};fresh_roi={x['frame'] for x in report['roiSamples'] if x['mode']=='fresh'};fresh_native={x['frame'] for x in report['nativeSamples'] if x['mode']=='fresh'}
 for row in report['roiSamples']:
  f=row['frame'];tail=f'actual/{roi_lookup[f]:06d}.png'
  if row['mode']=='reused':link_verified(actual_files[tail],out/tail)
  link_verified(expected_files[f'expected/{roi_lookup[f]:06d}.png'],out/'expected'/f'{roi_lookup[f]:06d}.png')
 for row in report['nativeSamples']:
  f=row['frame'];tail=f'native/{native_lookup[f]:06d}.png'
  if row['mode']=='reused':link_verified(actual_files[tail],out/tail);paths[f]=out/tail
 extra={f for x in report['repairJoinTargets'] for f in x['frames']}
 # Additional join frames absent from the original extraction have no prior
 # raster to reuse, even when their old/new decoded MD5 happens to match.
 for f in extra-set(native_lookup):fresh_native.add(f)
 for f in extra&set(native_lookup):
  if (out/'native'/f'{native_lookup[f]:06d}.png').exists():paths[f]=out/'native'/f'{native_lookup[f]:06d}.png'
 receipts=[]
 for scene in data['t']['scenes']:
  rf=sorted(f for f in fresh_roi if scene['startFrame']<=f<scene['endFrame']);nf=sorted(f for f in fresh_native if scene['startFrame']<=f<scene['endFrame'])
  if not rf and not nf:continue
  folder=out/'fresh-ranges'/scene['id'];receipt=extract_bounded(args.master,scene,rf,nf,folder,data['newHashes'],master_sha);receipts.append(receipt)
  for i,f in enumerate(rf):link_verified(folder/'roi'/f'{i:06d}.png',out/'actual'/f'{roi_lookup[f]:06d}.png')
  for i,f in enumerate(nf):
   dest=out/'native'/f'{native_lookup[f]:06d}.png' if f in native_lookup else out/'repair-joins/native'/f'{f:09d}.png';link_verified(folder/'native'/f'{i:06d}.png',dest);paths[f]=dest
 assert all((out/'actual'/f'{i:06d}.png').exists() and (out/'expected'/f'{i:06d}.png').exists() for i in range(2269))
 assert all((out/'native'/f'{i:06d}.png').exists() for i in range(1813))
 clock_by_frame={r['frame']:r for r in report['reusedClockBoundaries']};cues=data['c']['cues'];starts=[Fraction(qa.clock_cs(x['start']),100) for x in cues];geom={x['id']:x for x in data['layout']['rows']['ko']};oldrows={x['frame']:x for x in data['oldReport']['samples']};results=[];raw_fail=[];unresolved=[]
 for row,sample in zip(report['roiSamples'],data['plan']['samples']):
  f=row['frame'];index=roi_lookup[f];a=out/'actual'/f'{index:06d}.png';e=out/'expected'/f'{index:06d}.png'
  if row['mode']=='reused':item=dict(oldrows[f])
  else:
   moment=Fraction(f,FPS);i=bisect.bisect_right(starts,moment)-1;cue=cues[i] if i>=0 and moment<Fraction(qa.clock_cs(cues[i]['end']),100) else None
   with Image.open(a) as ai,Image.open(e) as ei:
    if cue:detail=qa.comparison(ai,ei,geom[cue['id']]['box']);passed=detail['pass'];kind='expected-caption'
    elif 120<=f<data['t']['temporalContract']['outroStartFrame']:detail=qa.unexpected_caption_like_box(ai);passed=not detail['unexpectedWhiteBoxCandidate'];kind='expected-no-caption'
    else:detail={'excluded':'original branding/member identity; no lecture caption expected'};passed=True;kind='preserved-branding-or-members'
   item={'frame':f,'seconds':float(moment),'tags':sample['tags'],'expectedCueId':cue['id'] if cue else None,'kind':kind,'pass':passed,'metrics':detail}
  item.update(actualRoi=rel(a),expectedRoi=rel(e),rasterDisposition=row['mode'],decodedIdentity={'oldMd5':row['oldMd5'],'newMd5':row['newMd5']},clockBoundaryResolved=f in clock_by_frame,effectivePass=item['pass'] or f in clock_by_frame)
  if not item['pass']:raw_fail.append(item)
  if not item['effectivePass']:unresolved.append(item)
  results.append(item)
 files=[proof(out/'actual'/f'{i:06d}.png') for i in range(2269)]+[proof(out/'native'/f'{i:06d}.png') for i in range(1813)]
 extraction={'inputs':{'masterSha256':master_sha,'frames':[x['frame'] for x in data['plan']['samples']],'nativeFrames':data['plan']['nativeFrames'],'roi':[0,880,1920,200],'format':'RGB PNG','decodePasses':len(receipts),'fullMasterDecodePasses':0},'files':files,'frameMapping':{'roi':[x['frame'] for x in data['plan']['samples']],'native':data['plan']['nativeFrames']},'reusedByDecodedHash':report['counts'],'freshRangeReceipts':receipts,'scope':'No whole-master caption re-decode. Prior rasters reused only with identical global-frame yuv420p MD5; fresh bounded scenes verify selected full YUV MD5 in the same extraction invocation.'};save(out/'actual-extraction.json',extraction)
 expected={**data['oldExpected'],'files':[proof(out/'expected'/f'{i:06d}.png') for i in range(2269)],'reusedFrom':report['inputs']['priorExpectedExtraction'],'allExpectedRastersReusedExactly':True,'newAssRasterRender':False};save(out/'expected-extraction.json',expected)
 save(out/'caption-input-contract.json',{'inputs':report['inputs'],**data['checked']})
 visual=qa.visual_qa.derive_motion_boards(data['plan'],out)
 joinrows=[];font=ImageFont.truetype(str(qa.FONT),16)
 for target in report['repairJoinTargets']:
  board=Image.new('RGB',(1500,3*239),'#111111');draw=ImageDraw.Draw(board);framefiles=[]
  for i,f in enumerate(target['frames']):
   file=paths[f]
   with Image.open(file) as im:picture=im.convert('RGB').resize((375,211),Image.Resampling.LANCZOS)
   x=(i%4)*375;y=(i//4)*239;draw.text((x+5,y+4),f'{target["scene"]} f{f}',font=font,fill='white');board.paste(picture,(x,y+28));framefiles.append({'frame':f,**proof(file),'currentYuvMd5':data['newHashes'][f]['md5']})
  dest=out/'repair-joins'/f'{target["id"]}-mobile.jpg';dest.parent.mkdir(exist_ok=True);board.save(dest,quality=95);joinrows.append({**target,'nativeFrames':framefiles,'mobileBoard':proof(dest),'humanPixelReview':'pending actual opening'})
 repair_targets=[x for x in visual['targets'] if x['id'] in ['v6-08.B02','v6-26.B02']]
 assert len(repair_targets)==2
 save(out/'repair-review-targets.json',{'inputs':report['inputs'],'motionTargets':repair_targets,'joinTargets':joinrows,'noNewSourceDecodeForBoards':True,'humanPixelReview':'pending direct native/375px review'})
 assert stat==(args.master.stat().st_size,args.master.stat().st_mtime_ns),'Master changed during bounded extraction'
 report.update(status='changed-range extraction and strict comparison complete; sampled visual review remains separate',completedAt=now(),newFullMasterDecodePasses=0,newBoundedSceneDecodePasses=len(receipts),strictPixelThresholdsChanged=False,rawFailureCount=len(raw_fail),unresolvedFailureCount=len(unresolved),samples=results,failures=raw_fail,unresolvedFailures=unresolved,freshRangeExtractions=receipts,actualExtraction=proof(out/'actual-extraction.json'),expectedExtraction=proof(out/'expected-extraction.json'),inputCoverage=proof(out/'caption-input-contract.json'),visualReviewTargets=proof(out/'visual-review-targets.json'),repairReviewTargets=proof(out/'repair-review-targets.json'),humanWholeListening='pending',realTimeMotionReview='pending; temporal samples are not continuous playback')
 raw={'schemaVersion':1,'revision':'article-flow-v6','inputs':report['inputs'],'status':'strict pixel comparison with prior exact-clock exceptions kept separate','captionCueCount':588,'sampleCount':2269,'failureCount':len(raw_fail),'samples':results,'failures':raw_fail,'scope':{'sourceMasterFullDecodePasses':0,'boundedSceneDecodePasses':len(receipts),'strictThresholdsUnchanged':True,'humanWholeListening':'pending'}};save(out/'caption-output-review.json',raw)
 save(out/'caption-output-reviewed.json',{'schemaVersion':1,'revision':'article-flow-v6','inputs':report['inputs'],'status':'pass within caption pixel/hash reuse scope' if not unresolved else 'unresolved pixel flags; inspect before approval','rawAutomatedReport':proof(out/'caption-output-review.json'),'rawAutomatedFailureCount':len(raw_fail),'rawAutomatedFailureFrames':[r['frame'] for r in raw_fail],'reviewedBoundaryCount':len(clock_by_frame),'unresolvedFailureCount':len(unresolved),'captionCueCount':588,'automatedSampleCount':2269,'strictPixelThresholdsChanged':False,'clockExceptions':report['reusedClockBoundaries'],'humanWholeListening':'pending','realTimeMotionReview':'pending','fullFrameNativeMobileReview':'prior decoded-equal samples reusable only under their actual direct-review records; changed ranges pending'})
 required=[out/name for name in ['sample-plan.json','actual-extraction.json','expected-extraction.json','caption-input-contract.json','visual-review-targets.json','repair-review-targets.json','caption-output-review.json','caption-output-reviewed.json']]
 # This completion marker is written last. Include rasters/boards too: a
 # cached success never bypasses missing, mutated or incomplete QA evidence.
 bindings={rel(p):proof(p) for p in required}
 for row in [*files,*expected['files'],*visual['boards']]:bindings[row['file']]=row
 for receipt in receipts:
  row=receipt['selectedFramehash'];bindings[row['file']]=row
  directory=(R/row['file']).parent
  for name in ['extraction.json','process.json','range.ffgraph','range.log']:
   file=directory/name;bindings[rel(file)]=proof(file)
 for target in joinrows:
  bindings[target['mobileBoard']['file']]=target['mobileBoard']
  for row in target['nativeFrames']:bindings[row['file']]={'file':row['file'],'sha256':row['sha256']}
 report.update(completionState='all-required-artifacts-written-and-hashed',completedFiles=[bindings[k] for k in sorted(bindings)])
 cached_completion(report,report['inputs'])
 verify.save(done,report)
 print(json.dumps({'report':rel(done),'sha256':sha(done),'counts':report['counts'],'boundedSceneDecodes':len(receipts),'unresolvedFailureCount':len(unresolved)},ensure_ascii=False))
 if unresolved:raise SystemExit(2)

def self_test():
 assert ranges([])==[] and ranges([1,2,4,6,7])==[[1,3],[4,5],[6,8]]
 select=balanced_select([0,1000,3000,100000]);assert select.count('eq(pts\\,')==4 and select.count('(')<12
 sample='#tb 0: 1/60000\n0, 0, 0, 1000, 3110400, '+'0'*32+'\n'
 rows,tb=verify.parse_decoded_frames(sample,1);assert rows[0]['md5']=='0'*32 and tb=='1/60000'
 old=[dict(md5='a'),dict(md5='b'),dict(md5='c')];new=[dict(md5='a'),dict(md5='x'),dict(md5='c')]
 assert ranges([i for i,(a,b) in enumerate(zip(old,new)) if a['md5']!=b['md5']])==[[1,2]]
 base={'inputs':{'test':1},'completionState':'all-required-artifacts-written-and-hashed','completedFiles':[proof(Path(__file__))],'unresolvedFailureCount':0,'unresolvedFailures':[]}
 assert cached_completion(base,{'test':1})==0
 failed={**base,'unresolvedFailureCount':1,'unresolvedFailures':[{'frame':1}]};assert cached_completion(failed,{'test':1})==2,'A prior exit2 must remain a failure on cache reuse'
 for broken in [{**base,'completionState':'interrupted'},{**base,'completedFiles':[]}]:
  try:cached_completion(broken,{'test':1})
  except AssertionError:pass
  else:raise AssertionError('Incomplete cache accepted')
 ast.parse(Path(__file__).read_text('utf8'))
 print('PASS CPU-only range/identity/selected-expression/parser checks; no media/model/decode opened')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prior-qa',type=Path);ap.add_argument('--prior-integrity',type=Path);ap.add_argument('--prior-framehash-directory',type=Path);ap.add_argument('--prior-master',type=Path);ap.add_argument('--prior-scene-plan',type=Path);ap.add_argument('--integrity',type=Path,default=Q/'integrity.json');ap.add_argument('--framehash-directory',type=Path);ap.add_argument('--master',type=Path,default=O/'euler-captioned.mp4');ap.add_argument('--output-directory',type=Path,default=Q/'encoded-captions-final');ap.add_argument('--changed-scene',action='append',default=None);ap.add_argument('--run',action='store_true');ap.add_argument('--plan-only',action='store_true');ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
 if args.self_test:self_test();return
 assert args.prior_qa and args.prior_integrity,'Supply the preserved prior QA/integrity paths; default never infers archived evidence'
 assert not(args.run and args.plan_only)
 args.changed_scene=args.changed_scene or ['v6-08','v6-09','v6-26','v6-27'];report,data=plan(args)
 args.output_directory.mkdir(parents=True,exist_ok=True);save(args.output_directory/'reuse-plan.json',report)
 if args.run:execute(args,report,data)
 else:print(json.dumps({'plan':rel(args.output_directory/'reuse-plan.json'),'status':report['status'],'counts':report['counts'],'noMediaDecoded':True},ensure_ascii=False))

if __name__=='__main__':main()
