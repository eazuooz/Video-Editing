"""CPU-only sample caption/label compositing and integrity evidence."""
from pathlib import Path
import hashlib,json,math,re,shutil,subprocess

ROOT=Path(__file__).resolve().parents[5]
P=ROOT/'projects/game-math-euler-axis-angle'
OUT=P/'production/local/revision-v2/unity-preview'

def stamp(seconds):
    h,rest=divmod(seconds,3600);m,s=divmod(rest,60)
    return f'{int(h)}:{int(m):02d}:{s:05.2f}'

def main():
    ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe')
    baseline=(P/'script/final.ko.ass').read_text(encoding='utf-8-sig')
    first=next(line for line in baseline.splitlines() if '오일러 각은 숫자 세 개로 자세를 표현합니다.' in line)
    start=first.split(',')[1]
    lines=[line for line in baseline.splitlines() if line.startswith('Dialogue:') and line.split(',')[1]==start]
    head=baseline.split('[Events]')[0]+'[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n'
    events=[]
    for line in lines:
        fields=line.split(',',3);fields[1]='0:00:00.00';fields[2]='0:00:03.00';events.append(','.join(fields))
    def text(s,t,x,y,size,color='101810',layer=4,align=7):
        return f'Dialogue: {layer},{stamp(s)},{stamp(t)},Text,,0,0,0,,{{\\an{align}\\pos({x},{y})\\fs{size}\\c&H{color}&\\b1\\bord0}}'
    events.append(text(0,3,120,85,60)+'오일러 각 (Euler angles)')
    events.append(text(0,3,120,163,44)+'세 숫자 + 회전축 + 적용 순서')
    events.append(text(0,3,120,690,44)+'연한 축: 고정된 월드 축\\N진한 축: 몸체와 함께 도는 축')
    events.append(text(0,3,120,815,44)+'R = Ry(h) Rx(p) Rz(b)  ·  오른손 / 열벡터')
    colors={'a.bodyX':'4234D5','a.bodyY':'4C8515','a.bodyZ':'C36422'}
    labels={'a.bodyX':'x','a.bodyY':'y','a.bodyZ':'z'}
    states=[json.loads(l) for l in (OUT/'03-rotation-sample.anchors.ndjson').read_text().splitlines()]
    for i in range(0,len(states),3):
        center=next(a['pixelTopLeft'] for a in states[i]['anchors'] if a['name']=='a.center')
        for a in states[i]['anchors']:
            if a['name'] not in colors or not a['inFrame']:continue
            pos=a['pixelTopLeft'];dx=pos['x']-center['x'];dy=pos['y']-center['y'];length=math.hypot(dx,dy)
            x=round(pos['x']+dx/max(length,1)*36);y=round(pos['y']+dy/max(length,1)*36)
            events.append(text(i/60,min(3,(i+3)/60),x,y,44,colors[a['name']],5,5)+labels[a['name']])
    ass=OUT/'03-caption-preview.ass';ass.write_text(head+'\n'.join(events)+'\n',encoding='utf8')
    raw=OUT/'03-rotation-sample.mp4';captioned=OUT/'03-caption-preview.mp4'
    subprocess.run([ffmpeg,'-v','error','-y','-i',str(raw),'-vf','ass=03-caption-preview.ass',
        '-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',str(captioned)],cwd=OUT,check=True)
    for name,time in [('start',0),('middle',1.5),('end',2.98)]:
        dest=OUT/f'03-caption-{name}.png'
        subprocess.run([ffmpeg,'-v','error','-y','-ss',str(time),'-i',str(captioned),'-frames:v','1',str(dest)],check=True)
    subprocess.run([ffmpeg,'-v','error','-y','-ss','1.5','-i',str(captioned),'-vf','scale=375:-1','-frames:v','1',str(OUT/'03-caption-mobile.png')],check=True)
    data=json.loads(subprocess.check_output([ffprobe,'-v','error','-select_streams','v:0','-show_entries',
        'stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(raw)],text=True))['streams'][0]
    assert data['width']==1920 and data['height']==1080 and data['r_frame_rate']=='60/1' and int(data['nb_frames'])==180,data
    subprocess.run([ffmpeg,'-v','error','-i',str(raw),'-f','null','-'],check=True)
    report=dict(schemaVersion=1,scope='180frame spatial system sample only, not whole-video approval',
        geometry='self-authored aircraft; no game implementation/physics claim',stream=data,
        rawSha256=hashlib.sha256(raw.read_bytes()).hexdigest(),captionedSha256=hashlib.sha256(captioned.read_bytes()).hexdigest(),
        anchors=len(states),captionSource='Exact baseline scene03first caption, same boxed-white-forest style and fixed960,970/48px',
        fullDecode='passed',visualFhdAnd375px='pending direct inspection',wholeLesson=False)
    (OUT/'sample-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
