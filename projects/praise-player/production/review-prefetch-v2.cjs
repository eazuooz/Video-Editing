// Read public publisher/store metadata before choosing any new game excerpts.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const qfile=path.join(root,'production/batches/private-review-expansion/queue.json');
const q=JSON.parse(fs.readFileSync(qfile,'utf8')),item=q.items.find(x=>x.slug==='praise-player');
if(!q.items.slice(0,3).every(x=>x.status==='complete-private-review'))throw Error('Previous revisions unfinished');
if(item.newPrivateUpload||item.execution?.state==='running')throw Error('Existing execution must be resumed');
q.currentSlug='praise-player';q.preparationSlug='praise-player';q.updatedAt=new Date().toISOString();
item.status='researching-expansion';item.stage='fresh-publisher-footage-and-visible-action-review';
item.prefetch={updatedAt:q.updatedAt,candidates:['Hi-Fi RUSH','Tony Hawk’s Pro Skater 1 + 2','Rocket League'],priorUse:'Hi-Fi RUSH/Rocket League were rejected prior candidates, not previously used footage; no THPS source/script matches in project JSON/Markdown.',sourceAudio:'All new source audio muted; original approved Nimbus stays continuous.',publicRights:'pending final review; do not infer a blanket license from a downloadable press kit',downloadAttempt:{source:'https://hifirush.krafton.com/ko/media',result:'Official owner press page video tiles observed; two UI clicks yielded no download event and no asset. No hidden app state or security bypass used. Review publisher-owned public store footage instead.'}};
q.nextAction='Inspect fresh praise-player source actions before writing six additive spoken examples. Preserve all original 192.533333 seconds of PPT and all baseline voice; no synthesis/render started.';
fs.writeFileSync(qfile,JSON.stringify(q,null,2)+'\n');
(async()=>{const records=[];for(const appid of [1817230,2395210]){
 const url=`https://store.steampowered.com/api/appdetails?appids=${appid}&l=english&cc=us`;
 const response=await fetch(url);if(!response.ok)throw Error(response.status+' '+url);
 const json=await response.json(),data=json[appid]?.data;if(!json[appid]?.success)throw Error('Unavailable '+appid);
 records.push({appid,url,name:data.name,developers:data.developers,publishers:data.publishers,movies:data.movies});
 console.log(JSON.stringify({appid,name:data.name,publishers:data.publishers,movies:data.movies}));
}fs.writeFileSync(path.join(__dirname,'publisher-movie-candidates-v2.json'),JSON.stringify({checkedAt:new Date().toISOString(),records},null,2)+'\n');})().catch(e=>{console.error(e);process.exitCode=1});
