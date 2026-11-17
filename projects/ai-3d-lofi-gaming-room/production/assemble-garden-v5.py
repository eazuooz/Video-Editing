"""Build the PC nature/material review; leave the approved v1 files untouched."""
from pathlib import Path
import hashlib,json,subprocess

root=Path(__file__).resolve().parents[3]
folder=root/'projects/ai-3d-lofi-gaming-room/production/local/garden-v5'
music=root/'sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3'
rows=[
 (0,10,'등받이를 낮추고 좁혀, 앉아 있는 캐릭터가 잘 보이게 했습니다.','A shorter, narrower chair back reveals the seated character.'),
 (10,18,'모니터를 13cm 낮추고, 의자와 손의 접촉은 유지했습니다.','The display is 13 cm lower; seat and hand contacts are preserved.'),
 (18,27,'창밖에 겹겹의 숲과 밝은 달, 별을 더했습니다.','Layered forest, moon and stars fill the window at night.'),
 (27,32,'낮에는 숲과 하늘도 함께 밝아집니다.','The forest and sky brighten during the day.'),
 (32,39,'머리카락과 나뭇잎은 더 크게, 천천히 흔들립니다.','Hair and foliage sway more visibly, with restrained slow movement.'),
 (39,48,'PC 실행본의 메모 버튼으로, 로컬에 자동 저장되는 노트를 열어보세요.','Open Notes in the PC build for a locally autosaved memo.')]


def tc(t,ass=False):return f'0:{int(t//60):02}:{int(t%60):02}.00' if ass else f'00:{int(t//60):02}:{int(t%60):02},000'
for lang,col in [('ko',2),('en',3)]:
 text='\n\n'.join(f'{i+1}\n{tc(r[0])} --> {tc(r[1])}\n{r[col]}' for i,r in enumerate(rows))+'\n'
 (folder/f'lofi-room-garden-v5.{lang}.srt').write_bytes(text.encode())
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
audio="[1:a]atrim=0:48,asetpts=PTS-STARTPTS,loudnorm=I=-26:TP=-3:LRA=8,volume=0.7[m];[2:a]atrim=0:48,asetpts=PTS-STARTPTS,loudnorm=I=-27:TP=-3:LRA=7,volume=0.95[f];[m][f]amix=inputs=2:normalize=0,afade=t=in:d=0.7,afade=t=out:st=47:d=1,alimiter=limit=0.89:level=false[a]"
base=['ffmpeg','-hide_banner','-loglevel','error','-y','-i','unity-native-clean.mp4','-i',str(music),'-stream_loop','-1','-i',str(fire),'-map','0:v:0','-map','[a]','-filter_complex',audio,'-t','48','-c:a','aac','-b:a','192k','-ar','48000']
subprocess.run(base+['-c:v','copy','-movflags','+faststart','lofi-room-garden-v5.clean.mp4'],cwd=folder,check=True)
subprocess.run(base+['-vf','ass=captions.ass','-c:v','h264_nvenc','-preset','p5','-cq','19','-pix_fmt','yuv420p','-movflags','+faststart','lofi-room-garden-v5.captioned.mp4'],cwd=folder,check=True)
video=folder/'lofi-room-garden-v5.captioned.mp4'
for second in [2,14,22,30,35,44]:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(video),'-frames:v','1',str(folder/f'review-{second:02}.png')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','18','-i',str(root/'projects/ai-3d-lofi-gaming-room/production/local/hearth-v4/lofi-room-hearth-v4.clean.mp4'),'-frames:v','1',str(folder/'before-v4.png')],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
timestamps=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]))['frames']
t=[float(x['best_effort_timestamp_time']) for x in timestamps]
assert len(t)==2880 and all(abs(b-a-1/60)<.00001 for a,b in zip(t,t[1:]));assert probe['streams'][0]['width']==1920 and probe['streams'][0]['height']==1080 and probe['streams'][0]['r_frame_rate']=='60/1';assert any(x['codec_type']=='audio' for x in probe['streams'])
subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(video),'-f','null','-'],check=True)
outputs=[]
for name in ['lofi-room-garden-v5.clean.mp4','lofi-room-garden-v5.captioned.mp4','lofi-room-garden-v5.ko.srt','lofi-room-garden-v5.en.srt']:
 p=folder/name;outputs.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
report={'kind':'PC v5 visibility, forest/moon, wind and local memo review; not the full production video','width':1920,'height':1080,'fps':60,'duration':48,'videoFrames':2880,'consistentPts':True,'fullDecodePassed':True,'outputs':outputs,'music':{'title':'Morning Coffee','creator':'HoliznaCC0','license':'CC0 1.0','source':'https://opengameart.org/content/lo-fi-and-chill-collection','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/'},'fireAudio':{'title':'Fireplace Sound loop','creator':'PaGDev','source':'https://opengameart.org/content/fireplace-sound-loop','license':'CC0 1.0'},'audioMethod':'Review uses the same local music and crackle assets mixed to the shot plan; not a real-time AudioListener capture','humanReview':False,'youtubeUploaded':False,'webBuild':'deferred-by-user-PC-first'}
(folder/'delivery.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'frames':len(t),'outputs':outputs},ensure_ascii=True))
