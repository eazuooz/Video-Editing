import base from './vite.config';
import {fileURLToPath} from 'node:url';
export default {...base,server:{...base.server,fs:{...base.server?.fs,allow:[...(base.server?.fs?.allow??[]),fileURLToPath(new URL('../projects/shorts-interior-mapping-window',import.meta.url))]}}};
