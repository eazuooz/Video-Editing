// Directly reviewed source ranges: exclude full title cards, black introductions,
// isolated wand cards and reused action from different Noita trailers.
const fs=require('node:fs'),path=require('node:path');
const file=path.join(__dirname,'write-example-map-v2.cjs');
let s=fs.readFileSync(file,'utf8');
const changes=[
 ["[['breach',5,17.5],['breach-squad-arachnophile-combo',.05,7.45]]","[['breach',10,17.5],['breach-squad-arachnophile-combo',.05,7.45]]"],
 ["[['noita2',.15,9.85],['noita1',34.6,44.8]]","[['noita2',1.5,16.7]]"],
 ["[['noita3',35.0,46.9],['noita1',10.2,19.9]]","[['noita3',34,47.7],['noita3',21,25.2]]"],
 ["[['noita1',60.2,68.7],['noita2',19.9,26.9]]","[['noita2',19.9,28.9],['noita3',26.5,32.3]]"],
 ["[['ftl',.15,18.9]]","[['ftl',1.5,18.9]]"],
 ["[['noita3',47.1,60.9],['noita1',45.0,55.4]]","[['noita2',29.5,41.5],['noita3',50,56.3]]"],
 ["[['ftl',19.0,40.0]]","[['ftl',19,35]]"],
 ["[['breach-squad-misteaters-combo',.05,11.1],['breach',17.6,28.8]]","[['breach-squad-misteaters-combo',.05,11.1],['breach',17.6,26.9]]"],
 ["[['ftl',50.1,59.7],['ftl',64.6,74.9]]","[['ftl',52.5,57.8],['ftl',64.6,73]]"],
 ["[['noita3',61.1,74.4],['noita2',44.3,54.0]]","[['noita2',41.7,54],['noita3',57,63.9]]"],
 ["[['breach-squad-heatsinkers-combo',.05,8.95],['breach',39.7,50.5]]","[['breach-squad-heatsinkers-combo',.05,8.95],['breach',42,50.5]]"],
 ["[['noita1',80.1,89.4],['noita3',74.6,85.0]]","[['noita3',64,70],['noita3',77,86.8],['noita2',54.1,57.7]]"],
 ["[['ftl',59.8,64.5],['ftl',40.1,44.0]]","[['ftl',59.8,64.5]]"],
 ["[['noita1',94.5,99.7],['breach-weapon-bounceshot',.05,5.15]]","[['noita3',95,102.5],['breach-weapon-bounceshot',.05,5.15]]"],
 ["[['breach',50.6,55.3],['breach-weapon-bounceshot',.05,5.15],['breach-squad-heatsinkers-combo',.05,8.95]]","[['breach',50.6,54],['breach-squad-heatsinkers-combo',.05,8.95],['breach-squad-cataclysm-combo',.05,10.25]]"],
 ["[['noita1',.2,5.0],['noita3',20.1,29.7]]","[['noita3',12,19]]"],
 ["[['ftl',75.0,81.5],['ftl',.15,44.0],['ftl',50.1,59.7],['ftl',64.6,74.9]]","[['ftl',1.5,35],['ftl',52.5,57.8],['ftl',64.6,73]]"],
 ["[['breach-squad-misteaters-combo',.05,16.2],['breach-squad-bombermechs-combo',.05,19.7],['breach',5,28.8],['noita3',20.1,29.7]]","[['breach-squad-misteaters-combo',.05,16.2],['breach-squad-bombermechs-combo',.05,19.7],['breach',10,26.9],['breach',42,54],['breach-enemy-combo',.05,3.7],['breach-combat-volcanofall',0,3.02],['ftl',1.5,35],['ftl',52.5,57.8],['ftl',64.6,73]]"],
];
for(const [from,to] of changes){if(!s.includes(from))throw Error('Already applied or missing source marker: '+from);s=s.replace(from,to);}
fs.writeFileSync(file,s);
console.log('Reviewed windows saved in editable source mapper; exact nonoverlap allocation follows accepted speech.');
