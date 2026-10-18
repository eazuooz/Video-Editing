/** Native editable development-tool summaries, with their inspected game frames. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../../..');
const project=path.dirname(here);
const dependencies=process.env.CODEX_PRESENTATION_NODE_MODULES ?? 'C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_NODE_MODULES=dependencies;
const require=createRequire(path.join(dependencies,'../package.json'));
const {Presentation,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const skill='C:/Users/1/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const workspace=path.join(here,'local/tool-slides');
const output=path.join(root,'output/ai-games-showcase-2026/planning');
await fs.mkdir(output,{recursive:true});
const plan=JSON.parse(await fs.readFile(path.join(project,'planning/production-plan.json'),'utf8'));
const research=JSON.parse(await fs.readFile(path.join(project,'sources/research.json'),'utf8'));
const cards=plan.scenes.map(s=>s.developmentSummary).filter(Boolean);
if(cards.length!==6)throw Error('Expected exactly six game summaries');
const presentation=Presentation.create({slideSize:{width:1920,height:1080}});
const staging=path.join(workspace,'.codex-finalizer');await fs.mkdir(staging,{recursive:true});
const candidate=path.join(staging,'candidate.pptx');
if(!process.argv.includes('--finalize-only')){
const palette={background:'#000000',heading:'#E8CF83',text:'#F5F5F5',muted:'#B8C0BD'};
function text(slide,name,value,left,top,width,height,size,color=palette.text,bold=false){
 const shape=slide.shapes.add({name,geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;shape.text.style={typeface:'Malgun Gothic',fontSize:size,color,bold};
 shape.text.insets=0;shape.text.verticalAlignment='top';return shape;
}
for(const [index,card] of cards.entries()){
 const slide=presentation.slides.add();slide.background.fill=palette.background;
 text(slide,'game-title',card.title,96,76,1728,90,card.title.length>27?58:64,palette.heading,true);
 text(slide,'summary-label','개발 환경 · 사용 도구',96,178,1100,65,46,palette.text,true);
 const image=await fs.readFile(path.join(workspace,card.frame));
 slide.images.add({blob:image.buffer.slice(image.byteOffset,image.byteOffset+image.byteLength),contentType:'image/png',alt:card.credit,fit:'contain',position:{left:96,top:330,width:640,height:360}});
 text(slide,'frame-credit',card.credit,96,714,640,92,27,palette.muted);
 let y=266;
 for(const [i,[label,value]] of card.rows.entries()){
  text(slide,`label-${i}`,label,800,y,1024,48,36,palette.muted);
  const multiline=value.includes('\n');
  text(slide,`value-${i}`,value,800,y+46,1024,multiline?112:62,48,palette.text,true);
  y+=multiline?180:130;
 }
 text(slide,'brand','얌얌코딩',1600,184,224,50,32,palette.heading,true);
 const game=research.games.find(g=>g.id===card.game);
 slide.speakerNotes.text=[`Video placement: scene${index+2}, paragraph${card.paragraph}; exactly300frames/5seconds at60fps.`,
 'Narrate one short sentence; do not read the complete list or speed up speech to meet the visual duration.',
 `Frame provenance: ${card.frameSource}; ${card.sourceTime===null?'direct browser screenshot':`source second${card.sourceTime}`}.`,
 `Source credit: ${card.credit}. Keep fixed captions960,970/max2lines outside slide content.`,
 'Model versions are creator-disclosed or explicitly unknown. Earlier Codex use is labeled. Blender is a source creator tool, not a change to our production toolset.',
 ...game.sources.map(s=>`${s.kind}: ${s.url}`)].join('\n');
 const layout=await slide.export({format:'layout'});
 await fs.writeFile(path.join(workspace,`slide-${index+1}.layout.json`),await layout.text());
}
await(await PresentationFile.exportPptx(presentation)).save(candidate);
}
const finalPath=path.join(output,'ai-games-development-tools-v2.pptx');
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,
 pythonExecutable:'C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','18288000,10287000','--validate-bullet-geometry','--validate-heading-fit'],
 explicitTotalSlideCount:6,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:['Malgun Gothic']},verifyArtifactToolImport:true,
 receiptPath:path.join(staging,'tool-slides-v2-validation.json')});
execFileSync(process.execPath,[path.join(here,'render-tool-slides.cjs'),finalPath,workspace],{stdio:'inherit',windowsHide:true});
console.log(JSON.stringify({slides:cards.length,finalPath,previewDirectory:workspace}));
