import {Circle,Img,Line,Node,Rect,Txt} from '@motion-canvas/2d';
import {Vector2} from '@motion-canvas/core';
import evidence from '../../../../projects/shorts-normal-map-illusion/sources/deadcells-v2.json';
const ROOT='/@fs/D:/Github/VideoEditing/projects/shorts-normal-map-illusion/production/local/native-gameplay-v2/deadCells/';
const anchors=evidence.editorialGuides.inset.anchors;
export function createDeadCellsGameplay({enabled,localFrame,sourceSeconds}:{enabled:()=>boolean;localFrame:()=>number;sourceSeconds:()=>number}){
 const root=new Node({opacity:()=>enabled()?1:0});
 const src=()=>ROOT+'frame-'+String(Math.max(0,Math.min(395,localFrame()))).padStart(5,'0')+'.png';
 const centre=()=>{
  const time=sourceSeconds();const left=anchors.filter(a=>a.sourceSeconds<=time).at(-1)??anchors[0];const right=anchors.find(a=>a.sourceSeconds>=time)??anchors[anchors.length-1];const u=right.sourceSeconds===left.sourceSeconds?0:Math.max(0,Math.min(1,(time-left.sourceSeconds)/(right.sourceSeconds-left.sourceSeconds)));
  return new Vector2(left.x+(right.x-left.x)*u,left.y+(right.y-left.y)*u);
 };
 root.add(<Img src={src} width={880} height={495} position={[0,-207]}/>);
 const fullPoint=()=>new Vector2((centre().x-960)*880/1920,-207+(centre().y-540)*880/1920);
 root.add(<Circle position={fullPoint} width={85} height={85} stroke="#73D7CD" lineWidth={4}/>);
 root.add(<Line points={()=>[fullPoint().add([0,42]),[220,43]]} stroke="#73D7CD" lineWidth={3}/>);
 const inset=new Rect({width:240,height:240,position:[220,165],clip:true});root.add(inset);
 inset.add(<Img src={src} width={1440} height={810} position={()=>new Vector2((960-centre().x)*240/320,(540-centre().y)*240/320)}/>);
 root.add(<Rect width={244} height={244} position={[220,165]} stroke="#73D7CD" lineWidth={4}/>);
 root.add(<Txt text="캐릭터 확대" position={[-170,125]} fontFamily="Malgun Gothic" fontSize={37} fontWeight={700} fill="#73D7CD"/>);
 root.add(<Txt text="같은 프레임" position={[-170,180]} fontFamily="Malgun Gothic" fontSize={32} fill="#B8C3BC"/>);
 return root;
}
