// Weighted streaming selection only. Final RIS/ReSTIR lighting normalization,
// visibility, source densities and spatial/temporal bias correction are separate.
export type Reservoir={sample:string|null,weightSum:number,candidates:number};
export function streamCandidate(r:Reservoir,sample:string,weight:number,u:number):Reservoir{
 if(!Number.isFinite(weight)||!Number.isFinite(u)||weight<0||u<0||u>=1)throw Error('Invalid weight/random variate');
 const sum=r.weightSum+weight;
 return{sample:sum>0&&u*sum<weight?sample:r.sample,weightSum:sum,candidates:r.candidates+1};
}
export function replacementProbability(previousWeight:number,newWeight:number){
 if(previousWeight<0||newWeight<0)throw Error('Weights must be nonnegative');
 const sum=previousWeight+newWeight;return sum>0?newWeight/sum:0;
}
