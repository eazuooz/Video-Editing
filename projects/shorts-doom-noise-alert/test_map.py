"""Two distinguishable experiments with identical geometry; toggle only the second sound boundary."""
from capture import RAW, MEDIA, sample, compare, dump
import struct

def wad(path,lumps):
    position=12
    directory=[]
    for name,data in lumps:
        directory.append(struct.pack('<ii8s',position,len(data),name.encode()))
        position+=len(data)
    path.write_bytes(struct.pack('<4sii',b'PWAD',len(lumps),position)+b''.join(buf for _,buf in lumps)+b''.join(directory))
def build(second_block):
    x=[0,240,368,624];lines=[];sides=[];things=[]
    text='namespace = "ZDoom";\n'
    for v in x:
        for y in [0,256]:text+=f'vertex {{ x = {float(v)}; y = {float(y)}; }}\n'
    for i in range(3):
        text+='sector { heightfloor=0; heightceiling=144; texturefloor="FLOOR4_8"; textureceiling="CEIL3_5"; lightlevel=192; }\n'
    def edge(a,b,right,left=None,flag=False):
        f=len(sides);sides.append((right,'STARTAN2' if left is None else '-'))
        spec=f'v1={a}; v2={b}; sidefront={f};'
        if left is None:spec+=' blocking=true;'
        else:
            spec+=f' sideback={len(sides)}; twosided=true; blocksound={str(flag).lower()};';sides.append((left,'-'))
        lines.append('linedef { '+spec+' }\n')
    edge(0,1,0)
    for i in range(3):
        j=2*i
        edge(j+1,j+3,i);edge(j+2,j,i)
        if i<2:edge(j+3,j+2,i,i+1,True if i==0 else second_block)
    edge(7,6,2)
    for sec,middle in sides:text+=f'sidedef {{sector={sec}; texturemiddle="{middle}";}}\n'
    text+=''.join(lines)
    for t,px,py,ang in [(1,90,128,14),(3001,475,126,0),(2028,32,34,0),(2028,605,220,0)]:
        text+=f'thing {{x={float(px)};y={float(py)};angle={ang};type={t};skill1=true;skill2=true;skill3=true;skill4=true;skill5=true;single=true;}}\n'
    out=MEDIA/('two.wad' if second_block else 'one.wad');wad(out,[('MAP01',b''),('TEXTMAP',text.encode()),('ENDMAP',b'')]);return out
if __name__=='__main__':
    for second in [False,True]:
        p=build(second)
        # The files belong to this experiment; keep each distinct scan and FHD recording.
        q=sample('map01',False,True,p)
        s=sample('map01',True,True,p)
        print(p.name,compare(q,s),flush=True)
