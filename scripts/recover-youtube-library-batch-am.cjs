const fs=require('node:fs'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),base=path.join(root,'output/youtube-library-refresh/v2');
const sourceRoot='C:/Users/eazuo/.codex/generated_images/01a0f353-11d3-7000-a47a-38e0f33ddae7';
// Recovered after reboot by viewing every PNG and matching its exact headline
// and planned distinctive scene, not by guessing completion from timestamps.
const matches=[
 ['l8JRpRMAcnY','exec-9fe7d2bf-7868-40e4-bc92-4b9420afbc9a.png'],
 ['AmY1VGBzO1g','exec-40fb9885-98be-4426-8f88-2a994612fbeb.png'],
 ['ZLA_ldmrzW0','exec-053fcdd6-57c7-4fe3-9b60-f47dee414224.png'],
 ['upO4CW3INvE','exec-cb01908c-f104-48f3-ac1c-f3fe3079bd77.png'],
 ['QHFhEYo4G-o','exec-aa9da319-0540-482f-b5c8-5c6b94082c75.png'],
 ['8jba9-Gops0','exec-6ea2dabd-e323-4bae-9b9f-71f2288600b9.png'],
 ['SjHe4n6O_1E','exec-e46046e3-b7ab-4f2f-b6c8-f1d143b23e43.png'],
 ['aWX4j548emY','exec-93fc175f-0d17-4b1a-9856-073adfc93874.png']
];
for(const [id,name]of matches){
 if(fs.existsSync(path.join(base,'raw',id+'.json')))throw new Error('Already accepted '+id);
 const source=path.join(sourceRoot,name);
 const result=spawnSync(process.execPath,[path.join(root,'scripts/accept-youtube-library-v2.cjs'),id,source],{encoding:'utf8',windowsHide:true});
 if(result.status!==0)throw new Error(result.stderr||result.stdout);
 const draft=path.join(base,'drafts',id);fs.mkdirSync(draft,{recursive:true});
 for(const [ext,dest]of[['png','initial.png'],['json','initial.json'],['prompt.txt','initial.prompt.txt']]) fs.copyFileSync(path.join(base,'raw',id+'.'+ext),path.join(draft,dest),fs.constants.COPYFILE_EXCL);
 console.log(result.stdout.trim());
}
