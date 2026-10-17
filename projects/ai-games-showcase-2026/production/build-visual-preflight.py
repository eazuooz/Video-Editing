"""Render one silent FHD60 layout sample. This is not a narrated final video."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[3]
P=R/'projects/ai-games-showcase-2026'
O=P/'production/local/visual-preflight'
O.mkdir(parents=True,exist_ok=True)
control=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))
assert control['selectedVideo']=='ai-games-showcase-2026'
source=R/'production/preflight/ai-games-showcase-2026/local/fish-creator-demo.mp4'
out=O/'fish-layout-silent.mp4'
ass=O/'sample.ass'
ass.write_text('''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Malgun Gothic,48,&H00FFFFFF,&H00FFFFFF,&H00151F1B,&H00151F1B,-1,0,0,0,100,100,0,0,3,12,0,2,96,96,110,1
Style: Title,Malgun Gothic,52,&H0083CFE8,&H0083CFE8,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Body,Malgun Gothic,40,&H00F5F5F5,&H00F5F5F5,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Credit,Malgun Gothic,28,&H00F5F5F5,&H00F5F5F5,&H00000000,&H00000000,0,0,0,0,100,100,0,0,3,6,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,0:00:12.00,Title,,0,0,0,,{\\pos(96,84)}I Just Wanted to Fish
Dialogue: 1,0:00:00.00,0:00:04.00,Body,,0,0,0,,{\\pos(96,158)}섬을 돌아다니며 즐기는 낚시
Dialogue: 1,0:00:04.00,0:00:12.00,Body,,0,0,0,,{\\pos(96,158)}약 3주 작업 · 개발 중
Dialogue: 1,0:00:04.00,0:00:12.00,Body,,0,0,0,,{\\pos(96,216)}Claude Opus 5.5
Dialogue: 1,0:00:04.00,0:00:12.00,Body,,0,0,0,,{\\pos(96,274)}Blender MCP → Unity 6
Dialogue: 1,0:00:00.00,0:00:12.00,Credit,,0,0,0,,{\\pos(1240,84)}게임·자료: Fork Dev / ForkedPush
Dialogue: 2,0:00:00.00,0:00:05.80,Caption,,0,0,0,,{\\pos(960,970)}섬을 돌아다니며 낚시하는 게임입니다.
Dialogue: 2,0:00:05.80,0:00:12.00,Caption,,0,0,0,,{\\pos(960,970)}제작자가 공개한 작업 기간은\\N거의 3주입니다.
''',encoding='utf8')
# Relative filter path avoids Windows drive-colon escaping.
assrel=ass.relative_to(R).as_posix()
vf=f"scale=1920:1080,fps=60,drawbox=x=64:y=56:w=850:h=170:color=black@0.88:t=fill:enable='lt(t,4)',drawbox=x=64:y=56:w=850:h=298:color=black@0.88:t=fill:enable='gte(t,4)',ass='{assrel}'"
recipe={'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'assSha256':hashlib.sha256(ass.read_bytes()).hexdigest(),'sourceInSeconds':14,'durationSeconds':12,'filter':vf,'status':'silent-layout-only-not-final','codec':'libx264','cpuThreads':4}
receipt=O/'execution.json'
if out.exists() and receipt.exists() and json.loads(receipt.read_text(encoding='utf8')).get('recipe')==recipe:
    print('Unchanged sample reused');raise SystemExit(0)
subprocess.run(['ffmpeg','-v','warning','-y','-ss','14','-i',str(source),'-frames:v','720','-an','-vf',vf,'-c:v','libx264','-preset','fast','-crf','20','-threads','4','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],cwd=R,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)],text=True))
receipt.write_text(json.dumps({'recipe':recipe,'probe':probe,'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'visualReview':'pending'},indent=2)+'\n',encoding='utf8')
for name,second,scale in [('sample-1080.png','7',None),('sample-mobile.png','7','375:-1')]:
    cmd=['ffmpeg','-v','error','-y','-ss',second,'-i',str(out),'-frames:v','1']
    if scale:cmd+=['-vf','scale='+scale]
    subprocess.run(cmd+[str(O/name)],check=True)
print(out)
