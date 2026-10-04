const fs=require('fs'),path=require('path'),crypto=require('crypto');
const base=__dirname, target=path.join(base,'action-bank-v2.json');
if(fs.existsSync(target))throw Error('Preserve revised bank; do not rerun.');
const oldFile=path.join(base,'action-bank-v1.json');
const bank=JSON.parse(fs.readFileSync(oldFile,'utf8'));
const removed={
 'ranch-06':'Non-game animation and unrelated battle interrupt the proposed ranch example.',
 'coop-03':'Most of the interval is scenery/idle movement; the tail enters an office interview. It is not necessary to the reward claim.',
 'coop-04':'Developer-name overlay and development telemetry compromise the station example; cleaner placement actions exist.',
 'coop-05':'Brief library menu with development telemetry then an office interview; hold rather than claim quota.',
 'shatter-05':'Movement near a time mechanism does not substantiate the proposed reward-production claim strongly enough.'
};
bank.rejectedCuts=bank.cuts.filter(c=>removed[c.id]).map(c=>({...c,rejectionReason:removed[c.id]}));
bank.cuts=bank.cuts.filter(c=>!removed[c.id]);
const revised={
 'ammo-15':[83,89,'End before the observed logo transition.'],
 'shatter-02':[21,25,'End before the observed dialogue/scene tail.'],
 'shatter-04':[40,42.5,'End before THE TOWER title. Ingredient warning is not proof of a paid unlock.'],
 'shatter-07':[66,73,'Start after the area title; verify exact fade in native frames.'],
 'coop-01':[75,83,'End before the office cut.'],
 'coop-02':[88,98,'Start after the developer-name fade; native boundary remains to verify.'],
 'coop-06':[150,152,'End before date text.'],
 'coop-07':[155,163,'End before logo.'],
 'base-01':[140,149,'Include adjacent distinct station placements, not the later feature card.'],
 'base-02':[149,151.5,'Stop before REBUILD THE WORLD title.'],
 'ranch-02':[21,34,'Stop before the dialogue-only tail.']
};
for(const c of bank.cuts){
 if(revised[c.id]){const [a,z,why]=revised[c.id]; c.previousInterval={in:c.sourceInSeconds,out:c.sourceOutSeconds};c.sourceInSeconds=a;c.sourceOutSeconds=z;c.durationSeconds=z-a;c.revisionReason=why;}
 if(c.id==='shatter-04')c.visibleAction='The potion tree changes selected entries. Medium Healing Potion displays0/1 Weeping Velvetcap and an ingredient warning before a separately edited Completed view; do not infer a normal uninterrupted paid unlock.';
 if(c.id==='ammo-10')c.visibleAction='Ground-effect combat and separate Ground Research/ammunition UI changes. The research footer says required ingredients are missing; the promotional montage is not a continuous earned unlock.';
 if(c.id==='ammo-13')c.visibleAction='A water item and Lightning research tree/UPGRADE selection appear; the interface also shows missing-ingredient text, so successful payment is not established.';
 c.nativeBoundaryReview='pending-revised-bank';c.finalApproved=false;
}
const add=(id,a,z,group,visibleAction)=>bank.cuts.push({id,sourceId:'n8wJDqZanbM',sourceInSeconds:a,sourceOutSeconds:z,durationSeconds:z-a,group,visibleAction,focus:bank.groups.find(g=>g.key===group).focus,speed:1,sourceAudio:'exclude-all',classification:'candidate-existing-game-action',nativeBoundaryReview:'pending-new-bank',fixedCaptionSafety:'pending',finalApproved:false});
add('overview-01',104,111,'conditions','The character moves to an object/pickup near a portal, then continues; stop before the resources title. Acquisition interaction is visible, but a precise reward condition is not claimed.');
add('overview-02',113,120,'limits','Elemental attacks and ground effects damage enemies, followed by visible material pickups in separate encounters. This motivates combination/availability test questions, not a controlled damage comparison.');
add('overview-03',125,131,'functions','Equipment, Life/Repair/Utility ammunition and crafting selections change in the actual interface. A readable life-bullet description motivates separating direct damage from healing roles; exact text needs full-size verification.');
add('overview-04',131,137,'limits','Actual attacks with different projectile and area effects, ending before the sanctuary feature card. Visible effects provide our proposed interaction-testing example.');
add('overview-05',155,160,'access','A map is revealed and floor/world cells are placed as the character moves across the resulting space. Describe the visible route-building action without inventing its acquisition rule.');
add('overview-06',160,168,'review','Different elemental combat actions in separate encounters provide a catalogue test question: what changes in the action, which target/context is tested? No measured balance defect is claimed.');
add('overview-07',173,176,'review','The character moves back through the base portal; stop before the logo transition. This is a short return-to-production-context bridge, not idle filler.');
for(const c of bank.cuts){const fps=bank.sources.find(s=>s.videoId===c.sourceId).fps; if(Math.abs(c.sourceInSeconds*fps-Math.round(c.sourceInSeconds*fps))>1e-6||Math.abs(c.sourceOutSeconds*fps-Math.round(c.sourceOutSeconds*fps))>1e-6)throw Error('Not source frame aligned');}
for(const s of bank.sources){const cuts=bank.cuts.filter(c=>c.sourceId===s.videoId).sort((a,b)=>a.sourceInSeconds-b.sourceInSeconds);for(let i=1;i<cuts.length;i++)if(cuts[i].sourceInSeconds<cuts[i-1].sourceOutSeconds)throw Error('Overlapping raw interval: '+s.videoId);}
bank.previousBank={path:'action-bank-v1.json',sha256:crypto.createHash('sha256').update(fs.readFileSync(oldFile)).digest('hex'),cutCount:38,candidateSeconds:220};
bank.preparedAt=new Date().toISOString();bank.status='revised-candidate-bank-awaiting-dense-native-and-claim-review';bank.uniqueCandidateSeconds=bank.cuts.reduce((n,c)=>n+c.durationSeconds,0);bank.cutCount=bank.cuts.length;bank.sourceIntervalsApproved=false;
bank.boundaries.push('Missing-ingredient warnings observed in the official promotional research shots prevent a claim that the footage demonstrates successful normal payment/unlock.');
fs.writeFileSync(target,JSON.stringify(bank,null,2)+'\n');
process.stdout.write(JSON.stringify({cutCount:bank.cutCount,candidateSeconds:bank.uniqueCandidateSeconds,rejected:bank.rejectedCuts.map(c=>c.id),file:target})+'\n');
