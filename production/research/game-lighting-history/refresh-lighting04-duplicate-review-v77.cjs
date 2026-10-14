// Re-read current content-bearing receipt fields and both changed manifests.
// Foreign schedules/receipts are evidence only; this writes no foreign files.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const sha=t=>crypto.createHash('sha256').update(t).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const previous=read('production/preflight/game-lighting-history-04.json');
const expected={
 'projects/game-math-camera-frustum/publishing/youtube-upload.json':'1d3778d84acb507075a25f78cf140c6634121474ae217ac01b2ad80901fbdff3',
 'projects/game-math-camera-projection/publishing/youtube-upload.json':'a7e4f2b0e6e32b4c108798ef32164af32e1273aacf5b80f03fe6542c7b203d14',
 'projects/game-math-mesh-uv/publishing/youtube-upload.json':'d029190d6e01d2efe5c48188c9f65100e8c5dbc29e2388724088d49862bc69ea',
 'projects/game-math-normal-transform-uv/publishing/youtube-upload.json':'5be6bc5261d57e7321b956508fcc4cb9500234e2998c5bb680823bb43d5633dc',
 'projects/game-math-polygon-centers-v2/project.json':'5edd59b414844f3565e97a70040f6e8636d9eb0897f4053e145bfc3df820d9b8',
 'projects/game-math-polygon-centers-v2/publishing/youtube-upload.json':'594739a6ad594292fd8d5b18e4d87acfbd946dc570cf1772dd0a243180f9729d',
 'projects/game-math-polygon-partition-v2/project.json':'f00b0551056387ee0bf60afec4c00f9eefb5ac69983a111d42527ca8fb0733d3',
 'projects/game-math-polygon-partition-v2/publishing/youtube-upload.json':'563056a2f745dc5abdcc0a86a2264e5c0ff370ec707af07d94b0fbba0c90e404',
 'projects/game-math-polygons-triangulation/publishing/youtube-upload.json':'688341ce030bd1971f4a0e9c05bfb6cfa5b35447064ec9684730f21fa3934b51',
 'projects/game-math-projection-depth/publishing/youtube-upload.json':'d6ce1397e5a43a505121f4515df84f1d3c872e965952b89277c160aa2e00912a',
 'projects/game-math-rendering-light/publishing/youtube-upload.json':'5bcd865707b6e00ff6702892257604c7ee49b92be534b769c3c1bf04ae13983f'
};
const changed=previous.inputFiles.filter(f=>!fs.existsSync(f.path)||sha(fs.readFileSync(f.path,'utf8'))!==f.sha256);
if(changed.length!==11||changed.some(f=>!expected[f.path]||!fs.existsSync(f.path)||sha(fs.readFileSync(f.path,'utf8'))!==expected[f.path]))throw Error('A new delta needs direct content review; do not refresh automatically');
const out='production/research/game-lighting-history/episode04-current-duplicate-rereview-v77.json';
if(fs.existsSync(out))throw Error('Preserve prior review');
const reason='Two complete current polygon manifests and all nine changed receipts\' KO/EN viewer descriptions, complete chapter lists, titles, actual IDs and current schedule/status fields were directly read. Polygon centers now schedules YgcN8vs0gNo on Nov2 and partition pfagaQK-xfI on Nov4, retaining the old L7SXFwn4i2k privately. Their centroid/incenter/circumcenter, ordered boundary, L-shape ear clipping and area7 questions are distinct from rendering history04. Other receipts still teach camera/frustum/projection/depth/mesh/normals/UV and the math rendering-light lesson. The latter overlaps terminology (forward/deferred, BRDF and rendering equation), already compared in the previous full-script inventory, but answers a numerical pixel/light-quantity question rather than this chronological image reconstruction, display controls and captured frame-resource workflow. Their original full paired script hashes are unchanged. Preserve their white40:60/noBGM exception and saved schedules; no foreign content or setting is changed. Carry the previous83-project full-script and actual Studio lIDe30dqC28 private review. Our current37 new guided paragraphs, original111 PCM and five framing takes are unchanged; final coverage/ratio/mixed/pixel/private approvals remain false. Evidence: '+out;
const contents=changed.filter(f=>f.path.includes('/publishing/')).map(f=>{const j=read(f.path);return {path:f.path,titles:{ko:j.metadata.title,en:j.englishMetadata.title},descriptionBody:j.descriptionBody,videoId:j.videoId,currentVisibility:j.currentVisibility,scheduleVerification:j.scheduleVerification,status:j.status};});
fs.writeFileSync(out,JSON.stringify({reviewedAt:new Date().toISOString(),previous:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v71.json',changes:changed.map(f=>({path:f.path,previousSha256:f.sha256,sha256:expected[f.path],completeManifestDirectlyRead:f.path.endsWith('/project.json'),receiptContentFieldsDirectlyRead:f.path.includes('/publishing/')})),receiptContentRead:contents,unchangedFullScriptsCarried:true,decision:'distinct',comparison:reason,actualStudioEvidence:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',foreignFilesModified:false},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',out],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
