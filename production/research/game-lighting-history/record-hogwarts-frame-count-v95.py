"""Record the observed ffprobe count and read the actual MP4 edit list.

No extraction, remux, repeated full decode, timing approval or media mutation.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'production/research/game-lighting-history/local/hogwarts-official-site-v79/hogwarts-official-site-castle2022.mp4'
TARGET=ROOT/'projects/game-lighting-history-04/production/hogwarts-native-frame-count-v95.json'
EXPECTED='f7129a728b7833ca6205d63550f77c5cc6975bd0e77b93426103565c52563aed'
data=SOURCE.read_bytes()
digest=hashlib.sha256(data).hexdigest()
if digest!=EXPECTED:raise RuntimeError('Native source changed; inspect current media')
if TARGET.exists():raise RuntimeError('Preserve prior observed count evidence')
def boxes(start,end):
 at=start
 while at+8<=end:
  size,kind=struct.unpack_from('>I4s',data,at);header=8
  if size==1:
   size=struct.unpack_from('>Q',data,at+8)[0];header=16
  elif size==0:size=end-at
  if size<header or at+size>end:raise RuntimeError('Invalid MP4 box')
  yield kind.decode('ascii'),at+header,at+size
  at+=size
def child(start,end,kind):
 found=[(a,b) for k,a,b in boxes(start,end) if k==kind]
 if len(found)!=1:raise RuntimeError('Expected one '+kind)
 return found[0]
def header_clock(a):
 version=data[a]
 clock=a+(20 if version==1 else 12)
 rate=struct.unpack_from('>I',data,clock)[0]
 duration=struct.unpack_from('>Q' if version==1 else '>I',data,clock+4)[0]
 return dict(version=version,timeScale=rate,durationTicks=duration,durationSeconds=duration/rate)
moov=child(0,len(data),'moov');mvhd=child(*moov,'mvhd');movie=header_clock(mvhd[0])
tracks=[]
for kind,a,b in boxes(*moov):
 if kind!='trak':continue
 mdia=child(a,b,'mdia');mdhd=child(*mdia,'mdhd');media=header_clock(mdhd[0])
 hdlr=child(*mdia,'hdlr');handler=data[hdlr[0]+8:hdlr[0]+12].decode('ascii')
 edits=[]
 for k,e,f in boxes(a,b):
  if k!='edts':continue
  elst=child(e,f,'elst');version=data[elst[0]];count=struct.unpack_from('>I',data,elst[0]+4)[0];cursor=elst[0]+8
  for _ in range(count):
   fmt='>Qqhh' if version==1 else '>Iihh';duration,media_time,integer,fraction=struct.unpack_from(fmt,data,cursor);cursor+=struct.calcsize(fmt)
   edits.append(dict(segmentDurationTicks=duration,segmentDurationSeconds=duration/movie['timeScale'],mediaTimeTicks=media_time,mediaTimeSeconds=media_time/media['timeScale'] if media_time!=-1 else None,rateInteger=integer,rateFraction=fraction))
 tracks.append(dict(handler=handler,mediaClock=media,editList=edits))
video=[t for t in tracks if t['handler']=='vide']
if len(video)!=1:raise RuntimeError('Expected one native video track')
observed=dict(width=1920,height=1080,r_frame_rate='30/1',time_base='1/15360',start_pts=0,start_time='0.000000',duration_ts=2719242,duration='177.033984',nb_frames='5401',nb_read_frames='5311')
record=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),source=dict(path=SOURCE.relative_to(ROOT).as_posix(),sha256=digest),status='native-edited-playback-frame-count-observed; exact-use-cut-review-pending',observedProbe=dict(command='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe -v error -threads 2 -select_streams v:0 -count_frames -show_entries stream=width,height,r_frame_rate,time_base,start_pts,start_time,duration_ts,duration,nb_frames,nb_read_frames:format=duration -of json '+SOURCE.relative_to(ROOT).as_posix(),exitCode=0,wallTimeSeconds=9.6,stream=observed,formatDuration='177.033984',provenance='Actual tool output read directly in this turn; probe is not rerun by this recorder.'),movieClock=movie,tracks=tracks,decodedPlaybackFrames=5311,containerFrameEntries=5401,differenceEntries=90,expectedThirtyFpsFramesRounded=5311,nativePlaybackStartsAtPtsZero=True,sourceMutated=False,newFramesExtracted=0,gpuJobs=0,exactCutAndMovingPixelsApproved=False,fullContinuousMovingReviewApproved=False,rightsApprovedForPublicUse=False,finalTimingApproved=False,uploaded=False)
TARGET.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(record=TARGET.relative_to(ROOT).as_posix(),decodedFrames=5311,containerEntries=5401,videoEditList=video[0]['editList'],finalTimingApproved=False),ensure_ascii=False))
