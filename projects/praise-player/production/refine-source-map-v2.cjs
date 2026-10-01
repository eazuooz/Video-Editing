// Findings from direct inspection of 37 dense source contact sheets.
const fs=require('node:fs'),crypto=require('node:crypto');
const file='projects/praise-player/production/final-v2/example-map.json';
const m=JSON.parse(fs.readFileSync(file,'utf8'));
const repairs=[
 ['sports',90.7,106.3,90.7,105.8,'Exclude full Soccer title'],
 ['hifi-deep-dive',65.3,82.9,65.3,82,'Exclude crowd/story shot without HUD'],
 ['ringfit',343.5,350.6,343.85,350.3,'Exclude static controller transition and next menu'],
 ['sports',270.2,274.7,271.35,274.7,'Start at Win/result, omit customization'],
 ['hifi-deep-dive',11.3,22.5,11.3,22.35,'Omit full explanatory rhythm chart'],
 ['hifi-deep-dive',173.8,189.8,173.8,188.1,'Omit guitar story cutscene'],
 ['hifi-deep-dive',109.7,123.3,111,123.3,'Omit opening dialogue'],
 ['hifi-deep-dive',139,154.5,139,152.9,'Omit character story close-up'],
 ['hifi-remix',86,94.4,86,89.8,'Omit story/cinematic montage'],
 ['hifi-deep-dive',267.1,277.5,271,277.5,'Start at controllable boss combat; retain native QTE'],
 ['hifi-arcade',10,22.3,11.4,22.3,'Omit BPM RUSH full title'],
 ['sports',131,145.4,131,144.05,'Omit Chambara full title'],
 ['hifi-deep-dive',155,158.9,155.9,158.65,'Omit story transition at both boundaries'],
 ['hifi-deep-dive',98.6,106.2,98.9,106.2,'Omit blurred promotional transition'],
 ['hifi-arcade',26.1,31.1,26.1,30.4,'Keep native ability menu; omit new-mode full title'],
 ['hifi-arcade',36.5,48.8,36.5,45.8,'Omit full unlock-rewards promotional title'],
 ['ringfit',248,251.4,248,250.1,'Omit full-room exercise shot'],
 ['hifi-deep-dive',253.3,262.2,256.1,260.45,'Omit character/boss story montage; keep traversal'],
 ['hifi-deep-dive',236.3,242.1,236.3,240.55,'Omit story team shot'],
 ['hifi-deep-dive',163,166.8,163,164.95,'Omit celebratory story close-up'],
 ['hifi-arcade',66.1,74.5,66.1,73.45,'Omit final cat story shot'],
 ['ringfit',82.3,86.6,82.3,84.4,'Keep real traversal, omit exercise-only room'],
 ['hifi-deep-dive',49.2,58.2,49.2,55.95,'Omit robot/character story dialogue'],
 ['ringfit',290,313.8,290.3,313.3,'Omit MINIGAMES title and blank tail']
];
for(const [key,a,b,x,y,reason] of repairs){
 const matches=m.chapters.flatMap(c=>c.groups.flatMap(g=>g.windows)).filter(w=>w[0]===key&&w[1]===a&&w[2]===b);
 if(matches.length!==1)throw Error('Repair must match exactly once: '+key+' '+a);
 matches[0][1]=x;matches[0][2]=y;
}
for(const c of m.chapters)for(const g of c.groups)for(const [k,a,b] of g.windows){
 if((m.originalExclusionRanges[k]||[]).some(([x,y])=>a<y&&b>x))throw Error('Original excerpt reused');
}
for(const s of Object.values(m.sources))s.status='direct-action-windows-reviewed-public-rights-pending';
fs.writeFileSync(file,JSON.stringify(m,null,2)+'\n');
fs.writeFileSync('projects/praise-player/production/final-v2/source-boundary-repairs.json',JSON.stringify({reviewedAt:new Date().toISOString(),densePages:37,denseSamples:877,repairs,mapSha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),note:'In-game results, settings/ability menus, native button timing and input demonstrations remain actual game/development footage; full promotional titles, story cutscenes and isolated exercise-room shots are excluded.'},null,2)+'\n');
console.log('24 directly observed boundary repairs; all original source intervals remain excluded.');
