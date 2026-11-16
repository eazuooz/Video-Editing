"""Build the PC nature/material review; leave the approved v1 files untouched."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
folder=root/'projects/ai-3d-lofi-gaming-room/production/local/atmosphere-v3'
music=root/'sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3'
rows=[
 (0,6,'창가의 빛과 바람 · PC 품질 보완본입니다.','Window light and a gentle breeze: the revised PC prototype.'),
 (6,16,'실제 걷기 클립의 보폭을 유지하며 곡선으로 돌아갑니다.','Native root-motion strides follow a continuous curved route.'),
 (16,22,'원본 4K 색상·표면 재질을 화면 100% 해상도로 그립니다.','Original 4K color and PBR surfaces, rendered at native resolution.'),
 (22,30,'머리카락은 관성·복원력·길이 제약과 충돌 처리를 더했습니다.','Loose hair now uses inertia, restoring forces, length constraints and collisions.'),
 (30,36,'잎의 뿌리는 고정하고 끝부분이 잔잔하게 흔들립니다.','Leaf roots stay fixed while their tips sway gently.'),
 (36,43,'창가 빛줄기 · 부드러운 그림자 · 은은한 블룸 효과.','Depth-clipped window shafts, soft shadows and restrained bloom.'),
 (43,48,'낮밤·바람·빛줄기·머리카락 효과를 직접 비교해 보세요.','Compare day/night, breeze, light shafts and hair motion in the PC build.')]

def tc(t,ass=False):return f'0:{int(t//60):02}:{int(t%60):02}.00' if ass else f'00:{int(t//60):02}:{int(t%60):02},000'
for lang,col in [('ko',2),('en',3)]:
 text='\n\n'.join(f'{i+1}\n{tc(r[0])} --> {tc(r[1])}\n{r[col]}' for i,r in enumerate(rows))+'\n'
 (folder/f'lofi-room-atmosphere-v3.{lang}.srt').write_bytes(text.encode())
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
subprocess.run(base+['-c:v','copy','-movflags','+faststart','lofi-room-atmosphere-v3.clean.mp4'],cwd=folder,check=True)
subprocess.run(base+['-vf','ass=captions.ass','-c:v','h264_nvenc','-preset','p5','-cq','19','-pix_fmt','yuv420p','-movflags','+faststart','lofi-room-atmosphere-v3.captioned.mp4'],cwd=folder,check=True)
video=folder/'lofi-room-atmosphere-v3.captioned.mp4'
for second in [2,10,18,24,28,33,39,46]:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(video),'-frames:v','1',str(folder/f'review-{second:02}.png')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','44','-i',str(root/'projects/ai-3d-lofi-gaming-room/production/local/nature-v2/lofi-room-nature-v2.clean.mp4'),'-frames:v','1',str(folder/'before-v2.png')],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
timestamps=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]))['frames']
t=[float(x['best_effort_timestamp_time']) for x in timestamps]
assert len(t)==2880 and all(abs(b-a-1/60)<.00001 for a,b in zip(t,t[1:]));assert probe['streams'][0]['width']==1920 and probe['streams'][0]['height']==1080 and probe['streams'][0]['r_frame_rate']=='60/1';assert any(x['codec_type']=='audio' for x in probe['streams'])
subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(video),'-f','null','-'],check=True)
outputs=[]
for name in ['lofi-room-atmosphere-v3.clean.mp4','lofi-room-atmosphere-v3.captioned.mp4','lofi-room-atmosphere-v3.ko.srt','lofi-room-atmosphere-v3.en.srt']:
 p=folder/name;outputs.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
report={'kind':'PC atmosphere and physical secondary-motion review, not the full production video','width':1920,'height':1080,'fps':60,'duration':48,'videoFrames':2880,'consistentPts':True,'fullDecodePassed':True,'outputs':outputs,'music':{'title':'Morning Coffee','creator':'HoliznaCC0','license':'CC0 1.0','source':'https://opengameart.org/content/lo-fi-and-chill-collection','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/'},'humanReview':False,'youtubeUploaded':False,'webBuild':'deferred-by-user-PC-first'}
(folder/'delivery.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'frames':len(t),'outputs':outputs},ensure_ascii=True))
