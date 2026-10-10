export type V3 = [number, number, number];
export type Interval = [number, number];
// Educational exact-arithmetic contract. t is a ray parameter, not necessarily
// metric distance: the worked direction (1,1,1) is deliberately not normalized.
export function slabIntervals(o: V3, d: V3, low: V3, high: V3): Interval[] {
  return low.map((v, i) => {
    if (v > high[i]) throw Error('Invalid box bounds');
    if (d[i] === 0) return o[i] < v || o[i] > high[i] ? [Infinity, -Infinity] : [-Infinity, Infinity];
    const a = (v - o[i]) / d[i], b = (high[i] - o[i]) / d[i];
    return [Math.min(a, b), Math.max(a, b)];
  });
}
export function commonInterval(intervals: Interval[], tMin = 0, tMax = Infinity) {
  const enter = Math.max(tMin, ...intervals.map(i => i[0]));
  const exit = Math.min(tMax, ...intervals.map(i => i[1]));
  return {enter, exit, hit: enter <= exit};
}
export function rayPoint(o: V3, d: V3, t: number): V3 {
  return o.map((v, i) => v + t * d[i]) as V3;
}
export function triangleHit(o: V3, d: V3, a: V3, b: V3, c: V3, tMin = 0, tMax = Infinity) {
  const sub=(x:V3,y:V3)=>x.map((v,i)=>v-y[i]) as V3;
  const cross=(x:V3,y:V3):V3=>[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]];
  const dot=(x:V3,y:V3)=>x.reduce((n,v,i)=>n+v*y[i],0);
  const e1=sub(b,a),e2=sub(c,a),p=cross(d,e2),det=dot(e1,p);
  if(Math.abs(det)<1e-10)return null;
  const s=sub(o,a),u=dot(s,p)/det,q=cross(s,e1),v=dot(d,q)/det,t=dot(e2,q)/det;
  return u>=0&&v>=0&&u+v<=1&&t>=tMin&&t<=tMax?{t,u,v}:null;
}
