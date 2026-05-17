# Grok Follow-Up: Best 9B-19B Models for AMD APU (22GB RAM)

Hey Grok — follow-up to our earlier query. We rebuilt llama.cpp from latest mainline (b9199) and got a 5% Vulkan prefill boost. MTP speculative decoding is now available. Here's our updated baselines:

**Current Vulkan baselines (AMD Radeon 840M, RADV GFX1152, KHR_coopmat):**
- 9B Q4_K_M → 11.0 t/s decode, 88 t/s prefill
- 7B Q4_K_M → 13.2 t/s decode, 99 t/s prefill
- 4B Q4_K_M → 17.5 t/s decode, 160 t/s prefill
- 1B Q4_K_M → 72.8 t/s decode, 661 t/s prefill

**Constraint:** 22 GB shared LPDDR5. Model + KV cache + OS must fit. Absolute ceiling ~18 GB for the GGUF file (leaves ~4 GB for overhead).

## What I Need From You

**Search X and web for the BEST models in the 9B–17B parameter range (and interesting 19Bs) released in the last 60 days.** Focus on:

1. **Dense models 9B–14B** — what's the new hotness? AnyLlama, Nemotron, InternLM, Command-R variants, new Mistral, new Qwen?
2. **Small MoE 10B–17B total / 2–4B active** — anything competitive with Qwen3.6-35B-A3B but smaller? Grok-2-mini? Kimi-VL?
3. **Oddball sizes 15B–19B** — sometimes these are sweet spots that get overlooked. Any hidden gems?
4. **Multimodal small** — vision + text at <20B that runs on llama.cpp Vulkan (not just CUDA)
5. **Agentic / tool-use models** — small models with strong function-calling, Fara 1.5-style screen interaction, etc.

## What to Filter OUT
- Anything that needs >18 GB for a Q4_K_M or comparable quant
- Anything CUDA-only (no Vulkan/CPU path)
- Ancient models (pre-March 2026) unless they're still SOTA
- Models with no GGUF releases (we need llama.cpp compat)

## Output Format
For each recommendation:
1. **Model name + HF repo** (exact path)
2. **Recommended quant** for 22GB (file size)
3. **Why it matters** — what task does it dominate?
4. **Expected decode speed** on our hardware (extrapolate from published numbers if you have them)
5. **MTP compatible?** (Qwen3.6-style multi-token prediction)

## Specific Question

Is there a **better 9B–14B dense model than Qwen3.5-9B** right now for general chat + coding? Qwen3.5-9B is our current gold standard at 11 t/s decode. What's the next step up in quality at roughly the same speed, or the same quality at higher speed?

Also: any new **Qwen3.6 dense models between 8B and 27B**? We know about 27B and 35B-A3B but is there a 9B/14B dense in the family?

Go deep on X — this is where the bleeding edge lives.
