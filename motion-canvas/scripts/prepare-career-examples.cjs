// Reproducible effects from the same actual input/state transitions as the prototype.
const fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'motion-canvas/src/projects/game-dev-career');
async function main(){
 const {exampleEvents,initialState,openChest,replay}=await import(pathToFileURL(path.join(base,'prototype.ts')));
 const tests=[];
 for(const [name,state,expected] of [['normal',initialState(),1],['no-key',{...initialState(),keys:0},0],['full',{...initialState(),items:[1,2,3,4]},4]]){
  const first=openChest(state),second=openChest(first);if(second.items.length!==expected||first.items.length!==second.items.length)throw Error('Prototype test failed '+name);
  tests.push({name,first,second});
 }
 const out=path.join(base,'assets/example-audio');fs.mkdirSync(out,{recursive:true});
 const seconds=require(path.join(root,'projects/game-dev-career/project.json')).editing.exampleSeconds,rate=48000,frames=Math.round(seconds*rate),reports=[];
 for(const [index,events] of Object.entries(exampleEvents)){
  const sound=new Float32Array(frames);
  for(const [at,action] of events){
   const before=replay(+index,at-.001),after=replay(+index,at);
   const success=after.items.length>before.items.length&&action==='open';
   const freq=success?660:action==='open'?170:440,duration=success?.42:.12;
   for(let i=0;i<Math.round(duration*rate);i++){
    const n=Math.round(at*rate)+i;if(n>=frames)break;const t=i/rate,envelope=Math.min(1,t/.012)*Math.exp(-t*(success?9:24));
    sound[n]+=.13*envelope*(Math.sin(2*Math.PI*freq*t)+.25*Math.sin(2*Math.PI*freq*1.5*t));
   }
  }
  const data=Buffer.alloc(44+frames*4);data.write('RIFF');data.writeUInt32LE(data.length-8,4);data.write('WAVEfmt ',8);data.writeUInt32LE(16,16);data.writeUInt16LE(1,20);data.writeUInt16LE(2,22);data.writeUInt32LE(rate,24);data.writeUInt32LE(rate*4,28);data.writeUInt16LE(4,32);data.writeUInt16LE(16,34);data.write('data',36);data.writeUInt32LE(frames*4,40);
  sound.forEach((v,i)=>{const q=Math.round(Math.max(-1,Math.min(1,v))*32767);data.writeInt16LE(q,44+i*4);data.writeInt16LE(q,46+i*4);});
  const id=String(+index+1).padStart(2,'0');fs.writeFileSync(path.join(out,id+'.wav'),data);reports.push({scene:id,events,duration:seconds,kind:'original-prototype-effects'});
 }
 fs.writeFileSync(path.join(root,'projects/game-dev-career/production/prototype-tests.json'),JSON.stringify({tests,sources:reports},null,2));console.log('Prototype tests passed; '+reports.length+' original effect tracks.');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
