// Pure offscreen artifact rendering. No browser, page automation or file URL access.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {createCanvas,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
const base=path.resolve(__dirname,'..'),game=require('../playtest/race.cjs');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');
const output=path.join(__dirname,'playtest-preview');fs.mkdirSync(output,{recursive:true});
for(const [name,seconds,follow,markers] of [['opening',0,false,true],['crossing',7,true,true],['route',17,true,true],['plain',7,true,false],['finish',40,true,true]]){
  const canvas=createCanvas(1920,1080),stubs=new Map();
  const context={Cloudpost:game,performance:{now:()=>0},URLSearchParams,location:{search:''},window:{},structuredClone,requestAnimationFrame:()=>{},addEventListener:()=>{},document:{body:{classList:{add:()=>{}}},querySelector:s=>{if(s==='canvas')return canvas;if(!stubs.has(s))stubs.set(s,{setAttribute:()=>{},textContent:''});return stubs.get(s);},querySelectorAll:()=>[]}};
  vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(base,'playtest/view.js'),'utf8'),context);
  vm.runInContext(`game.act(state,'select','moon');game.act(state,'camera','${follow?'follow':'overview'}');game.act(state,'markers',${markers});${seconds?"game.act(state,'start');":''}for(let frameIndex=0;frameIndex<${seconds*60};frameIndex++)game.tick(state,1/60);scale=${follow?1:.245};camX=${follow?"Math.max(-50,Math.min(game.finish-1300,state.racers[2].x-470))":"-70"};world();`,context);
  fs.writeFileSync(path.join(output,name+'.png'),canvas.toBuffer('image/png'));
}
console.log('Five offscreen canvas previews rendered; browser-input QA is not implied.');
