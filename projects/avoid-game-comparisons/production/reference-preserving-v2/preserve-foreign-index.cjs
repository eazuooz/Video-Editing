// Collector's legacy rebuild generator writes the shared index even for one
// selected project. Preserve that unrelated, already-dirty file byte-for-byte.
// Every selected-project output still uses the ordinary collector/generator.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const target=path.resolve(__dirname,'../../../../projects/rebuild-index.json');
const before=crypto.createHash('sha256').update(fs.readFileSync(target)).digest('hex');
const write=fs.writeFileSync;
fs.writeFileSync=function(file,...args){
 if(typeof file==='string' && path.resolve(file)===target){console.log('Preserved unrelated projects/rebuild-index.json');return;}
 return write.call(fs,file,...args);
};
process.on('exit',()=>{const after=crypto.createHash('sha256').update(fs.readFileSync(target)).digest('hex');if(after!==before){console.error('Shared rebuild index changed outside this collector; inspect without overwriting it');process.exitCode=1;}});
