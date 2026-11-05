from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];R=P.parents[1];pub=P/'publishing';slug=P.name
def rd(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def thumb():
 im=Image.new('RGB',(1280,720),'#fffaf1');d=ImageDraw.Draw(im)
 font=lambda z:ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',z)
 d.rectangle((8,8,1271,711),outline='#181a18',width=10);d.rectangle((18,18,1262,108),fill='#ffcf41')
 d.text((44,24),'게임수학 Part 2   /   빛과 셰이딩',font=font(45),fill='#151716')
 d.text((48,156),'같은 구인데',font=font(89),fill='#171917',stroke_width=1)
 d.text((48,293),'왜 다르게',font=font(102),fill='#c73531',stroke_width=1)
 d.text((48,438),'빛날까?',font=font(109),fill='#171917',stroke_width=1)
 for cx,cy,r,exp in [(905,402,164,9),(1098,515,117,78)]:
  y,x=np.mgrid[-r:r,-r:r];x=x/r;y=-y/r;z=np.sqrt(np.maximum(0,1-x*x-y*y))
  dot=np.maximum(0,-.44*x+.6*y+.66*z);hv=np.maximum(0,-.24*x+.34*y+.91*z)**exp
  base=np.asarray([.18,.51,.54]);rgb=np.clip((.19+dot[...,None]*.67)*base+.82*hv[...,None],0,1)
  patch=Image.fromarray(np.uint8(rgb**(1/2.2)*255));mask=Image.fromarray(np.uint8(np.clip((1-np.hypot(x,y))*r,0,1)*255));im.paste(patch,(cx-r,cy-r),mask)
 cat=Image.open(R/'shared/assets/branding/cat-reactions-v1/realize.png').convert('RGBA');cat=cat.crop(cat.getbbox());cat.thumbnail((210,195));im.paste(cat,(602,485),cat)
 im.save(pub/'thumbnail-v7.jpg',quality=95)
def main():
 thumb();e=rd(P/'production/teaching-v7/review-evidence.json');cap=Path(e['files']['captioned']['path']);assert sha(cap)==e['files']['captioned']['sha256']
 foot=rd(P/'planning/footage-audit.json');times=rd(P/'production/local/render-v7/timeline.json');defaults=rd(R/'shared/publishing/youtube-defaults.json')
 srcs=[]
 for s in foot['sources']:
  srcs.append(f"{s.get('title',s['game'])} — {s['uploader']} | {s['recordingUrl']}"+(" | CC BY, edited excerpt and annotations; recording only. https://creativecommons.org/licenses/by/3.0/" if 'Creative Commons' in s['recordingPermission']['basis'] else ''))
 srcs+=['3D Math Primer for Graphics and Game Development, Ch. 10 — Fletcher Dunn & Ian Parberry | https://gamemath.com/book/graphics.html','Analog Memory — EmaceArt | https://emaceart.itch.io/1990s-retro-game-environments-classic-mid-poly-rooms','Unity URP | https://docs.unity3d.com/Manual/urp/','Direct3D 11 / HLSL | https://learn.microsoft.com/en-us/windows/win32/direct3d11/','Qwen3-TTS | https://github.com/QwenLM/Qwen3-TTS','FFmpeg | https://ffmpeg.org/']
 chapters=[(0,'전조등이 드러낸 표면','A surface revealed by a headlamp'),(8,'법선과 빛·시선 방향','Normal, light and view directions'),(16,'하프웨이 벡터와 반짝임','The halfway vector'),(24,'간접광과 환경광','Indirect and ambient light'),(39,'정점과 픽셀에서 계산한 셰이딩','Per-vertex and per-pixel shading'),(48,'점 광원과 거리','Point lights and distance'),(56,'면광원과 입체각','Area lights and solid angle'),(72,'표면에 빛 저장하기','Storing light on a surface')]
 def chapter(n):
  out=[]
  for sid,k,v in chapters:
   t=0 if sid==0 else next(x['start'] for x in times if x['sid']==sid)//60
   out.append(f'{t//60:02}:{t%60:02} '+(k if n=='ko' else v))
  return '\n'.join(out)
 cn=(R/defaults['description']['channelDefaultSnapshot']).read_text('utf8').split('📚 수업 노트')[0].strip()
 ko='전조등이 지나갈 때에만 드러나는 표면의 굴곡, 같은 구에서 다르게 움직이는 반짝임. 게임 장면에서 출발해 법선, 반사 방향, 광원의 크기와 거리가 픽셀 색을 어떻게 결정하는지 살펴봅니다.\n\n'+chapter('ko')+'\n\n'+cn+'\n\n출처·자료·제작 도구\n'+'\n'.join(srcs)
 en='What makes the same sphere shine differently? Follow the normal, reflected light, and viewer on the surface itself, then compare vertex and pixel shading, local lights, and baking.\n\n'+chapter('en')+'\n\nYamYamCoding · Game programming and graphics\nCoaching: '+defaults['coaching']['url']+'\nDiscord: https://discord.gg/wZuqe7fqkR\nMembership: '+defaults['membershipUrl']+'\n\nSources and credits\n'+'\n'.join(srcs)
 for l,s in [('ko',ko),('en',en)]:(pub/f'description-v7.{l}.txt').write_text(s+'\n','utf8')
 file=pub/'youtube-upload-v7.json'
 receipt=rd(file) if file.exists() else {}
 receipt.update(version='M21 v7',metadata={'title':'같은 구인데 왜 다르게 빛날까? | 게임수학: 빛과 셰이딩','privacyStatus':'private','language':'ko','descriptionFile':'description-v7.ko.txt'},englishMetadata={'title':'Why Does the Same Sphere Shine Differently? | Game Math: Light and Shading','descriptionFile':'description-v7.en.txt'},video={'path':cap.relative_to(R).as_posix(),'sha256':sha(cap),'bytes':cap.stat().st_size},subtitles={l:e['files'][l] for l in ('ko','en')},thumbnail={'path':'thumbnail-v7.jpg','sha256':sha(pub/'thumbnail-v7.jpg')},userReview={'approved':True,'basis':'좋아~ 업로드 해줘~','fullContinuousListeningClaimed':False},status='prepared-awaiting-studio-transfer',privateVideoId=None)
 save(file,receipt)
if __name__=='__main__':main()

