"""
Web3Helper — Conversational interface for Web3 operations
Production-ready entry point with multi-model routing.
"""
import os
import json
import time
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, Any
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("web3helper")


@dataclass
class ModelConfig:
    name: str
    endpoint: str
    api_key_env: str
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_1k_in: float = 0.001
    cost_per_1k_out: float = 0.002


MODELS = {
    "mimo": ModelConfig("MiMo-V2-Pro", "https://platform.xiaomimimo.com/api/chat/openai-api/v1/chat/completions", "MIMO_API_KEY"),
    "deepseek": ModelConfig("deepseek-chat", "https://api.deepseek.com/v1/chat/completions", "DEEPSEEK_API_KEY"),
    "claude": ModelConfig("claude-sonnet-4", "https://api.anthropic.com/v1/messages", "ANTHROPIC_API_KEY"),
    "gpt": ModelConfig("gpt-4o", "https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY"),
}


class Router:
    """Cost- and latency-aware model router for Web3Helper."""

    def __init__(self, default: str = "mimo"):
        self.default = default
        self.client = httpx.AsyncClient(timeout=60.0)
        self.stats: dict[str, dict[str, float]] = {m: {"calls": 0, "latency_ms": 0, "cost_usd": 0} for m in MODELS}

    def pick(self, task_type: str) -> str:
        # Cheap default for simple tasks; escalate for complex reasoning
        if task_type in ("simple", "classify", "tag"):
            return "mimo"
        if task_type in ("code", "reason"):
            return "deepseek"
        if task_type in ("longctx", "analyze"):
            return "claude"
        return self.default

    async def call(self, model: str, messages: list[dict[str, str]], max_retries: int = 3) -> str:
        cfg = MODELS[model]
        api_key = os.environ.get(cfg.api_key_env, "")
        if not api_key:
            raise RuntimeError(f"Missing env var {cfg.api_key_env}")

        for attempt in range(max_retries):
            t0 = time.time()
            try:
                payload = {
                    "model": cfg.name,
                    "messages": messages,
                    "max_tokens": cfg.max_tokens,
                    "temperature": cfg.temperature,
                }
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                r = await self.client.post(cfg.endpoint, json=payload, headers=headers)
                r.raise_for_status()
                data = r.json()
                text = data["choices"][0]["message"]["content"]
                elapsed = (time.time() - t0) * 1000
                self.stats[model]["calls"] += 1
                self.stats[model]["latency_ms"] += elapsed
                log.info(f"{model} ok in {elapsed:.0f}ms ({len(text)} chars)")
                return text
            except httpx.HTTPError as e:
                wait = 2 ** attempt
                log.warning(f"{model} attempt {attempt + 1} failed: {e}, retry in {wait}s")
                await asyncio.sleep(wait)
        raise RuntimeError(f"{model} failed after {max_retries} retries")

    def report(self) -> dict[str, Any]:
        return {m: {"calls": s["calls"], "avg_ms": s["latency_ms"] / max(s["calls"], 1)} for m, s in self.stats.items()}


async def run_task(prompt: str, task_type: str = "default") -> str:
    router = Router()
    model = router.pick(task_type)
    log.info(f"Task '{task_type}' routed to {model}")
    return await router.call(model, [{"role": "user", "content": prompt}])


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Web3Helper: Conversational interface for Web3 operations")
    p.add_argument("--task", required=True, help="Task description or prompt")
    p.add_argument("--type", default="default", help="Task type for routing")
    args = p.parse_args()
    result = asyncio.run(run_task(args.task, args.type))
    print(result)
