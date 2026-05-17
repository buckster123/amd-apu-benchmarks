# Thread Post: Krackan Point (Ryzen AI 5 340) LLM Benchmarks

**Hardware:** Lenovo IdeaPad Slim 5 · AMD Ryzen AI 5 340 (6c Zen 5) · Radeon 840M iGPU (RDNA3) · 22 GB LPDDR5 · NPU: XDNA 2 (48 AIE tiles, ~16 TOPS)
**OS:** Ubuntu 25.10 · kernel 6.19.13 · llama.cpp Vulkan backend

---

## NPU Results (AMD Ryzen AI SDK 1.7.1, NPU-4K Full-Fusion, turbo pmode)

| Model | Params | pp512 | tg128 | Peak RAM |
|---|---|---:|---:|---:|
| SmolLM2-135M | 0.14 B | 1422 | 137.1 | 1.4 GB |
| Llama-3.2-1B | 1.24 B | 2133 | 64.6 | 6.8 GB |
| Qwen2.5-1.5B | 1.54 B | 1600 | 44.0 | 6.7 GB |
| Qwen2.5-3B | 3.09 B | 985 | 27.0 | 9.0 GB |
| Llama-3.2-3B | 3.21 B | 985 | 25.2 | 10.3 GB |
| Phi-4-mini | 3.84 B | 853 | 22.6 | 13.0 GB |
| Phi-4-mini-reasoning | 3.84 B | 853 | 22.7 | 13.0 GB |
| gemma-3-4b | 4.30 B | 320 | 17.2 | 10.1 GB |
| Mistral-7B | 7.25 B | 582 | 13.6 | 11.9 GB |
| Qwen2.5-7B | 7.62 B | 610 | 13.4 | 14.7 GB |
| DeepSeek-R1-Qwen-7B | 7.62 B | 610 | 13.4 | 14.9 GB |
| Meta-Llama-3.1-8B | 8.03 B | 557 | 13.2 | 15.8 GB |

**Key finding:** 7–8B class lands ~13 t/s decode at ~15W SoC power. NPU beats CPU (12.5 t/s) at lower wattage and destroys iGPU HIP (5.3 t/s). The Krackan 48-tile NPU punches above its weight vs published Strix 64-tile numbers on identical models.

**Did not complete:** gpt-oss-20b (MoE kernel aborts on Krackan tile layout), LFM2 (raw ONNX, needs different runner).

---

## Vulkan iGPU Results (llama.cpp, RADV GFX1152, KHR_coopmat, -ngl 999)

| Model | Params | Quant | pp512 | tg128 |
|---|---|---|---:|---:|
| Qwen2.5-7B | 7.62 B | Q4_K_M | 97.8 | **12.9** |
| Qwen3.5-9B | 8.95 B | Q4_K_M | 88.6 | **11.3** |
| Carnice-9B | 8.95 B | Q6_K | 94.6 | **9.5** |

**Key finding:** Vulkan on the 840M is **2.5× faster** than the old ROCm/HIP stack on the same silicon. A 9B Q4_K_M decodes at 11.3 t/s — within spitting distance of the NPU's 13 t/s on 7–8B. For users without NPU access (older Ryzen, desktop APUs), Vulkan is now the preferred path.

---

## Scaling Law (NPU decode)

Decode t/s roughly follows `100 / params(B)`:
- 0.14B → 137 t/s
- 1.2B → 65 t/s
- 3.8B → 23 t/s
- 7.6B → 13 t/s

Memory-bandwidth-bound on a fixed bus. Clean.

---

## Full reproduction

NPU: https://github.com/buckster123 (report + scripts)
Vulkan: `llama.cpp/build-vulkan/bin/llama-bench -m model.gguf -p 512 -n 128 -ngl 999 -t 6 -r 3`

---

*Contributing to @sudoingX's AMD consumer LLM thread. Numbers are 3-run average, room temp, no thermal throttling observed.*
