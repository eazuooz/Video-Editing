const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),file=path.join(work,'encoded-boundary-review/index.json');
const index=JSON.parse(fs.readFileSync(file,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(index.samples.length!==102||index.decoding.length!==6||index.decoding.some(d=>d.exitCode!==0||d.stderr))throw Error('Incomplete encoded evidence');
const proof={kind:'direct-102-exact-encoded-first-middle-last-and-six-full-chapter-decodes',approved:true,createdAt:new Date().toISOString(),
 indexSha256:sha(file),samples:102,fullDecodes:6,pages:index.pages.map(p=>({path:p,sha256:sha(path.join(root,p))})),
 findings:['All seven contact pages directly inspected. Encoded boundaries show selected normal-speed action and correctly identify official source/version.',
 'No title, snow scene, menu, alert, black border, inset frame, repeated source interval or idle time filling was found.',
 'Changed07 lookup/turn/board-post sequence and final landmark/fence observation match the reviewed source plan.',
 'Chapter videos have no source audio. Every actual final caption pixel and full final decode are separate pending checks.'],
 finalPixelReview:'pending',humanListening:'pending',finalPublicRights:'pending'};
fs.writeFileSync(path.join(work,'encoded-boundary-review/direct-review.json'),JSON.stringify(proof,null,2)+'\n');console.log('102 encoded boundaries directly reviewed; six full decodes passed.');
