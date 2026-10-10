import type {V3} from '../../game-lighting-history-shared/depth-space';
// Educational two-probe visibility comparison, not DDGI's complete eight-probe
// moment/normal/bias/trilinear interpolant. Display the scope on the diagram.
export function wallBlocks(a:V3,b:V3,wallY=0){
 const dx=b[0]-a[0];if(Math.abs(dx)<1e-10)return false;
 const t=-a[0]/dx;if(t<=0||t>=1)return false;
 const y=a[1]+t*(b[1]-a[1]),z=a[2]+t*(b[2]-a[2]);
 return Math.abs(y-wallY)<=150&&z>=0&&z<=160;
}
export function weightedIrradiance(values:number[],weights:number[]){
 const sum=weights.reduce((a,b)=>a+b,0);
 return sum<=1e-10?null:values.reduce((s,v,i)=>s+v*weights[i],0)/sum;
}
export function temporalIrradiance(old:number,newSample:number,oldWeight:number){
 if(oldWeight<0||oldWeight>1)throw Error('Blend weight must be in[0,1]');
 return oldWeight*old+(1-oldWeight)*newSample;
}
export function responseAfterUpdates(initial:number,target:number,oldWeight:number,n:number){
 return target+(initial-target)*Math.pow(oldWeight,n);
}
