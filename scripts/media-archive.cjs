// Dependency-free, lossless, size-bounded media backup. Requires Node.js 18+.
// pack <repo-relative-file> <repo-relative-archive-dir> [--review-only]
// verify <manifest.json>
// restore <manifest.json> [--root <existing-directory>]
const fs=require('node:fs'),fsp=require('node:fs/promises'),path=require('node:path');
const {createHash,randomUUID}=require('node:crypto');
const {createGzip,createGunzip}=require('node:zlib');
const {Transform,Readable,Writable}=require('node:stream');
const {pipeline}=require('node:stream/promises');
const ROOT=path.resolve(__dirname,'..'),PART_BYTES=80*1024*1024;
const digest=()=>createHash('sha256');
function inside(base,relative){
 if(typeof relative!=='string'||!relative||path.isAbsolute(relative)||relative.includes('\\')||relative.split('/').some(s=>s==='..'||s==='.git'))throw Error('Expected a safe relative path');
 const target=path.resolve(base,relative),boundary=path.resolve(base)+path.sep;
 if(!target.startsWith(boundary))throw Error('Path outside target root');
 let check=target;
 while(check!==path.resolve(base)){
  if(fs.existsSync(check)&&fs.lstatSync(check).isSymbolicLink())throw Error('Symlink paths are not supported');
  check=path.dirname(check);
 }
 return target;
}
async function hashFile(file){const h=digest();for await(const c of fs.createReadStream(file))h.update(c);return h.digest('hex');}
async function pack(sourceRelative,archiveRelative,{partBytes=PART_BYTES,reviewOnly=false,root=ROOT}={}){
 if(!Number.isInteger(partBytes)||partBytes<1024||partBytes>PART_BYTES)throw Error('Invalid part size');
 const source=inside(root,sourceRelative),dir=inside(root,archiveRelative),manifestFile=path.join(dir,'manifest.json');
 if(!(await fsp.stat(source)).isFile())throw Error('Source must be a regular file');
 if(fs.existsSync(manifestFile)){
  const m=await verify(manifestFile);
  if(m.source!==sourceRelative||m.sha256!==await hashFile(source))throw Error('Archive exists for different source content');
  return m;
 }
 if(fs.existsSync(dir)&&fs.readdirSync(dir).length)throw Error('Non-empty archive folder; keep it and choose a new version');
 fs.mkdirSync(dir,{recursive:true});
 const h=digest();let size=0,part=null,fd=null,partHash=null;
 const parts=[];
 const meter=new Transform({transform(c,_,done){size+=c.length;h.update(c);done(null,c);}});
 const compressed=createGzip({level:6});
 const compressJob=pipeline(fs.createReadStream(source),meter,compressed);
 compressJob.catch(()=>{}); // The awaited pipeline below owns error reporting.
 async function closePart(){if(!fd)return;await fd.close();part.sha256=partHash.digest('hex');parts.push(part);fd=null;}
 try{
  for await(const chunk of compressed){
   let offset=0;
   while(offset<chunk.length){
    if(!fd){part={file:`part-${String(parts.length+1).padStart(3,'0')}.gz`,bytes:0};partHash=digest();fd=await fsp.open(path.join(dir,part.file),'wx');}
    const slice=chunk.subarray(offset,offset+Math.min(partBytes-part.bytes,chunk.length-offset));
    let written=0;while(written<slice.length){const r=await fd.write(slice,written,slice.length-written);written+=r.bytesWritten;}
    partHash.update(slice);part.bytes+=slice.length;offset+=slice.length;
    if(part.bytes===partBytes)await closePart();
   }
  }
  await compressJob;
  await closePart();
 }finally{if(fd)await fd.close();}
 const manifest={schemaVersion:1,format:'gzip-split-v1',source:sourceRelative,bytes:size,sha256:h.digest('hex'),partSizeLimit:partBytes,privateReviewOnly:reviewOnly,parts};
 await fsp.writeFile(manifestFile,JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
 await verify(manifestFile);
 return manifest;
}
async function loadChecked(manifestFile){
 const m=JSON.parse(await fsp.readFile(manifestFile,'utf8'));
 if(m.schemaVersion!==1||m.format!=='gzip-split-v1'||!Array.isArray(m.parts)||!m.parts.length||!Number.isSafeInteger(m.bytes)||m.bytes<0||!/^[a-f0-9]{64}$/.test(m.sha256))throw Error('Invalid archive manifest');
 for(const [i,p]of m.parts.entries()){
  if(p.file!==`part-${String(i+1).padStart(3,'0')}.gz`||!Number.isSafeInteger(p.bytes)||p.bytes<=0||p.bytes>PART_BYTES)throw Error('Invalid part record');
  const file=inside(path.dirname(manifestFile),p.file);
  if((await fsp.stat(file)).size!==p.bytes||await hashFile(file)!==p.sha256)throw Error(`Part size/hash mismatch: ${p.file}`);
 }
 return m;
}
function unpackStream(manifestFile,m){
 return Readable.from((async function*(){for(const p of m.parts)for await(const c of fs.createReadStream(inside(path.dirname(manifestFile),p.file)))yield c;})()).pipe(createGunzip());
}
async function verify(manifestFile){
 const m=await loadChecked(manifestFile),h=digest();let bytes=0;
 await pipeline(unpackStream(manifestFile,m),new Writable({write(c,_,done){bytes+=c.length;h.update(c);done();}}));
 if(bytes!==m.bytes||h.digest('hex')!==m.sha256)throw Error('Restored content does not match original');
 return m;
}
async function restore(manifestFile,{root=ROOT}={}){
 const m=await verify(manifestFile),target=inside(root,m.source);
 if(fs.existsSync(target)){
  if((await fsp.stat(target)).size===m.bytes&&await hashFile(target)===m.sha256)return {target,skipped:true};
  throw Error('Refusing to overwrite different local content');
 }
 fs.mkdirSync(path.dirname(target),{recursive:true});
 const temp=`${target}.restoring-${randomUUID()}`;
 try{
  await pipeline(unpackStream(manifestFile,m),fs.createWriteStream(temp,{flags:'wx'}));
  if(await hashFile(temp)!==m.sha256)throw Error('Restore checksum failed');
  // Exclusive copy prevents a concurrent local edit from being overwritten.
  await fsp.copyFile(temp,target,fs.constants.COPYFILE_EXCL);
 }finally{if(fs.existsSync(temp))await fsp.unlink(temp);}
 return {target,skipped:false};
}
async function main(){
 const [command,first,second,...rest]=process.argv.slice(2);
 if(command==='pack'){
  const m=await pack(first,second,{reviewOnly:rest.includes('--review-only')});
  console.log(JSON.stringify({source:m.source,originalBytes:m.bytes,compressedBytes:m.parts.reduce((s,p)=>s+p.bytes,0),parts:m.parts.length,sha256:m.sha256,verified:true},null,2));
 }else if(command==='verify')console.log(JSON.stringify({verified:true,...await verify(path.resolve(ROOT,first))},null,2));
 else if(command==='restore'){
  const rootArg=process.argv.indexOf('--root');
  console.log(await restore(path.resolve(ROOT,first),{root:rootArg<0?ROOT:path.resolve(process.argv[rootArg+1])}));
 }else throw Error('Usage: media-archive.cjs pack <file> <archive-dir> [--review-only] | verify <manifest> | restore <manifest> [--root <directory>]');
}
module.exports={pack,verify,restore,inside};
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
