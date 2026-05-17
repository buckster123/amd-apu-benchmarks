# Grok Query: Latest AMD Local AI + Small Model Developments

Hey Grok — I need you to do a deep sweep of X (Twitter) and the web for the latest developments in local LLM inference on AMD hardware, plus any new small models worth benchmarking. I'm running a Ryzen AI 5 340 (Krackan Point, 6c Zen 5, Radeon 840M iGPU, XDNA 2 NPU with 48 AIE tiles, 22GB LPDDR5) on Ubuntu 25.10. Here's what I'm tracking:

## 1. AMD-Specific Stack Developments

**Search X and web for:**
- Any updates to **Ryzen AI SDK** beyond 1.7.1 (1.8? beta? leaked builds?)
- **ROCm 6.x** or newer Vulkan compute improvements for RDNA3 iGPUs
- **amdxdna driver** updates (out-of-tree vs in-tree kernel support)
- **llama.cpp Vulkan backend** improvements — KHR_coopmat, shader optimizations, new quant support
- **AMD GPU+CPU hybrid inference** stories — anyone splitting layers between iGPU and CPU for better throughput?
- Any benchmarks on **Strix/Krackan/Strix Halo** NPUs from other users
- **XDNA 3 / Ryzen AI 400** series rumors or leaks

## 2. Quantization & Format Breakthroughs

**Search for:**
- New GGUF quant types beyond Q4_K_M/Q5_K_M — IQ quants, new K-quants, anything with better quality/speed tradeoffs
- **AWQ / GPTQ** vs GGUF debates — any recent wins for AMD hardware specifically?
- **Dynamic quantization** or runtime quantization techniques
- **Q4_0_4_4, Q4_0_4_8** and other newer GGUF types — do they help on Vulkan?
- Anyone comparing **INT4 vs INT8** on AMD NPU vs iGPU?

## 3. New Small Models Worth Benchmarking

**Focus on sub-10B parameter models released in the last 2-3 months:**
- **Qwen3.5** series updates — any new variants beyond 4B/9B?
- **Phi-4** updates — Microsoft releases, distills, or finetunes
- **Llama 3.2/3.3** — any new 1B/3B variants or quantized releases
- **Gemma 3** — new sizes, vision variants, quantized releases
- **SmolLM / SmolVLM** updates — HuggingFace's tiny model line
- **DeepSeek** distill updates — any new Qwen/Llama-based distills
- **Mistral Small / Nemo** updates
- Any **MoE models** at <10B active params that run well on consumer hardware
- **Japanese, Chinese, or multilingual** small models that punch above their weight

## 4. Serving Stack & Inference Optimizations

**Search for:**
- **vLLM** AMD support improvements — ROCm backend, any new optimizations
- **SGLang** on AMD — anyone running it on Radeon/APU?
- **llama.cpp** speculative decoding improvements — draft model speeds, new algorithms
- **Prompt caching / prefix caching** breakthroughs for local inference
- **KV cache quantization** (Q4_K cache, 8-bit cache, etc.) — any quality/perf numbers?
- **Continuous batching** for local single-user setups — worth it or not?
- **AMD-specific model compilation** tools beyond Ryzen AI SDK (anyone using Vitis AI directly?)

## 5. X-Specific: People to Watch

**Sweep posts from these accounts (and their replies/threads) for the last 30-60 days:**
- @sudoingX (AMD benchmark thread curator)
- @browserdotsys (llama.cpp contributor)
- @_philschmid (HuggingFace)
- @rohanpaul_ai (ML engineer, benchmarks)
- @TheOllama (Ollama team)
- @teortextextex (AMD hardware analyst)
- @DrLisaSu (AMD CEO — any AI product announcements)
- @Tim_Dettmers (quantization researcher)
- @geohot (comma.ai, Tinygrad — AMD experiments)
- Anyone else posting AMD+NPU+LLM benchmarks recently

## 6. Reddit/HN/Web to Check

- r/LocalLLaMA — "AMD" or "Ryzen AI" or "Krackan" or "Strix" posts
- r/AMD — NPU or AI acceleration threads
- Hacker News — any AMD AI or local LLM stories
- GitHub trending — new repos for AMD inference, small models, quant tools

## Output Format

Please structure your findings as:

1. **Breaking/High-Impact** — anything that would change how I benchmark or what models I run
2. **New Models to Download** — specific model names + HF repos + recommended quants + why they matter for my hardware
3. **Stack Improvements** — software updates, new backends, or techniques that could improve existing numbers
4. **Interesting Threads/Posts** — X posts or articles worth reading in full (with links)
5. **Rumors/Leaks** — unverified but potentially significant (flagged as such)

My current baselines for reference:
- NPU (XDNA 2, 48 tiles): 7-8B models ≈ 13 t/s decode at ~15W
- Vulkan (RADV GFX1152): 7-8B ≈ 13 t/s, 9B ≈ 11 t/s
- CPU (6c Zen 5): 7-8B ≈ 13 t/s, sub-1B ≈ 367 t/s (cache resident)

Go deep — I want the cutting edge, not the well-known stuff. Surprise me.
