// Apply only the approved10.2/10.3 split while retaining other live queue records.
module.exports=function mergeCameraEpisodeRefinement(value,current,slug){
 value=require('./merge-projection-depth-refinement.cjs')(value,current,slug);
 value=require('./merge-mesh-episode-refinement.cjs')(value,current,slug);
 if(value.items.some(x=>x.slug===slug))return value;
 if(slug!=='game-math-camera-frustum')throw Error('Missing existing lecture queue entry');
 const history=current.episodeRefinementHistory?.find(x=>x.original?.slug==='game-math-camera-projection'&&x.original.order===9&&x.original.part===2&&x.original.totalParts===6);
 if(!history||JSON.stringify(history.original.sections)!==JSON.stringify(['10.2','10.3']))throw Error('Missing approved complete-concept split evidence');
 const projection=value.items.find(x=>x.slug===history.original.slug),next=current.items.find(x=>x.slug===history.original.slug),own=current.items.find(x=>x.slug===slug);
 const plan=['order','chapter','part','totalParts','titleKo','titleEn','viewerQuestion','sections','sourceNotion'];
 if(!projection||!next||!own||plan.some(k=>JSON.stringify(projection[k])!==JSON.stringify(history.original[k])))throw Error('Original camera plan changed concurrently; review before merging');
 if(own.order!==9||own.chapter!==10||own.part!==2||own.totalParts!==7||JSON.stringify(own.sections)!==JSON.stringify(['10.2.1','10.2.2','10.2.3','10.2.4','10.2.5'])||next.order!==10||next.part!==3||next.totalParts!==7||JSON.stringify(next.sections)!==JSON.stringify(['10.3.1','10.3.2','10.3.3','10.3.4','10.3.5','10.3.6']))throw Error('Unexpected refined camera coverage');
 for(const item of value.items){
  if(item.order<10)continue;
  item.order+=1;
  if(item.chapter===10){
   item.originalPlanBeforeCameraSplit=Object.fromEntries(['part','totalParts','titleKo','titleEn'].map(k=>[k,item[k]]));
   item.part+=1;item.totalParts=7;
  }
 }
 for(const k of plan)projection[k]=next[k];
 value.items.push(own);value.items.sort((a,b)=>a.order-b.order);
 value.episodeRefinementHistory??=[];
 if(!value.episodeRefinementHistory.some(x=>x.atUtc===history.atUtc))value.episodeRefinementHistory.push(history);
 return value;
};
