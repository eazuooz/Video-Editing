using System;
using System.Collections.Generic;
using UnityEngine;
namespace Yamyam.MathCurves {
 public sealed partial class CurveTeachingStage {
  void PascalPicture(double phase){
   int rows=Math.Min(5,2+(int)(phase*4));
   for(int n=0;n<rows;n++)for(int k=0;k<=n;k++){
    CVec p=new CVec(2+(k-n*.5)*.8,2.8-n*.55);
    Dot(p,Roles[n%4],CurveMathModel.Binomial(n,k).ToString("0"),.025f);
    if(n>0){if(k>0)Poly(new[]{W(new CVec(2+(k-1-(n-1)*.5)*.8,2.8-(n-1)*.55)),W(p)},Muted*.5f,.015f);if(k<n)Poly(new[]{W(new CVec(2+(k-(n-1)*.5)*.8,2.8-(n-1)*.55)),W(p)},Muted*.5f,.015f);}
   }
   basisCaption.text="0! = 1\nC(n,i) = n! / [i!(n−i)!]";
  }
  CurveSample BlossomPicture(CVec[] b,double t){
   Curve(u=>CurveMathModel.Bezier(b,u),Yellow);Controls(b);var row=(CVec[])b.Clone();
   for(int j=0;j<b.Length-1;j++){double a=shot.blossomParameters[j];var next=new CVec[row.Length-1];var points=new List<Vector3>();for(int i=0;i<next.Length;i++){next[i]=CurveMathModel.Lerp(row[i],row[i+1],a);Dot(next[i],Roles[(j+1)%4],next.Length==1?"blossom":"",.055f);points.Add(W(next[i]));}Poly(points,Roles[(j+1)%4],.03f);row=next;}
   basisCaption.text="보간 비율: "+string.Join(", ",Array.ConvertAll(shot.blossomParameters,x=>x.ToString("0.##")))+"\n결과 "+V(row[0]);
   return CurveMathModel.Sample(row[0],new CVec(),new CVec());
  }
  void Hull(CVec[] controls){
   var p=new List<CVec>(controls);p.Sort((a,b)=>a.x!=b.x?a.x.CompareTo(b.x):a.y.CompareTo(b.y));
   Func<CVec,CVec,CVec,double> cross=(a,b,c)=>(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
   var h=new List<CVec>();foreach(var v in p){while(h.Count>=2&&cross(h[h.Count-2],h[h.Count-1],v)<=0)h.RemoveAt(h.Count-1);h.Add(v);}int lower=h.Count;
   for(int i=p.Count-2;i>=0;i--){var v=p[i];while(h.Count>lower&&cross(h[h.Count-2],h[h.Count-1],v)<=0)h.RemoveAt(h.Count-1);h.Add(v);}var w=new List<Vector3>();foreach(var v in h)w.Add(W(v));Poly(w,Green,.05f);
  }
 }
}
