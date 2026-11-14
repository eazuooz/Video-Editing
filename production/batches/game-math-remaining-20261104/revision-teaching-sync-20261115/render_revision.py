"""Additive visual revision of the approved delivered lecture, with a finite scope.

Only --render starts encoding. Preparation and representative samples do not
mark a lecture complete. The prior masters, voice and publishing states remain.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import math
import html

import psutil

from inventory import HERE, ROOT, read, save, sha
from boards import Board, working, fixed_fall_graph, GOLD, WHITE, TEAL
from workings import WORKINGS
import motion_panels

FF = Path("C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe")
CREATE = getattr(subprocess, "CREATE_NO_WINDOW", 0)
REVISION = "teaching-sync-v1"


def library(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def additions(episode):
    return [g for g in read(HERE/"game-additions.json")["additions"] if g["episode"]==episode["id"]]


def game_labels(board,game):
    a=game["start"];b=a+game["duration"]
    board.rectangle(995,30,900,145,a,b)
    board.text(1000,46,"실제 게임 녹화 | 해설 모형",a,b,GOLD,44,width=850)
    board.text(1000,104,"오른쪽은 원리 설명 · 게임 실측 아님",a,b,WHITE,40,width=850)
    board.text(70,219,game["label"],a,b,GOLD,44,width=850)
    marks=game.get("marks")
    if not marks:return
    keys=marks["keys"];x,y,w,h=game["viewport"];radius=marks["radius"]
    end=min(game["duration"],marks["hideAfter"])
    board.text(70,837,marks["label"],a,a+end,TEAL,44,width=850)
    for i in range(math.ceil(end*20)):
        lo=i/20;hi=min(end,lo+.05)
        j=max(j for j,k in enumerate(keys) if k[0]<=lo)
        if j+1<len(keys):
            first,last=keys[j],keys[j+1];u=(lo-first[0])/(last[0]-first[0])
            px=first[1]+u*(last[1]-first[1]);py=first[2]+u*(last[2]-first[2])
        else:px,py=keys[-1][1:]
        cx,cy=x+px*w,y+py*h
        # A hollow editorial guide, not a detector, world-space radius or value.
        for k in range(32):
            q1=math.tau*k/32;q2=math.tau*(k+1)/32
            board.polygon([(cx+(radius-2)*math.cos(q1),cy+(radius-2)*math.sin(q1)),
                (cx+(radius+2)*math.cos(q1),cy+(radius+2)*math.sin(q1)),
                (cx+(radius+2)*math.cos(q2),cy+(radius+2)*math.sin(q2)),
                (cx+(radius-2)*math.cos(q2),cy+(radius-2)*math.sin(q2))],a+lo,a+hi,TEAL,6)


def guard():
    path = ROOT / "projects/game-math-shading-lights/production/run-capture-queue.py"
    spec = importlib.util.spec_from_file_location("math_sync_resource_guard", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def authorized(episode):
    c = read(ROOT / "shared/publishing/video-production-control.json")["explicitMathRemainingBatch20261104"]
    assert c["productionAllowedNow"] and episode["id"] in c["teachingSyncRevision20261115"]["scope"]
    assert c["teachingSyncRevision20261115"]["userRequest"]


def prepare(episode):
    authorized(episode)
    p = ROOT / "projects" / episode["slug"]
    folder = p / "production/local" / REVISION
    folder.mkdir(exist_ok=True)
    board = Board()
    for scene in episode["scenes"]:
        recipe = WORKINGS.get(episode["id"], {}).get(scene["scene"])
        if recipe:
            working(board, scene, recipe)
        if episode["id"] == "M25" and scene["scene"] == "003":
            fixed_fall_graph(board, scene, "2.4초 뒤")
    motion_panels.apply(board,episode,additions(episode))
    for game in additions(episode):game_labels(board,game)
    target = folder / "workings.ass"
    board.write(target)
    evidence = dict(episode=episode["id"], revision=REVISION,
        sourceEdition=episode["baselineRevision"], sourceFiles=episode["baselineOutputs"],
        formulaOverlaySha256=sha(target), workings=board.evidence,
        status="prepared-not-rendered", newMasterHumanReview=False,
        existingNarrationTempo=1, finalReviewReady=False)
    save(folder / "preparation.json", evidence)
    captions=library("preserved_math_captions",ROOT/"projects/buckshot-roulette-reverse-engineering/production/assemble_documentary.py")
    cues=captions.read_srt(episode["baselineOutputs"]["ko"])
    captions.caption_ass(folder/"captions.ko.ass",cues,0,{})
    return folder


def filters(episode,origin,end):
    inputs=[];graph=[f"[0:v]setsar=1,setpts=PTS-STARTPTS+{origin}/TB[b0]"]
    current="b0";count=0;index=1;audio=[]
    for game in additions(episode):
        begin=max(origin,game["start"]);finish=min(end,game["start"]+game["duration"])
        if finish<=begin:continue
        relative=begin-game["start"]
        if "nativeSource" in game:
            mask="0:0:1920:918"
        else:mask="56:178:886:738"
        next_name=f"b{count+1}";count+=1
        graph.append(f"[{current}]drawbox={mask}:color=black:t=fill:enable='gte(t,{begin})*lt(t,{finish})'[{next_name}]")
        current=next_name
        picture=game.get("preservedAnnotatedPicture",str(ROOT/game["source"]["file"]))
        picture_in=game.get("preservedPictureIn",game["sourceIn"])+relative
        inputs.extend(["-ss",str(picture_in),"-t",str(finish-begin),"-i",picture])
        x,y,w,h=game["viewport"]
        crop=""
        if game.get("preservedPictureCrop"):
            px,py,pw,ph=game["preservedPictureCrop"];crop=f"crop={pw}:{ph}:{px}:{py},"
        graph.append(f"[{index}:v]{crop}fps=60,scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,setpts=PTS-STARTPTS+{begin}/TB[g{index}]")
        next_name=f"b{count+1}";count+=1
        graph.append(f"[{current}][g{index}]overlay={x}:{y}:eof_action=pass:repeatlast=0:enable='gte(t,{begin})*lt(t,{finish})'[{next_name}]")
        current=next_name
        if game["audioMode"].startswith("add-original"):
            audio.append((index,begin-origin))
        index+=1
        if "nativeSource" in game:
            inputs.extend(["-ss",str(game["nativeIn"]+relative),"-t",str(finish-begin),"-i",game["nativeSource"]])
            cx,cy,cw,ch=game["nativeCrop"];x,y,w,h=game["nativeViewport"]
            graph.append(f"[{index}:v]crop={cw}:{ch}:{cx}:{cy},scale={w}:{h},setsar=1,fps=60,setpts=PTS-STARTPTS+{begin}/TB[n{index}]")
            next_name=f"b{count+1}";count+=1
            graph.append(f"[{current}][n{index}]overlay={x}:{y}:eof_action=pass:repeatlast=0:enable='gte(t,{begin})*lt(t,{finish})'[{next_name}]")
            current=next_name;index+=1
    graph.append(f"[{current}]ass=workings.ass,setpts=PTS-STARTPTS[vout]")
    if audio:
        graph.append(f"[0:a]asplit={len(audio)+1}[base]"+"".join(f"[side{i}]" for i in range(len(audio))))
        for i,(idx,delay) in enumerate(audio):
            graph.append(f"[{idx}:a]asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-3:LRA=11,aformat=sample_rates=48000:channel_layouts=stereo,adelay={round(delay*1000)}:all=1[ga{i}]")
            graph.append(f"[ga{i}][side{i}]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[duck{i}]")
        graph.append("[base]"+"".join(f"[duck{i}]" for i in range(len(audio)))+f"amix=inputs={len(audio)+1}:duration=first:normalize=0,aresample=192000,alimiter=limit=0.831764:level=false:latency=true,aresample=48000[aout]")
    return inputs,";\n".join(graph),bool(audio)


def command(args,folder,name):
    with (folder/(name+".log")).open("w",encoding="utf8") as log:
        result=subprocess.run([str(FF),"-hide_banner","-nostdin","-n","-threads","2",*map(str,args)],
            cwd=folder,stdout=log,stderr=subprocess.STDOUT,creationflags=CREATE)
    if result.returncode:raise RuntimeError((name,(folder/(name+".log")).read_text(encoding="utf8",errors="replace")[-2400:]))


def encoder():
    return ["-c:v","h264_nvenc","-preset","p5","-tune","hq","-rc","vbr","-cq","18","-b:v","0","-g","120","-pix_fmt","yuv420p","-video_track_timescale","90000"]


def encode(episode, sample=None, sample_revision=1):
    folder = prepare(episode)
    p = ROOT / "projects" / episode["slug"]
    G = guard()
    authorized(episode)
    reason = G.idle_reason()
    if reason:
        save(folder / "resource-wait.json", dict(reason=reason, running=False))
        raise RuntimeError(reason)
    owned = str(uuid.uuid4())
    with G.LEASE.open("x", encoding="utf-8") as stream:
        json.dump(dict(id=owned, owner=episode["slug"]+"-teaching-sync", pid=os.getpid(),
            createdAt=G.now(), scope="Explicit M21–M33 additive local revision"), stream)
    try:
        source = Path(episode["baselineOutputs"]["clean"])
        start = 0
        if sample:
            scene = next(s for s in episode["scenes"] if s["scene"] == sample)
            start = scene["start"]
            frames = round((scene["end"]-start)*60)
            output = folder / (f"sample-{sample}-v{sample_revision}.mp4")
            duration=frames/60
        else:
            meta=json.loads(subprocess.check_output([str(FF.with_name("ffprobe.exe")),"-v","error","-select_streams","v:0","-show_entries","stream=width,height,r_frame_rate,nb_frames","-of","json",str(source)],creationflags=CREATE))["streams"][0]
            assert (meta["width"],meta["height"],meta["r_frame_rate"])==(1920,1080,"60/1")
            frames=int(meta["nb_frames"]);duration=frames/60
            dest=ROOT/"output"/(episode["slug"]+"-"+REVISION)
            dest.mkdir(exist_ok=True)
            assert shutil.disk_usage(dest).free>source.stat().st_size*3+2*1024**3,"Reserve space for paired masters; preserve baseline media"
            output=dest/(episode["slug"]+".clean.mp4")
        if output.exists():
            raise RuntimeError("Preserve previous sample; change the reviewed sample revision before recapturing")
        extra,graph,remix=filters(episode,start,start+duration)
        if sample:graph=graph.replace("[vout]","[unsub]")+";[unsub]setpts=PTS+"+str(start)+"/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS[vout]"
        graphfile=folder/(output.stem+".ffgraph");graphfile.write_text(graph,encoding="utf8")
        args=["-ss",start,"-i",source,*extra,"-filter_complex_threads","2","-filter_complex",graph,
            "-map","[vout]","-map","[aout]" if remix else "0:a:0","-frames:v",frames,"-t",duration,*encoder()]
        args+= ["-c:a","aac","-b:a","192k"] if remix or sample else ["-c:a","copy"]
        args+=["-movflags","+faststart",output]
        state=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),episode=episode["id"],
            status="rendering-sample" if sample else "rendering-clean",startedAt=G.now(),finalReviewReady=False)
        save(folder/"worker.json",state)
        command(args,folder,output.stem)
        save(folder/(output.stem+".json"),dict(sample=bool(sample), scene=sample, sourceStart=start,
            sourceMasterSha256=sha(source), inputOverlaySha256=sha(folder/"workings.ass"),
            outputSha256=sha(output), finalMaster=False, actualVisualReview=False))
        if not sample:
            state["status"]="rendering-captioned";save(folder/"worker.json",state)
            cap=output.with_name(episode["slug"]+".captioned.mp4")
            command(["-i",output,"-vf","ass=captions.ko.ass","-map","0:v:0","-map","0:a:0",
                *encoder(),"-c:a","copy","-frames:v",frames,"-t",duration,"-movflags","+faststart",cap],folder,"captioned")
            for lang in ("ko","en"):
                shutil.copy2(episode["baselineOutputs"][lang],dest/(episode["slug"]+"."+lang+".srt"))
            files={kind:dict(path=str(path),sha256=sha(path)) for kind,path in {
                "clean":output,"captioned":cap,"ko":dest/(episode["slug"]+".ko.srt"),"en":dest/(episode["slug"]+".en.srt")}.items()}
            save(folder/"encoded.json",dict(episode=episode["id"],frames=frames,duration=duration,
                files=files,originalVoiceTempo=1,baselineSpeechPreserved=True,
                addedBgm=False,addedGameAudioIntervals=[g for g in additions(episode) if g["audioMode"].startswith("add-original")],
                status="encoded-QA-pending",finalReviewReady=False,humanReviewed=False))
            (dest/"index.html").write_text(f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{episode["id"]} 수정 검수</title><style>body{{background:#080808;color:#fff;font:18px/1.65 system-ui;max-width:1200px;margin:auto;padding:24px}}h1{{color:#e8cf83}}video{{width:100%}}a{{color:#73c7c2}}</style><h1>{episode["id"]} · 계산과 화면 동기화 수정본</h1><p>1080p60 · 인코딩 완료 / 내부 검수 중 · 사용자 시청 전</p><video controls preload="metadata" src="{cap.name}"></video><p><a href="{output.name}">Clean MP4</a> · <a href="{episode["slug"]}.ko.srt">한국어 자막</a> · <a href="{episode["slug"]}.en.srt">영어 자막</a></p>',encoding="utf8")
        state.update(status="sample-review-pending" if sample else "encoded-QA-pending",finishedAt=G.now())
        save(folder/"worker.json",state)
        print(output,flush=True)
    finally:
        G.release_lease(owned)


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("episodes",nargs="+")
    ap.add_argument("--sample")
    ap.add_argument("--sample-revision",type=int,default=1)
    ap.add_argument("--render",action="store_true")
    args=ap.parse_args()
    episodes={e["id"]:e for e in read(HERE/"inventory.json")["episodes"]}
    for eid in args.episodes:
        episode=episodes[eid]
        if args.render: encode(episode,args.sample,args.sample_revision)
        else: print(prepare(episode))
