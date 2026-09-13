const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {pack,verify,restore,inside}=require('./media-archive.cjs');
(async()=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'video-media-archive-test-'));
 const payload=crypto.randomBytes(220000);fs.mkdirSync(path.join(root,'input'));fs.writeFileSync(path.join(root,'input/test.wav'),payload);
 const m=await pack('input/test.wav','archive',{root,partBytes:65536});
 assert.ok(m.parts.length>1);assert.ok(m.parts.every(p=>p.bytes<=65536));
 const manifest=path.join(root,'archive/manifest.json');await verify(manifest);
 const destination=path.join(root,'restored');fs.mkdirSync(destination);
 const restored=await restore(manifest,{root:destination});assert.deepEqual(fs.readFileSync(restored.target),payload);
 assert.equal((await restore(manifest,{root:destination})).skipped,true);
 fs.writeFileSync(restored.target,'local change');await assert.rejects(()=>restore(manifest,{root:destination}),/overwrite/);
 assert.throws(()=>inside(root,'../escape.wav'),/relative/);
 fs.appendFileSync(path.join(root,'archive',m.parts[0].file),'corruption');await assert.rejects(()=>verify(manifest),/hash mismatch/);
 console.log(`PASS split/gzip/byte-exact restore/no-overwrite/corruption/traversal; fixtures retained: ${root}`);
})().catch(e=>{console.error(e);process.exitCode=1;});
