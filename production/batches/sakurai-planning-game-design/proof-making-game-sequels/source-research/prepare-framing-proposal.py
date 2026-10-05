"""Local composition samples from already extracted frames; no new source decode or final-cue approval."""
import hashlib,json,pathlib,time
from PIL import Image,ImageDraw,ImageFont
root=pathlib.Path(__file__).resolve().parents[5]
here=pathlib.Path(__file__).resolve().parent
state=json.loads((here/'native-review-v1.json').read_text('utf-8'))
wave=json.loads((here/'native-deathtrap-wave2.json').read_text('utf-8'))['sources'][0]
sources=state['sources']+[wave]
out=here.parent/'research-local/framing-proposal-v1';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
label_font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
samples=[(0,1200),(0,2100),(0,4200),(0,4980),(1,12600),(1,18585),(1,32070),(1,32340),(2,25920),(2,27990),(3,1860),(3,16380),(3,18960),(3,19620)]
records=[]
for index,(source_index,native) in enumerate(samples,1):
 s=sources[source_index];match=next(x for x in s['actionSamples'] if x['frame']==native)
 original=Image.open(root/match['path']).convert('RGB')
 crop=(0,0,1472,828) if s['videoId']=='kzZI_mbp0HY' else ((96,0,1728,972) if source_index==1 else (0,0,1920,1080))
 x,y,w,h=crop;scale=original.width/1920
 img=original.crop(tuple(round(v*scale) for v in (x,y,x+w,y+h))).resize((1920,1080),Image.Resampling.LANCZOS)
 draw=ImageDraw.Draw(img);text='관찰할 행동과 다음 작품의 선택을\n서로 나누어 살펴봅니다.'
 box=draw.multiline_textbbox((0,0),text,font=font,spacing=7,align='center');tw,th=box[2]-box[0],box[3]-box[1]
 left=(1920-tw-48)/2;top=970-(th+30)/2;right=1920-left;bottom=970+(th+30)/2
 draw.rectangle((left+12,top+12,right+12,bottom+12),fill='#154E39');draw.rectangle((left,top,right,bottom),fill='white',outline='black',width=2)
 draw.multiline_text(((1920-tw)/2,top+15-box[1]),text,fill='black',font=font,spacing=7,align='center')
 fn=out/f'sample-{index:02}.jpg';img.save(fn,quality=93)
 records.append({'sourceId':s['videoId'],'sourceOffsetSeconds':s['sourceOffsetSeconds'],'nativeFrame':native,'sourceFrame':match['path'],'sourceFrameSha256':match['sha256'],'nativeCrop':[x,y,w,h],'fixedCaptionCenter':[960,970],'captionFontPx':48,'captionLines':2,'captionText':'Synthetic layout placeholder, not approved narration/cue','path':fn.relative_to(root).as_posix(),'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'finalCaptionPixelApproval':False})
sheets=[]
for offset in range(0,len(records),4):
 sheet=Image.new('RGB',(1920,1140),'#eeeeee');draw=ImageDraw.Draw(sheet)
 for j,r in enumerate(records[offset:offset+4]):
  x=(j%2)*960;y=(j//2)*570
  draw.text((x+5,y+2),f"{r['sourceId']} n{r['nativeFrame']} crop{r['nativeCrop']}",font=label_font,fill='black')
  sheet.paste(Image.open(root/r['path']).resize((960,540)),(x,y+30))
 fn=out/f'sheet-{offset//4+1:02}.jpg';sheet.save(fn,quality=94);sheets.append({'path':fn.relative_to(root).as_posix(),'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'samples':len(records[offset:offset+4])})
record={'schemaVersion':1,'createdAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'extracted-awaiting-direct-composition-review','samples':records,'sheets':sheets,'newSourceDecode':False,'wholeShotMotionReviewed':False,'allCuesApproved':False,'newGitImages':0}
(here/'framing-proposal-v1.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'samples':len(records),'sheets':len(sheets),'newSourceDecode':False,'newGitImages':0}))
