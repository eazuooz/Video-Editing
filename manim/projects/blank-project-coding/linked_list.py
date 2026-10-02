"""Original-restored-v2: genuine Manim process animations; explanation time only.
Render with manim/.venv/Scripts/python.exe -m manim -qh --fps 60 this_file ClassName.
Bottom caption safe area is reserved. Color is paired with labels and active-line marks.
"""
from manim import *
from pygments import lex
from pygments.lexers import CppLexer
from pygments.token import Token

INK='#202733'; MUTED='#606D7B'; BLUE='#245CA8'; PURPLE='#7C3AAD'
GREEN='#23875B'; RED='#C34242'; AMBER='#BA750C'; PAPER='#FFFFFF'; LINE='#D6DEE8'
config.background_color=PAPER
config.pixel_width=1920; config.pixel_height=1080; config.frame_rate=60

def txt(s,size=28,color=INK,mono=False):
    return Text(s,font='Consolas' if mono else 'Malgun Gothic',font_size=size,color=color)

def node(value,point,color=BLUE):
    shadow=RoundedRectangle(width=2.08,height=1.22,corner_radius=.08,stroke_width=0,fill_color='#DDE5EE',fill_opacity=1).shift(RIGHT*.08+DOWN*.09)
    box=RoundedRectangle(width=2.08,height=1.22,corner_radius=.08,stroke_color=color,stroke_width=2.5,fill_color=WHITE,fill_opacity=1)
    split=Line([-0.04,-.59,0],[-.04,.59,0],color=LINE)
    data=txt(str(value),37,color,True).move_to([-.53,.12,0]); label=txt('data',16,MUTED,True).move_to([-.53,-.36,0])
    pointer=txt('next',22,PURPLE,True).move_to([.52,.1,0]); plabel=txt('포인터',15,MUTED).move_to([.52,-.35,0])
    return VGroup(shadow,box,split,data,label,pointer,plabel).move_to(point)

def arrow(a,b,color=PURPLE):
    return Arrow(a,b,buff=.08,color=color,stroke_width=4,max_tip_length_to_length_ratio=.14)

class ListBase(Scene):
    def heading(self,title,sub):
        self.add(txt('코드와 연결을 함께 따라가세요',19,MUTED).to_edge(UP,buff=.25).to_edge(LEFT,buff=.5))
        self.add(txt(title,37).move_to([-6.1,3.06,0],aligned_edge=LEFT),txt(sub,22,MUTED).move_to([-6.1,2.52,0],aligned_edge=LEFT))
        legend=VGroup(txt('파랑: 값',17,BLUE),txt('보라: 연결',17,PURPLE),txt('초록: 새 연결',17,GREEN),txt('노랑: 실행 줄',17,AMBER)).arrange(RIGHT,buff=.32).move_to([0,1.97,0]);self.add(legend)
    def code(self,lines):
        panel=RoundedRectangle(width=12.2,height=2.33,corner_radius=.07,fill_color='#F7F9FC',fill_opacity=1,stroke_color=LINE).move_to([0,-1.87,0]);self.add(panel)
        result=[]
        for i,line in enumerate(lines):
            y=-1.08-i*.39
            self.add(txt(str(i+1),16,MUTED,True).move_to([-5.78,y,0]))
            # Shape one whole monospace line. Independently positioning token
            # glyphs changed the advance widths and made punctuation overlap.
            colors={};pos=0
            for kind,value in lex(line,CppLexer()):
                value=value.rstrip('\n')
                if not value:continue
                color=BLUE if kind in Token.Keyword or kind in Token.Literal.Number else GREEN if kind in Token.Literal.String else MUTED if kind in Token.Comment else PURPLE if any(p in value for p in ['head','next','prev','node','victim']) else INK
                colors[f'[{pos}:{pos+len(value)}]']=color
                pos+=len(value)
            code_line=Text(line,font='Consolas',font_size=20,color=INK,t2c=colors,disable_ligatures=True).move_to([-5.3,y,0],aligned_edge=LEFT)
            self.add(code_line);result.append(y)
        self.cursor=RoundedRectangle(width=11.72,height=.37,corner_radius=.03,fill_color='#FFE9A2',fill_opacity=.36,stroke_color=AMBER,stroke_width=1.3).move_to([.05,result[0],0]).set_z_index(-1)
        panel.set_z_index(-3);self.add(self.cursor)
        self.rows=result
    def line(self,i): return self.cursor.animate.move_to([.05,self.rows[i],0])
    def finish(self,seconds=42):
        remaining=seconds-self.renderer.time
        if remaining>0:self.wait(remaining)

class NodeAndTraversal(ListBase):
    def construct(self):
        self.heading('Linked List: 값과 다음 노드의 주소','노드 선언 → 연결 → head에서 다음 주소를 따라가기')
        self.code(['struct Node { int data; Node* next; };','Node b{20, nullptr};','Node a{10, &b};','Node* head = &a;','for (Node* p=head; p; p=p->next) print(p->data);'])
        a=node(10,[-3.7,.55,0]);b=node(20,[.2,.55,0]);null=txt('nullptr',25,MUTED,True).move_to([4.2,.55,0]);ab=arrow(a.get_right(),b.get_left());bn=arrow(b.get_right(),null.get_left())
        self.play(FadeIn(b),self.line(1),run_time=1.1);self.wait(4)
        self.play(FadeIn(a),Create(ab),self.line(2),run_time=1.2);self.wait(5)
        head=txt('head',24,PURPLE,True).move_to([-3.7,1.55,0]);ha=arrow(head.get_bottom(),a.get_top());self.play(FadeIn(head),Create(ha),self.line(3),run_time=1);self.wait(4)
        self.play(FadeIn(null),Create(bn),self.line(4),run_time=1)
        marker=SurroundingRectangle(a,buff=.12,color=GREEN);self.play(Create(marker),run_time=.7);self.wait(4)
        self.play(Transform(marker,SurroundingRectangle(b,buff=.12,color=GREEN)),run_time=1.2);self.wait(4)
        self.play(Transform(marker,SurroundingRectangle(null,buff=.14,color=GREEN)),run_time=1.2);self.finish()

class InsertBetween(ListBase):
    def construct(self):
        self.heading('삽입: 기존 연결을 잃지 않는 순서','새 노드를 뒤에 연결한 다음, 앞 노드의 next를 바꿉니다')
        self.code(['Node* node = new Node{15, nullptr};','node->next = prev->next;','prev->next = node;','// 10 -> 15 -> 20 -> nullptr'])
        a=node(10,[-4.3,.85,0]);b=node(20,[4.3,.85,0]);ab=arrow(a.get_right(),b.get_left());self.add(a,b,ab)
        n=node(15,[0,.15,0],GREEN);self.play(FadeIn(n,shift=UP*.3),run_time=1);self.wait(7)
        nb=arrow(n.get_right(),b.get_left(),GREEN);self.play(Create(nb),self.line(1),run_time=1.3);self.wait(8)
        an=arrow(a.get_right(),n.get_left(),GREEN);self.play(FadeOut(ab),Create(an),self.line(2),run_time=1.4);self.wait(8)
        self.play(self.line(3),Indicate(n,color=GREEN,scale_factor=1.08),run_time=1.1);self.finish()

class DeleteMiddle(ListBase):
    def construct(self):
        self.heading('삭제: 연결을 바꾼 뒤 메모리를 해제','지울 노드의 next를 읽기 전에 삭제하면 안 됩니다')
        self.code(['Node* victim = prev->next;','prev->next = victim->next;','delete victim;','// 10 -> 20 -> nullptr'])
        a=node(10,[-4.2,.67,0]);v=node(15,[0,.67,0],RED);b=node(20,[4.2,.67,0]);av=arrow(a.get_right(),v.get_left());vb=arrow(v.get_right(),b.get_left());self.add(a,v,b,av,vb)
        label=txt('victim',20,RED,True).next_to(v,UP,buff=.1);self.play(FadeIn(label),run_time=.8);self.wait(7)
        # Route below the nodes; an upper arc crossed the subtitle and legend.
        left=[a.get_bottom()[0],-.46,0];right=[b.get_bottom()[0],-.46,0]
        bypass=VGroup(Line(a.get_bottom(),left,color=GREEN,stroke_width=4),Line(left,right,color=GREEN,stroke_width=4),Arrow(right,b.get_bottom(),buff=0,color=GREEN,stroke_width=4,max_tip_length_to_length_ratio=.3))
        self.play(FadeOut(av),Create(bypass),self.line(1),run_time=1.5);self.wait(8)
        cross=Cross(v,stroke_color=RED,stroke_width=5);self.play(Create(cross),self.line(2),run_time=1);self.wait(3)
        self.play(FadeOut(VGroup(v,label,vb,cross)),run_time=1.2);self.wait(5)
        self.play(self.line(3),Indicate(bypass,color=GREEN),run_time=1);self.finish()

class HeadAndEmpty(ListBase):
    def construct(self):
        self.heading('첫 노드를 지우면 head는 어디를 가리킬까?','빈 목록도 조건의 일부입니다: nullptr를 먼저 확인합니다')
        self.code(['if (head == nullptr) return;','Node* victim = head;','head = head->next;','delete victim;','// last node deleted: head == nullptr'])
        a=node(10,[-3.6,.56,0]);b=node(20,[.4,.56,0]);n=txt('nullptr',25,MUTED,True).move_to([4.3,.56,0]);ab=arrow(a.get_right(),b.get_left());bn=arrow(b.get_right(),n.get_left());h=txt('head',24,PURPLE,True).move_to([-3.6,1.55,0]);ha=arrow(h.get_bottom(),a.get_top());self.add(a,b,n,ab,bn,h,ha);self.wait(5)
        self.play(self.line(1),a[1].animate.set_stroke(RED),run_time=1);self.wait(4)
        hb=arrow(h.get_right(),b.get_top(),GREEN);self.play(ReplacementTransform(ha,hb),self.line(2),run_time=1.3);self.wait(5)
        self.play(FadeOut(a),FadeOut(ab),self.line(3),run_time=1.2);self.wait(5)
        hn=arrow(h.get_right(),n.get_top(),GREEN);self.play(ReplacementTransform(hb,hn),run_time=1.4);self.play(FadeOut(b),FadeOut(bn),self.line(4),run_time=1.2);self.wait(4)
        self.play(self.line(0),Indicate(n,color=GREEN),run_time=1);self.finish()
