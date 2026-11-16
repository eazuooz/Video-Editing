"""Build the PC nature/material review; leave the approved v1 files untouched."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
folder=root/'projects/ai-3d-lofi-gaming-room/production/local/nature-v2'
music=root/'sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3'
rows=[
 (0,6,'식물과 소품을 더한 두 번째 PC 테스트입니다.','The second PC test, with more plants and room detail.'),
 (6,18,'기존 걷기·대기 모션에 머리카락의 작은 흔들림을 더했습니다.','Original walk and idle clips, with subtle secondary hair motion.'),
 (18,25,'캐릭터는 4K 색상 텍스처 · 표면 굴곡과 거칠기도 반영했습니다.','4K character color texture, with normal and roughness maps.'),
 (25,32,'뒤쪽 머리카락이 움직임과 바람에 가볍게 흔들립니다.','The ponytail responds gently to motion and a light breeze.'),
 (32,38,'헤드폰도 색상·굴곡·거칠기·금속성 재질을 다듬었습니다.','The headphones now use color, normal, roughness and metallic maps.'),
 (38,43,'휘어진 잎·잎맥·줄기와 은은한 흔들림을 더했습니다.','Curved leaves, veins, stems and a gentle breeze.'),
 (43,48,'PC 실행 파일에서 낮밤·비·음악을 직접 조작할 수 있어요.','Control day, night, rain and music in the PC executable.')]
def tc(t,ass=False):return f'0:{int(t//60):02}:{int(t%60):02}.00' if ass else f'00:{int(t//60):02}:{int(t%60):02},000'
for lang,col in [('ko',2),('en',3)]:
 text='\n\n'.join(f'{i+1}\n{tc(r[0])} --> {tc(r[1])}\n{r[col]}' for i,r in enumerate(rows))+'\n'
 (folder/f'lofi-room-nature-v2.{lang}.srt').write_bytes(text.encode())
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
ass+='\n'.join(f'Dialogue: 0,{tc(a,True)},{tc(b,True)},Label,,0,0,0,,{ko}' for a,b,ko,en in rows)+'\n'
(folder/'captions.ass').write_bytes(ass.encode())
audio='atrim=0:48,asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-2:LRA=8,afade=t=in:d=0.8,afade=t=out:st=47:d=1'
base=['ffmpeg','-hide_banner','-loglevel','error','-y','-i','unity-native-clean.mp4','-i',str(music),'-map','0:v:0','-map','1:a:0','-af',audio,'-t','48','-c:a','aac','-b:a','192k','-ar','48000']
subprocess.run(base+['-c:v','copy','-movflags','+faststart','lofi-room-nature-v2.clean.mp4'],cwd=folder,check=True)
subprocess.run(base+['-vf','ass=captions.ass','-c:v','h264_nvenc','-preset','p5','-cq','19','-pix_fmt','yuv420p','-movflags','+faststart','lofi-room-nature-v2.captioned.mp4'],cwd=folder,check=True)
video=folder/'lofi-room-nature-v2.captioned.mp4'
for second in [2,10,21,28,35,40,45]:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(video),'-frames:v','1',str(folder/f'review-{second:02}.png')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','2','-i',str(root/'projects/ai-3d-lofi-gaming-room/production/local/unity-sample-v1/unity-sample.clean.mp4'),'-frames:v','1',str(folder/'before-v1.png')],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
timestamps=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]))['frames']
t=[float(x['best_effort_timestamp_time']) for x in timestamps]
assert len(t)==2880 and all(abs(b-a-1/60)<.00001 for a,b in zip(t,t[1:]));assert probe['streams'][0]['width']==1920 and probe['streams'][0]['height']==1080 and probe['streams'][0]['r_frame_rate']=='60/1';assert any(x['codec_type']=='audio' for x in probe['streams'])
subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(video),'-f','null','-'],check=True)
outputs=[]
for name in ['lofi-room-nature-v2.clean.mp4','lofi-room-nature-v2.captioned.mp4','lofi-room-nature-v2.ko.srt','lofi-room-nature-v2.en.srt']:
 p=folder/name;outputs.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
report={'kind':'PC nature-detail review, not the full production video','width':1920,'height':1080,'fps':60,'duration':48,'videoFrames':2880,'consistentPts':True,'fullDecodePassed':True,'outputs':outputs,'music':{'title':'Morning Coffee','creator':'HoliznaCC0','license':'CC0 1.0','source':'https://opengameart.org/content/lo-fi-and-chill-collection','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/'},'humanReview':False,'youtubeUploaded':False,'webBuild':'deferred-by-user-PC-first'}
(folder/'delivery.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'frames':len(t),'outputs':outputs},ensure_ascii=True))
