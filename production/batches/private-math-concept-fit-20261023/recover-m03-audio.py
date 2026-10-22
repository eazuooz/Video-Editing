from common import *
authorized('M03-original')
P=R/'projects/game-math-orientation-matrices';O=P/'production/local/concept-fit-v2';H=P/'production/concept-fit-v2'
src=O/'original-upload-recovered.mp4';d=probe(src);T=read(P/'production/timeline.json')
assert abs(float(d['format']['duration'])-T['seconds'])<.1
dst=O/'baseline-audio.m4a'
if not dst.exists():run(['ffmpeg','-v','error','-n','-i',src,'-map','0:a:0','-c:a','copy',dst])
v=next(x for x in d['streams'] if x['codec_type']=='video');a=next(x for x in d['streams'] if x['codec_type']=='audio')
save(H/'restoration.json',dict(verifiedAt=now(),baselineVideoId='6-kP65hrZcI',baselineTimelineSha256=sha(P/'production/timeline.json'),
 method='Authenticated YouTube Studio > Options > Download via observed link; read-only original recovery',reviewFile=rel(src),reviewSha256=sha(src),reviewDimensions=[v['width'],v['height']],reviewPixelsProductionAllowed=False,
 audioFile=rel(dst),audioSha256=sha(dst),audioCodec=a['codec_name'],audioSampleRate=a['sample_rate'],duration=float(d['format']['duration']),originalPcmAvailable=False,newTts=False,
 originalPrivateUploadStillExists=True,platformMutation=False))
c=read(B/'checkpoint.json');c['blocked']=[x for x in c['blocked'] if x['id']!='M03-original'];next(e for e in c['entries'] if e['id']=='M03-original')['status']='original-aac-restored-concept-matched-edit-planning';c['updatedAt']=now();save(B/'checkpoint.json',c)
print('Original15:03 AAC recovered; downloaded720p pixels excluded from production. '+sha(dst))
