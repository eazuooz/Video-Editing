(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Cloudpost = factory();
})(typeof window === 'object' ? window : globalThis, function () {
  const finish = 6600;
  const obstacles = [720, 1360, 1990, 2680, 3390, 4060, 4770, 5460, 6100];
  const identities = [
    {id:'star', name:'별', color:'#df793c', emblem:'★', style:'좁은 길을 빠르게', speed:166, lane:-1},
    {id:'leaf', name:'잎', color:'#43836d', emblem:'◆', style:'넓은 다리를 차분히', speed:151, lane:0},
    {id:'moon', name:'달', color:'#5979c7', emblem:'●', style:'기회를 보고 도약', speed:158, lane:1},
  ];
  function create(seed=7) {
    return {seed, time:0, phase:'ready', selected:null, cameraMode:'overview', markers:true, auto:true,
      racers:identities.map((p,i)=>({...p,x:80-i*16,height:0,vy:0,stun:0,finishTime:null,hits:0,jumps:0,cleared:[],hitObstacles:[]})), events:[]};
  }
  function event(s,type,p,extra={}) {s.events.push({t:+s.time.toFixed(3),type,id:p?.id||null,...extra});}
  function act(s,action,value) {
    if(action==='start' && s.phase==='ready'){s.phase='racing';event(s,'start');}
    if(action==='select'){s.selected=identities.some(p=>p.id===value)?value:null;event(s,'spectator-selection',null,{selected:s.selected});}
    if(action==='camera' && ['follow','overview'].includes(value))s.cameraMode=value;
    if(action==='markers')s.markers=!!value;
    if(action==='auto')s.auto=!!value;
    if(action==='pause' && ['racing','paused'].includes(s.phase))s.phase=s.phase==='paused'?'racing':'paused';
    if(action==='jump' && s.phase==='racing')jump(s,s.racers[0]);
  }
  function jump(s,p) {if(p.height<=0 && !p.stun && p.finishTime===null){p.vy=425;p.height=.01;p.jumps++;event(s,'jump',p);}}
  function tick(s,dt,input={}) {
    if(s.phase!=='racing')return s;
    dt=Math.min(1/30,Math.max(0,dt));s.time+=dt;
    for(let i=0;i<s.racers.length;i++){
      const p=s.racers[i];if(p.finishTime!==null)continue;
      const nextIndex=obstacles.findIndex(x=>x>p.x-22 && !p.cleared.includes(x) && !p.hitObstacles.includes(x));
      const next=obstacles[nextIndex];
      if((i>0||s.auto)&&next!==undefined&&next-p.x<69&&next-p.x>20){
        // Reproducible route decisions, independent of spectator state.
        const cautious=i===1;
        const miss=!cautious && (nextIndex*3+s.seed+i*5)%7===0;
        if(!miss)jump(s,p);
      }
      if(p.stun>0)p.stun=Math.max(0,p.stun-dt);
      const moving=i>0||s.auto||input.right;
      if(moving)p.x+=p.speed*dt*(p.stun>0?.16:1);
      if(p.height>0||p.vy>0){p.vy-=1040*dt;p.height+=p.vy*dt;if(p.height<=0){p.height=0;p.vy=0;event(s,'land',p);}}
      for(const x of obstacles){
        if(p.hitObstacles.includes(x)||p.cleared.includes(x))continue;
        if(Math.abs(p.x-x)<22&&p.height<28){p.stun=1.2;p.hits++;p.hitObstacles.push(x);event(s,'collision',p,{obstacle:x});}
        else if(p.x>x+23){p.cleared.push(x);event(s,'clear-obstacle',p,{obstacle:x});}
      }
      if(p.x>=finish){p.x=finish;p.finishTime=s.time;event(s,'finish',p);}
    }
    if(s.racers.every(p=>p.finishTime!==null)){s.phase='finished';event(s,'race-complete');}
    return s;
  }
  function raceFacts(s) {return {time:s.time,phase:s.phase,racers:s.racers.map(({id,x,height,vy,stun,finishTime,hits,jumps,cleared,hitObstacles})=>({id,x,height,vy,stun,finishTime,hits,jumps,cleared,hitObstacles}))};}
  function routeY(p) {const fork=p.x>1850&&p.x<3030?Math.sin((p.x-1850)/1180*Math.PI)*70:0;return 540+p.lane*96+(p.id==='leaf'?-fork:fork*.35);}
  return {create,act,tick,raceFacts,routeY,identities,obstacles,finish};
});
