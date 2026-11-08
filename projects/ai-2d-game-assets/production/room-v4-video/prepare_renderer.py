from pathlib import Path
import json
H=Path(__file__).resolve().parent;P=H.parents[1];V3=H.parent/'room-v3'
s=(V3/'render-scenes.cjs').read_text('utf8').replace('production/local/room-v3','production/local/room-v4-video').replace('ai-2d-room-v3/video','ai-2d-room-v4-video/video')
s=s.replace("SITE=path.join(R,'sites/yamyam-cartographers-room/dist')", "SITE='C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/site-snapshot'")
s=s.replace("const replacements=['17','18','19','22','26','28'];", "const replacements=JSON.parse(fs.readFileSync(path.join(H,'revision-plan.json'))).replaceVisualIds;")
s=s.replace("const selectedRows=rows.filter(s=>!/^\\d+$/.test(s.id)||replacements.includes(s.id));", "const selectedRows=rows.filter(s=>replacements.includes(s.id)||s.id==='W36');")
s=s.replace("require('../room-v2/game-runtime.cjs')", "require('./game-runtime.cjs')")
# Preserve actual earlier tool-output inputs, rather than inventing new executions.
s=s.replace("production/local/room-v4-video/pixelbolt-ledger-large", "production/local/room-v3/pixelbolt-ledger-large")
s=s.replace("production/local/room-v4-video/pixel-clean", "production/local/room-v3/pixel-clean")
s=s.replace("const radio=path.join(P,'production/local/room-v4-video/radio-ui.png');", "const radio=path.join(P,'production/local/room-v4-video/browser-evidence/radio-playing-fhd.png');")
s=s.replace("for(let [n,file]of Object.entries(f))images[n]=await loadImage(file);", "Object.assign(f,{roomFinal:path.join(SITE,'assets/room-background-v4.png'),deskFinal:path.join(SITE,'assets/desk-v4.png'),roomPrior:path.join(SITE,'assets/room.png')});for(const [key,name] of [['radioNext','radio-next-native.jpg'],['radioPlaylist','radio-playlist-native.jpg'],['memoSaved','memo-saved-native.jpg']]){const file=path.join(L,'browser-evidence',name);if(fs.existsSync(file))f[key]=file;}for(let [n,file]of Object.entries(f))images[n]=await loadImage(file);")
s=s.replace("function eventSetup(id){runtime.game.reset();events=[];eventIndex=0;", "function eventSetup(id){runtime.game.reset();events=[];eventIndex=0;if(['01','30','02','16','W36'].includes(id)){runtime.game.capture('write',0);}")
s=s.replace("if(id==='V33')events=[{t:Math.max(0,cue(id,'접근해서',10)-5.5),a:'write'}];", "if(id==='V33'){events=[{t:Math.max(0,cue(id,'접근해서',10)-4),a:'write'}];}")
# Correct the current stool crop and target positions; old crop was stretched.
s=s.replace("gameView(820,230,940,640,[220,70,206,140]);", "gameView(820,230,960,640,[276,80,150,100]);")
s=s.replace("820+(369-220)/206*940,y=230+(142-70)/140*640", "820+(369-276)/150*960,y=230+(142-80)/100*640")
s=s.replace("230+(172-70)/140*640", "230+(174-80)/100*640")
s=s.replace("gameView(840,220,960,650,[220,70,206,140]);", "gameView(840,220,960,640,[276,80,150,100]);")
s=s.replace("840+(369-220)/206*960,y=220+(142-70)/140*650", "840+(369-276)/150*960,y=220+(142-80)/100*640")
# Read unchanged ASR timing from previous revision when the one-new-passage cache lacks it.
s=s.replace("if(!fs.existsSync(f))f=path.join(P,'production/local/room-v2/asr',id+'.json');", "if(!fs.existsSync(f))f=path.join(P,'production/local/room-v3/asr',id+'.json');if(!fs.existsSync(f))f=path.join(P,'production/local/room-v2/asr',id+'.json');")
# Preview just enough 60Hz state advancement for verified samples; never render a stale UI by default.
s=s.replace("const mode=process.argv[2]||'preview'", "const mode=process.argv[2]||'preview'")
(H/'render-scenes.cjs').write_text(s,'utf8')
runtime=(H.parent/'room-v2/game-runtime.cjs').read_text('utf8')
runtime=runtime.replace("path.resolve(__dirname,'../../../..','sites/yamyam-cartographers-room/dist')", "'C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/site-snapshot'")
runtime=runtime.replace("window:{addEventListener(){}}", "CustomEvent:class{constructor(type,options){this.type=type;this.detail=options?.detail}},window:{addEventListener(){},dispatchEvent(){}}")
(H/'game-runtime.cjs').write_text(runtime,'utf8')
print('Prepared latest-site-only renderer and isolated runtime')
