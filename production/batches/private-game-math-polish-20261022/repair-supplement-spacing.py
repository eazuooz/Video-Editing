"""Redraw only observed cramped multiline beat labels; all wording/time retained."""
import sys
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();assert e.id in ['M05','M06']
old=R/'production/batches/game-math-part2-teaching-revision'
items=read(old/'quaternion-additive-draft.json')['additions']+read(old/'quaternion-episode-framing.json')['scenes']
for override in read(old/'quaternion-clarified-additions-v3.json')['overrides']:
 for item in items:
  if item['id']==override['id']:item.update(override)
lookup={x['id']:x for x in items};events=[];repairs=[]
def stamp(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
def event(a,z,layer,style,words):events.append(f'Dialogue: {layer},{stamp(a)},{stamp(z)},{style},,0,0,0,,{words}')
for s in e.T['scenes']:
 if s['id'] not in lookup:continue
 item=lookup[s['id']];beats=item.get('beats',item['ko']);starts=s['lineStarts'];assert len(beats)==len(starts)
 for i,beat in enumerate(beats):
  lines=beat.replace(' / ','\n').splitlines()
  if len(lines)==1:continue
  assert len(lines)<=3
  a=s['start']+starts[i];z=s['start']+(starts[i+1] if i+1<len(starts) else s['seconds'])
  size=50
  while max(ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',size).getlength(line) for line in lines)>790:size-=1
  assert size>=40
  positions=[783+(j-(len(lines)-1)/2)*64 for j in range(len(lines))]
  event(a,z,8,'SpacingMask',r'{\an7\pos(0,0)\p1}m 972 681 l 1832 681 1832 889 972 889{\p0}')
  for words,y in zip(lines,positions):event(a,z,9,'SpacingText',rf'{{\an5\pos(1392,{y})\fs{size}}}'+words)
  repairs.append({'scene':s['id'],'beatIndex':i,'start':a,'end':z,'originalText':beat,'lines':lines,'fontPx':size,'baselineStepPx':64,'yCenters':positions,'reason':'Actual encoded N02/N09 multiline labels nearly touch; same shared supplementary-label format repaired only at multiline beats'})
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: SpacingMask,Malgun Gothic,50,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: SpacingText,Malgun Gothic,50,&H00202020,&H00202020,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
ass=e.O/'supplement-spacing.ass';ass.write_text(header+'\n'.join(events)+'\n',encoding='utf8')
save(e.H/'supplement-spacing-repair.json',{'timelineSha256':sha(e.P/'production/timeline.json'),'ass':rel(ass),'assSha256':sha(ass),'changes':repairs,'scriptAndSpeechUnchanged':True,'status':'pending-still-preflight-and-final-reencode'})
if '--preview' in sys.argv:
 movie=e.D/f'{e.slug}.captioned.mp4';master=sha(movie);out=e.O/'supplement-spacing-preview';out.mkdir(exist_ok=True);tiles=[];records=[]
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
 for i,item in enumerate(repairs):
  t=(item['start']+item['end'])/2;dst=out/f'{i:02d}-{item["scene"]}.png'
  e.ff(['-ss',t,'-i',movie,'-vf',f'setpts=PTS+{t}/TB,ass=supplement-spacing.ass','-frames:v','1','-threads','1',dst],'supplement-spacing-preview.log',e.O)
  records.append({'image':rel(dst),'imageSha256':sha(dst),'seconds':t,'scene':item['scene']})
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS),(0,29));ImageDraw.Draw(tile).text((5,3),f'{e.id} {item["scene"]} {t:.2f}s',font=font,fill='white');tiles.append(tile)
 for i in range(0,len(tiles),8):
  sheet=Image.new('RGB',(1500,480),'#222222')
  for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,((j%4)*375,(j//4)*240))
  sheet.save(out/f'sheet-{i//8+1:02d}.jpg',quality=94)
 save(e.H/'supplement-spacing-preflight.json',{'status':'await-direct-inspection','previousMasterSha256':master,'assSha256':sha(ass),'samples':records,'finalEncodedPixels':'pending'})
print(e.id,len(repairs),'exact multiline beat intervals repaired; final encode pending',flush=True)
