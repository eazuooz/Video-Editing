export const palette = {
  bg: '#0a110d', field: '#14221a', grid: '#375346', white: '#f5f4ec',
  muted: '#b9ccc0', gold: '#f2d786', teal: '#83d9cd', coral: '#f3a08a',
};

export function board(ctx: CanvasRenderingContext2D) {
  const text = (value: string, x: number, y: number, size = 39, color = palette.white) => {
    ctx.font = `600 ${size}px "Malgun Gothic", sans-serif`;
    ctx.textBaseline = 'middle';
    ctx.fillStyle = color;
    ctx.fillText(value, x, y);
  };
  const box = (x: number, y: number, w: number, h: number, color = palette.field) => {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
  };
  const path = (points: [number, number][], color: string, width = 5) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    points.forEach(([x, y], i) => i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y));
    ctx.stroke();
  };
  const dot = (x: number, y: number, radius: number, color = palette.teal) => {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  };
  return {text, box, path, dot};
}
