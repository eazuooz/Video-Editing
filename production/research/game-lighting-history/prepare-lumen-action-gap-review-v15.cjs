const fs=require('node:fs'),path=require('node:path');
const target=path.join(__dirname,'extract-native-action-support-v15.cjs');
if(fs.existsSync(target))throw Error('Preserve prepared extraction');
let s=fs.readFileSync(path.join(__dirname,'extract-native-action-support-v14.cjs'),'utf8').replaceAll('v14','v15').replaceAll('ddgi-action-gaps','lumen-action-gaps');
const old="[['escape-naraka-rtxgi-2021',5,38,null],['rtxgi-ue5-preview2-2022',313,318,null]]";
if(!s.includes(old))throw Error('Expected source definitions missing');
s=s.replace(old,"[['lumen-content-examples-2021',181,203,'crop=1280:720:0:20'],['lumen-content-examples-2021',284,315,'crop=1280:720:0:20'],['lumen-content-examples-2021',336,355,'crop=1280:720:0:20'],['lumen-content-examples-2021',529,555,'crop=1280:720:0:20'],['lumen-content-examples-2021',602,625,'crop=1280:720:0:20']]");
fs.writeFileSync(target,s);console.log('Prepared121 new temporal samples in five unreviewed Lumen action gaps; prior samples/media preserved. Extraction/direct review still pending.');
