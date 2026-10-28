"""Measured brand UI outside Unity's world-only grayscale render.

The same cut-local cues drive Unity object changes and these transparent labels.
Official photographs are explanation images, never simulated engine output.
No media generation occurs on import. Native and source footage stay unchanged.
"""
from pathlib import Path
import json,math,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
import audio_pipeline as a

H=Path(__file__).resolve().parent
W,HIGH=1920,1080
WHITE='#F5F5F5';YELLOW='#E8CF83';GREY='#B8B8B8'
FONT=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')
PHOTO=H.parents[1]/'production/local/batch-v1/visual-assets'
PHOTO_VARIANTS={'proof-options','puyo-official-filters','mirror-still'}

def progress(row,key,t,frames,low=.28,high=.62):
 cue=next((x for x in row.get('cues',[]) if x['key']==key),None)
 start,end=(cue['start'],cue['end']) if cue else (max(1,frames/60)*low,max(1,frames/60)*high)
 value=max(0,min(1,(t-start)/(end-start))) if end!=start else float(t>=end)
 return value*value*(3-2*value)

def picture_state(row,t,frames):
 v=row['variant'];p=progress(row,'change',t,frames)
 s={'variant':v,'title':'','status':'','detail':'','count':'','photo':None,'flip':False,'option':0}
 if v in PHOTO_VARIANTS:
  s['chip']='자료 그림 · 해설'
  if v=='proof-options':
   s.update(title='서로 다른 색각 조건에서 같은 정보를 확인',status='조각과 배경을 구분할 수 있는가?',detail='색각 시뮬레이션의 검사 항목을 설명한 도식',photo='puyo.jpg',option=int(p>=.5))
  elif v=='puyo-official-filters':
   s.update(title='플레이어가 구분하기 좋은 필터를 선택',status='필터 OFF' if p<.5 else '필터 ON · 색과 무늬의 선택지',detail='뿌요뿌요 테트리스 2 · 색 조정 메뉴',photo='puyo-filter-10.jpg' if p<.5 else 'puyo-filter-11.jpg')
  else:
   s.update(title='익숙한 그림을 다른 방향으로 확인',status='같은 스크린샷' if p<.5 else '같은 스크린샷 · 좌우반전',detail='설명용 좌우반전 · 실제 게임 진행 아님',photo='mario.jpg',flip=p>=.5)
 elif v.startswith('forest-') or v=='inspection-comparison':
  gray=(p if v in ('forest-gray','inspection-comparison') else 1-p if v=='forest-color-restored' else 1 if v in ('forest-background-repair','forest-path-repair') else 0)
  state={'forest-background-repair':'1. 뒤쪽 나무의 대비 줄이기','forest-path-repair':'2. 길과 목표의 경계 살리기','forest-color-restored':'3. 색을 돌려놓고 다시 확인'}.get(v,'흑백: 밝기 관계 검사' if gray>.99 else '컬러: 같은 장면' if gray<.01 else '컬러 → 흑백')
  s.update(chip='해설용 시연',title='같은 장면에서 색만 빼면 무엇이 남을까?',status=state,detail='밝기 관계 검사 · 같은 물체와 카메라')
 else:
  state={'token-color':'색으로 같은 종류 찾기','token-hue-loss':'색 차이만 줄이기','token-theme':'조각과 배경을 함께 확인','token-brightness':'한쪽은 밝게, 한쪽은 어둡게','token-background-problem':'어두운 조각이 배경에 묻힙니다','token-edge-repair':'맞닿는 경계를 분리','token-symbols':'모양을 읽어도 같은 종류','token-color-restored':'색 + 명도 + 모양'}[v]
  detail='구분 단서를 줄인 모형 · 색각 재현 아님' if v in ('token-hue-loss','token-theme') else '같은 종류에는 같은 표시' if v=='token-symbols' else '밝은 윤곽이 배경과 조각을 나눕니다' if v=='token-edge-repair' else '모양과 위치는 그대로'
  s.update(chip='해설용 시연',title='색이 전하던 정보, 다른 단서로 확인하기',status=state,detail=detail,count='○  ○  ○  +  ○  =  4' if v=='token-symbols' and progress(row,'fourth-piece',t,frames,.60,.82)>.99 else '')
 return s

def font(size,bold=False):
 f=ImageFont.truetype(str(FONT),size)
 try:f.set_variation_by_name('Bold' if bold else 'Regular')
 except (ValueError,AttributeError):pass
 return f

def render_ui(s):
 image=Image.new('RGBA',(W,HIGH),(0,0,0,255) if s['variant'] in PHOTO_VARIANTS else (0,0,0,0));draw=ImageDraw.Draw(image);bounds=[]
 def label(text,x,y,size=44,color=WHITE,width=1600,height=80,bold=False):
  if not text:return
  f=font(size,bold);box=draw.textbbox((0,0),text,font=f,stroke_width=0);tw,th=box[2]-box[0],box[3]-box[1]
  if tw>width or th>height:raise ValueError(f'UI text needs explicit relayout: {text} {tw}x{th}>{width}x{height}')
  left,top=round(x-tw/2),round(y-th/2)
  if top+th>=892:raise ValueError('UI enters protected caption region')
  draw.text((left-box[0],top-box[1]),text,font=f,fill=color,stroke_width=2,stroke_fill='#000000')
  bounds.append({'text':text,'bounds':[left,top,left+tw,top+th],'fontSize':size,'color':color})
 def photo(name,cx,cy,w,h,flip=False):
  source=Image.open(PHOTO/name).convert('RGBA');fitted=ImageOps.contain(source,(w,h),Image.Resampling.LANCZOS)
  if flip:fitted=ImageOps.mirror(fitted)
  image.alpha_composite(fitted,(round(cx-fitted.width/2),round(cy-fitted.height/2)))
  bounds.append({'photo':name,'sourceSize':source.size,'displaySize':fitted.size,'bounds':[cx-fitted.width/2,cy-fitted.height/2,cx+fitted.width/2,cy+fitted.height/2],'aspectPreserved':True,'flipIllustration':flip})
 label(s['title'],830,98,54,YELLOW,1470,90,True)
 label(s['chip'],1740,73,28,GREY,260,45)
 v=s['variant']
 if v=='proof-options':
  label(s['status'],960,205,46);photo(s['photo'],490,520,870,489)
  label('→',995,425,76,YELLOW,120,100);label('→',995,635,76,YELLOW,120,100)
  label('Protanopia-type',1430,425,46,YELLOW if s['option']==0 else GREY,730,90)
  label('Deuteranopia-type',1430,635,46,YELLOW if s['option']==1 else GREY,730,90)
  label(s['detail'],960,830,44,GREY,1650,65)
 elif v in PHOTO_VARIANTS:
  label(s['status'],960,190,46);photo(s['photo'],960,520,1024,576,s['flip']);label(s['detail'],960,855,40,GREY,1650,60)
 elif v.startswith('forest-') or v=='inspection-comparison':
  label(s['status'],960,202,46);label(s['detail'],960,825,44,GREY)
  label('플레이어',430,740,44,WHITE,300,65);label('목표',1430,740,44,WHITE,300,65)
 else:
  label(s['status'],960,205,46);label(s['detail'],960,820,44,GREY);label(s['count'],960,270,50,YELLOW)
 return image,bounds

def prepare(plan,cues,root):
 root=Path(root);root.mkdir(parents=True,exist_ok=True);rows={x['cutId']:x for x in cues['cuts']};records=[]
 for cut in plan['cuts']:
  if cut['kind']!='explanation':continue
  row=rows[cut['id']];phases=[];previous=None
  for frame in range(cut['frames']):
   state=picture_state(row,frame/60,cut['frames']);key=json.dumps(state,sort_keys=True,ensure_ascii=False)
   if key!=previous:
    if phases:phases[-1]['endFrame']=frame
    image,bounds=render_ui(state);name=f"{cut['id']}-{len(phases):02d}.png";dest=root/name;image.save(dest)
    phases.append({'startFrame':frame,'endFrame':cut['frames'],'image':a.artifact(dest),'state':state,'bounds':bounds});previous=key
  records.append({'cutId':cut['id'],'frames':cut['frames'],'worldRequired':row['variant'] not in PHOTO_VARIANTS,'phases':phases})
 result={'revision':'clarity-v3','renderer':'Unity world-only grayscale + independently authored2D brand UI/photo composition','coordinates':'1920x1080 original stage coordinates; fixed caption970 untouched','cueSha256':hashlib.sha256(json.dumps(cues,sort_keys=True).encode()).hexdigest(),'sourceModule':a.artifact(Path(__file__)),'font':{'path':str(FONT),'sha256':a.sha(FONT)},'photoInputs':[a.artifact(PHOTO/n) for n in ['puyo.jpg','puyo-filter-10.jpg','puyo-filter-11.jpg','mario.jpg']],'cuts':records,'status':'prepared-final-pixels-unreviewed'}
 a.save(root/'ui-manifest.json',result);return result

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--plan',default=str(H/'edit-plan.draft.json'));ap.add_argument('--cues',default=str(H/'unity-cues.draft.json'));ap.add_argument('--output',default=str(H/'evidence/ui-draft-v1'));args=ap.parse_args()
 a.require_authorized('prepare-measured-explanation-ui');result=prepare(a.read(args.plan),a.read(args.cues),args.output)
 print(f"Prepared {len(result['cuts'])} measured UI cut states; final pixel proof pending")
