const fs=require('fs'),path=require('path');
const {createCanvas,GlobalFonts}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
const P=path.resolve(__dirname,'..'),L=path.join(__dirname,'local');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf','YamyamCaption');
const c=createCanvas(1920,1080).getContext('2d');c.font='48px YamyamCaption';
const cues=JSON.parse(fs.readFileSync(path.join(L,'captions.json'))),rows=cues.map(x=>({index:x.index,scene:x.scene,text:x.ko,width:c.measureText(x.ko).width+24}));
const overflow=rows.filter(x=>x.width>1760);if(overflow.length)throw Error(JSON.stringify(overflow));
const report={font:'Malgun Gothic Bold',px:48,cues:rows.length,maximumBoxWidth:Math.max(...rows.map(x=>x.width)),allowedWidth:1760,overflow:[],shortTailPolicy:'Join final predicates up to7characters where total<=34characters; preserve existing ASR anchors and translations.'};
fs.writeFileSync(path.join(P,'production/caption-width-qa.json'),JSON.stringify(report,null,2));console.log(report);
