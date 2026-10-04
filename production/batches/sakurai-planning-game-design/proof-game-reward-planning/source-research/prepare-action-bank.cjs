// Discovery-reviewed candidate actions. This does not authorize final cuts or narration timing.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const base = __dirname;
const target = path.join(base, 'action-bank-v1.json');
if (fs.existsSync(target)) throw Error('Preserve existing research bank; write a reviewed revision separately.');
const states = ['acquisition.json', 'acquisition-additional.json', 'acquisition-targeted.json'].map(f => JSON.parse(fs.readFileSync(path.join(base, f), 'utf8')));
const sources = states.flatMap(s => s.results);
if (sources.length !== 7 || sources.some(s => s.fullDecode.exitCode !== 0 || s.fullDecode.diagnostics !== 0)) throw Error('Seven actually decoded official sources required.');
const groups = [
  {key:'functions', claim:'List the player action each reward changes before treating every reward as a numerical power increase.', diagram:'Reward catalogue: combat effect / route capability / base production.', focus:'Freeze and shatter effects differ from making a crossing possible; identify the action, not an assumed damage multiplier.', insert:'Overview and the first detailed action example, then explanation01.'},
  {key:'conditions', claim:'A reward plan needs the prerequisites, materials, output and later dependency together.', diagram:'Requirement → unlock/research → craft → usable action; unobserved conditions marked unknown.', focus:'Watch material collection and changes in the actual research/crafting interface. These separate edits do not establish one continuous earned-unlock playthrough.', insert:'Between explanation01 and explanation02.'},
  {key:'limits', claim:'Set constraints on accumulation and combinations according to the intended play experience; universal stronger-is-better is not the goal.', diagram:'Proposed limits: context / combinations / availability / balance checks.', focus:'Several elemental effects and players share the same combat space. The balance checklist is our proposal, not a measured balance defect or competitive-game claim.', insert:'Between explanation02 and explanation03.'},
  {key:'access', claim:'Access, production and ways of moving can be planned as distinct reward roles; do not invent earned or cosmetic-only properties.', diagram:'Power / capability / production / presentation columns; verified role versus unshown acquisition condition.', focus:'Mounted movement, feeding/collection and animal variations are visible; their exact unlock rules and equal statistics are not shown.', insert:'Between explanation03 and explanation04.'},
  {key:'production', claim:'In-game material requirements and the developer work needed to build a reward are different budgets.', diagram:'Player costs versus art / animation / UI / effects / testing work; estimates labeled as planning.', focus:'New animals, stations, effects and library entries visibly need distinct presentation. No source reveals the developers internal cost or implementation.', insert:'Between explanation04 and explanation05.'},
  {key:'review', claim:'Review the catalogue for coverage, missing conditions and manageable production scope before adding more items.', diagram:'Catalogue row → prerequisite → changed action → required assets → test question.', focus:'Return to different visible functions and interactions; distinguish what the footage proves from the questions our plan still needs to answer.', insert:'Between explanation05 and the conclusion / explanation06.'},
];
const raw = [
  ['ammo-01','3nIAR1g8RAU',7,13,'functions','Projectiles visibly freeze an enemy, followed by a separate shattering-combat shot.'],
  ['ammo-02','3nIAR1g8RAU',13,16,'conditions','The player approaches a research station and its Frost research interface is opened.'],
  ['ammo-03','3nIAR1g8RAU',16,20,'conditions','A defeated eye-like enemy and material pickup transition are shown.'],
  ['ammo-04','3nIAR1g8RAU',20,24,'conditions','Ore/material and research/inventory views show different required components.'],
  ['ammo-05','3nIAR1g8RAU',24,29,'conditions','The source cuts among ammo description, research, fuel processing and powder selection.'],
  ['ammo-06','3nIAR1g8RAU',29,35,'functions','A character freezes and shatters enemies; no controlled before/after damage comparison.'],
  ['ammo-07','3nIAR1g8RAU',35,39,'functions','A character crosses a gap with a bright movement effect; inspect the exact transition before naming its mechanic.'],
  ['ammo-08','3nIAR1g8RAU',39,43,'conditions','Purple enemy combat is followed by a visible material pickup.'],
  ['ammo-09','3nIAR1g8RAU',43,49,'conditions','Ore, composter, teleport research, ammo selection and crafting are shown in successive short cuts.'],
  ['ammo-10','3nIAR1g8RAU',49,54,'conditions','A ground effect is followed by Ground Research changing to Completed and ammo selection.'],
  ['ammo-11','3nIAR1g8RAU',54,62,'functions','The character uses ground/movement effects to cross a gap.'],
  ['ammo-12','3nIAR1g8RAU',62,70,'limits','Water and electric combat effects and enemy/material actions occur in different encounters.'],
  ['ammo-13','3nIAR1g8RAU',70,75,'conditions','A water item and Lightning research interface change, including a research/upgrade selection.'],
  ['ammo-14','3nIAR1g8RAU',75,83,'limits','Electric splash and ice-related combat effects act around enemies.'],
  ['ammo-15','3nIAR1g8RAU',83,90,'review','Additional elemental interaction and gap-crossing actions end before the promotional card.'],
  ['shatter-01','xNUn4fn4br8',18,21,'review','A character moves among enemies in an exploration area.'],
  ['shatter-02','xNUn4fn4br8',21,26,'review','The character attacks and dodges an enemy area attack.'],
  ['shatter-03','xNUn4fn4br8',35,38,'production','A distinct enemy and attack animation appear in a fungal area.'],
  ['shatter-04','xNUn4fn4br8',40,43,'conditions','The potion research tree selects Medium Healing Potion and changes to Completed.'],
  ['shatter-05','xNUn4fn4br8',48,51,'production','The character moves through the tower near the time mechanism.'],
  ['shatter-06','xNUn4fn4br8',55,61,'production','Ice combat with different enemies and effects; different source encounters are not controlled comparisons.'],
  ['shatter-07','xNUn4fn4br8',65,73,'review','Different enemy attacks, dodging and elemental attacks appear in the desert area.'],
  ['shatter-08','xNUn4fn4br8',78,82,'limits','Combat continues around overlapping elemental hazards.'],
  ['coop-01','ZTV0rPQ0_ik',75,84,'limits','Several player characters and elemental effects share a combat area.'],
  ['coop-02','ZTV0rPQ0_ik',87,98,'limits','Co-op players use different attacks, defeat enemies and receive material pickups.'],
  ['coop-03','ZTV0rPQ0_ik',98,105,'review','An enemy fight is followed by a group moving through a snowy environment.'],
  ['coop-04','ZTV0rPQ0_ik',121,128,'production','Characters move between distinct crafting/research stations in the tower.'],
  ['coop-05','ZTV0rPQ0_ik',129,132,'production','The general library interface is opened and a book entry is selected.'],
  ['coop-06','ZTV0rPQ0_ik',150,153,'review','Character interaction and a pickup occur before the date overlay.'],
  ['coop-07','ZTV0rPQ0_ik',155,164,'limits','Snow, poison and other co-op attacks are shown before the logo end card.'],
  ['base-01','n8wJDqZanbM',140,147,'production','Different stations are placed and the tower floor expands; inspect internal feature-card boundaries.'],
  ['base-02','n8wJDqZanbM',149,152,'production','A research station appears and the player moves beside it.'],
  ['ranch-01','JziX-60OyCc',17,21,'access','An animal-selection/name interface changes before returning to the ranch.'],
  ['ranch-02','JziX-60OyCc',21,35,'access','The player interacts with cow/sheep animals and visible collection icons appear.'],
  ['ranch-03','JziX-60OyCc',38,44,'conditions','The source shows an animal-related cost interface and Feed Grass interaction.'],
  ['ranch-04','JziX-60OyCc',44,48,'access','The player moves while mounted on an animal.'],
  ['ranch-05','JziX-60OyCc',55,63,'access','Mounted movement and ranch interactions occur in separate shots.'],
  ['ranch-06','JziX-60OyCc',67,74,'production','Animal shelter and character/animal interactions show different visual assets and motions.'],
];
const cuts = raw.map(([id,sourceId,begin,end,group,action])=>({id,sourceId,sourceInSeconds:begin,sourceOutSeconds:end,durationSeconds:end-begin,group,visibleAction:action,focus:groups.find(g=>g.key===group).focus,speed:1,sourceAudio:'exclude-all',classification:'candidate-existing-game-action',nativeBoundaryReview:'pending',fixedCaptionSafety:'pending',finalApproved:false}));
for (const s of sources) {
  const ordered = cuts.filter(c=>c.sourceId===s.videoId).sort((a,b)=>a.sourceInSeconds-b.sourceInSeconds);
  for(let i=1;i<ordered.length;i++) if(ordered[i].sourceInSeconds < ordered[i-1].sourceOutSeconds) throw Error('Overlapping source actions');
}
const result={schemaVersion:1,preparedAt:new Date().toISOString(),status:'candidate-bank-awaiting-native-boundary-and-claim-review',sources:sources.map(s=>({videoId:s.videoId,title:s.title,channel:s.channel,uploadDate:s.uploadDate,localMediaPath:s.localMediaPath,fileBytes:s.fileBytes,fileSha256:s.fileSha256,fps:Number(s.streams.find(x=>x.codec_type==='video').r_frame_rate.split('/')[0])/Number(s.streams.find(x=>x.codec_type==='video').r_frame_rate.split('/')[1]),fullDecode:s.fullDecode})),groups,cuts,uniqueCandidateSeconds:cuts.reduce((n,c)=>n+c.durationSeconds,0),cutCount:cuts.length,boundaries:['Normal source speed only; no loops, artificial slow-down or idle filler.','Promotional text, edited montage, static interfaces, animation, presenter footage and faces are not automatically actual-action quota.','Separate shots are not one uninterrupted unlock playthrough. Only conditions actually readable on screen may be narrated as fact.','Balance, catalogue structure and asset-cost checklists are our independent planning proposals, not developer documents or measured problems.','No numerical power comparison, cosmetic-only character claim, unshown acquisition condition or exact production budget is inferred.','Every caption and final encoded boundary remains pending.'],overviewRequired:true,narrationWritten:false,final60_40Measured:false,captionCueApproval:false,finalPublicRights:'pending'};
fs.writeFileSync(target,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({cutCount:cuts.length,uniqueCandidateSeconds:result.uniqueCandidateSeconds,sha256:crypto.createHash('sha256').update(fs.readFileSync(target)).digest('hex'),finalApproval:false}));
