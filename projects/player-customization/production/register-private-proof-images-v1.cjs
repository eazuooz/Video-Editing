// Usage: node projects/player-customization/production/register-private-proof-images-v1.cjs
// Only the three individually viewed publishing proofs; encoded/source QA rasters remain local.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/player-customization/publishing/';
const reasons={
 'private-cc-off-game-v1.png':'Minimal actual private-upload proof at30s: full existing-game picture, Korean fixed-bottom burned caption and current title/private badge. 1080p60 and CC-off observations are preserved in the paired AX/pixel-review record. Source and encoded QA images remain local.',
 'private-cc-off-white-v1.png':'Minimal actual private-upload proof at45s: full white projected spatial explanation with top/side/front faces, action-path/range comparison and fixed-bottom Korean burned caption; title and private badge identify the current upload. This is not a reusable QA contact sheet.',
 'end-screen-saved-reopened-v1.png':'Minimal actual saved/reopened Studio proof of this upload\'s original membership scene, unobscured title/member identities and three distinct playlist/subscribe/canonical coaching elements confined to the final10seconds. The exact60fps times are in the paired JSON/AX record.'
};
const registryPath='shared/git-essential-images.json',registry=JSON.parse(fs.readFileSync(path.join(root,registryPath),'utf8'));
let ignores=fs.readFileSync(path.join(root,'.gitignore'),'utf8').trimEnd();
const records=Object.entries(reasons).map(([file,reason])=>({path:base+file,purpose:'minimal-publishing-proof',reason,reviewedAt:new Date().toISOString(),sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,base+file))).digest('hex'),project:'player-customization'}));
for(const entry of records){const old=registry.entries.find(e=>e.path===entry.path);if(old&&old.sha256!==entry.sha256)throw Error('Previously registered proof changed: '+entry.path);if(!old)registry.entries.push(entry);if(!ignores.split(/\r?\n/).includes('!'+entry.path))ignores+='\n!'+entry.path;}
fs.writeFileSync(path.join(root,registryPath),JSON.stringify(registry,null,2)+'\n');
fs.writeFileSync(path.join(root,'.gitignore'),ignores+'\n');
console.log(JSON.stringify({reviewedPublishingProofs:records,sourceEncodedQaImagesAdded:0,staged:false}));
