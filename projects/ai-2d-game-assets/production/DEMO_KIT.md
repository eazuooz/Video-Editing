# AI 2D asset video · demonstration kit

This kit contains the real outputs shown in the video, actual ComfyUI API graphs, and a UI workflow generated from the running server's node schema. Model weights are not included. No trained character LoRA is included or claimed.

## Reproduce the style comparison
1. Install ComfyUI using its official instructions.
2. Download Illustrious XL v0.1 and PixelArt SakuLike ILXL v0.1 from the links in the source ledger. Read the exact model/data/output conditions.
3. Put the files in models/checkpoints and models/loras. Use the names from the workflow, or select your actual file names in its nodes.
4. Load comfy-style08-workflow.json. The API graphs are also supplied for programmatic runs.
5. Keep seed20261108,768x1344,24steps,CFG6,euler_ancestral,normal. Compare both LoRA strengths0 and0.8.
6. Downscale the resulting image deliberately. The 8x example belongs to this LoRA's described pixel scale; it is not a general rule.

## Asset conventions
Character:96x168, hard alpha,20visible colors after a24-color maximum quantization. Workshop:426x240. The generated source images are retained for comparison.
Pixelbolt spirit:24x24 base frames; read the atlas metadata and animation sequence, not a guessed fixed FPS. pixelfx exports also contain their real frame durations and frame rectangles. Use Point/Nearest for crisp pixel enlargement.

## Rights and execution
pixelfx and Pixelbolt code/example artwork notices are in licenses. Generated character and workshop assets were created for this production. Other tools discussed in the video are not bundled. Read ASSET_PROVENANCE.md and the project source ledger for tested versus illustrated operations. Keep provider terms and model/data rights separate from the code license.
