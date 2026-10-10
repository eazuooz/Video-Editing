const fs=require('node:fs'),path=require('node:path');
const sources=[
{id:'vnpUykzHpv8',slug:'nvrtx-showcase-2021',primary:'https://developer.nvidia.com/blog/try-nvidia-game-development-sdks-in-the-interactive-rtx-technology-showcase/',chapter:'13b/15a/15b UE4.26 actual SDK toggles; separate DDGI/direct light/reflection inputs'},
{id:'0X1RtXCvPFQ',slug:'dlss2-overview-2020',primary:'https://www.nvidia.com/en-us/geforce/news/nvidia-dlss-2-0-a-big-leap-in-ai-rendering/',chapter:'14b actual game temporal image comparisons; exclude product cards and diagrams from actual quota'},
{id:'via-LSKo_q4',slug:'deliver-moon-dlss2-2020',primary:'https://www.nvidia.com/en-us/geforce/news/nvidia-dlss-2-0-a-big-leap-in-ai-rendering/',chapter:'14b native lower-resolution reconstruction comparison'},
{id:'1fSx2VBHKz0',slug:'wolfenstein-dlss2-2020',primary:'https://www.nvidia.com/en-us/geforce/news/nvidia-dlss-2-0-a-big-leap-in-ai-rendering/',chapter:'14a/14b ray effects and temporal reconstruction, source version2020'},
{id:'ycNk1nj0KsQ',slug:'rtxgi-ue5-preview2-2022',primary:'https://developer.nvidia.com/blog/shaping-the-future-of-graphics-with-nvidia-technologies-in-unreal-engine-5/',chapter:'15a DDGI actual volume placement/debug controls; exclude installation/file dialogs and static explanatory slides'},
{id:'49rBP1DoOwo',slug:'hardware-rt-ue5-preview2-2022',primary:'https://developer.nvidia.com/blog/shaping-the-future-of-graphics-with-nvidia-technologies-in-unreal-engine-5/',chapter:'13a/13b actual engine RT enable/debug settings; exclude installation and prose cards'},
{id:'Xk15X9ab7iw',slug:'dlss-ue5-preview2-2022',primary:'https://developer.nvidia.com/blog/shaping-the-future-of-graphics-with-nvidia-technologies-in-unreal-engine-5/',chapter:'14b actual viewport reconstruction setting comparison; DLSS/DLAA/NIS distinct'}
];
const src=fs.readFileSync(path.join(__dirname,'acquire-episode03-native-v3.cjs'),'utf8');
const script=src.replace("local/episode03-native-v3'","local/episode03-native-v4'").replace(/const sources=\[[\s\S]*?\];/,`const sources=${JSON.stringify(sources,null,2)};`);
if(script===src||script.includes("local/episode03-native-v3'"))throw Error('Scoped copy failed');
fs.writeFileSync(path.join(__dirname,'acquire-episode03-native-v4.cjs'),script);
console.log(JSON.stringify({preparedSources:sources.length,mediaProduced:false}));
