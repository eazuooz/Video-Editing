from common import *
import ast
src=(B/'prepare-m13-source-playback.py').read_text(encoding='utf8')
q=read(R/'shared/output/private-math-concept-fit-20261023/candidates/m14/inspection.json')['sources']
shots=[dict(id='M14 water boundary',source=q['tiny']['path'],start=32.5,end=38.5),dict(id='M14 square processing',source=q['shapeB']['path'],start=42.8,end=47.6),dict(id='M14 belt construction',source=q['shapeB']['path'],start=30,end=32.25),dict(id='M14 tile addition',source=q['dorf']['path'],start=94.6,end=97),dict(id='M14 tile undo',source=q['dorf']['path'],start=118.8,end=120.2),dict(id='M14 final boundary',source=q['dorf']['path'],start=179,end=183.8)]
a=src.index('sources=');z=src.index('\nout=',a);src=src[:a]+'sources='+repr(shots)+src[z:];src=src.replace('m13','m14');exec(compile(src,'m14-source-page','exec'))
