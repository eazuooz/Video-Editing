const fs=require('node:fs'),f='projects/responsive-game-feedback/production/final-v2/example-map.json',m=JSON.parse(fs.readFileSync(f,'utf8'));
if(m.directBoundaryRefinement)throw Error('Already refined');
m.chapters[0].groups[1].windows=[['oni',458,474]];
m.chapters[1].groups[2].claim='Native material/tool/status information plus continuing work; do not claim completed production or an unobserved literal rejection';
m.chapters[2].groups[2].windows=[['oni',1071,1088]];
m.directBoundaryRefinement={reviewedAt:new Date().toISOString(),proof:'11 exact-window sheets255 samples directly inspected, plus45 native boundary samples',notes:['Exclude new gas-overlay transition479 from object-information group','Job grid starts1071; preceding oxygen-overlay frames are not menu evidence','Print cut is anchored to1535 start so selection and confirmation remain visible','Native red X is Cancel Tool; no invalid-placement assertion','Microbe Musher states insufficient resources; world status/material panels illustrate what to inspect, not a fictitious completed item','All black frames/PAX notice/developer Cell Painter excluded']};fs.writeFileSync(f,JSON.stringify(m,null,2)+'\n');
