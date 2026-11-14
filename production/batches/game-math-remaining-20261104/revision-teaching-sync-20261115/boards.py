"""Typeset, speech-anchored workings on the existing native lecture picture.

Mathematical glyphs are vector outlines from mathtext, not plain code strings.
The purpose, input meanings and parent equation stay on screen while the next
operation is revealed. Existing audio is not stretched to fit an animation.
"""
import math
import re
from pathlib import Path

from matplotlib.path import Path as MPath
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from PIL import ImageFont

WHITE = "EBF2F4"
GOLD = "83CEE9"
TEAL = "C2C773"
MUTED = "909E9A"
RED = "9390EA"


def stamp(t):
    n = round(t * 100)
    return f"{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}"


def header():
    return ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080",
            "WrapStyle: 2", "ScaledBorderAndShadow: yes", "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: Default,Noto Sans CJK KR,48,&H00EBF2F4,&H00EBF2F4,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
            "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]


class Board:
    def __init__(self):
        self.lines = header()
        self.evidence = []

    def event(self, a, b, text, layer=5):
        if b > a:
            self.lines.append(f"Dialogue: {layer},{stamp(a)},{stamp(b)},Default,,0,0,0,,{text}")

    def polygon(self, points, a, b, color="000000", layer=2):
        path = "m " + " ".join(map(str, points[0])) + " l " + " ".join(f"{x:.2f} {y:.2f}" for x,y in points[1:]+points[:1])
        self.event(a,b,r"{\an7\pos(0,0)\p1\bord0\shad0\1c&H"+color+"&}"+path,layer)

    def rectangle(self, x, y, w, h, a, b, color="000000", layer=2):
        self.polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],a,b,color,layer)

    def text(self, x, y, text, a, b, color=WHITE, size=48, align=7, width=None):
        assert "{" not in text and "}" not in text
        if width:
            font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",size)
            rows=[]
            for paragraph in text.split("\n"):
                line=""
                for word in paragraph.split():
                    candidate=(line+" "+word).strip()
                    if font.getlength(candidate)>width and line:
                        rows.append(line);line=word
                    else:line=candidate
                rows.append(line)
            text="\n".join(rows)
        self.event(a,b,r"{\an"+str(align)+r"\pos("+f"{x},{y}"+r")\fs"+str(size)+r"\1c&H"+color+r"&\bord0\shad0\fad(100,0)}"+text.replace("\n",r"\N"))
        return (size+8)*len(text.split("\n"))

    def equation(self, x, y, tex, a, b, color=WHITE, width=830, size=53):
        if " || " in tex:
            total=0
            for line in tex.split(" || "):
                total+=self.equation(x,y+total,line,a,b,color,width,size)+16
            return total-16
        p = TextPath((0,0), "$"+tex+"$",size=size,prop=FontProperties(family="DejaVu Sans"),usetex=False)
        bounds=p.get_extents();scale=min(1,width/max(1,bounds.width))
        if size*scale<42:
            # Prefer real equation lines to shrinking a long derivation into an
            # unreadable code-like string. Only split at a top-level relation.
            split=None;depth=0
            for i,char in enumerate(tex):
                if char=="{":depth+=1
                elif char=="}":depth-=1
                elif char=="=" and depth==0:split=i+1;break
            if split and tex[split:]:
                h=self.equation(x,y,tex[:split],a,b,color,width,size)
                return h+20+self.equation(x+20,y+h+20,tex[split:],a,b,color,width-20,size)
            raise ValueError(("Formula needs authored multiline layout",tex,round(size*scale,1)))
        def point(v): return (x+(v[0]-bounds.xmin)*scale,y+(bounds.ymax-v[1])*scale)
        def xy(v):
            q=point(v);return f"{q[0]:.2f} {q[1]:.2f}"
        pieces=[];last=(0,0);first=(0,0)
        for vertices, code in p.iter_segments(curves=True,simplify=False):
            if code==MPath.MOVETO:
                last=first=tuple(vertices);pieces.append("m "+xy(vertices))
            elif code==MPath.LINETO:
                last=tuple(vertices);pieces.append("l "+xy(vertices))
            elif code==MPath.CURVE3:
                c=vertices[:2];end=vertices[2:]
                c1=(last[0]+2*(c[0]-last[0])/3,last[1]+2*(c[1]-last[1])/3)
                c2=(end[0]+2*(c[0]-end[0])/3,end[1]+2*(c[1]-end[1])/3)
                pieces.append("b "+xy(c1)+" "+xy(c2)+" "+xy(end));last=tuple(end)
            elif code==MPath.CURVE4:
                pieces.append("b "+xy(vertices[:2])+" "+xy(vertices[2:4])+" "+xy(vertices[4:]));last=tuple(vertices[4:])
            elif code==MPath.CLOSEPOLY:
                pieces.append("l "+xy(first));last=first
        self.event(a,b,r"{\an7\pos(0,0)\p1\bord0\shad0\1c&H"+color+r"&\fad(100,0)}"+" ".join(pieces))
        return bounds.height*scale

    def write(self, path):
        Path(path).write_text("\n".join(self.lines)+"\n",encoding="utf-8")


def norm(text):
    return re.sub(r"[^\w]", "", text).lower()


def cue(scene, phrase):
    """Use an existing actual spoken caption boundary; never guessed character time."""
    words=[e for e in scene.get("wordCueEvidence",[]) if norm(phrase) in norm(e.get("phrase",""))]
    if len(words)==1 and words[0].get("word",{}).get("timestamp"):
        return max(scene["start"],2+words[0]["word"]["timestamp"][0])
    candidates = [c for c in scene["captionEvidence"] if norm(phrase) in norm(c["text"])]
    if len(candidates) != 1:
        raise ValueError((scene["scene"], phrase, len(candidates)))
    return max(scene["start"], candidates[0]["start"])


def working(board, scene, recipe):
    start,end=scene["start"],scene["end"]
    left=recipe.get("side","right")=="left"
    x=70 if left else 1000
    board.rectangle(x-14,178,886,738,start,end)
    board.text(x,219,recipe["purpose"],start,end,GOLD,width=850)
    relation_height=board.equation(x,304,recipe["relation"],start,end,TEAL)
    legend_top=max(405,304+relation_height+30)
    for i,meaning in enumerate(recipe.get("inputs",[])):
        legend_top+=board.text(x,legend_top,meaning,start,end,MUTED,44,width=850)
    steps=recipe.get("steps",[])
    times=[cue(scene, step[0]) for step in steps]
    if times != sorted(times):raise ValueError((scene["scene"],"nonmonotonic operations",times))
    top=max(530,legend_top+35)
    # Keep the parent equation above and the last two operations below it.
    # A full proof can span adjacent scenes without becoming tiny text.
    for i,(phrase,tex,meaning) in enumerate(steps):
        a=times[i];b=times[i+1] if i+1<len(times) else end
        previous=steps[i-1] if i and recipe.get("keepPrevious",True) else None
        if previous:
            previous_height=board.equation(x,top,previous[1],a,b,WHITE,size=50)
        else:previous_height=-30
        next_top=top+previous_height+30
        current_height=board.equation(x,next_top,tex,a,b,GOLD,size=54)
        explanation_y=max(top+(180 if previous else 140),next_top+current_height+30)
        explanation_height=board.text(x,explanation_y,meaning,a,b,WHITE,44,width=850)
        if explanation_y+explanation_height>918:
            raise ValueError((scene["scene"],"Working exceeds fixed caption clearance",tex))
        board.evidence.append(dict(scene=scene["scene"],operation=tex,anchor=phrase,
            start=a,end=b,persistentRelation=recipe["relation"],inputLegend=recipe.get("inputs",[]),
            cueBasis="Actual delivered KO subtitle clause boundary",minimumReadableDwell=b-a))


def fixed_fall_graph(board,scene,stage_phrase):
    """A fixed numerical example must use the very same t in all three graphs."""
    a,b=scene["start"],scene["end"];at=cue(scene,stage_phrase)
    board.rectangle(996,178,886,738,a,b)
    move=cue(scene,"t초 뒤")
    left,right=1130,1770;width=right-left
    def path(points,color,start,end,thickness=3):
        for p,q in zip(points,points[1:]):
            dx,dy=q[0]-p[0],q[1]-p[1];l=math.hypot(dx,dy)
            if l:
                nx,ny=-dy/l*thickness/2,dx/l*thickness/2
                board.polygon([(p[0]+nx,p[1]+ny),(q[0]+nx,q[1]+ny),(q[0]-nx,q[1]-ny),(p[0]-nx,p[1]-ny)],start,end,color)
    for row,(label,color,fn,maximum) in enumerate([
        ("position",GOLD,lambda t:16*t*t,100),
        ("velocity",TEAL,lambda t:32*t,80),
        ("acceleration",RED,lambda t:32,36)]):
        top=253+row*179;base=top+119
        board.text(left,top-25,["위치 y(t) [ft]","속도 v(t) [ft/s]","가속도 a(t) [ft/s²]"][row],a,b,color,44)
        path([(left,top+19),(left,base),(right,base)],MUTED,a,b,2)
        board.text(left-55,base-25,"0",a,b,MUTED,40)
        board.text(right-55,base+8,"2.4 s",a,b,MUTED,40)
        path([(left+width*i/80,base-90*fn(2.4*i/80)/maximum) for i in range(81)],color,a,b,4)
        phases=[(a,move,0)]
        for i in range(math.ceil((at-move)*20)):
            lo=move+i/20;hi=min(at,lo+.05)
            phases.append((lo,hi,2.4*(hi-move)/(at-move)))
        phases.append((at,b,2.4))
        # One t drives all three plots; reach and hold the spoken 2.4s result.
        for lo,hi,t in phases:
            x=left+width*t/2.4;y=base-90*fn(t)/maximum
            path([(x,top+20),(x,base)],MUTED,lo,hi,2)
            board.rectangle(x-6,y-6,12,12,lo,hi,color)
        board.text(right+8,base-90*fn(2.4)/maximum-27,["92.16","76.8","32"][row],at,b,color,40)
    board.text(1125,800,"t = 2.4 s → v = 76.8 ft/s",at,b,TEAL,46)
    board.text(1125,857,"같은 t를 세 식에 함께 대입",at,b,WHITE,44)
