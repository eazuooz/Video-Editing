"""Restore the meaning of the original 'large/small screen' passage without moving either main camera.

Both native performers remain at their original displayed sizes. The centre inset copies
the exact same left-side source frame into a small display for the first two captions.
"""
from pipeline import *
import subprocess
ap,vp=libs();ap.require_authorized('video-cuts');p=read(H/'edit-plan.json');edit=L/'edit'
cut=next(x for x in p['cuts'] if x['id']=='A02-E011');raw=R/cut['renderedSource'];assert sha(raw)==cut['renderedSourceSha256']
assert read(R/cut['unrealCapture']['path'])['movieSha256']==sha(raw)
cues=read(edit/'captions.json')['cues'];last=next(c for c in cues if c['cue']==44)
end_frame=round(last['start']*60)-cut['startFrame'];t=end_frame/60
original=edit/'A02-E011.mp4';receipt=edit/'A02-E011-render.json';base=read(receipt)
assert base['outputSha256']==sha(original)
native_px=L/'unreal/A02-E011-raw.mp4';assert sha(native_px)==read(R/cut['unrealCapture']['path'])['nativePixels']['sha256']
labels=edit/'A02-E011-size-labels.ass';ass,geo=vp.explanation_kind_label(cut,p)
def text(x,y,size,s,color):return r'{\an5\pos('+f'{x},{y}'+r')\fs'+str(size)+r'\b1\bord0\shad0\1c&H'+color+r'&}'+s
ass+=vp.event(0,t,text(960,307,40,'화면 크기 비교','83CFE8'),5)
ass+=vp.event(0,t,text(960,645,34,'왼쪽과 같은 동작','F0F0F0'),5)
labels.write_text(ass,encoding='utf8')
f="[1:v]crop=660:680:150:200,scale=260:268:flags=lanczos,setsar=1[mini];"
f+=f"[0:v]drawbox=x=733:y=259:w=454:h=433:color=0x101513:t=fill:enable='lt(t,{t})',drawbox=x=733:y=259:w=454:h=433:color=0x789488:t=3:enable='lt(t,{t})'[bg];"
f+=f"[bg][mini]overlay=830:344:enable='lt(t,{t})',ass={vp.filter_path(labels)}[out]"
tmp=edit/'E011-with-size-inset.partial.mp4'
vp.run(['-threads','4','-i',str(raw),'-threads','2','-i',str(native_px),'-an','-filter_complex',f,'-map','[out]','-frames:v',str(cut['frames']),*vp.ENCODER,'-movflags','+faststart',str(tmp)],edit/'E011-inset.log')
vp.assert_video(tmp,cut['frames']);original_before=read(H/'screen-size-inset.json')['previousEditedNoInset'] if base.get('containsDisplaySizeInset') else artifact(original);tmp.replace(original)
spec={'purpose':'Only during the preserved screen-size introduction: same source frame as the baseline left mannequin, reduced displayed image. Both native mains, camera, amplitude and timing unchanged.','nativeSource':artifact(raw),'sourceCrop':[150,200,660,680],'displayWindow':[830,344,260,268],'panel':[733,259,454,433],'globalFrames':[cut['startFrame'],cut['startFrame']+end_frame],'durationSeconds':t,'smallInsetDoesNotCoverMainPerformersOrCaption':True,'previousEditedNoInset':original_before}
spec['unlabelledSameNativeFrames']=artifact(native_px);save(H/'screen-size-inset.json',spec);cut['screenSizeInset']=artifact(H/'screen-size-inset.json');save(H/'edit-plan.json',p)
base['signature'].update(cut=cut,displayInset=spec,sourceSha256=sha(raw),codeSha256=sha(Path(__file__)),assSha256=sha(labels));base['outputSha256']=sha(original);base['containsDisplaySizeInset']=True;save(receipt,base)
print('E011 inset exactly',end_frame,'frames. The voice, subtitles, mix and native comparison are unchanged.')
