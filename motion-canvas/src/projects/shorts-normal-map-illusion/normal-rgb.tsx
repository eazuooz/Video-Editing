import {Line,Node,Rect,Txt} from '@motion-canvas/2d';

export type RGBPhase='none'|'signed'|'packing'|'neutral';
const C={white:'#FFFFFF',yellow:'#FFD25A',teal:'#73D7CD',muted:'#B8C3BC',r:'#F27C70',g:'#92DF9C',b:'#8AB6F0'};
const FONT='Malgun Gothic';
// The formula describes logical linear normal-map data. Imported GPU formats
// may pack channels differently; this is not a material-colour measurement.
export function createNormalRGB({phase,elapsed,step=()=>99}:{phase:()=>RGBPhase;elapsed:()=>number;step?:()=>number}){
 const root=new Node({opacity:()=>phase()==='none'?0:1});
 root.add(<Rect width={1000} height={650} fill="#000000" opacity={.93} position={[0,-20]}/>);
 root.add(<Txt text="표면 기준 방향 · 접선 공간" position={[0,-330]} fontFamily={FONT} fontSize={35} fontWeight={700} fill={C.teal}/>);
 const signed=new Node({opacity:()=>phase()==='signed'?1:0});root.add(signed);
 signed.add(<Txt text="가로 성분 x 를 보면" position={[0,-225]} fontFamily={FONT} fontSize={43} fontWeight={700} fill={C.white}/>);
 signed.add(<Line points={[[-370,-30],[370,-30]]} stroke={C.r} lineWidth={6} startArrow endArrow arrowSize={17} opacity={()=>step()>=1?1:0}/>);
 signed.add(<Line points={[[0,-55],[0,-5]]} stroke={C.white} lineWidth={4} opacity={()=>step()>=1?1:0}/>);
 for(const [x,value,label] of [[-300,'−1','왼쪽'],[0,'0','기울지 않음'],[300,'+1','오른쪽']] as const){
  signed.add(<Txt text={value} position={[x,-110]} fontFamily={FONT} fontSize={56} fontWeight={700} fill={C.white} opacity={()=>step()>=1?1:0}/>);
  signed.add(<Txt text={label} position={[x,50]} fontFamily={FONT} fontSize={37} fill={C.white} opacity={()=>step()>=1?1:0}/>);
 }
 signed.add(<Txt text="RGB 저장 값에는 음수를 그대로 넣지 않습니다" position={[0,230]} fontFamily={FONT} fontSize={35} fill={C.yellow} opacity={()=>step()>=2?1:0}/>);
 const packed=new Node({opacity:()=>phase()==='packing'?1:0});root.add(packed);
 packed.add(<Txt text="방향 값 → 0–1 사이의 저장 값" position={[0,-230]} fontFamily={FONT} fontSize={40} fontWeight={700} fill={C.white}/>);
 for(const [i,a,b] of [[0,'−1','0'],[1,'0','0.5'],[2,'+1','1']] as const){
  const x=(i-1)*300;
  packed.add(<Rect width={270} height={185} position={[x,-30]} fill="#101613" stroke={C.muted} lineWidth={2}/>);
  packed.add(<Txt text={a+' → '+b} position={[x,-30]} fontFamily={FONT} fontSize={48} fontWeight={700} fill={()=>step()>=i?C.yellow:C.muted}/>);
 }
 packed.add(<Txt text="저장 값 = (방향 값 + 1) ÷ 2" position={[0,150]} fontFamily={FONT} fontSize={42} fontWeight={700} fill={C.teal}/>);
 packed.add(<Txt text="읽을 때: 방향 값 = 저장 값 × 2 − 1" position={[0,220]} fontFamily={FONT} fontSize={34} fill={C.white}/>);
 const neutral=new Node({opacity:()=>phase()==='neutral'?1:0});root.add(neutral);
 neutral.add(<Txt text={()=>step()<1?'표면에서 수직으로 나가는 방향':'표면에 수직인 방향: (0, 0, 1)'} position={[0,-240]} fontFamily={FONT} fontSize={42} fontWeight={700} fill={C.white}/>);
 neutral.add(<Txt text="방향 값           저장 값           약 8비트 값" position={[30,-155]} fontFamily={FONT} fontSize={32} fill={C.muted}/>);
 const perpendicular=new Node({opacity:()=>step()<1?1:0});neutral.add(perpendicular);
 perpendicular.add(<Line points={[[-140,100],[140,100]]} stroke={C.white} lineWidth={5}/>);
 perpendicular.add(<Line points={[[0,100],[0,-45]]} stroke={C.b} lineWidth={9} endArrow arrowSize={20}/>);
 perpendicular.add(<Line points={[[0,75],[25,75],[25,100]]} stroke={C.white} lineWidth={3}/>);
 perpendicular.add(<Txt text="표면 바깥 z" position={[0,-90]} fontFamily={FONT} fontSize={36} fontWeight={700} fill={C.b}/>);
 perpendicular.add(<Txt text="표면" position={[185,100]} fontFamily={FONT} fontSize={32} fill={C.white}/>);
 for(const [i,name,component,stored,byte,colour] of [[0,'R · 가로','0','0.5','128',C.r],[1,'G · 세로','0','0.5','128',C.g],[2,'B · 바깥','1','1','255',C.b]] as const){
  const y=-80+i*80;
  neutral.add(<Txt text={name} position={[-350,y]} fontFamily={FONT} fontSize={33} fontWeight={700} fill={colour}/>);
  neutral.add(<Txt text={()=>step()<1?'':component+(step()>=(i===2?3:2)?'    →    '+stored+'    →    '+byte:'')} position={[110,y]} fontFamily={FONT} fontSize={41} fontWeight={700} fill={colour}/>);
 }
 neutral.add(<Rect width={100} height={80} position={[-310,220]} fill="#8080FF" stroke={C.white} lineWidth={3} opacity={()=>step()>=4?1:0}/>);
 neutral.add(<Txt text="빨강·초록은 절반, 파랑은 최대" position={[100,200]} fontFamily={FONT} fontSize={34} fontWeight={700} fill={C.white} opacity={()=>step()>=3?1:0}/>);
 neutral.add(<Txt text={()=>step()>=5?'표면색이 아닌 방향 데이터':'파랑이 강한 보라색'} position={[45,255]} fontFamily={FONT} fontSize={33} fill={C.muted} opacity={()=>step()>=4?1:0}/>);
 return root;
}
