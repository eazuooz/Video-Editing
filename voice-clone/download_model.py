"""Download Chatterbox weights serially for reliable Windows transfers."""

import os

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from huggingface_hub import snapshot_download


snapshot_download(
    repo_id="ResembleAI/chatterbox",
    repo_type="model",
    revision="main",
    allow_patterns=[
        "ve.pt",
        "t3_mtl23ls_v2.safetensors",
        "s3gen.pt",
        "grapheme_mtl_merged_expanded_v1.json",
        "conds.pt",
        "Cangjie5_TC.json",
    ],
    max_workers=1,
)
print("Model download complete.")
