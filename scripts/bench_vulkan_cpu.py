#!/usr/bin/env python3
"""
Krackan Vulkan + CPU GGUF Benchmark Pipeline
Downloads models if missing, runs llama-bench for both backends, writes JSON results.
"""
import json, os, subprocess, sys, time, re, glob
from pathlib import Path

LLAMA_BENCH_VK = "/home/andre/llama.cpp/build-vulkan/bin/llama-bench"
LLAMA_BENCH_CPU = "/home/andre/llama.cpp/build/bin/llama-bench"
MODELS_DIR = Path("/home/andre/models")
RESULTS_DIR = Path("/home/andre/models/results")
RESULTS_DIR.mkdir(exist_ok=True)

# Focused model list: repo -> {filename, size_estimate_gb, params_b}
MODELS = {
    "SmolLM2-135M": {
        "repo": "bartowski/SmolLM2-135M-Instruct-GGUF",
        "file": "SmolLM2-135M-Instruct-Q4_K_M.gguf",
        "params": 0.14,
    },
    "Llama-3.2-1B": {
        "repo": "bartowski/Llama-3.2-1B-Instruct-GGUF",
        "file": "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "params": 1.24,
    },
    "Qwen3.5-4B": {
        "repo": "bartowski/Qwen_Qwen3.5-4B-GGUF",
        "file": "Qwen_Qwen3.5-4B-Q4_K_M.gguf",
        "params": 3.5,
    },
    "Phi-4-mini": {
        "repo": "bartowski/microsoft_Phi-4-mini-instruct-GGUF",
        "file": "microsoft_Phi-4-mini-instruct-Q4_K_M.gguf",
        "params": 3.84,
    },
    "Mistral-7B": {
        "repo": "bartowski/Mistral-7B-Instruct-v0.3-GGUF",
        "file": "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "params": 7.25,
    },
    "DeepSeek-R1-Distill-Qwen-7B": {
        "repo": "bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF",
        "file": "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
        "params": 7.62,
    },
    "Meta-Llama-3.1-8B": {
        "repo": "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
        "file": "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "params": 8.03,
    },
}

# Already on disk (may need manual handling for shards)
EXISTING = {
    "Qwen2.5-7B": {
        "path": MODELS_DIR / "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf",
        "params": 7.62,
    },
    "Qwen3.5-9B": {
        "path": MODELS_DIR / "Qwen3.5-9B-Q4_K_M.gguf",
        "params": 8.95,
    },
    "Carnice-9B": {
        "path": MODELS_DIR / "carnice-9b/Carnice-9b-Q6_K.gguf",
        "params": 8.95,
    },
}

def download_model(name, info):
    path = MODELS_DIR / info["file"]
    if path.exists():
        print(f"[SKIP] {name}: already present")
        return path
    print(f"[DOWNLOAD] {name} from {info['repo']}")
    url = f"https://huggingface.co/{info['repo']}/resolve/main/{info['file']}"
    # Use wget for resume support
    cmd = ["wget", "-q", "--show-progress", "-c", "-O", str(path), url]
    rc = subprocess.call(cmd)
    if rc != 0 or not path.exists():
        print(f"[FAIL] {name} download failed")
        return None
    return path

def run_bench(path, backend="vulkan", ngl=999):
    bench_bin = LLAMA_BENCH_VK if backend == "vulkan" else LLAMA_BENCH_CPU
    out_file = RESULTS_DIR / f"{path.stem}_{backend}.json"
    cmd = [
        bench_bin,
        "-m", str(path),
        "-p", "512",
        "-n", "128",
        "-ngl", str(ngl),
        "-t", "6",
        "-r", "3",
        "--output", "json",
    ]
    print(f"  -> bench {backend} ...")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        print(f"  -> TIMEOUT on {backend}")
        return None
    if proc.returncode != 0:
        err = proc.stderr[-500:] if proc.stderr else ""
        print(f"  -> ERROR rc={proc.returncode}: {err}")
        return None
    # Parse JSON from stdout
    stdout = proc.stdout.strip()
    if stdout.startswith("["):
        try:
            data = json.loads(stdout)
            with open(out_file, "w") as f:
                json.dump(data, f, indent=2)
            return data
        except json.JSONDecodeError:
            pass
    # Fallback: try line-by-line
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("[") or line.startswith("{"):
            try:
                data = json.loads(line)
                with open(out_file, "w") as f:
                    json.dump(data, f, indent=2)
                return data
            except json.JSONDecodeError:
                continue
    # Final fallback
    print(f"  -> no JSON found, scraping stdout")
    return {"raw": stdout[:2000]}

def extract_pp_tg(data):
    """Extract pp512 and tg128 from llama-bench JSON output.
    llama-bench --output json returns a list of objects with:
      n_prompt: prompt length (512 for pp, 0 for tg)
      n_gen: gen length (128 for tg, 0 for pp)
      avg_ts: average tok/s
    """
    pp = tg = None
    if isinstance(data, list):
        for entry in data:
            n_prompt = entry.get("n_prompt", 0)
            n_gen = entry.get("n_gen", 0)
            avg_ts = entry.get("avg_ts")
            if n_prompt == 512 and n_gen == 0:
                pp = avg_ts
            elif n_prompt == 0 and n_gen == 128:
                tg = avg_ts
    return pp, tg

def main():
    all_results = {}

    # 1. Download missing models
    print("=== Phase 1: Downloads ===")
    for name, info in MODELS.items():
        download_model(name, info)

    # 2. Benchmark downloaded models
    print("\n=== Phase 2: Vulkan Bench ===")
    for name, info in MODELS.items():
        path = MODELS_DIR / info["file"]
        if not path.exists():
            continue
        print(f"[{name}] Vulkan")
        data = run_bench(path, "vulkan", ngl=999)
        pp, tg = extract_pp_tg(data) if data else (None, None)
        all_results.setdefault(name, {})["vulkan"] = {"pp512": pp, "tg128": tg, "params": info["params"]}

    print("\n=== Phase 3: CPU Bench ===")
    for name, info in MODELS.items():
        path = MODELS_DIR / info["file"]
        if not path.exists():
            continue
        print(f"[{name}] CPU")
        data = run_bench(path, "cpu", ngl=0)
        pp, tg = extract_pp_tg(data) if data else (None, None)
        all_results.setdefault(name, {})["cpu"] = {"pp512": pp, "tg128": tg}

    # 3. Benchmark existing models
    print("\n=== Phase 4: Existing Models ===")
    for name, info in EXISTING.items():
        path = info["path"]
        if not path.exists():
            continue
        print(f"[{name}] Vulkan + CPU")
        data_vk = run_bench(path, "vulkan", ngl=999)
        pp_vk, tg_vk = extract_pp_tg(data_vk) if data_vk else (None, None)
        data_cpu = run_bench(path, "cpu", ngl=0)
        pp_cpu, tg_cpu = extract_pp_tg(data_cpu) if data_cpu else (None, None)
        all_results[name] = {
            "vulkan": {"pp512": pp_vk, "tg128": tg_vk, "params": info["params"]},
            "cpu": {"pp512": pp_cpu, "tg128": tg_cpu},
        }

    # 4. Save summary
    summary_path = RESULTS_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n=== Summary written to {summary_path} ===")
    print(json.dumps(all_results, indent=2))

if __name__ == "__main__":
    main()
