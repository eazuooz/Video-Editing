// Select only the authorized complete-concept split, preserving other live jobs.
module.exports=function mergeProjectionDepthRefinement(value,current,slug){
 if(slug!=='game-math-camera-projection'||value.items.some(x=>x.slug==='game-math-projection-depth'))return value;
 const history=current.episodeRefinementHistory?.find(x=>x.original?.slug===slug&&x.original.order===10&&x.original.part===3&&x.original.totalParts===7&&x.result?.includes('game-math-projection-depth'));
 if(!history)throw Error('Missing measured complete point-to-pixel split evidence');
 const prior=value.items.find(x=>x.slug===slug),own=current.items.find(x=>x.slug===slug),followup=current.items.find(x=>x.slug==='game-math-projection-depth');
 const keys=['order','chapter','part','totalParts','titleKo','titleEn','viewerQuestion','sections','sourceNotion'];
 if(!prior||!own||!followup||keys.some(k=>JSON.stringify(prior[k])!==JSON.stringify(history.original[k])))throw Error('Original projection plan changed concurrently; inspect the actual plan');
 if(own.order!==10||own.part!==3||own.totalParts!==8||followup.order!==11||followup.part!==4||followup.totalParts!==8||followup.renderComplete||followup.privateUploadComplete)throw Error('Unexpected projection split or prematurely completed next episode');
 for(const item of value.items){
  if(item.order<11)continue;
  item.order+=1;
  if(item.chapter===10){
   item.originalPlanBeforeProjectionDepthSplit=Object.fromEntries(['part','totalParts','titleKo','titleEn'].map(k=>[k,item[k]]));
   item.part+=1;item.totalParts=8;
  }
 }
 for(const k of keys)prior[k]=own[k];
 value.items.push(followup);value.items.sort((a,b)=>a.order-b.order);
 value.episodeRefinementHistory??=[];
 if(!value.episodeRefinementHistory.some(x=>x.atUtc===history.atUtc))value.episodeRefinementHistory.push(history);
 return value;
};
