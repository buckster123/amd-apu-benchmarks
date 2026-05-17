# AMD APU LLM Benchmarks

Cross-backend LLM inference benchmarks on AMD consumer APUs. NPU, Vulkan iGPU, and CPU — real numbers on real hardware.

## Hardware Under Test

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen AI 5 340 (6c/12t Zen 5) |
| iGPU | AMD Radeon 840M (RDNA3, RADV GFX1152) |
| NPU | AMD XDNA 2 (48 AIE tiles, ~16 TOPS) |
| RAM | 22 GB LPDDR5 (unified) |
| OS | Ubuntu 25.10 |

## Latest Results

**12 models tested across Vulkan + CPU (24 configs).**

Top performers (decode tok/s, Vulkan):

| Model | Params | Decode | Prefill |
|---|---|---:|---:|
| SmolLM2-135M | 0.14B | 178 | 3042 |
| Llama-3.2-1B | 1.24B | 73 | 661 |
| Phi-4-mini | 3.84B | 23 | 200 |
| Qwen3.5-4B | 3.50B | 18 | 160 |
| Mistral-7B | 7.25B | 13 | 92 |
| Qwen2.5-7B | 7.62B | 13 | 99 |
| Meta-Llama-3.1-8B | 8.03B | 13 | 91 |
| Qwen3.5-9B | 8.95B | 11 | 88 |
| gemma-3-12B | 11.77B | 8 | 61 |
| Mistral-Nemo-12B | 12.25B | 8 | 64 |

See [results/](results/) for full data, charts, and thread-ready posts.

## Key Finding

**Qwen architecture dominates on AMD Vulkan.** At 9B parameters, Qwen3.5-9B decodes at 11 t/s — 31% faster than gemma-3-12B (7.55 t/s) and 25% faster than Mistral-Nemo-12B (8.24 t/s), despite having fewer parameters.

Architecture efficiency > parameter count on KHR_coopmat.

## Reproduction

```bash
# Vulkan
~/llama.cpp/build-vulkan/bin/llama-bench -m model.gguf -p 512 -n 128 -ngl 999 -t 6 -r 3 --output md

# CPU
~/llama.cpp/build/bin/llama-bench -m model.gguf -p 512 -n 128 -ngl 0 -t 6 -r 3 --output md
```

## Contributing

Drop a PR with your AMD APU numbers. Include model, quant, backend, and 3-run averages.

## License

CC-BY 4.0 — cite the hardware spec when republishing numbers.
