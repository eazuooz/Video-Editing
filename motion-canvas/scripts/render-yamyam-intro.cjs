const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),slug='small-window-game-design',revision='v2',sceneDir='intro-cats-v2',source=path.join(root,'motion-canvas/src/projects',slug,sceneDir),preview=path.join(root,'projects',slug,'preview/intro-'+revision),out=path.join(root,'output/intro-sample');
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;};
const save=(f,s)=>fs.writeFileSync(f,typeof s==='string'?s:JSON.stringify(s,null,2)+'\n');
(async()=>{
 fs.mkdirSync(preview,{recursive:true});fs.mkdirSync(out,{recursive:true});
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'projects',slug,'project.json'),'utf8'));
 if(manifest.audio.backgroundMusic.approvalStatus!=='approved')throw Error('Music approval required');
 run('ffmpeg',['-v','error','-y','-i',path.join(root,manifest.audio.backgroundMusic.file),'-vn','-af','loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,atrim=start=4:duration=2,asetpts=PTS-STARTPTS,afade=t=in:d=0.08,afade=t=out:st=1.88:d=0.12','-c:a','pcm_s16le',path.join(source,'discovery-excerpt.wav')]);
 const reg=path.join(root,'motion-canvas/projects.json'),list=JSON.parse(fs.readFileSync(reg,'utf8')),route=`./src/projects/${slug}/${sceneDir}/project.ts`;if(!list.includes(route)){list.push(route);save(reg,list);}
 const browser=await puppeteer.launch({headless:true,protocolTimeout:600000});
 try{const p=await browser.newPage();await p.goto('http://127.0.0.1:9210/render-worker.html');await p.waitForFunction(()=>typeof renderVideo==='function');
  await p.evaluate(async({route,revision})=>{await document.fonts.load("900 116px 'Malgun Gothic'");await renderVideo({route:route.replace('./','/'),name:`yamyam-intro-sample-${revision}-visual`,frames:120,fps:60,width:1920,height:1080,exactFrameRange:true});},{route,revision});
  const r=await p.evaluate(()=>renderJob);if(!r.done||r.result!==0||r.errors.length)throw Error(JSON.stringify(r));save(path.join(preview,'render-qa.json'),r);
 }finally{await browser.close();}
 const visual=path.join(root,`shared/output/motion-canvas/yamyam-intro-sample-${revision}-visual.mp4`),final=path.join(out,`yamyam-intro-${revision}.mp4`);
 run('ffmpeg',['-v','error','-y','-i',visual,'-i',path.join(source,'discovery-excerpt.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t','2','-movflags','+faststart',final]);
 run('ffmpeg',['-v','error','-i',final,'-f','null','-']);
 const info=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',final]));if(+info.streams.find(s=>s.codec_type==='video').nb_frames!==120)throw Error('Frame count');save(path.join(preview,'media-qa.json'),info);
 for(const time of [.15,.55,1.2,1.85])run('ffmpeg',['-v','error','-y','-ss',String(time),'-i',final,'-frames:v','1',path.join(preview,`frame-${time}.png`)]);
 fs.copyFileSync(final,path.join(preview,`yamyam-intro-${revision}.mp4`));
 save(path.join(out,'index.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><title>얌얌코딩 인트로 샘플</title><style>body{max-width:1080px;margin:40px auto;padding:0 24px;font:18px/1.6 "Malgun Gothic",sans-serif;color:#202020}video{width:100%;border:1px solid #ddd}a{color:#2f5faa}</style><h1>얌얌코딩 | 게임 기획·디자인</h1><p>2초 인트로 단독 샘플 · 1920×1080/60fps · 본편/기존 SRT 변경 없음</p><video controls loop playsinline preload="auto" src="yamyam-intro-v1.mp4"></video><p><a href="yamyam-intro-v1.mp4" download>MP4 내려받기</a> · <a href="../index.html">전체 결과물</a></p><p>Discovery — Scott Buckley (4–6초 발췌, 볼륨 조정·짧은 페이드).<br>\'Discovery\' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au<br><a href="https://www.scottbuckley.com.au/library/discovery/">음악 출처</a> · <a href="https://creativecommons.org/licenses/by/4.0/">라이선스</a></p></html>');
 // This page replaces the unapproved chicken preview; the old media is preserved.
 const indexPath=path.join(out,'index.html');save(indexPath,fs.readFileSync(indexPath,'utf8').replaceAll('yamyam-intro-v1.mp4',`yamyam-intro-${revision}.mp4`).replace('2초 인트로 단독 샘플','사용자 원본 고양이 로고 · 2초 인트로 단독 샘플'));
 console.log(final);
})().catch(e=>{console.error(e);process.exitCode=1;});
