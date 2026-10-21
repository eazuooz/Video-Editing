"""Decode/integrity evidence only; never substitutes for direct visual review."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();records=[]
def pcm_hash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','pcm_s16le','-f','hash','-hash','sha256','-']).decode().strip()
original=pcm_hash(e.O/'baseline-audio.m4a')
for kind in ['clean','captioned']:
 p=e.D/f'{e.slug}.{kind}.mp4';v=e.verify(p,e.T['frames']);e.ff(['-v','error','-i',p,'-f','null','-'],f'decode-{kind}.log')
 assert pcm_hash(p)==original,'The recovered performance must not be shortened or re-encoded'
 records.append({'kind':kind,'path':rel(p),'sha256':sha(p),'frames':int(v['nb_frames']),'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'fullDecode':True,'unchangedRecoveredDecodedPcmSha256':original})
assert len(e.T['koCaptions'])==len(e.T['enCaptions'])
assert all(abs(a['start']-b['start'])<.001 and abs(a['end']-b['end'])<.001 for a,b in zip(e.T['koCaptions'],e.T['enCaptions']))
save(e.H/'technical-qa.json',{'outputs':records,'captionPairs':len(e.T['koCaptions']),'originalTimelineSha256':sha(e.P/'production/timeline.json'),'wordsAndCueTimesPreserved':True,'newTts':False,'newMusic':False,'originalPcmRecovered':False,'directVisualReview':'pending','humanReview':'pending'})
print(e.id,'full decode/frame count/recovered PCM/caption timing passed; direct visual QA still required',flush=True)
