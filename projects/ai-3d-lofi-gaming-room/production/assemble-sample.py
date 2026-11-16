"""Assemble the native Unity sample, concise labels and the verified CC0 track."""
from pathlib import Path
import hashlib, json, subprocess

root=Path(__file__).resolve().parents[3]
folder=root/'projects/ai-3d-lofi-gaming-room/production/local/unity-sample-v1'
music=root/'sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3'
captions=[
 (0,5,'Tripo로 만든 캐릭터와 헤드폰을 Unity에 넣었습니다.','A Tripo character and headphones, running in Unity.'),
 (5,17,'Tripo 걷기 모션 · 이동 거리는 애니메이션에 맞췄습니다.','Native Tripo walk; movement follows its root-motion distance.'),
 (17,24,'대기 동작과 캐릭터를 가까이 확인합니다.','A closer look at the character and its native idle animation.'),
 (24,29,'헤드폰은 2천 삼각형으로 줄인 3D 모델입니다.','The headphones were reduced to 2,000 triangles.'),
 (29,32,'낮과 밤 조명도 바꿔 봅니다.','Switching between daytime and night lighting.'),
 (32,36,'첫 Unity 샘플 · 다음은 앉기·독서와 방 꾸미기입니다.','First Unity sample. Sitting, reading and room detail come next.')]
def timecode(t,ass=False):
 h=int(t//3600);m=int(t//60)%60;s=int(t)%60
 return f'{h}:{m:02}:{s:02}.00' if ass else f'{h:02}:{m:02}:{s:02},000'
for language,index in [('ko',2),('en',3)]:
 text='\n\n'.join(f'{i+1}\n{timecode(a)} --> {timecode(b)}\n{row[index]}' for i,row in enumerate(captions) for a,b in [row[:2]])+'\n'
 (folder/f'unity-sample.{language}.srt').write_bytes(text.encode('utf-8'))
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Malgun Gothic,34,&H00F0F1E7,&H00F0F1E7,&H001F2522,&HA020221C,-1,0,0,0,100,100,0,0,1,2,0,2,80,80,48,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
ass+='\n'.join(f'Dialogue: 0,{timecode(a,True)},{timecode(b,True)},Label,,0,0,0,,{ko}' for a,b,ko,en in captions)+'\n'
(folder/'captions.ass').write_bytes(ass.encode('utf-8'))
audio='atrim=0:36,asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-2:LRA=8,afade=t=in:d=0.8,afade=t=out:st=35:d=1'
base=['ffmpeg','-hide_banner','-loglevel','error','-y','-i','unity-native-clean.mp4','-i',str(music),'-map','0:v:0','-map','1:a:0','-af',audio,'-t','36','-c:a','aac','-b:a','192k','-ar','48000']
subprocess.run(base+['-c:v','copy','-movflags','+faststart','unity-sample.clean.mp4'],cwd=folder,check=True)
subprocess.run(base+['-vf','ass=captions.ass','-c:v','h264_nvenc','-preset','p5','-cq','19','-pix_fmt','yuv420p','-movflags','+faststart','unity-sample.captioned.mp4'],cwd=folder,check=True)
outputs=[]
for name in ['unity-sample.clean.mp4','unity-sample.captioned.mp4','unity-sample.ko.srt','unity-sample.en.srt']:
 p=folder/name;outputs.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
report={'kind':'36-second-native-Unity-sample-not-final-production-video','width':1920,'height':1080,'fps':60,'duration':36,'outputs':outputs,'music':{'title':'Morning Coffee','creator':'HoliznaCC0','license':'CC0 1.0','source':'https://opengameart.org/content/lo-fi-and-chill-collection','author':'https://opengameart.org/users/holizna','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/','sourceSha256':hashlib.file_digest(music.open('rb'),'sha256').hexdigest()},'humanReview':False,'youtubeUploaded':False,'webGameBuilt':False}
(folder/'delivery.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'outputs':outputs},ensure_ascii=True))
