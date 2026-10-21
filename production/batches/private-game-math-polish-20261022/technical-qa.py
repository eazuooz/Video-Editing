"""Decode/integrity evidence only; never substitutes for direct visual review."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();records=[]
def pcm_hash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','pcm_s16le','-f','hash','-hash','sha256','-']).decode().strip()
def video_timestamps(p,frames):
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,duration_time','-of','json',str(p)]))['packets']
 assert len(data)==frames,('Unexpected encoded video packet count',len(data),frames)
 pts=sorted(float(x['pts_time']) for x in data)
 max_error=max(abs(t-i/60) for i,t in enumerate(pts))
 assert max_error<.00002,('Non-contiguous presentation timestamps',max_error)
 durations=[float(x['duration_time']) for x in data if 'duration_time' in x]
 assert all(abs(t-1/60)<.00002 for t in durations),'Variable or unexpected packet duration'
 return {'packets':len(data),'firstPts':pts[0],'lastPts':pts[-1],'maxErrorFrom60FpsGridSeconds':max_error,'contiguous':True}
original=pcm_hash(e.O/'baseline-audio.m4a')
for kind in ['clean','captioned']:
 p=e.D/f'{e.slug}.{kind}.mp4';v=e.verify(p,e.T['frames']);e.ff(['-v','error','-i',p,'-f','null','-'],f'decode-{kind}.log')
 assert pcm_hash(p)==original,'The recovered performance must not be shortened or re-encoded'
 records.append({'kind':kind,'path':rel(p),'sha256':sha(p),'frames':int(v['nb_frames']),'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'timestamps':video_timestamps(p,e.T['frames']),'fullDecode':True,'unchangedRecoveredDecodedPcmSha256':original})
assert len(e.T['koCaptions'])==len(e.T['enCaptions'])
assert all(abs(a['start']-b['start'])<.001 and abs(a['end']-b['end'])<.001 for a,b in zip(e.T['koCaptions'],e.T['enCaptions']))
save(e.H/'technical-qa.json',{'outputs':records,'captionPairs':len(e.T['koCaptions']),'originalTimelineSha256':sha(e.P/'production/timeline.json'),'wordsAndCueTimesPreserved':True,'newTts':False,'newMusic':False,'originalPcmRecovered':False,'directVisualReview':'pending','humanReview':'pending'})
print(e.id,'full decode/frame count/recovered PCM/caption timing passed; direct visual QA still required',flush=True)
