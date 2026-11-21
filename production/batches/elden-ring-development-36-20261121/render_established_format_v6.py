"""Restore the approved original-twelve Shorts compositor for the 36 Elden Ring revisions."""
from argparse import ArgumentParser
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import psutil
from PIL import Image, ImageDraw

import build_pc_review as edit
import make_unity_revision_v3 as native
import render_clarity_music_v5 as previous
from make_approved_voice_v2 import DEFAULT_OUTPUT, HERE, ROOT, read, save, sha

OLD = DEFAULT_OUTPUT.with_name("pc-review-v5")
OUT = DEFAULT_OUTPUT.with_name("pc-review-v6")
WORK = Path("D:/YamyamProduction/elden-ring-development-36-format-v6")
FORMAT = HERE / "format-contract-v6.json"
CAPTIONS = HERE / "caption-clauses-v6.json"
VERSION = "established-shorts-format-v6"


def module(path):
    spec = importlib.util.spec_from_file_location("elden_established_original_twelve", path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def compositor(contract, number):
    for source in contract["sourceModules"].values():
        assert sha(ROOT / source["path"]) == source["sha256"]
    source = contract["sourceModules"]["bodyComposer"]
    existing = module(ROOT / source["path"])
    key = f"elden-ring-{number}"
    existing.TITLES[key] = contract["titles"][number]["titleLines"]
    painter = existing.Composer.__new__(existing.Composer)
    painter.slug = key
    painter.title = existing.layout.font(76, True)
    painter.label = existing.layout.font(34, True)
    painter.caption = existing.layout.font(48)
    painter.cats = {}
    for asset in read(ROOT / "shared/assets/branding/cat-reactions-v1/provenance.json")["assets"]:
        path = ROOT / asset["path"]
        assert sha(path) == asset["sha256"]
        with Image.open(path) as picture:
            painter.cats[asset["pose"]] = picture.convert("RGBA")
    return painter


def rectangles(size):
    width, height = size
    scaled_height = round(984 * height / width)
    assert scaled_height <= 984
    return (0, 396 + (984 - scaled_height)//2, 984, scaled_height)


def draw_base(painter, label, destination, phase=None):
    picture = painter.base(label)
    if phase:
        ImageDraw.Draw(picture).text((492, 1412), phase, font=painter.label,
                                     anchor="mm", fill="#f5f5f5")
    picture.save(destination)


def make_cut(episode, index, cut, input_video, size, painter, contract, destination):
    key = f"{episode['id']}-{index}"
    frames = cut["frames"]
    explain = index in (1, 3)
    offset = 0 if explain else cut["start"]
    body = rectangles(size)
    x, y, width, height = body
    if explain:
        lesson = contract["phases"][key]
        native_timing = read(HERE / "review-receipt-v4.json")["results"][int(episode["id"])-1]["cuts"][(index-1)//2]
        assert native_timing["sha256"] == sha(input_video)
        first, last = cut["subtitleFrames"]
        frame_offset = sum(piece["frames"] for piece in read(OLD/episode["id"]/"verification.json")["cuts"][:index])
        speech_first, speech_last = first-frame_offset, last-frame_offset
        starts = [round(speech_first + t*(speech_last-speech_first)) for t in lesson["phaseStarts"]]
        phrases = lesson["lines"]
        for phase in range(3):
            draw_base(painter, phrases[phase], destination/f"{index}-base-{phase}.png",
                      previous.PHASES[phase])
    else:
        starts = []
        draw_base(painter, "엘든 링 실제 플레이", destination/f"{index}-base-0.png")
    inputs = ["-loop",1,"-framerate",60,"-i",destination/f"{index}-base-0.png"]
    if explain:
        for phase in (1,2):
            inputs.extend(["-loop",1,"-framerate",60,"-i",destination/f"{index}-base-{phase}.png"])
    raw_index = 3 if explain else 1
    inputs.extend(["-ss",f"{offset:.8f}","-threads",2,"-i",input_video])
    cat = destination/f"{index}-reaction.png"
    reaction = "puzzled" if not explain else "realize"
    overlay = Image.new("RGBA",(1080,1920))
    painter.reaction(overlay,reaction)
    overlay.save(cat)
    inputs.extend(["-loop",1,"-framerate",60,"-i",cat])
    if explain:
        a, b = (t/60 for t in starts)
        scene = (f"[0:v][1:v]overlay=enable='gte(t,{a:.8f})'[phase1];"
                 f"[phase1][2:v]overlay=enable='gte(t,{b:.8f})'[base];")
        enabled = f"between(t,{max(0,b):.8f},{min(frames/60,b+2):.8f})"
    else:
        scene = "[0:v]null[base];"
        enabled = f"between(t,0.20,{min(2.2,frames/60):.8f})"
    scene += (f"[{raw_index}:v]scale={width}:{height}:flags=lanczos,format=rgba,setsar=1[body];"
              f"[base][body]overlay={x}:{y}:shortest=1[picture];"
              f"[picture][{raw_index+1}:v]overlay=enable='{enabled}'[out]")
    target=destination/f"{index}-clean.mp4"
    edit.ffmpeg(*inputs,"-filter_complex_threads",2,"-filter_complex",scene,"-map","[out]","-an",
                "-frames:v",frames,"-c:v","libx264","-threads",4,"-preset","ultrafast","-crf",19,
                "-pix_fmt","yuv420p",target)
    return {"source":str(input_video),"sourceSha256":sha(input_video),
            "bodyRect":list(body),"originalAspectPreserved":True,"sourceStart":offset,
            "sourceSpeed":1,"reaction":reaction,"phaseStarts":[0,*starts] if explain else [],
            "originalTemplate":contract["sourceModules"]["bodyComposer"]}


def caption_track(number, painter, paragraphs, frames, destination):
    transparent = Image.new("RGBA",(1080,270))
    blank = destination/"caption-empty.png"
    transparent.save(blank)
    events=[]
    cues=[cue for item in paragraphs if item["episode"]==number for cue in item["cues"]]
    assert all(cues[i]["endFrame"] <= cues[i+1]["startFrame"] for i in range(len(cues)-1))
    cursor=0
    for i,cue in enumerate(cues):
        start,end=cue["startFrame"],cue["endFrame"]
        assert 0<=cursor<=start<end<=frames
        if start>cursor:
            events.append((blank,start-cursor))
        picture=Image.new("RGBA",(1080,1920))
        painter.captioned(picture,cue["text"])
        png=destination/f"caption-{i:03}.png"
        picture.crop((0,1470,1080,1740)).save(png)
        events.append((png,end-start))
        cursor=end
    if cursor<frames:
        events.append((blank,frames-cursor))
    assert sum(length for _,length in events)==frames
    rows=["ffconcat version 1.0"]
    for path,length in events:
        rows.extend([f"file '{path.as_posix()}'","option framerate 60",f"duration {length/60:.10f}"])
    rows.extend([f"file '{blank.as_posix()}'","option framerate 60"])
    listing=destination/"caption-overlays.ffconcat"
    listing.write_text("\n".join(rows)+"\n",encoding="utf-8")
    srt=[]
    for i,cue in enumerate(cues,1):
        srt.append(f"{i}\n{edit.code_time(cue['startFrame'])} --> {edit.code_time(cue['endFrame'])}\n{cue['text']}\n")
    (destination/"ko.srt").write_text("\n".join(srt),encoding="utf-8")
    return listing,cues


def caption_pixels(movie,cues,folder):
    # Verify actual encoded white-box appearance at cue centers and silent intervals.
    frames=[(cue["startFrame"]+cue["endFrame"])//2 for cue in cues]
    quiet=[]
    for a,b in zip(cues,cues[1:]):
        if b["startFrame"]-a["endFrame"]>=4:
            quiet.append((a["endFrame"]+b["startFrame"])//2)
    selected=sorted(set(frames+quiet))
    data=edit.run("ffmpeg","-v","error","-threads",2,"-i",movie,"-vf",
                   "select="+"+".join(f"eq(n\\,{f})" for f in selected)+",crop=1080:270:0:1470",
                   "-fps_mode","passthrough","-pix_fmt","rgb24","-f","rawvideo","-")
    stride=1080*270*3
    assert len(data)==len(selected)*stride
    for i,frame in enumerate(selected):
        picture=Image.frombytes("RGB",(1080,270),data[i*stride:(i+1)*stride])
        mask=picture.point(lambda c:255 if c>220 else 0).convert("L")
        white=sum(1 for pixel in mask.getdata() if pixel>220)
        assert (white>6000)==(frame in frames),(movie,frame,white)
    return {"positiveCues":len(frames),"silentSamples":len(quiet),
            "exactFontPx":48,"maximumLines":2,"whiteBoxAndForestShadow":True}


def render(episode,contract,clauses,sources,routes,fingerprint,output):
    number=episode["id"]
    dest=output/number
    dest.mkdir(parents=True,exist_ok=True)
    if (dest/"verification.json").exists():
        result=read(dest/"verification.json")
        assert result["revisionId"]==fingerprint
        assert all(sha(dest/result[flavor]["path"])==result[flavor]["sha256"] for flavor in ("clean","captioned"))
        return result
    record=deepcopy(read(OLD/number/"verification.json"))
    painter=compositor(contract,number)
    body_records=[]
    for i,cut in enumerate(record["cuts"]):
        if i in (1,3):
            source=Path(cut["unity"]["path"])
            assert sha(source)==cut["unity"]["sha256"]
            info=edit.probe(source)["streams"][0]
            size=(info["width"],info["height"])
        else:
            name,start,*_=routes[number][i//2]
            source=sources[name]["path"]
            assert sources[name]["sha256"]==cut["sha256"] and start==cut["start"]
            size=sources[name]["size"]
        body_records.append(make_cut(episode,i,cut,source,size,painter,contract,dest))
    listing=dest/"clean.txt"
    listing.write_text("".join(f"file '{(dest/f'{i}-clean.mp4').as_posix()}'\n" for i in range(4)),encoding="utf-8")
    prior=OLD/number/"clean.mp4"
    assert sha(prior)==record["clean"]["sha256"]
    clean=dest/"clean.mp4"
    edit.ffmpeg("-f","concat","-safe",0,"-i",listing,"-i",prior,
                "-map","0:v:0","-map","1:a:0","-c","copy","-movflags","+faststart",clean)
    assert native.track_sha(clean,"a")==native.track_sha(prior,"a")
    frames=sum(cut["frames"] for cut in record["cuts"])
    record["clean"]=edit.validate(clean,frames)
    subtitle_input,cues=caption_track(number,painter,clauses["paragraphs"],frames,dest)
    captioned=dest/"captioned.mp4"
    edit.ffmpeg("-threads",2,"-i",clean,"-f","concat","-safe",0,"-i",subtitle_input,
                "-filter_complex_threads",2,"-filter_complex",
                "[0:v][1:v]overlay=0:1470:eof_action=pass:shortest=1[out]",
                "-map","[out]","-map","0:a:0","-c:v","libx264","-threads",4,
                "-preset","ultrafast","-crf",19,"-c:a","copy","-frames:v",frames,
                "-pix_fmt","yuv420p","-movflags","+faststart",captioned)
    assert native.track_sha(captioned,"a")==native.track_sha(prior,"a")
    record["captioned"]=edit.validate(captioned,frames)
    record["captionPixelReview"]=caption_pixels(captioned,cues,dest)
    shutil.copy2(OLD/number/"en.srt",dest/"en.srt")
    record["subtitles"]={lang:sha(dest/f"{lang}.srt") for lang in ("ko","en")}
    assert record["subtitles"]["en"]==read(OLD/number/"verification.json")["subtitles"]["en"]
    record.update(revisionId=fingerprint,establishedShortsFormat=True,
                  formatContractSha256=sha(FORMAT),captionClausePlanSha256=sha(CAPTIONS),
                  originalAspectPreserved=True,formatSources=body_records,
                  previousGameplayPreserved=True,previousSourceIntervalsPreserved=True,
                  existingNarrationPreserved=True,previousAudioTrackPreserved=True)
    save(dest/"verification.json",record)
    print(f"{number}: original Shorts layout, {len(cues)} timed captions, audio preserved",flush=True)
    return record


def main():
    parser=ArgumentParser()
    parser.add_argument("--pilot",action="store_true")
    parser.add_argument("--execute",action="store_true")
    args=parser.parse_args()
    assert args.pilot != args.execute
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    contract,clauses=read(FORMAT),read(CAPTIONS)
    assert sha(ROOT/contract["approvedReference"]["path"])==contract["approvedReference"]["sha256"]
    assert clauses["validation"]["originalTextReconstruction"] and clauses["validation"]["positiveWholeWordBoundaries"]
    plan=read(HERE/"episodes-v1.json")
    source_receipt=read(HERE/"review-receipt-v5.json")
    assert source_receipt["manifestSha256"]==sha(OLD/"manifest.json")
    assert source_receipt["reviewPageSha256"]==sha(OLD/"index.html")
    sources,routes=edit.open_inputs(DEFAULT_OUTPUT.with_name("pc-review-v1"))
    fp=hashlib.sha256("".join(sha(path) for path in (Path(__file__),FORMAT,CAPTIONS,OLD/"audit.json")).encode()).hexdigest()
    if args.pilot:
        plan=[episode for episode in plan if episode["id"] in {"01","14","29"}]
    output=WORK/"pilot" if args.pilot else OUT
    results=[render(episode,contract,clauses,sources,routes,fp,output) for episode in plan]
    previous.VERSION=VERSION
    previous.review(output,plan,results,read(HERE/"clarity-plan-v5.json"),fp)
    page=output/"index.html"
    html=page.read_text("utf-8").replace(
        "Unity 시연 72구간에서 처음 상태, 조작, 화면의 결과를 순서대로 표시했습니다. 편별로 시연 단계 버튼을 누르면 해당 위치로 이동합니다.",
        "기존 쇼츠 양식으로 제목·중앙 영상·흰색 고정 자막을 맞췄습니다. 시연 단계 버튼을 누르면 영상의 해당 위치로 이동합니다.")
    page.write_text(html,encoding="utf-8",newline="\n")
    audit=read(output/"audit.json")
    audit.update(reviewPageSha256=sha(page),formatContractSha256=sha(FORMAT),
                 captionClausePlanSha256=sha(CAPTIONS),sourceReviewSha256=sha(OLD/"audit.json"),
                 nativeUnityCuts=2*len(plan),timedKoreanCues=sum(r["captionPixelReview"]["positiveCues"] for r in results),
                 reusedOriginalTemplate=contract["sourceModules"]["bodyComposer"],
                 actualFullListening=False,actualRealtimePlayback=False)
    save(output/"audit.json",audit)
    print("Verified review "+str(page),flush=True)


if __name__=="__main__":
    main()
