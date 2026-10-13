// Filled only by the guarded producer after current PCM ASR and native review.
// No guessed duration or stretching of the old lookdev videos.
export type SpeechActionStep={actionStartFrame:number;actionDurationFrames:number;spokenTrigger:string;to:Record<string,number>};
export type ExplanationBlock={paragraphKey:string;frames:number;pcmStartFrame:number;pcmEndFrame:number;actionStartFrame:number;actionDurationFrames:number;spokenTrigger:string;actionSteps?:SpeechActionStep[]};
export type EpisodeAnimationTiming={schemaVersion:1;fps:60;reviewedCurrentVoiceSha256:string;storyboardSha256:string;finalInterleavingPlanSha256:string;all26WindowsDirectlyCompared:true;bodyRatioApproved:true;scenes:Record<string,{explanationFrames:number;blocks:ExplanationBlock[]}>};
export const PLAN:EpisodeAnimationTiming|null=null;
