import {validateProductionInput} from './model';

// Missing PCM/timing is a hard error, never a synthesized preview timeline.
const timing = import.meta.glob(
  '../../../../projects/shorts-splatoon-surface-ink/production/visual-timing.json',
  {eager: true, import: 'default'},
);
const config = import.meta.glob(
  '../../../../projects/shorts-splatoon-surface-ink/production/visual-config.json',
  {eager: true, import: 'default'},
);
export const requireProductionInput = () => validateProductionInput(
  Object.values(timing)[0], Object.values(config)[0],
);
