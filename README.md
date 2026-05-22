# Web3Helper

> Chat to interact with Web3

Conversational interface for Web3 operations

## Overview

Web3Helper is a production-grade web3 toolkit built to streamline real-world AI workflows. It integrates multiple state-of-the-art language models — including MiMo, DeepSeek, Claude, and GPT — through a unified interface, enabling developers to mix-and-match models per task while keeping latency, cost, and reliability under tight control.

## Features

- **Multi-model routing** — automatic selection between MiMo, DeepSeek, Claude, and GPT based on task type, cost, and latency requirements
- **Streaming inference** — first-token latency under 200ms with backpressure handling
- **Failover and retry** — circuit breaker pattern with exponential backoff across providers
- **Cost tracking** — per-request token accounting with budget alerts
- **Caching layer** — semantic deduplication of similar requests via embedding hash
- **Observability** — structured logging, OpenTelemetry traces, and Prometheus metrics
- **Async-first** — built on asyncio with native batching support
- **Plug-and-play** — drop-in CLI plus Python SDK with type-safe interfaces

## Quick Start

```bash
pip install -r requirements.txt
export MIMO_API_KEY="your_mimo_key"
python main.py --task "your task here"
```

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │───▶│  Router/Cache│───▶│  MiMo / DSK  │
│   (CLI/SDK)  │    │   (FastAPI)  │    │   Claude/GPT │
└──────────────┘    └──────────────┘    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Postgres +  │
                    │    Redis     │
                    └──────────────┘
```

## Models Used

- **MiMo-V2-Pro** — primary inference for cost-sensitive tasks
- **DeepSeek-V3** — code and reasoning
- **Claude Sonnet** — analysis, long context
- **GPT-4o** — creative generation, function calling

## Development

Built with Python 3.11+, FastAPI, Pydantic, asyncio. Tested on Linux/macOS.

## License

MIT
