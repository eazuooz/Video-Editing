const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
(async()=>{
  const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
  try{
    const p=await browser.newPage();await p.goto('http://127.0.0.1:9210/render-worker.html');
    const result=await p.evaluate(async()=>{
      const {default:project}=await import('/src/projects/small-window-game-design/project.ts?project');
      const audio=new Audio(project.audio);audio.preload='auto';await new Promise((resolve,reject)=>{audio.onloadedmetadata=resolve;audio.onerror=reject;});
      const context=new AudioContext();await context.resume();const node=context.createMediaElementSource(audio),analyser=context.createAnalyser();node.connect(analyser);analyser.connect(context.destination);const samples=[];
      for(const time of [1,7,67,97,137,172,214]){
        audio.currentTime=time;await audio.play();await new Promise(resolve=>setTimeout(resolve,300));
        const data=new Float32Array(analyser.fftSize);analyser.getFloatTimeDomainData(data);const rms=Math.sqrt(data.reduce((n,v)=>n+v*v,0)/data.length);samples.push({seek:time,currentTime:audio.currentTime,paused:audio.paused,rms});audio.pause();
      }
      await context.close();return {projectLoaded:!!project,sceneCount:project.scenes?.length,audioDuration:audio.duration,samples};
    });
    if(result.sceneCount!==7||Math.abs(result.audioDuration-222.466667)>.05||result.samples.some(s=>s.paused||s.currentTime<=s.seek||s.rms<=0))throw Error(JSON.stringify(result));
    fs.writeFileSync(path.resolve(__dirname,'../../projects/small-window-game-design/production/intro-v3/editor-playback-qa.json'),JSON.stringify(result,null,2));console.log(result);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
