"""Visual-only D27/D28 assembler. No task starts on import.

prepare reuses every unchanged game cut and validates exact Unity frame counts;
pair creates the two masters using the existing encoded AAC without re-mixing;
verify decodes both complete masters and proves the audio/caption preservation.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
MEDIA=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
SLUGS=('in-game-cutscenes','start-with-climax')

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def run(args,log):
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('w',encoding='utf-8') as f:r=subprocess.run(['ffmpeg','-hide_banner','-v','warning','-n',*map(str,args)],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
 if r.returncode:raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-4000:])
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def streamhash(p,map='0:a:0'):
 return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map',map,'-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def audio_timeline(p):
 packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts_time,dts_time,duration_time,side_data_list','-of','json',str(p)]))['packets']
 return {'sha256':hashlib.sha256(json.dumps(packets,sort_keys=True).encode()).hexdigest(),'packetCount':len(packets),'firstPacket':packets[0],'lastPacket':packets[-1]}
def check_video(p,frames):
 v=next(x for x in probe(p)['streams'] if x['codec_type']=='video')
 if (v['width'],v['height'],Fraction(v['avg_frame_rate']),int(v.get('nb_frames',0)))!=(1920,1080,60,frames):raise ValueError(('Frame format mismatch',str(p),v))
 return v
def authorized(slug):
 c=read(ROOT/'shared/publishing/video-production-control.json')
 # The parent stores the exact new finite selection before capture/encoding.
 # A matching record can live in either established scoped collection.
 candidates=[]
 for key in ('finiteBatchAuthorizations','scopedBatchAuthorizations'):
  d=c.get(key,{})
  if isinstance(d,dict):candidates += [v for k,v in d.items() if 'unity' in k and isinstance(v,dict)]
 if not any(slug in json.dumps(x,ensure_ascii=False) and x.get('localProductionAuthorized',x.get('fullProductionAuthorized',False)) for x in candidates):
  raise ValueError('Current explicitly selected Unity visual revision authorization missing')

def context(slug,capture_root=None):
 if slug not in SLUGS:raise ValueError('Wrong project')
 p=ROOT/'projects'/slug;rev=p/'production/unity-visual-v2';plan=read(rev/'plan.json');old=read(ROOT/plan['baselinePlan'])
 assert sha(ROOT/plan['baselinePlan'])==plan['baselinePlanSha256'],'Frozen edit changed'
 for kind,key in [('captioned.mp4','baselineCaptioned'),('clean.mp4','baselineClean')]:
  assert sha(ROOT/plan[key])==plan['baselineSha256'][kind], 'Frozen reviewed master changed'
 out=MEDIA/slug/plan.get('mediaEditDirectory','edit');out.mkdir(parents=True,exist_ok=True)
 capture=Path(capture_root) if capture_root else MEDIA/slug/'captures'
 assert out.resolve().is_relative_to(MEDIA.resolve())
 return p,rev,plan,old,out,capture

def prepare(slug,capture_root):
 authorized(slug);p,rev,plan,old,out,capture=context(slug,capture_root)
 olddir=ROOT/old['outputDir'];parts=[]
 baseline_pair=read(olddir/'pair-build.json')
 assert baseline_pair['outputs']['captioned']['sha256']==plan['baselineSha256']['captioned.mp4']
 assert baseline_pair['outputs']['clean']['sha256']==plan['baselineSha256']['clean.mp4']
 items=[('branding',120,None),*[(c['id'],c['frames'],c) for c in old['cuts']],('membership',600,None)]
 for item_index,(name,frames,cut) in enumerate(items):
  changed=cut is not None and cut['kind']=='explanation'
  selected=next((x for x in plan['cuts'] if x['id']==name),None)
  source=(MEDIA/slug/'render'/selected['captureVersion']/name/'unity.mp4') if changed and selected.get('captureVersion') else (capture/name/'unity.mp4') if changed else olddir/(name+'.mp4')
  if changed:
   success=source.parent/'capture-success.json'
   if not success.exists():success=source.parent/'render-success.json'
   if not success.exists():raise FileNotFoundError('Unity successful capture receipt missing: '+str(source))
   receipt=read(success);request=read(source.parent/'request.json')
   freeze=read(ROOT/plan['captureFreezeRecords'][selected['captureVersion']])
   subset=[x for x in freeze['files'] if not Path(x['path']).name.endswith('Stage.cs') or Path(x['path']).name in ['DesignLessonStage.cs','D27D28Stage.cs']]
   fingerprint=hashlib.sha256(json.dumps(subset,sort_keys=True).encode()).hexdigest()
   assert fingerprint==freeze['fingerprints']['D27D28Stage']==receipt['compiledSourceFingerprint']==request['expectedFingerprint'],'Unapproved compiled capture'
   stage=next(x for x in subset if x['path'].endswith('/D27D28Stage.cs'))
   assert stage['sha256']==selected['captureStageSourceSha256'],'Wrong per-cut stage source'
   frozenFiles={x['path']:x['sha256'] for x in subset}
   for archived in plan.get('captureCommonSourceArchive',[]):
    assert sha(ROOT/archived['archivedSource'])==archived['sha256']==frozenFiles[archived['captureSource']],'Archived capture runtime is not the frozen runtime'
   proof=read(ROOT/plan['targetedRevisionProof'])
   assert sha(ROOT/proof['beforeSource'])==proof['beforeSha256'] and sha(ROOT/proof['afterSource'])==proof['afterSha256']
   assert sha(ROOT/proof['diff'])==proof['diffSha256'],'Targeted equivalence proof changed'
   assert (name in proof['affectedCuts'][slug])==(selected['captureVersion']=='v4'),'Capture version disagrees with exact changed-cut proof'
   assert receipt['status']=='complete' and receipt['frames']==frames and receipt['completed']==frames and not receipt['error'],'Incomplete Unity receipt'
  if not source.is_file():raise FileNotFoundError(source)
  check_video(source,frames)
  sourcehash=sha(source)
  if not changed:assert sourcehash==baseline_pair['signature']['cutSha256'][item_index],('Changed preserved gameplay/bookend',name)
  joined=out/'join'/(name+'.mp4');receipt=out/'join'/(name+'.json')
  if receipt.exists():
   r=read(receipt);assert r['sourceSha256']==sourcehash and r['outputSha256']==sha(joined),'Prior join hash mismatch'
  else:
   run(['-i',source,'-map','0:v:0','-an','-sn','-dn','-c:v','copy','-video_track_timescale','60000','-movflags','+faststart',joined],out/'join'/(name+'.log'))
   v=check_video(joined,frames);assert Fraction(v['time_base'])==Fraction(1,60000)
   assert streamhash(source,'0:v:0')==streamhash(joined,'0:v:0'),'Join changed compressed pixels'
   write(receipt,{'source':str(source),'sourceSha256':sourcehash,'outputSha256':sha(joined),'frames':frames,'videoPacketIdentity':True})
  parts.append({'id':name,'frames':frames,'kind':'unity-explanation' if changed else 'unchanged-original-cut','source':str(source),'sourceSha256':sourcehash,'joined':str(joined),'joinedSha256':sha(joined),**({'captureVersion':selected['captureVersion'],'compiledSourceFingerprint':fingerprint,'captureStageSourceSha256':selected['captureStageSourceSha256'],'successReceiptSha256':sha(success)} if changed else {})})
 assert sum(x['frames'] for x in parts)==old['totalFrames']
 concat=out/'concat.txt';concat.write_text('\n'.join("file '"+Path(x['joined']).as_posix().replace("'","'\\''")+"'" for x in parts)+'\n',encoding='utf-8')
 aac=out/'preserved-audio.m4a';base=ROOT/plan['baselineClean']
 if not aac.exists():run(['-i',base,'-map','0:a:0','-vn','-c:a','copy','-movflags','+faststart',aac],out/'preserve-audio.log')
 audiohash=streamhash(base);assert audiohash==streamhash(aac),'AAC must be copied unchanged'
 timeline=audio_timeline(base);assert timeline==audio_timeline(aac),'AAC timing or priming differs'
 for language in ('ko','en'):
  src=olddir/f'captions.{language}.srt';dst=out/f'{slug}.{language}.srt'
  if dst.exists():assert sha(src)==sha(dst)
  else:shutil.copy2(src,dst)
 write(out/'assembly-inputs.json',{'slug':slug,'revision':'unity-visual-v2','parts':parts,'totalFrames':old['totalFrames'],'fps':60,'baselineCaptioned':plan['baselineCaptioned'],'baselineCaptionedSha256':plan['baselineSha256']['captioned.mp4'],'baselineClean':plan['baselineClean'],'baselineCleanSha256':plan['baselineSha256']['clean.mp4'],'audioPacketsSha256':audiohash,'audioTimeline':timeline,'aacSha256':sha(aac),'ass':str(olddir/'captions.ko.ass'),'assSha256':sha(olddir/'captions.ko.ass'),'unchangedNarration':True,'unchangedGameFootage':True,'unchangedSrt':True})
 print('Prepared',slug,len(parts),'segments; copied exact AAC',flush=True)

def pair(slug):
 authorized(slug);p,rev,plan,old,out,_=context(slug);e=read(out/'assembly-inputs.json')
 for x in e['parts']:assert sha(Path(x['joined']))==x['joinedSha256']
 assert sha(out/'preserved-audio.m4a')==e['aacSha256'];assert sha(Path(e['ass']))==e['assSha256']
 clean=out/f'{slug}.clean.mp4';cap=out/f'{slug}.captioned.mp4'
 if clean.exists() or cap.exists():raise FileExistsError('Existing pair preserved; inspect or use a distinct output revision')
 # One continuous frame clock prevents a reset when input H.264 metadata changes.
 ass=Path(e['ass']).as_posix().replace(':','\\:').replace("'","'\\''")
 graph="[0:v]setpts=N/(60*TB),settb=1/60000,setsar=1,format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709,split=2[clean][ci];[ci]ass='"+ass+"'[captioned]"
 args=['-filter_threads','1','-filter_complex_threads','1','-f','concat','-safe','0','-reinit_filter','0','-i',out/'concat.txt','-i',out/'preserved-audio.m4a','-filter_complex',graph]
 for key,target in [('clean',clean),('captioned',cap)]:
  args += ['-map',f'[{key}]','-map','1:a:0','-frames:v',str(old['totalFrames']),'-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000','-fps_mode','passthrough','-c:a','copy','-movflags','+faststart',target]
 run(args,out/'pair.log')
 write(out/'pair.json',{'status':'encoded-awaiting-complete-verification','inputsSha256':sha(out/'assembly-inputs.json'),'cleanSha256':sha(clean),'captionedSha256':sha(cap),'audioPacketsSha256':e['audioPacketsSha256']})
 print('Encoded',slug,flush=True)

def verify(slug):
 p,rev,plan,old,out,_=context(slug);e=read(out/'assembly-inputs.json');records={}
 for kind in ('clean','captioned'):
  file=out/f'{slug}.{kind}.mp4';v=check_video(file,old['totalFrames']);audio=streamhash(file)
  assert audio==e['audioPacketsSha256'],'Audio differs from frozen approved baseline'
  timeline=audio_timeline(file);assert timeline==e['audioTimeline'],'Audio packet timing/priming or final padding changed'
  run(['-xerror','-err_detect','explode','-threads','4','-i',file,'-map','0:a:0','-vn','-f','null','-'],out/f'{kind}-audio-decode.log')
  args=['ffprobe','-v','error','-threads','4','-err_detect','explode','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(file)]
  process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8');count=0;maxerr=0
  for line in process.stdout:
   cell=line.strip().split(',')[0]
   if not cell:continue
   try:pts=float(cell)
   except ValueError:continue
   err=abs(pts-count/60);assert err<.000025,('PTS discontinuity',kind,count,pts);maxerr=max(maxerr,err);count+=1
  stderr=process.stderr.read();assert process.wait()==0 and not stderr.strip(),stderr
  assert count==old['totalFrames'],('Full decoded frame count',count)
  records[kind]={'path':str(file),'sha256':sha(file),'width':1920,'height':1080,'fps':60,'decodedFrames':count,'maxPtsErrorSeconds':maxerr,'audioPacketsSha256':audio,'audioTimeline':timeline,'fullDecode':'pass'}
 for language in ('ko','en'):assert sha(out/f'{slug}.{language}.srt')==plan['baselineSha256'][f'{language}.srt']
 write(out/'structural-verification.json',{'status':'pass','outputs':records,'aacIdenticalToBaselineAndEachOther':True,'srtIdenticalToBaseline':True,'bodyGameplayFrames':old['actualFrames'],'bodyExplanationFrames':old['explanationFrames'],'bodyGameplayShare':old['actualFrames']/old['bodyFrames'],'totalFrames':old['totalFrames'],'durationSeconds':old['totalFrames']/60,'visualReview':'separate required','humanReview':'pending new visual revision'})
 print('Verified',slug,'complete pair, exact audio/captions',flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','pair','verify']);ap.add_argument('slug',choices=SLUGS);ap.add_argument('--capture-root');a=ap.parse_args()
 if a.stage=='prepare':prepare(a.slug,a.capture_root)
 elif a.stage=='pair':pair(a.slug)
 else:verify(a.slug)
