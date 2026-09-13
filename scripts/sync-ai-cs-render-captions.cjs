// Update only sidecar text after rendering; cue numbers/times must be unchanged.
// Original render-input hashes remain intact in the render .json.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const video=path.resolve(root,process.argv[2]??'');
if(!video.startsWith(path.join(root,'shared/output/motion-canvas')+path.sep)||!video.endsWith('.mp4'))throw Error('Expected a review MP4');
const stem=video.slice(0,-4),qaPath=`${stem}-qa.json`;
const m=JSON.parse(fs.readFileSync(path.join(root,'projects/ai-era-cs-fundamentals/project.json'),'utf8'));
const qa=JSON.parse(fs.readFileSync(qaPath,'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const timecodes=p=>fs.readFileSync(p,'utf8').split(/\r?\n/).filter(s=>/^\d+$|^\d\d:\d\d:\d\d,\d{3} --> /.test(s)).join('\n');
const beforeVideoHash=hash(video),updates=[];
for(const [lang,key]of [['ko','captionsKo'],['en','captionsEn']]){
 const src=path.join(root,m.paths[key]),dest=`${stem}.${lang}.srt`;
 if(timecodes(src)!==timecodes(dest))throw Error('Retiming requires a new delivery, not a text-only update');
 const oldHash=hash(dest),newHash=hash(src);
 if(oldHash===newHash)continue;
 const oldEntry=qa.captions.find(c=>c.language===lang);
 if(oldEntry.sha256!==oldHash)throw Error('Existing sidecar differs from its QA record');
 const backup=`${stem}.${lang}.before-text-balance.srt`;
 if(fs.existsSync(backup))throw Error('Backup exists; refusing ambiguous repeat update');
 fs.copyFileSync(dest,backup,fs.constants.COPYFILE_EXCL);
 fs.copyFileSync(src,dest);
 if(hash(dest)!==newHash)throw Error('Copy mismatch');
 oldEntry.sha256=newHash;
 updates.push({language:lang,previousSha256:oldHash,sha256:newHash,backup:path.relative(root,backup).replaceAll('\\','/')});
}
if(hash(video)!==beforeVideoHash)throw Error('Video changed during sidecar update');
if(updates.length){
 qa.captionTextRefinement={checkedAt:new Date().toISOString(),timecodesUnchanged:true,videoUnchanged:true,videoSha256:beforeVideoHash,updates};
 fs.writeFileSync(qaPath,JSON.stringify(qa,null,2)+'\n');
}
console.log(`Updated ${updates.length} subtitle sidecars; MP4 and KO/EN cue timecodes unchanged`);
