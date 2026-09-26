# YouTube publishing — English

## Title

RenderFormer Explained | Neural Rendering of 3D Triangle Meshes with Transformers (Paper & Code Walkthrough)

## Description

Can a transformer take a triangle mesh and render an image with global illumination? This 44-minute paper walkthrough follows RenderFormer (SIGGRAPH 2025) from transformer basics all the way to the public code.

We first build up self-attention, Q/K/V, multi-head attention, residual connections and normalization, the decoder and cross-attention. Then we cover how RenderFormer turns triangles into tokens, how RoPE encodes 3D position, its two-stage view-independent and view-dependent design, and how camera rays are used to reconstruct the final image. For developers and students interested in neural rendering and AI for computer graphics.

▶ Chapters
0:00 Introduction
1:02 Transformers and input representation
5:27 Self-attention and multi-head attention
11:51 Residuals, normalization and FFN
14:39 Decoder, masking and cross-attention
19:53 RenderFormer's overall architecture
22:35 Triangle tokens and the public code
29:05 Spatial position encoding and RoPE
34:22 The view-independent transformer
36:55 Camera rays and image reconstruction
41:44 Training data, results and limitations

▶ Paper & code
RenderFormer: Transformer-based Neural Rendering of Triangle Meshes with Global Illumination
Chong Zeng, Yue Dong, Pieter Peers, Hongzhi Wu, Xin Tong (SIGGRAPH 2025)
https://arxiv.org/abs/2505.21925
Official code (MIT License): https://github.com/microsoft/renderformer
Attention Is All You Need — Vaswani et al., 2017: https://arxiv.org/abs/1706.03762

This video is based on the channel's own explanatory material and is not affiliated with the paper's authors or Microsoft. Code explanations refer to a specific commit of the public repository.

#RenderFormer #Transformer #NeuralRendering

## Tags

RenderFormer, transformer, neural rendering, self-attention, attention, RoPE, paper review, deep learning, computer graphics, global illumination, SIGGRAPH 2025, 3D rendering, AI rendering
