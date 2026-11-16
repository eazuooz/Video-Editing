"""Build the PC nature/material review; leave the approved v1 files untouched."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
folder=root/'projects/ai-3d-lofi-gaming-room/production/local/hearth-v4'
music=root/'sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3'
rows=[
 (0,5,'아이맥과 벽난로, 레코드 플레이어가 있는 작은 방입니다.','A small room with an all-in-one computer, fireplace and record player.'),
 (5,14,'의자로 걸어가 정렬한 뒤, 실제 연결 모션으로 앉습니다.','Walk to the chair, align, then sit with a native transition clip.'),
 (14,24,'작은 책상에서 아이맥을 사용합니다.','Use the compact all-in-one computer at the smaller desk.'),
 (24,34,'책을 가져와 읽고, 손과 의자 높이를 맞췄습니다.','Bring the book over to read, with fitted hand and seat contacts.'),
 (34,40,'책을 내려놓고 일어나, 의자 옆으로 비켜납니다.','Set the book down, stand up, and step away from the chair.'),
 (40,50,'겹쳐진 불꽃·불티·연기, 그리고 장작 타는 소리입니다.','Layered flame particles, embers, smoke and real crackling wood.'),
 (50,58,'로파이 음악은 창가의 레코드 플레이어에서 흘러나옵니다.','Lofi music plays from the record player under the window.'),
 (58,64,'낮에는 창가의 빛, 밤에는 벽난로의 온기를 더했습니다.','Window light in the day, warm firelight at night.'),
 (64,72,'아이맥·독서·일어나기·음악·장작 소리를 직접 조작해 보세요.','Try computer, reading, standing, music and fire-sound controls in the PC build.')]

def tc(t,ass=False):return f'0:{int(t//60):02}:{int(t%60):02}.00' if ass else f'00:{int(t//60):02}:{int(t%60):02},000'
for lang,col in [('ko',2),('en',3)]:
 text='\n\n'.join(f'{i+1}\n{tc(r[0])} --> {tc(r[1])}\n{r[col]}' for i,r in enumerate(rows))+'\n'
 (folder/f'lofi-room-hearth-v4.{lang}.srt').write_bytes(text.encode())
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
fire=root/'unity/LofiGamingRoomWeb/Assets/LofiRoom/Audio/fireplace.ogg'
audio="[1:a]atrim=0:72,asetpts=PTS-STARTPTS,loudnorm=I=-26:TP=-3:LRA=8,volume='if(between(t,40,50),0.22,0.7)':eval=frame[m];[2:a]atrim=0:72,asetpts=PTS-STARTPTS,loudnorm=I=-27:TP=-3:LRA=7,volume=0.95[f];[m][f]amix=inputs=2:normalize=0,afade=t=in:d=0.7,afade=t=out:st=71:d=1,alimiter=limit=0.89:level=false[a]"
base=['ffmpeg','-hide_banner','-loglevel','error','-y','-i','unity-native-clean.mp4','-i',str(music),'-stream_loop','-1','-i',str(fire),'-map','0:v:0','-map','[a]','-filter_complex',audio,'-t','72','-c:a','aac','-b:a','192k','-ar','48000']
subprocess.run(base+['-c:v','copy','-movflags','+faststart','lofi-room-hearth-v4.clean.mp4'],cwd=folder,check=True)
subprocess.run(base+['-vf','ass=captions.ass','-c:v','h264_nvenc','-preset','p5','-cq','19','-pix_fmt','yuv420p','-movflags','+faststart','lofi-room-hearth-v4.captioned.mp4'],cwd=folder,check=True)
video=folder/'lofi-room-hearth-v4.captioned.mp4'
for second in [2,10,18,28,36,44,54,61,68]:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(video),'-frames:v','1',str(folder/f'review-{second:02}.png')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','2','-i',str(root/'projects/ai-3d-lofi-gaming-room/production/local/atmosphere-v3/lofi-room-atmosphere-v3.clean.mp4'),'-frames:v','1',str(folder/'before-v3.png')],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
timestamps=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]))['frames']
t=[float(x['best_effort_timestamp_time']) for x in timestamps]
assert len(t)==4320 and all(abs(b-a-1/60)<.00001 for a,b in zip(t,t[1:]));assert probe['streams'][0]['width']==1920 and probe['streams'][0]['height']==1080 and probe['streams'][0]['r_frame_rate']=='60/1';assert any(x['codec_type']=='audio' for x in probe['streams'])
subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(video),'-f','null','-'],check=True)
outputs=[]
for name in ['lofi-room-hearth-v4.clean.mp4','lofi-room-hearth-v4.captioned.mp4','lofi-room-hearth-v4.ko.srt','lofi-room-hearth-v4.en.srt']:
 p=folder/name;outputs.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
report={'kind':'PC interactions, iMac, hearth and record-player review; not the full production video','width':1920,'height':1080,'fps':60,'duration':72,'videoFrames':4320,'consistentPts':True,'fullDecodePassed':True,'outputs':outputs,'music':{'title':'Morning Coffee','creator':'HoliznaCC0','license':'CC0 1.0','source':'https://opengameart.org/content/lo-fi-and-chill-collection','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/'},'fireAudio':{'title':'Fireplace Sound loop','creator':'PaGDev','source':'https://opengameart.org/content/fireplace-sound-loop','license':'CC0 1.0'},'audioMethod':'Review uses the same local music and crackle assets mixed to the shot plan; not a real-time AudioListener capture','humanReview':False,'youtubeUploaded':False,'webBuild':'deferred-by-user-PC-first'}
(folder/'delivery.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'frames':len(t),'outputs':outputs},ensure_ascii=True))
