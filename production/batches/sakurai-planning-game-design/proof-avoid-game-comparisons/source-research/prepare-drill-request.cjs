const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../../../');
const base='production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research';
const target=path.join(root,base,'request-pepper-drill.json');
if(fs.existsSync(target))throw Error('Request already exists; continue actual checkpoint.');
const request=JSON.parse(fs.readFileSync(path.join(__dirname,'request-pepper-reveal.json'),'utf8'));
request.createdAt=new Date().toISOString();
request.purpose='Find additional unique native drilling/terrain actions after Reveal was excluded as duplicate of the already reviewed console trailer; exact intervals remain pending.';
const evidence=base+'/pepper-drill-official.ax.txt';
request.sources=[{
 videoId:'o3Fomp9HdHs',game:'Pepper Grinder',resourceLabel:'DRILLfomercial',url:'https://www.youtube.com/watch?v=o3Fomp9HdHs',
 expectedChannels:['DevolverDigital','Devolver Digital'],status:'official-creator-page-ID-and-normal-UI-verified-actions-pending',
 officialUiEvidence:evidence,officialUiSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,evidence))).digest('hex'),
 versionCaution:'UI premiere2024-03-06,80-second demo advertisement. Separate real game actions from text/marketing or presenters. Historical March28 announcement is not a current release fact.'
}];
fs.writeFileSync(target,JSON.stringify(request,null,2)+'\n');
console.log(JSON.stringify({request:base+'/request-pepper-drill.json',createdAt:request.createdAt}));
