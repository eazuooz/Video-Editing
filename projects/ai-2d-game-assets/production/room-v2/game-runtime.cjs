// Execute the deployed game source, not an imitation of another application's UI.
const fs=require('fs'),path=require('path'),vm=require('vm');
const {createCanvas,Image}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
module.exports=async function runtime(){
 const root=path.resolve(__dirname,'../../../..','sites/yamyam-cartographers-room/dist'),canvas=createCanvas(1920,1080),els=new Map();
 function el(id){if(els.has(id))return els.get(id);const e={style:{},dataset:{},textContent:'',className:'',open:false,classList:{add(){},remove(){},toggle(){}},children:[],addEventListener(n,fn){this['on'+n]=fn},setAttribute(){},append(v){this.children.push(v)},getBoundingClientRect(){return{x:0,y:0,width:1920,height:1080}},remove(){},showModal(){this.open=true},close(){this.open=false},closest(){return this}};els.set(id,e);return e;}
 Object.assign(canvas,{addEventListener(){},setAttribute(){},style:{},getBoundingClientRect(){return{x:0,y:0,width:1920,height:1080}}});els.set('#room',canvas);
 class LocalImage extends Image{constructor(){super();this.ready=new Promise((resolve,reject)=>{this.onload=resolve;this.onerror=reject})}set src(v){super.src=fs.readFileSync(path.join(root,v))}decode(){return this.ready}}
 const ctx={console,URLSearchParams,Image:LocalImage,Math,Set,Promise,performance:{now:()=>0},location:{search:'?capture&qa'},localStorage:{getItem:()=>null,setItem(){}},document:{querySelector:el,querySelectorAll:()=>[],body:el('body'),createElement:tag=>el(tag+Math.random())},window:{addEventListener(){}},requestAnimationFrame(){},fetch:async p=>({ok:fs.existsSync(path.join(root,p)),json:async()=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'))})};
 vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(root,'game.js'),'utf8'),ctx,{filename:'deployed-game.js'});
 for(let i=0;i<400&&!ctx.window.roomGame?.ready;i++)await new Promise(r=>setTimeout(r,25));
 if(!ctx.window.roomGame?.ready)throw Error('Room game failed to initialize');
 return {canvas,game:ctx.window.roomGame,source:path.join(root,'game.js')};
};
