import base from '../../../motion-canvas/vite.config.ts';
// Only this selected project's reviewed local media is additionally served.
export default {...base,server:{...base.server,fs:{...base.server.fs,
 allow:[...base.server.fs.allow,'D:/Github/VideoEditing/projects/shorts-zombie-quiet-director']}}};
