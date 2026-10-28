"""Small lexical JSON value patcher; keeps unrelated source bytes unchanged."""
import copy,json

class Node:
    def __init__(self,start,end,value,children=None):self.s=start;self.e=end;self.v=value;self.c=children
def parse(text):
    decoder=json.JSONDecoder()
    def ws(i):
        while i<len(text) and text[i].isspace():i+=1
        return i
    def rec(i):
        i=ws(i);start=i
        if text[i]=='{':
            children={};value={};i=ws(i+1)
            while text[i]!='}':
                key,end=decoder.raw_decode(text,i);i=ws(end);assert text[i]==':'
                child,i=rec(i+1);children[key]=child;value[key]=child.v;i=ws(i)
                if text[i]==',':i=ws(i+1)
                else:assert text[i]=='}';break
            return Node(start,i+1,value,children),i+1
        if text[i]=='[':
            children=[];value=[];i=ws(i+1)
            while text[i]!=']':
                child,i=rec(i);children.append(child);value.append(child.v);i=ws(i)
                if text[i]==',':i=ws(i+1)
                else:assert text[i]==']';break
            return Node(start,i+1,value,children),i+1
        value,end=decoder.raw_decode(text,i);return Node(start,end,value),end
    node,end=rec(0);assert not text[end:].strip();return node
def load(raw):return json.loads(raw.decode('utf-8-sig'))
def patch(raw,path,value):
    text=raw.decode('utf-8-sig');newline='\r\n' if '\r\n' in text else '\n';parent=parse(text)
    for key in path[:-1]:parent=parent.c[key]
    key=path[-1]
    def fmt(v,indent):
        lines=json.dumps(v,ensure_ascii=False,indent=2).splitlines()
        return newline.join([lines[0]]+[' '*indent+x for x in lines[1:]])
    def indent_at(pos):
        start=text.rfind('\n',0,pos)+1;return len(text[start:pos])-len(text[start:pos].lstrip())
    exists=isinstance(parent.c,dict) and key in parent.c or isinstance(parent.c,list) and isinstance(key,int) and 0<=key<len(parent.c)
    if exists:
        child=parent.c[key]
        new=text[:child.s]+fmt(value,indent_at(child.s))+text[child.e:]
    elif isinstance(parent.c,dict):
        indent=indent_at(parent.s)+2;item=' '*indent+json.dumps(key,ensure_ascii=False)+': '+fmt(value,indent)
        if parent.c:
            last=list(parent.c.values())[-1];new=text[:last.e]+','+newline+item+text[last.e:]
        else:new=text[:parent.s+1]+newline+item+newline+' '*(indent-2)+text[parent.e-1:]
    elif isinstance(parent.c,list) and key=='append':
        indent=indent_at(parent.s)+2;item=' '*indent+fmt(value,indent)
        if parent.c:
            last=parent.c[-1];new=text[:last.e]+','+newline+item+text[last.e:]
        else:new=text[:parent.s+1]+newline+item+newline+' '*(indent-2)+text[parent.e-1:]
    else:raise AssertionError(path)
    desired=copy.deepcopy(json.loads(text));target=desired
    for key2 in path[:-1]:target=target[key2]
    if key=='append' and isinstance(target,list):target.append(value)
    else:target[key]=value
    assert json.loads(new)==desired
    return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+new.encode('utf-8')
def upsert(raw,parent,key,value):
    matches=[i for i,x in enumerate(load(raw)[parent]) if x[key]==value[key]]
    assert len(matches)<=1
    return patch(raw,[parent,matches[0] if matches else 'append'],value)
