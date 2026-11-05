"""Render the labeled input and material from the same linear uniform on the WARP device."""
import subprocess,time,os
from common import WORK,BASE,VOICE,write,read
from narration import LESSONS
# The input begins when its role has been named; the end state stays visible for the conclusion.
# The two integers refer to starts of the narrated clauses, counted from zero.
DEMOS={
 6:('광원의 초록 성분','약하게','강하게',3,4),
 12:('광택 지수 n','넓은 반짝임','좁은 반짝임',2,4),
 20:('빛이 오는 방향','표면 정면','표면 뒤쪽',2,4),
 21:('빛이 오는 방향','표면 정면','비스듬한 빛',1,3),
 30:('같은 광원의 방향','표면 정면','옆면과 뒷면',1,3),
 39:('표면점 P의 위치','어두운 꼭짓점 쪽','밝은 꼭짓점 쪽',2,4),
 42:('같은 광원의 위치','왼쪽','오른쪽',2,3),
 58:('광원과 표면 사이 거리 d','안쪽 경계','바깥 경계',2,4),
}
def specification(s):
    a=read(VOICE/f'{s:03}-alignment.json');frames=__import__('math').ceil((a['duration']+.16)*60)
    left,right=DEMOS[s][3:]
    lo=round((a['clauses'][left]+.06)*60)
    hi=round((a['clauses'][right]+.06)*60)
    if s==42:hi=round((a['duration']-1)*60)
    return frames,lo,max(lo+60,min(frames-1,hi))
def render(s):
    n,a,b=specification(s);dst=WORK/'demos';dst.mkdir(exist_ok=True)
    movie=dst/f'{s:03}.mp4';receipt=dst/f'{s:03}.json'
    exe=WORK/'surface.exe';shader=BASE/'surface.hlsl'
    from common import sha
    stamp=[sha(shader),sha(exe),n,a,b]
    if receipt.exists() and read(receipt)['stamp']==stamp and movie.is_file():return
    with (dst/f'{s:03}.log').open('w') as log:
        device=subprocess.Popen([str(exe),str(shader),str(s),str(n),str(a),str(b)],stdout=subprocess.PIPE,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','bgra','-s','852x480','-r','60','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','13','-pix_fmt','yuv420p','-g','120','-bf','0','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',str(movie)],stdin=device.stdout,stderr=log,check=True)
        finally:device.stdout.close()
        if device.wait()!=0:raise RuntimeError(f'WARP render failed: {s}')
    write(receipt,dict(stamp=stamp,renderer='D3D11 WARP · VS/PS Shader Model 5',input=DEMOS[s][0],linearRampFrames=[a,b],frames=n));print('Shader',s,n,flush=True)
if __name__=='__main__':
    deadline=time.monotonic()+2400;pending=set(DEMOS)
    while pending:
        ready=sorted(s for s in pending if (VOICE/f'{s:03}-alignment.json').is_file())
        for s in ready:render(s);pending.remove(s)
        if pending:
            if time.monotonic()>deadline:raise RuntimeError('Missing speech clock for shader')
            time.sleep(2)
