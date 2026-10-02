from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUT=Path(__file__).parent/'images'
OUT.mkdir(parents=True,exist_ok=True)
FONT='C:/Windows/Fonts/malgun.ttf'
BOLD='C:/Windows/Fonts/malgunbd.ttf'
INK='#202020'; GRAY='#637080'; LINE='#cad2dc'; BLUE='#2f5faa'; GREEN='#255842'; RED='#b53f3f'
def font(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)
def text(x,y,s,n=30,c=INK,b=False):
    d.multiline_text((x,y),s,font=font(n,b),fill=c,spacing=12)
def centered(box,s,n=30,c=INK,b=False):
    x,y,w,h=box; lines=s.split('\n'); lh=n+13
    for i,l in enumerate(lines):
        tw=d.textlength(l,font=font(n,b)); text(x+(w-tw)/2,y+(h-lh*len(lines))/2+i*lh,l,n,c,b)
def card(x,y,w,h,label,c='#e7eef8',n=30,tc=INK):
    d.polygon([(x+12,y+12),(x+w+12,y+12),(x+w+12,y+h+12),(x+12,y+h+12)],fill='#e3e7ec')
    d.rectangle((x,y,x+w,y+h),fill=c,outline=LINE,width=2)
    centered((x,y,w,h),label,n,tc,True)
def arrow(x1,y1,x2,y2,c=GRAY,w=4):
    d.line((x1,y1,x2,y2),fill=c,width=w)
    a=math.atan2(y2-y1,x2-x1); r=15
    d.polygon([(x2,y2),(x2-r*math.cos(a-.45),y2-r*math.sin(a-.45)),(x2-r*math.cos(a+.45),y2-r*math.sin(a+.45))],fill=c)
def base(no,title,sub,h=920):
    global im,d
    im=Image.new('RGB',(1600,h),'white');d=ImageDraw.Draw(im)
    text(65,34,'YAMYAM ENGINE  /  DX12 FRAME SYNC',24,BLUE,True)
    text(65,85,f'{no}  {title}',49,INK,True)
    text(65,158,sub,28,GRAY)
    d.line((65,217,1535,217),fill=LINE,width=2)
def foot(s,h=920):
    d.rectangle((65,h-136,1535,h-54),fill='#f2f4f7')
    centered((65,h-136,1470,82),s,30,INK,True)
    text(65,h-39,'현재 엔진의 개념도 · 길이와 간격은 실제 실행 시간을 뜻하지 않습니다.',20,GRAY)
def save(name): im.save(OUT/name)

base('01','CPU가 제출을 끝내도 GPU는 일하고 있습니다','가로축은 시간입니다. 같은 세로선은 같은 시점이며, CPU와 GPU는 서로 다른 줄에서 진행합니다.')
arrow(250,255,1505,255);text(1340,222,'시간 →',24,GRAY)
text(70,336,'CPU',35,BLUE,True);text(70,553,'GPU',35,GREEN,True)
card(245,310,270,114,'슬롯 0 명령 기록',n=31)
card(560,310,260,114,'목록 제출\nSignal(10) 예약',n=28)
card(875,310,550,114,'안전한 슬롯 1에서 다음 명령 준비',c='#edf4ee',n=29)
arrow(521,367,554,367);arrow(826,367,869,367)
card(245,523,320,114,'이전에 제출된 작업',c='#f2f4f7',n=28)
card(625,523,540,114,'슬롯 0의 명령 실행 중',c='#edf4ee',n=31)
card(1230,523,270,114,'완료 값 = 10',c='#edf4ee',n=29)
arrow(573,580,619,580);arrow(1175,580,1224,580)
arrow(690,436,690,508,BLUE)
text(265,693,'슬롯 0을 아직 Reset하면 안 되는 구간',30,RED,True)
arrow(265,674,1165,674,RED)
text(1210,690,'이후 재사용 가능',27,GREEN,True)
foot('안전한 순서: 이전 사용 완료 확인 → Allocator Reset → 새 명령 기록')
save('01-cpu-gpu-timeline.png')

base('02','슬롯에 적힌 번호와 GPU 완료 값을 비교합니다','예: 슬롯 0에는 Fence 10, 슬롯 1에는 Fence 11이 저장되어 있고, 다음에는 슬롯 0을 씁니다.')
card(80,270,680,240,'슬롯 0  ·  다음에 재사용\nCommandAllocator 0\n저장한 FenceValue = 10',n=34)
card(830,270,680,240,'슬롯 1\nCommandAllocator 1\n저장한 FenceValue = 11',c='#edf4ee',n=34)
card(80,565,680,155,'GPU 완료 값 9 < 10\n슬롯 0은 10까지 기다립니다',c='#fbeeed',n=31,tc=RED)
card(830,565,680,155,'GPU 완료 값 10 ≥ 10\n슬롯 0 재사용 가능 · 11 대기 불필요',c='#edf4ee',n=29,tc=GREEN)
foot('백버퍼 = 픽셀을 담는 공간  /  Allocator = 명령 기록을 뒷받침하는 공간')
save('02-frame-slots.png')

base('03','에디터의 시작 조건은 두 가지입니다','WaitForNextFrameResources()는 다음 두 조건이 모두 충족된 뒤 명령 메모리를 재사용합니다.')
card(95,278,660,220,'조건 A  ·  Fence\n이 슬롯의 이전 GPU 사용이\n끝났는가?',n=34)
card(845,278,660,220,'조건 B  ·  Frame latency\n표시 지연 정책상\n다음 프레임을 시작해도 되는가?',c='#fff6d8',n=32)
arrow(425,515,685,610,BLUE);arrow(1175,515,915,610,'#aa8231')
card(540,610,520,112,'A와 B 모두 충족',c='#edf4ee',n=38,tc=GREEN)
text(95,564,'명령 메모리의 안전',29,BLUE,True)
text(1100,564,'너무 앞서가지 않도록 조절',27,'#916b1f',True)
foot('Fence가 끝났다는 사실만으로 표시 지연 조건까지 충족된 것은 아닙니다.')
save('03-two-wait-conditions.png')

base('04','추가 창이 읽는 작업까지 Fence 앞에 넣습니다','YamYam의 추가 OS 창은 엔진과 같은 Command Queue를 사용합니다. 아래는 GPU 큐의 개념적 순서입니다.',1030)
card(75,292,410,164,'메인 목록\nGame / Scene RT 생성\n메인 창 ImGui 합성',n=30)
card(590,292,410,164,'추가 OS 창 목록\nGame / Scene 텍스처 읽기\n해당 창에 ImGui 그리기',c='#edf4ee',n=28)
card(1105,292,410,164,'최종 Signal(N)\n앞선 사용의 완료 지점',c='#fff6d8',n=29)
arrow(500,374,577,374);arrow(1015,374,1092,374)
d.line((82,510,1515,510),fill=GREEN,width=4)
text(355,538,'완료 값이 N 이상이면 이 Signal 앞에 놓인 작업의 완료를 확인',31,GREEN,True)
card(95,625,1410,155,'리사이즈로 버린 옛 Texture / SRV\n반환 예약 → 최종 N에 연결(Seal) → N 완료 후 실제 반환(Collect)',c='#f2f4f7',n=32)
text(97,814,'CPU 호출 순서: 메인 제출 → 추가 창 렌더링·Present → 메인 Present → Signal',28,GRAY)
foot('최종 Fence 전에 모든 소비자의 제출을 포함해야 자원을 너무 일찍 반환하지 않습니다.',1030)
save('04-imgui-final-fence.png')
print('Created 4 diagrams:',OUT)
