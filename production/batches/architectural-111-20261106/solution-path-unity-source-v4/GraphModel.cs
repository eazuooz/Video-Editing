using System;
using System.Collections.Generic;

namespace Yamyam.Architectural111.SolutionPathV4 {
    // Our deliberately small room-connectivity model; not recovered Spelunky code.
    [Serializable] public sealed class Edge { public int a,b; public string role; public Edge(int x,int y,string r){a=Math.Min(x,y);b=Math.Max(x,y);role=r;} }
    [Serializable] public sealed class Graph {
        public int seed,sideVariant,templateVariant,entrance,exit;
        public int[] mandatoryRoute,roomVariants; public string[] roomRoles; public Edge[] edges;
        public bool brokenConnector; public int brokenA=-1,brokenB=-1;
        public bool Has(int a,int b){foreach(var e in edges)if(e.a==Math.Min(a,b)&&e.b==Math.Max(a,b))return true;return false;}
        public bool[] Reachable(int first,int edgeCount=-1){
            var seen=new bool[16];var q=new Queue<int>();seen[first]=true;q.Enqueue(first);int count=edgeCount<0?edges.Length:edgeCount;
            while(q.Count>0){int u=q.Dequeue();for(int i=0;i<count;i++){var e=edges[i];int v=e.a==u?e.b:(e.b==u?e.a:-1);if(v>=0&&!seen[v]){seen[v]=true;q.Enqueue(v);}}}return seen;
        }
        public int Degree(int id){int n=0;foreach(var e in edges)if(e.a==id||e.b==id)n++;return n;}
        public void Validate(){
            if(mandatoryRoute.Length<4||mandatoryRoute[0]!=entrance||mandatoryRoute[mandatoryRoute.Length-1]!=exit||entrance/4!=0||exit/4!=3)throw new InvalidOperationException("Own route endpoint invariant");
            var used=new HashSet<int>();foreach(int id in mandatoryRoute)if(id<0||id>=16||!used.Add(id))throw new InvalidOperationException("Repeated/invalid route room");
            var keys=new HashSet<int>();foreach(var e in edges){if(e.a<0||e.b>=16||e.a==e.b||Math.Abs(e.a/4-e.b/4)+Math.Abs(e.a%4-e.b%4)!=1||!keys.Add(e.a*16+e.b))throw new InvalidOperationException("Invalid or duplicate reciprocal connector");}
            if(!brokenConnector&&!Reachable(entrance)[exit])throw new InvalidOperationException("Mandatory route disconnected");
            for(int i=0;i<16;i++)if(roomRoles[i]=="sealed"&&Degree(i)!=0)throw new InvalidOperationException("Sealed optional room has a port");
        }
    }
    public struct SeedStream {
        uint state;
        public SeedStream(int seed,uint channel){state=unchecked((uint)seed)^channel;if(state==0)state=0x9e3779b9u;}
        public uint Next(){uint x=state;x^=x<<13;x^=x>>17;x^=x<<5;state=x;return x;}
        public int Range(int n){if(n<=0)throw new ArgumentOutOfRangeException("n");return (int)(Next()%(uint)n);}
    }
    public static class GraphModel {
        public static Graph Generate(int seed,int sideVariant,int templateVariant,bool breakConnector=false){
            var routeRandom=new SeedStream(seed,0xa341316cu);var route=new List<int>();int x=routeRandom.Range(4);route.Add(x);
            // Entrance chosen on top row. Exit is only known after the bottom-row walk.
            for(int y=0;y<4;y++){
                int target=routeRandom.Range(4);while(x!=target){x+=x<target?1:-1;route.Add(y*4+x);}
                if(y<3)route.Add((y+1)*4+x);
            }
            var edges=new List<Edge>();var active=new bool[16];var roles=new string[16];for(int i=0;i<16;i++)roles[i]="sealed";
            for(int i=0;i<route.Count;i++){active[route[i]]=true;roles[route[i]]="mandatory";if(i>0)edges.Add(new Edge(route[i-1],route[i],"mandatory"));}
            var branchRandom=new SeedStream(seed,unchecked(0xc8013ea4u+(uint)sideVariant*0x9e3779b9u));
            int optional=16-route.Count;int count=Math.Max(0,optional-1); // retain at least one sealed optional room when space exists
            for(int k=0;k<count;k++){
                var choices=new List<Edge>();for(int a=0;a<16;a++)if(active[a])for(int b=0;b<16;b++)if(!active[b]&&Math.Abs(a/4-b/4)+Math.Abs(a%4-b%4)==1)choices.Add(new Edge(a,b,"side"));
                if(choices.Count==0)break;var e=choices[branchRandom.Range(choices.Count)];int room=active[e.a]?e.b:e.a;active[room]=true;roles[room]="side";edges.Add(e);
            }
            var templateRandom=new SeedStream(seed,0xad90777du);var variants=new int[16];for(int i=0;i<16;i++)variants[i]=(templateRandom.Range(2)+templateVariant)%2;
            var g=new Graph{seed=seed,sideVariant=sideVariant,templateVariant=templateVariant,entrance=route[0],exit=route[route.Count-1],mandatoryRoute=route.ToArray(),roomVariants=variants,roomRoles=roles};
            if(breakConnector){int k=Math.Max(1,route.Count/2);g.brokenA=route[k-1];g.brokenB=route[k];edges.RemoveAll(e=>e.a==Math.Min(g.brokenA,g.brokenB)&&e.b==Math.Max(g.brokenA,g.brokenB));g.brokenConnector=true;}
            g.edges=edges.ToArray();g.Validate();return g;
        }
    }
}
