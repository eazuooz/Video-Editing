export interface TimedCaption {from:number;to:number;text:string}
// Chapter exports start on the nearest frame. Cue boundaries retain the
// assembled timeline's first frame at or after each absolute cue time.
// Round the animated clock to its frame before comparison: floating-point
// interpolation must not hide a cue exactly on its intended onset.
export function captionAtFrame(cues:readonly TimedCaption[],chapterStartSeconds:number,localSeconds:number,fps=60){
 const frame=Math.round(chapterStartSeconds*fps)+Math.round(localSeconds*fps);
 return cues.find(c=>frame>=Math.ceil((chapterStartSeconds+c.from)*fps-1e-7)
  &&frame<Math.ceil((chapterStartSeconds+c.to)*fps-1e-7))?.text??'';
}
