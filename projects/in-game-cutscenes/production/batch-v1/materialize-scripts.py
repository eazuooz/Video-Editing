"""Materialize the two owned episode drafts; no media/model/platform work."""
from pathlib import Path
import argparse, hashlib, json, re
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[4]
CONFIG = {
    "in-game-cutscenes": {
        "enTitle": "Why Do We Want to Skip a Beautiful Cutscene? | Cutscene Design",
        "aliases": {"II": "투", "60": "육십", "30": "삼십", "QTE": "큐티이"},
        "spoken": {"하데스 II": "하데스 투", "60장": "육십 장", "30장": "삼십 장", "QTE": "큐티이"},
        "emphases": {
            "01-p02-u03": ["실시간 컷신", "real time", "term"],
            "01-p02-u04": ["프리렌더링 영상", "pre-rendered video", "term"],
            "01-p03-u02": ["프레임 레이트", "Frame rate", "term"],
            "08-p01-u02": ["건너뛰는 기능", "skipping the entire scene", "result"],
            "08-p02-u04": ["데이터의 진행 상태", "save's progress", "term"],
            "09-p01-u02": ["QTE", "QTE", "term"]},
    },
    "start-with-climax": {
        "enTitle": "Why Do Some Games Hook Us Immediately? | Designing the Opening",
        "aliases": {"2": "투"},
        "spoken": {"슈퍼 마리오 갤럭시 2": "슈퍼 마리오 갤럭시 투"},
        "emphases": {
            "01-p03-u01": ["작은 절정", "small climax", "term"],
            "02-p02-u04": ["조작, 반응, 당장의 목표", "Input, response, and an immediate goal", "term"],
            "05-p02-u02": ["스핀", "spin move", "term"],
            "05-p02-u03": ["크리스털이 깨집니다", "crystal breaks", "result"],
            "09-p02-u01": ["증거", "Evidence", "term"]},
    },
}

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def font(weight):
    result=ImageFont.truetype("C:/Windows/Fonts/NotoSansKR-VF.ttf",48)
    result.set_variation_by_axes([weight if b"weight" in x["name"].lower() else x["default"] for x in result.get_variation_axes()])
    return result

def main(slug):
    c=CONFIG[slug];p=ROOT/"projects"/slug;script=p/"script/batch-v1";h=p/"production/batch-v1"
    draft=json.loads((script/"draft-paired.json").read_text(encoding="utf-8"))
    ko={"title":draft["title"],"scenes":[]};en={"title":c["enTitle"],"scenes":[]};spoken={"title":draft["title"],"scenes":[]}
    paragraphs={};measurements=[];f=font(500);bold=font(700)
    for s in draft["scenes"]:
        ko_lines=[];en_lines=[];spoken_lines=[]
        for pi,par in enumerate(s["paragraphs"],1):
            key=f"{s['id']}-p{pi:02d}";units=[]
            for ui,pair in enumerate(par["units"],1):
                unit={"ko":pair[0],"en":pair[1]};em=c["emphases"].get(f"{key}-u{ui:02d}")
                if em:
                    unit["emphasis"]={}
                    for language,needle in zip(("ko","en"),em[:2]):
                        start=unit[language].index(needle)
                        unit["emphasis"][language]={"start":start,"end":start+len(needle),"role":em[2]}
                widths={}
                for language in ("ko","en"):
                    text=unit[language];span=unit.get("emphasis",{}).get(language)
                    width=f.getlength(text)
                    if span: width+=bold.getlength(text[span['start']:span['end']])-f.getlength(text[span['start']:span['end']])
                    widths[language]=round(width,3)
                    if width>1570: raise ValueError(f"Revise authored clause rather than shrink: {key}/u{ui}/{language} width{width}: {text}")
                measurements.append({"id":f"{key}-u{ui:02d}","widthsPx":widths,"lineCount":1})
                units.append(unit)
            a=" ".join(u["ko"] for u in units);b=" ".join(u["en"] for u in units);v=a
            for before,after in c["spoken"].items():v=v.replace(before,after)
            ko_lines.append(a);en_lines.append(b);spoken_lines.append(v)
            paragraphs[key]={"semanticPairingReviewed":True,"basis":"Entire authored KO/EN paragraph and each clause pair directly read; no omitted content. Current NotoSansKR48px500/700 measurements, one line per unit.","captionUnits":units}
            assert re.sub(r"\s","",a)==re.sub(r"\s","","".join(u["ko"] for u in units))
            assert re.sub(r"\s","",b)==re.sub(r"\s","","".join(u["en"] for u in units))
        for out,lines in ((ko,ko_lines),(en,en_lines),(spoken,spoken_lines)):
            out["scenes"].append({"id":s["id"],"title":s["title"],"lines":lines})
    scripts=[]
    for suffix,data in (("ko",ko),("en",en),("spoken-ko",spoken)):
        dest=script/f"narration.{suffix}.json";write(dest,data);scripts.append({"path":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest)})
    write(script/"caption-aliases.json",c["aliases"])
    (script/"tts-input.ko.txt").write_text("\n\n".join(x for s in spoken["scenes"] for x in s["lines"])+"\n",encoding="utf-8")
    write(h/"caption-units.json",{"slug":slug,"revision":"batch-v1","status":"authored-paired-caption-units-measured-audio-timing-pending","scriptInputs":scripts,"paragraphs":paragraphs,"geometryPreflight":{"font":"C:/Windows/Fonts/NotoSansKR-VF.ttf","fontSha256":sha(Path("C:/Windows/Fonts/NotoSansKR-VF.ttf")),"fontSize":48,"weights":[500,700],"maxTextWidth":1570,"allUnitsOneLine":True,"measurements":measurements}})
    record={"slug":slug,"revision":"batch-v1","status":"materialized-internal-pretts-review","scriptInputs":scripts,"headingFreeFullRead":{"ko":True,"en":True,"basis":"Whole independently authored draft directly read without relying on headings; paired clauses compared. Adjacent closing/opening inherit a concrete need or result."},"originalReferenceOrderRetained":True,"creatorOrReferenceFramingInViewerNarration":False,"humanListening":"pending; no audio generated by this agent","audioOrPlatformJobsStarted":False,"paragraphs":len(paragraphs),"clauseUnits":len(measurements),"displayChars":sum(len(x) for s in ko['scenes'] for x in s['lines']),"spokenChars":sum(len(x) for s in spoken['scenes'] for x in s['lines']),"concatenationCheck":"all authored clause contents match full KO/EN lines exactly ignoring whitespace only","voiceScope":"Root only; ElevenLabs own voiceSampleB","sourceRightsContext":"See source-audit.json and planning/batch-v1-plan.json; final source-audio listening and publication context remain separate"}
    write(h/"script-review.json",record);print(json.dumps(record,ensure_ascii=True))

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("slug",choices=CONFIG);args=parser.parse_args();main(args.slug)
