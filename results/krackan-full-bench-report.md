# Krackan Point (Ryzen AI 5 340) Cross-Backend LLM Benchmark

**Hardware:** Lenovo IdeaPad Slim 5 · AMD Ryzen AI 5 340 (6c Zen 5) · Radeon 840M iGPU (RDNA3) · 22 GB LPDDR5 · NPU: XDNA 2 (48 AIE tiles)
**OS:** Ubuntu 25.10 · kernel 6.19.13-061913-generic
**Backends:** NPU (Ryzen AI SDK 1.7.1) · Vulkan (llama.cpp RADV GFX1152) · CPU (6 threads)
**Date:** May 2026

---

## Complete Results: Decode Throughput (tok/s)

| Model | Params | Quant | NPU | Vulkan | CPU | Winner |
|---|---|---:|---:|---:|---:|:---|
| SmolLM2-135M-Instruct | 0.14 B | Q4_K_M | 137.1 | 178.4 | **366.7** | CPU |
| Llama-3.2-1B-Instruct | 1.24 B | Q4_K_M | 64.6 | **72.8** | 68.1 | Vulkan |
| Qwen3.5-4B-Instruct | 3.50 B | Q4_K_M | — | **17.5** | 16.2 | Vulkan |
| Phi-4-mini-instruct | 3.84 B | Q4_K_M | 22.6 | **23.3** | 22.8 | Vulkan |
| Qwen2.5-7B-Instruct | 7.62 B | Q4_K_M | **13.4** | 13.2 | 13.2 | NPU |
| Mistral-7B-Instruct | 7.25 B | Q4_K_M | **13.6** | 13.4 | 13.3 | NPU |
| DeepSeek-R1-Distill-Qwen-7B | 7.62 B | Q4_K_M | **13.4** | 13.1 | 13.1 | NPU |
| Meta-Llama-3.1-8B-Instruct | 8.03 B | Q4_K_M | **13.2** | 13.1 | 12.4 | NPU |
| Qwen3.5-9B-Instruct | 8.95 B | Q4_K_M | — | **11.0** | 10.0 | Vulkan |
| Carnice-9B | 8.95 B | Q6_K | — | **9.6** | 8.1 | Vulkan |

**Config:** 512-token prompt, 128-token generation, 3 repetitions, batch=1.

## Complete Results: Prompt Processing (tok/s)

| Model | Params | NPU | Vulkan | CPU |
|---|---|---:|---:|---:|
| SmolLM2-135M | 0.14 B | 1422 | **3042** | 2391 |
| Llama-3.2-1B | 1.24 B | **2133** | 661 | 685 |
| Qwen3.5-4B | 3.50 B | — | 160 | **196** |
| Phi-4-mini | 3.84 B | **853** | 200 | 244 |
| Qwen2.5-7B | 7.62 B | **610** | 99 | 136 |
| Mistral-7B | 7.25 B | **582** | 92 | 124 |
| DeepSeek-R1-Qwen-7B | 7.62 B | **610** | 99 | 135 |
| Meta-Llama-3.1-8B | 8.03 B | **557** | 91 | 126 |
| Qwen3.5-9B | 8.95 B | — | 88 | **122** |
| Carnice-9B | 8.95 B | — | 94 | **105** |

---

## Key Findings

### 1. Backend choice depends heavily on model size

| Size Class | Best Backend | Why |
|---|---|---|
| **Sub-1B** | CPU | Model fits in L3 cache; no GPU dispatch overhead |
| **1–4B** | Vulkan | iGPU parallelism exceeds CPU; NPU not available for all |
| **7–8B** | NPU | Dedicated AI engine wins on efficiency; decode ~13 t/s |
| **9B+** | Vulkan | iGPU has more raw bandwidth than NPU at this scale |

### 2. The NPU "sweet spot" is 7–8B params

At 7–8B, the NPU delivers the best decode throughput (~13 t/s) while using only ~15W SoC power. The CPU matches on decode but uses more power (~25–30W). The iGPU is slightly behind on decode but much slower on prefill.

### 3. CPU is surprisingly competitive

For Qwen2.5-7B Q4_K_M, the 6-core Zen 5 CPU does **13.2 t/s decode** — essentially matching both NPU (13.4) and Vulkan (13.2). The Zen 5 architecture's IPC improvements and AVX-512-like wide vectors make it a viable fallback.

### 4. Q6_K penalty is real

Carnice-9B at Q6_K decodes at 9.6 t/s (Vulkan) vs Qwen3.5-9B at Q4_K_M doing 11.0 t/s. Same parameter count, ~15% slower from higher precision weights. Memory bandwidth bound.

### 5. Vulkan has matured massively

Compared to the old ROCm/HIP stack (5.3 t/s on Qwen2.5-7B in our April tests), the RADV Vulkan + KHR_coopmat path now delivers **13.2 t/s** — a **2.5× improvement**. This makes the 840M a legitimate inference backend, not just a display driver.

---

## Power Efficiency (estimated)

| Backend | 7B Decode | SoC Power | Efficiency (tok/s/W) |
|---|---:|---:|---:|
| NPU | 13.4 | ~15W | **0.89** |
| Vulkan | 13.2 | ~18W | 0.73 |
| CPU | 13.2 | ~28W | 0.47 |

*NPU power estimated from xrt-smi sensors; CPU/Vulkan from powertop package power. Estimates, not measured directly.*

---

## Reproduction

```bash
# NPU bench (requires Ryzen AI SDK 1.7.1)
model_benchmark -i model_dir/ -l 128 -g 128 -r 3 -w 1 -f prompt.txt

# Vulkan bench
~/llama.cpp/build-vulkan/bin/llama-bench -m model.gguf -p 512 -n 128 -ngl 999 -t 6 -r 3 --output md

# CPU bench
~/llama.cpp/build/bin/llama-bench -m model.gguf -p 512 -n 128 -ngl 0 -t 6 -r 3 --output md
```

---

*Benchmark suite: 10 models × 3 backends = 30 test configurations. All numbers are 3-run averages. Room temperature, no thermal throttling observed. NPU data from Apr 21 2026 sweep; Vulkan/CPU from May 17 2026.*

## Session 2 Update (May 17 2026)

- Rebuilt llama.cpp from mainline (39cf5d619 / b9199): ~5% Vulkan prefill improvement
- MTP speculative decoding (--spec-type draft-mtp) now available in build
- MTP is Qwen3.6-27B DENSE ONLY — 35B-A3B MoE does NOT support speculative decode
- Unsloth Dynamic 2.0 quants available for Qwen3.6-27B/35B-A3B

## Session 3 Update (May 17 2026) — Grok-Recommended Models Tested

### Zyphra/ZAYA1-8B — FAILED
- **Status:** Unknown architecture 'zaya' — not yet supported in llama.cpp (b9199)
- **Note:** Model downloaded (5.2GB Q4_K_M) but cannot load. Community GGUFs exist but llama.cpp lacks the architecture definition.
- **Action required:** Wait for llama.cpp PR or use alternative inference engine (vLLM, transformers)

### google/gemma-3-12b-it — TESTED
| Backend | pp512 | tg128 | Notes |
|---|---:|---:|:---|
| Vulkan (-ngl 999) | 61.0 | **7.55** | Slower than expected; gemma architecture less Vulkan-optimized |
| ROCm/CPU (-ngl 0) | 79.6 | 6.95 | CPU build fell back to ROCm; decode similar to Vulkan |

**Analysis:** gemma-3-12B is **slower than Qwen3.5-9B** (7.6 vs 11.0 t/s decode) despite having more parameters. The gemma architecture doesn't leverage KHR_coopmat as efficiently as Qwen/Llama on AMD. Grok's 10-13 t/s prediction was optimistic for this hardware.

**Verdict:** Qwen3.5-9B remains the better choice for this machine. gemma-3-12B might shine with vision tasks (multimodal) but for text-only chat, it's a downgrade.

## Session 4 Update (May 17 2026) — Grok-Recommended Models + Final Dataset

### Final Dataset: 12 Models Tested

| Model | Params | Vulkan pp | Vulkan tg | CPU pp | CPU tg |
|---|---|---:|---:|---:|---:|
| SmolLM2-135M | 0.14 B | 3042.5 | **178.4** | 2390.7 | **366.7** |
| Llama-3.2-1B | 1.24 B | 660.8 | **72.8** | 684.9 | 68.1 |
| Phi-4-mini | 3.84 B | 199.5 | **23.3** | 244.3 | 22.8 |
| Qwen3.5-4B | 3.50 B | 160.1 | **17.5** | 196.4 | 16.2 |
| Mistral-7B | 7.25 B | 92.2 | **13.4** | 124.3 | 13.3 |
| Qwen2.5-7B | 7.62 B | 98.6 | **13.2** | 135.5 | 13.2 |
| DeepSeek-R1-Qwen-7B | 7.62 B | 98.9 | **13.1** | 135.1 | 13.1 |
| Meta-Llama-3.1-8B | 8.03 B | 90.6 | **13.1** | 126.0 | 12.4 |
| Qwen3.5-9B | 8.95 B | 88.2 | **11.0** | 122.4 | 10.0 |
| Carnice-9B | 8.95 B | 93.6 | **9.6** | 105.4 | 8.1 |
| gemma-3-12B | 11.77 B | 61.0 | 7.55 | 79.6 | 6.95 |
| Mistral-Nemo-12B | 12.25 B | 63.7 | 8.24 | 80.9 | 7.33 |

### Key Finding: Architecture Efficiency on AMD Vulkan

**Qwen architecture dominates on AMD KHR_coopmat:**
- Qwen3.5-9B (8.95B params): **11.0 t/s** decode
- gemma-3-12B (11.77B params): **7.55 t/s** decode (-31%)
- Mistral-Nemo-12B (12.25B params): **8.24 t/s** decode (-25%)

More parameters does NOT equal better speed. Qwen's MLP structure maps significantly better to AMD's coopmat path than Gemma's gated MLP or Mistral's sliding window attention.

### ZAYA1-8B: Unsupported
- llama.cpp PR #23112 (branch: Zaya1) adds support but is still DRAFT
- Fetched branch successfully but not built/tested this session
- Expected to be the "AMD-native" star once merged

### Qwen3.6-27B/35B-A3B: Deferred
- 16-17GB+ Q4_K_M, tight fit on 22GB RAM
- MTP speculative decoding confirmed available in b9199 build
- 35B-A3B MoE does NOT support MTP (dense-only)


## ZAYA1-8B Deep Dive

**Build:** llama.cpp PR #23112 (draft branch `zaya1-pr`)
**Status:** BENCH WORKS, GENERATION BROKEN

### Performance

| Test | Prefill | Decode |
|---|---:|---:|
| pp512 / tg128 | 315 t/s | 25.2 t/s |
| pp2048 / tg128 | 312 t/s | 25.7 t/s |
| pp4096 / tg128 | 295 t/s | 25.4 t/s |

### Context Scaling: Excellent
- Prefill drops only **6%** from 512 to 4096 tokens
- Decode stays **flat** across all context lengths
- Compare to dense models: typically 20-30% prefill drop

### Memory Footprint
- Model: 5.17 GiB (Q4_K_M)
- GPU allocation: ~4.9 GiB model + ~0.9 GiB compute
- Total VRAM used: ~5.8 GiB out of 22 GB
- **Leaves 16+ GB free** for OS, KV cache, other apps

### Known Issues (Draft PR)
- `llama-bench`: Works perfectly
- `llama-cli`: Produces empty tokens (generation path bug)
- `llama-server`: Untested, likely same issue
- **Verdict:** Benchmarkable but not chat-ready until PR merges

### Comparison to Dense 8-9B Models

| Model | Decode | Memory | Context Scaling |
|---|---:|---:|:---|
| ZAYA1-8B | **25.2** | 5.2 GB | Excellent (6% drop) |
| Qwen3.5-9B | 11.0 | 5.3 GB | Good |
| Meta-Llama-3.1-8B | 13.1 | 4.4 GB | Good |

ZAYA1 decodes **2.3x faster** than Qwen3.5-9B at similar memory usage.
