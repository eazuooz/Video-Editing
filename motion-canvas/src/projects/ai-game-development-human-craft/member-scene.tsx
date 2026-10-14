import {makeScene2D,Img,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
// Original screenshot rows, including truncation, are preserved as supplied.
// Never synthesize a profile, badge, full handle, or an extra member.
export default makeScene2D(function*(view){
 view.fill('#ffffff');
 view.add(new Txt({text:'MEMBERSHIP',x:-875,y:-160,offset:[-1,0],fontSize:28,fontWeight:500,fill:'#617f9e',fontFamily:"'Malgun Gothic',sans-serif"}));
 view.add(new Txt({text:'멤버쉽가입 감사드립니다.',x:-875,y:-75,offset:[-1,0],fontSize:61,fontWeight:700,fill:'#111111',fontFamily:"'Malgun Gothic',sans-serif"}));
 view.add(new Txt({text:'채널을 함께 만들어 주셔서 고맙습니다.',x:-875,y:15,offset:[-1,0],fontSize:32,fill:'#777777',fontFamily:"'Malgun Gothic',sans-serif"}));
 view.add(new Img({src:'/@fs/D:/Github/VideoEditing/shared/assets/membership/member-list-20260929.png',x:645,y:0,width:460,height:955}));
 view.add(new Img({src:'/@fs/D:/Github/VideoEditing/shared/assets/branding/yamyamcoding-cats-original.png',x:915,y:486,width:72,height:72}));
 yield* waitFor(10);
});
