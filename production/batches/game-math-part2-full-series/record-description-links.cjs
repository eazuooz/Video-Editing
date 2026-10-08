// Record observed native description edits; this script never writes to YouTube.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const defaults=read(path.join(__dirname,'description-links.json'));
const evidence=path.join(root,'shared/output/game-math-part2-full-series/description-links');
const records=fs.readdirSync(evidence).filter(f=>/^game-math-.*\.json$/.test(f)).map(f=>read(path.join(evidence,f)));
if(records.length!==10)throw Error('Expected ten actually saved existing lectures.');
const files=['production/batches/game-math-part2-full-series/description-links.json','production/batches/game-math-part2-full-series/publishing.cjs','production/batches/game-math-part2-full-series/record-description-links.cjs'];
for(const row of records){
  if(!row.titlePreserved||row.nativeVisibilityBefore!==row.nativeVisibilityAfter)throw Error('Native title/visibility changed: '+row.slug);
  const base='projects/'+row.slug+'/publishing',receiptFile=base+'/youtube-upload.json';
  const receipt=read(path.join(root,receiptFile));
  if(receipt.videoId!==row.videoId)throw Error('Actual upload identity mismatch.');
  const revision={schemaVersion:1,scope:'description-only',slug:row.slug,videoId:row.videoId,verifiedAtUtc:row.verifiedAtUtc,
    nativeTitle:row.nativeTitle,nativeVisibilityBefore:row.nativeVisibilityBefore,nativeVisibilityAfter:row.nativeVisibilityAfter,
    titlePreserved:true,privacyAndSchedulingPreserved:true,chaptersFooterAndExistingLinksPreserved:true,
    originalUploadReceiptPrivacyIsHistorical:true,mediaSubtitlesThumbnailAndOtherSettingsUnchanged:true,
    homepage:defaults.homepage,wiki:defaults.wiki,part2:defaults.part2,languages:{}};
  for(const lang of ['ko','en']){
    const r=row[lang];if(!r?.savedAndReopened||typeof r.before!=='string'||typeof r.after!=='string')throw Error('Unverified localized edit.');
    const insertion='\n\n'+defaults[lang]+'\n\n';
    if(!r.after.includes(insertion)||r.after.replace(insertion,'\n\n').trimEnd()!==r.before.trimEnd())throw Error('Description preservation audit failed: '+row.slug+'/'+lang);
    for(const url of [defaults.homepage,defaults.wiki,defaults.part2])if(!r.after.includes(url))throw Error('Missing canonical link.');
    const raw=fs.readFileSync(path.join(root,r.proof),'utf8');
    const normalized=raw.replace(/\r\n/g,'\n').split('\n').map(l=>l.replace(/[ \t]+$/,'')).join('\n').replace(/\n*$/,'\n');
    const proof=base+'/qa/description-links-'+lang+'.ax.txt';fs.mkdirSync(path.dirname(path.join(root,proof)),{recursive:true});fs.writeFileSync(path.join(root,proof),normalized);
    revision.languages[lang]={before:r.before,after:r.after,beforeSha256:hash(r.before),afterSha256:hash(r.after),languageOnPlatform:r.language||'ko',savedAndReopened:true,
      proof,proofSha256:hash(normalized),originalEvidence:r.proof,originalEvidenceSha256:hash(raw),normalization:'Only line endings and line-final whitespace; native content otherwise intact.'};
    files.push(proof);
    if(lang==='ko')receipt.metadata.description=r.after;else receipt.englishMetadata.description=r.after;
    // Preserve the existing footer boundary and the independently authored chapter body.
    if(typeof receipt.descriptionBody?.[lang]==='string'&&!receipt.descriptionBody[lang].includes(defaults[lang]))receipt.descriptionBody[lang]=receipt.descriptionBody[lang].replace('\n\n',insertion);
  }
  const revisionFile=base+'/revisions/description-links-20261008.json';fs.mkdirSync(path.dirname(path.join(root,revisionFile)),{recursive:true});fs.writeFileSync(path.join(root,revisionFile),JSON.stringify(revision,null,2)+'\n');
  receipt.descriptionLinksRevision={path:revisionFile,verifiedAtUtc:row.verifiedAtUtc,scope:'description-only',koSavedAndReopened:true,enSavedAndReopened:true,
    nativeVisibilityBefore:row.nativeVisibilityBefore,nativeVisibilityAfter:row.nativeVisibilityAfter,privacyAndSchedulingPreserved:true,chaptersFooterAndExistingLinksPreserved:true};
  fs.writeFileSync(path.join(root,receiptFile),JSON.stringify(receipt,null,2)+'\n');
  files.push(receiptFile,revisionFile,'projects/'+row.slug+'/rebuild.json');
}
const summary={schemaVersion:1,verifiedExistingLectures:records.length,allDescriptionsSavedAndReopened:true,sourceDefaults:'production/batches/game-math-part2-full-series/description-links.json',
  userEvidence:defaults.userEvidence,scope:'Existing and future Game Math PART2 lectures',
  items:records.map(r=>({slug:r.slug,videoId:r.videoId,nativeVisibility:r.nativeVisibilityAfter,ko:true,en:true,revision:'projects/'+r.slug+'/publishing/revisions/description-links-20261008.json'}))};
const summaryPath='production/batches/game-math-part2-full-series/description-links-review.json';fs.writeFileSync(path.join(root,summaryPath),JSON.stringify(summary,null,2)+'\n');files.push(summaryPath);
fs.writeFileSync(path.join(root,'tmp/part2-description-links-git-paths.json'),JSON.stringify(files,null,2)+'\n');
console.log(JSON.stringify({verified:records.length,slugs:records.map(r=>r.slug),preservedNativeStates:summary.items.map(i=>i.nativeVisibility)}));
