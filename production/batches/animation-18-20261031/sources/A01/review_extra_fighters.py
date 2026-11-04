from pathlib import Path
import subprocess,json,hashlib
P=Path(__file__).resolve().parent
out={}
for key in ['donkey-kong','kirby','luigi','wii-fit','mii','krool']:
 p=P/f'smash-{key}.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,sample_rate,channels','-show_entries','format=duration','-of','json',str(p)]))
 r=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-i',str(p),'-vf','fps=2,scale=480:270,tile=4x5','-an','-y',str(P/f'extra-{key}-%02d.jpg')],capture_output=True,text=True)
 info=json.loads((P/f'smash-{key}.info.json').read_text(encoding='utf-8'))
 out[key]={'path':str(p).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decoded':probe,'url':info['webpage_url'],'creator':info['uploader'],'title':info['title'],'description':info.get('description'),'decodeReturnCode':r.returncode,'decodeErrors':r.stderr,'contactSamplingFps':2,'pageDuration':10,'musicIdentityFromMetadata':None,'visualReview':'pending explicit inspection'}
 print(key,len(list(P.glob(f'extra-{key}-*.jpg'))),flush=True)
(P/'additional-fighters-inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
