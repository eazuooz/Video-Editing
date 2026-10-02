const fs=require('node:fs');const path=require('node:path');
const root=path.resolve(__dirname,'..','output','youtube-library-refresh');
const excluded=new Set(['PLUU7_j2ihric','PLWKwcHKTXy5RSvmpWyWAG9kWMEqI2AYjn','PLWKwcHKTXy5QXZEw5dJ6ubggsBhLtTsBa']);
const inventoryPath=path.join(root,'inventory.json');const changesPath=path.join(root,'changes.json');
for(const file of [inventoryPath,changesPath]){
  const backup=file.replace(/\.json$/, '-before-game-design-exclusion.json');
  if(!fs.existsSync(backup))fs.copyFileSync(file,backup);
}
const inventory=JSON.parse(fs.readFileSync(inventoryPath,'utf8'));
inventory.policy.exclude=[...excluded];
inventory.policy.overlap='exclude a video if it appears in any excluded playlist, even when it appears elsewhere';
inventory.scopeUpdatedAt=new Date().toISOString();
for(const playlist of inventory.playlists)if(!playlist.skipped)playlist.excluded=excluded.has(playlist.id);
for(const video of inventory.videos){
  for(const playlist of video.playlists)playlist.excluded=excluded.has(playlist.id);
  video.inExcludedPlaylist=video.playlists.some(x=>x.excluded);
  video.target=video.ownedByChannel&&video.playlists.some(x=>!x.excluded)&&!video.inExcludedPlaylist;
}
inventory.counts.targetVideos=inventory.videos.filter(x=>x.target).length;
inventory.counts.excludedByPlaylistMembership=inventory.videos.filter(x=>x.ownedByChannel&&x.inExcludedPlaylist).length;
fs.writeFileSync(inventoryPath,`${JSON.stringify(inventory,null,2)}\n`);
const report=JSON.parse(fs.readFileSync(changesPath,'utf8'));
const allowed=new Set(inventory.videos.filter(x=>x.target).map(x=>x.id));
const removed=report.changes.filter(x=>!allowed.has(x.id));
report.changes=report.changes.filter(x=>allowed.has(x.id));report.count=report.changes.length;
report.excludedPlaylistIds=[...excluded];report.scopeUpdatedAt=new Date().toISOString();
fs.writeFileSync(changesPath,`${JSON.stringify(report,null,2)}\n`);
fs.writeFileSync(path.join(root,'scope.json'),`${JSON.stringify({updatedAt:new Date().toISOString(),excludedPlaylistIds:[...excluded],excludedPlaylistTitles:['게임 디자인 · Planning & Game Design & Tech','C++ 기초 문법','C++ 자료구조 및 기초 알고리즘'],overlap:'exclude by any excluded membership',count:report.count,removedVideoIds:removed.map(x=>x.id)},null,2)}\n`);
console.log(JSON.stringify({targetVideos:report.count,removed:removed.map(x=>({id:x.id,title:x.originalTitle})),excludedByPlaylistMembership:inventory.counts.excludedByPlaylistMembership}));
