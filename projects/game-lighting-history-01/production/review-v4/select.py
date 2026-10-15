"""Proposed short observation windows; target geometry follows direct frame review."""
from probe import *
import datetime,hashlib
WINDOWS=[
 ('visibility',0,44.7,49.7,'보이는 표면'),
 ('wall-edge',1,94.5,99.1,'옆에서 본 벽'),
 ('surface',2,186,190.5,'빛을 받는 표면'),
 ('diagnostic',2,198,202,'반사 진단 보기'),
 ('doom-sector',5,246,248.2,'구역의 밝기'),
 ('quake-texture',7,345.5,348.5,'벽의 무늬'),
 ('seam',14,403.8,407.5,'이웃 면의 경계'),
 ('lm-resolution',8,437,441.7,'라이트맵 해상도'),
 ('lm-edge',8,454.3,458.4,'빛의 경계'),
 ('uv',9,473,477.8,'텍스처 좌표 · UV'),
 ('quake2',10,502.85,505.3,'어두운 통로의 표면'),
 ('baked-wall',12,539.4,543,'벽의 표면'),
 ('editor-move',13,573.6,578.8,'편집 중인 물체'),
 ('floor',16,630.5,635.5,'멀리 모이는 바닥 무늬'),
 ('mip',17,659.1,662.1,'밉 단계의 세부 무늬'),
 ('mask',18,701.2,704.8,'패킹된 마스크'),
 ('rail',19,735.6,740,'가는 선과 빈 공간'),
 ('triangles',21,810,814.7,'화면을 덮는 삼각형'),
 ('doom3',22,901.6,904.3,'빛을 받는 면'),
 ('robot-inner',25,1010.8,1014.2,'표면 안의 명암'),
 ('robot-outer',25,1019.8,1023.6,'실제 바깥 윤곽'),
 ('hl2',26,1053,1056.4,'인물과 주변 공간'),
 ('robot-normal',32,1272,1278.5,'몸체가 향하는 면'),
 ('probes',29,1445.6,1450.6,'조명 정보를 읽을 위치'),
 ('character',30,1540.1,1545.4,'이동하는 캐릭터'),
 ('probe-depth',34,1612.1,1616.7,'공간 표본의 배치'),
 ('shadow-stairs',35,1909.4,1911.5,'계단의 그림자 수신'),
 ('csm-area',36,1942.1,1946.5,'그림자를 기록할 영역'),
 ('csm-setting',37,1957.6,1962.7,'캐스케이드 개수'),
 ('csm-far',37,1995,1998.4,'먼 지형의 범위'),
 ('book',38,2098.3,2101.3,'기본색 · Base Color'),
 ('vr',41,2244,2247,'손의 가장자리'),
 ('msaa',42,2289,2295.3,'확대된 가장자리'),
 ('reflection',43,2350,2354.6,'반사 진단 보기'),
 ('ao-gap',44,2385.8,2389.8,'틈의 주변 가림'),
 ('ao-setting',45,2460.1,2462.7,'Power / Bias'),
 ('ao-contact',45,2462.9,2464.7,'큐브의 접촉부'),
]
def main():
 windows=[];inv=rd(O/'inventory.json');plan=rd(B/'plan.json')
 for name,g,a,b,label in WINDOWS:
  lo,hi=round(a*60),round(b*60)
  nodes=[n for n in plan['nodes'] if n['endFrame']>lo and n['startFrame']<hi]
  assert all(n['role']=='actual' for n in nodes),(name,nodes)
  windows.append(dict(id=name,group=g,startFrame=lo,endFrame=hi,label=label,nodes=[n['id'] for n in nodes],status='geometry-pending'))
 existing=H/'annotations.json'
 if not existing.exists():wr(existing,dict(policyId='footage-focus-annotations-v1',revision='review-v4',baseline='review-v3',editorialGuidesOnly=True,style='shared/publishing/footage-annotation-style.json',windows=windows))
 q=O/'windows';q.mkdir(exist_ok=True)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
 with av.open(str(B/'pair/captioned.mp4')) as c:
  c.streams.video[0].thread_type='AUTO'
  for w in windows:
   pts=list(range(w['startFrame'],w['endFrame'],30))+[w['endFrame']-1]
   board=Image.new('RGB',(1440,310*((len(pts)+2)//3)),'#151515');draw=ImageDraw.Draw(board)
   for j,f in enumerate(pts):
    x,y=(j%3)*480,(j//3)*310;im=frame(c,f);board.paste(im.resize((480,270)),(x,y+30))
    draw.text((x+4,y+3),f'{w["id"]} · {f/60:.2f}s',font=font,fill='white')
   board.save(q/(w['id']+'.jpg'),quality=92)
   print(w['id'],flush=True)
if __name__=='__main__':main()
