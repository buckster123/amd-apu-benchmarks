# ZAYA1-8B Deep Dive

**Build:** llama.cpp PR #23112 (draft branch `zaya1-pr`)
**Status:** BENCH WORKS, GENERATION BROKEN

## Performance

| Test | Prefill | Decode |
|---|---:|---:|
| pp512 / tg128 | 315 t/s | 25.2 t/s |
| pp2048 / tg128 | 312 t/s | 25.7 t/s |
| pp4096 / tg128 | 295 t/s | 25.4 t/s |

## Context Scaling: Excellent
- Prefill drops only **6%** from 512 to 4096 tokens
- Decode stays **flat** across all context lengths
- Compare to dense models: typically 20-30% prefill drop

## Memory Footprint
- Model: 5.17 GiB (Q4_K_M)
- GPU allocation: ~4.9 GiB model + ~0.9 GiB compute
- Total VRAM used: ~5.8 GiB out of 22 GB
- **Leaves 16+ GB free** for OS, KV cache, other apps

## Known Issues (Draft PR)
- `llama-bench`: Works perfectly
- `llama-cli`: Produces empty tokens (generation path bug)
- `llama-server`: Untested, likely same issue
- **Verdict:** Benchmarkable but not chat-ready until PR merges

## Comparison to Dense 8-9B Models

| Model | Decode | Memory | Context Scaling |
|---|---:|---:|:---|
| ZAYA1-8B | **25.2** | 5.2 GB | Excellent (6% drop) |
| Qwen3.5-9B | 11.0 | 5.3 GB | Good |
| Meta-Llama-3.1-8B | 13.1 | 4.4 GB | Good |

ZAYA1 decodes **2.3x faster** than Qwen3.5-9B at similar memory usage.
