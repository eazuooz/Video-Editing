const fs=require('fs'),path=require('path');const W=__dirname,R=path.resolve(W,'../../../..'),read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const name=process.argv[2],ids=process.argv.slice(3);if(!name||!ids.length)throw Error('repair-name scene-id ... required');
const m=read(path.join(W,'voice.manifest.json')),s=read(path.join(W,'narration.tts.ko.json'));s.scenes=s.scenes.filter(s=>ids.includes(s.id));if(s.scenes.length!==ids.length)throw Error('Unknown scenes');
const script=path.join(W,name+'.ko.json');fs.writeFileSync(script,JSON.stringify(s,null,2)+'\n');m.paths.script=path.relative(R,script).replaceAll('\\','/');m.tts.filenameStem='blank-project-coding-original-restored-v2-'+name;m.paths.scriptEn=null;
fs.writeFileSync(path.join(W,name+'.manifest.json'),JSON.stringify(m,null,2)+'\n');console.log('Isolated same-text repair '+ids.join(', '));
