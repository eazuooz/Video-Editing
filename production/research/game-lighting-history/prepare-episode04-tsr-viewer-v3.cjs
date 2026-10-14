const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='production/research/game-lighting-history/local/episode04-native-v1';
const input=base+'/native-review-v2.html',output=base+'/native-review-v3.html';
if(fs.existsSync(path.join(root,output)))throw Error('Preserve existing viewer');
const state=JSON.parse(fs.readFileSync(path.join(__dirname,'local/episode04-tsr-process-v1/execution-v2.json'),'utf8'));
if(state.current||state.completed.length!==4)throw Error('Completed four original cycles required');
let html=fs.readFileSync(path.join(root,input),'utf8');
const match=html.match(/const entries=(\[.*?\]),v=document/);
if(!match)throw Error('Observed viewer structure changed');
const entries=JSON.parse(match[1]);
for(const r of state.completed){
 if(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,r.media))).digest('hex')!==r.sha256)throw Error('Native source changed');
 entries.push({id:r.id,title:r.focus,src:'/@fs/D:/Github/Video-Editing/'+r.media,offset:0,sha256:r.sha256,duration:+r.probe.format.duration});
}
html=html.replace(match[0],'const entries='+JSON.stringify(entries)+',v=document').replace("s.value='outer-worlds-2-dlss45'","s.value='tsr-disocclusion'");
fs.writeFileSync(path.join(root,output),html);
console.log(JSON.stringify({output,sources:entries.length,newMedia:0,newImages:0,finalUseApproved:false}));
