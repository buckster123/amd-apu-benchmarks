# Thread Post: Krackan Point (Ryzen AI 5 340) LLM Benchmarks

**Hardware:** Lenovo IdeaPad Slim 5 · AMD Ryzen AI 5 340 (6c Zen 5) · Radeon 840M iGPU (RDNA3) · 22 GB LPDDR5 · NPU: XDNA 2 (48 AIE tiles)
**OS:** Ubuntu 25.10 · llama.cpp Vulkan backend (RADV GFX1152, KHR_coopmat)

---

## NPU Results (Ryzen AI SDK 1.7.1, NPU-4K, turbo)

| Model | Params | pp512 | tg128 |
|---|---|---:|---:|
| SmolLM2-135M | 0.14 B | 1422 | **137** |
| Llama-3.2-1B | 1.24 B | 2133 | **65** |
| Qwen2.5-1.5B | 1.54 B | 1600 | 44 |
| Qwen2.5-3B | 3.09 B | 985 | 27 |
| Llama-3.2-3B | 3.21 B | 985 | 25 |
| Phi-4-mini | 3.84 B | 853 | 23 |
| gemma-3-4b | 4.30 B | 320 | 17 |
| Mistral-7B | 7.25 B | 582 | **14** |
| Qwen2.5-7B | 7.62 B | 610 | **13** |
| DeepSeek-R1-Qwen-7B | 7.62 B | 610 | **13** |
| Meta-Llama-3.1-8B | 8.03 B | 557 | **13** |

## Vulkan iGPU Results (llama.cpp, RADV GFX1152, KHR_coopmat, -ngl 999)

| Model | Params | Quant | pp512 | tg128 |
|---|---|---|---:|---:|
| SmolLM2-135M-Instruct | 0.14 B | Q4_K_M | **3042** | **178** |
| Llama-3.2-1B-Instruct | 1.24 B | Q4_K_M | 661 | **73** |
| Phi-4-mini-instruct | 3.84 B | Q4_K_M | 200 | 23 |
| Qwen3.5-4B-Instruct | 3.50 B | Q4_K_M | 160 | 18 |
| ZAYA1-8B | 8.84 B total / 760M active | Q4_K_M | **315** | **25** |
| Mistral-7B-Instruct | 7.25 B | Q4_K_M | 92 | **13** |
| Qwen2.5-7B-Instruct | 7.62 B | Q4_K_M | 99 | 13 |
| DeepSeek-R1-Qwen-7B | 7.62 B | Q4_K_M | 99 | 13 |
| Meta-Llama-3.1-8B | 8.03 B | Q4_K_M | 91 | 13 |
| Qwen3.5-9B-Instruct | 8.95 B | Q4_K_M | 88 | **11** |
| Carnice-9B | 8.95 B | Q6_K | 94 | 10 |
| gemma-3-12b-it | 11.77 B | Q4_K_M | 61 | 8 |
| Mistral-Nemo-12B | 12.25 B | Q4_K_M | 64 | 8 |

| Model | Params | Quant | pp512 | tg128 |
|---|---|---|---:|---:|
| SmolLM2-135M | 0.14 B | Q4_K_M | 2391 | **367** |
| Llama-3.2-1B | 1.24 B | Q4_K_M | 685 | 68 |
| Qwen3.5-4B | 3.50 B | Q4_K_M | 196 | 16 |
| Phi-4-mini | 3.84 B | Q4_K_M | 244 | 23 |
| Qwen2.5-7B | 7.62 B | Q4_K_M | 136 | 13 |
| Mistral-7B | 7.25 B | Q4_K_M | 124 | 13 |
| DeepSeek-R1-Qwen-7B | 7.62 B | Q4_K_M | 135 | 13 |
| Meta-Llama-3.1-8B | 8.03 B | Q4_K_M | 126 | 12 |
| Qwen3.5-9B | 8.95 B | Q4_K_M | 122 | 10 |
| Carnice-9B | 8.95 B | Q6_K | 105 | 8 |

---

## Cross-Backend Winners (decode)

| Model | Best Backend | Tok/s | Why |
|---|---|---:|:---|
| SmolLM2-135M | **CPU** | 367 | Fits in L3 cache, no GPU overhead |
| Llama-3.2-1B | **Vulkan** | 73 | iGPU parallelism edges CPU |
| Phi-4-mini | **Vulkan** | 23 | 3-way tie; Vulkan by a hair |
| Qwen2.5-7B | **NPU** | 13.4 | Dedicated AI engine wins at this scale |
| Mistral-7B | **NPU** | 13.6 | Same — NPU sweet spot |
| Meta-Llama-3.1-8B | **NPU** | 13.2 | Same — NPU sweet spot |
| Qwen3.5-9B | **Vulkan** | 11.0 | iGPU bandwidth > NPU at 9B |
| Carnice-9B | **Vulkan** | 9.6 | Q6_K bandwidth-bound; iGPU wins |

## Key Takeaways

1. **Sub-1B: CPU wins** — models live in cache; GPU dispatch is pure overhead
2. **1–4B: Vulkan wins** — iGPU parallelism pays off; NPU not available for all
3. **7–8B: NPU wins** — dedicated XDNA tiles are most efficient here (~15W, ~13 t/s)
4. **9B+: Vulkan wins** — raw memory bandwidth exceeds NPU capacity
5. **Vulkan is 2.5× faster than old HIP** — RADV + KHR_coopmat is the real deal

---

*Contributing to @sudoingX's AMD consumer LLM thread. All numbers 3-run average. Full report + scripts: github.com/buckster123*
