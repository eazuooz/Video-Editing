// Deliver the reviewed normal-construction boundary without copying other live jobs.
module.exports=function mergeMeshEpisodeRefinement(value,current,slug){
 const nextSlug='game-math-normal-transform-uv';
 if(slug!=='game-math-mesh-uv'||value.items.some(x=>x.slug===nextSlug))return value;
 const history=current.episodeRefinementHistory?.find(x=>x.original?.slug===slug&&x.original.order===12&&x.original.part===5&&x.original.totalParts===8&&JSON.stringify(x.result)===JSON.stringify([slug,nextSlug]));
 if(!history)throw Error('Missing complete normal-construction split evidence');
 const prior=value.items.find(x=>x.slug===slug),own=current.items.find(x=>x.slug===slug),followup=current.items.find(x=>x.slug===nextSlug);
 const keys=['order','chapter','part','totalParts','titleKo','titleEn','viewerQuestion','sections','sourceNotion'];
 if(!prior||!own||!followup||keys.some(k=>JSON.stringify(prior[k])!==JSON.stringify(history.original[k])))throw Error('Original mesh plan changed concurrently; inspect before delivery');
 if(own.order!==12||own.part!==5||own.totalParts!==9||followup.order!==13||followup.part!==6||followup.totalParts!==9||followup.renderComplete||followup.privateUploadComplete)throw Error('Unexpected mesh episode coverage or prematurely delivered next lecture');
 if(JSON.stringify(own.sections)!==JSON.stringify(['10.4','10.4.1','10.4.2-normal-construction'])||JSON.stringify(followup.sections)!==JSON.stringify(['10.4.2-normal-transform','10.5']))throw Error('Useful source coverage changed');
 for(const item of value.items){
  if(item.order<13)continue;
  item.order+=1;
  if(item.chapter===10){item.part+=1;item.totalParts=9;}
 }
 for(const k of keys)prior[k]=own[k];
 value.items.push(followup);value.items.sort((a,b)=>a.order-b.order);
 value.episodeRefinementHistory??=[];
 if(!value.episodeRefinementHistory.some(x=>x.atUtc===history.atUtc))value.episodeRefinementHistory.push(history);
 return value;
};
