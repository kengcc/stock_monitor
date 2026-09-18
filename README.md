# Stock Monitor

> **Disclaimer:** This is an experimental repo for trying out agentic coding and harness engineering. Don't take the functionality seriously.

[English](#english) | [中文](#中文)

---

## English

AI-powered stock news monitoring with Telegram bot interface. Aggregates news from multiple free sources, analyzes with AI, and delivers summaries via Telegram.

### Screenshots

| Summary List | Detailed Analysis | Breaking News |
|:---:|:---:|:---:|
| ![Summary](docs/images/summary.png) | ![Detail](docs/images/detail.png) | ![Breaking](docs/images/breaking.png) |

### Features

- **Multi-source news aggregation** - Yahoo Finance, Google News, Seeking Alpha, MarketWatch (free RSS), Finnhub API
- **AI-powered analysis** - Works with any OpenAI-compatible API (DeepSeek, OpenAI, Groq, Ollama, etc.)
- **Telegram bot** - `/add`, `/remove`, `/priority`, `/list`, `/summary`, `/health` commands with inline buttons
- **Watchlist priorities** - Rank stocks as CRITICAL, HIGH, MEDIUM, or LOW
- **Two-level summary** - Compact overview list + click for detailed analysis
- **Daily auto-push** - Summary before US market open (7:30 AM ET)
- **Breaking news alerts** - Hourly check for urgent high-impact news
- **Bilingual output** - Chinese or English (`LANGUAGE=zh` or `LANGUAGE=en`)
- **Caching** - `/summary` returns cached results instantly, zero extra API cost

### Quick Start

```bash
git clone https://github.com/wangkayn/stock_monitor.git
cd stock_monitor

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API keys (see Configuration below)

mkdir -p data logs
python main.py
```

### Configuration

Copy `.env.example` to `.env` and fill in:

#### Required

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Create via [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `AI_API_KEY` | API key for your AI provider |
| `AI_BASE_URL` | API endpoint (see AI Providers below) |
| `AI_MODEL` | Model name |

#### AI Providers

Any OpenAI-compatible API works:

| Provider | BASE_URL | MODEL | Cost |
|----------|----------|-------|------|
| **DeepSeek** | `https://api.deepseek.com` | `deepseek-chat` | ~$0.001/summary |
| OpenAI | _(leave empty)_ | `gpt-4o-mini` | ~$0.01/summary |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.1-70b-versatile` | Free tier |
| Ollama | `http://localhost:11434/v1` | `llama3` | Free (local) |

#### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGUAGE` | `zh` | Output language: `zh` (Chinese) or `en` (English) |
| `FINNHUB_API_KEY` | - | [Finnhub](https://finnhub.io) API key (free, recommended) |
| `CHECK_INTERVAL_MINUTES` | `60` | News fetch interval |
| `DAILY_SUMMARY_TIME` | `07:30` | Daily push time (ET) |

### Bot Commands

| Command | Description |
|---------|-------------|
| `/add TICKER [PRIORITY]` | Add stock with optional priority (defaults to MEDIUM) |
| `/priority TICKER PRIORITY` | Change priority to LOW, MEDIUM, HIGH, or CRITICAL |
| `/remove TICKER` | Remove stock |
| `/list` | View watchlist ranked from CRITICAL to LOW |
| `/summary` | Get cached summary (click for details) |
| `/health` | Check bot runtime status |
| `/help` | Show help |

### How It Works

```
Startup → Initial fetch → Cache
                ↓
Every 60 min → Fetch news (RSS+API) → AI analyze → Update cache → Check breaking news
                ↓
07:30 daily → Fetch + Analyze → Auto-push to Telegram
                ↓
/summary → Return cached result instantly (no API call)
/health → Show runtime status and last fetch time
```

### News Sources

**Free (no API key needed):** Yahoo Finance RSS, Google News RSS, Seeking Alpha RSS, MarketWatch RSS

**API (free tier):** Finnhub (60 calls/min), NewsAPI (100 req/day)

### Running as a Service

```bash
./start.sh              # Start in background
./stop.sh               # Stop
tail -f logs/stock_monitor.log  # View logs
```

### Project Structure

```
main.py                     # Entry point, scheduler, caching
src/
  ai_analyzer.py            # AI analysis (OpenAI-compatible)
  news_fetcher.py           # News aggregation (RSS + API)
  social_fetcher.py         # Social media (Reddit/Twitter)
  stock_manager.py          # Watchlist management
  chat/
    base.py                 # ChatAdapter abstract base class
    telegram_adapter.py     # Telegram implementation
  locale/
    zh.py                   # Chinese strings
    en.py                   # English strings
```

### Architecture

See the [Mermaid architecture diagram](docs/architecture/README.md).

---

## 中文

> **说明：** 这是一个用于探索智能体编程（agentic coding）和 harness 工程的实验性仓库，请勿将其功能当回事。

AI 驱动的股票新闻监控系统，通过 Telegram Bot 推送新闻摘要和突发新闻提醒。

### 截图展示

| 摘要列表 | 详细分析 | 突发新闻 |
|:---:|:---:|:---:|
| ![摘要](docs/images/summary.png) | ![详情](docs/images/detail.png) | ![突发](docs/images/breaking.png) |

### 功能特点

- **多源新闻聚合** - Yahoo Finance、Google News、Seeking Alpha、MarketWatch (免费 RSS) + Finnhub API
- **AI 智能分析** - 支持任意 OpenAI 兼容 API（DeepSeek、OpenAI、Groq、Ollama 等）
- **Telegram 机器人** - `/add`、`/remove`、`/priority`、`/list`、`/summary`、`/health` 命令 + 内联按钮交互
- **关注优先级** - 使用 CRITICAL、HIGH、MEDIUM 或 LOW 对股票进行分级
- **两级摘要** - 紧凑概览列表 + 点击查看详细分析
- **每日自动推送** - 美股开盘前自动推送摘要（7:30 AM ET）
- **突发新闻提醒** - 每小时检测紧急高影响新闻
- **双语输出** - 支持中文或英文输出（`LANGUAGE=zh` 或 `LANGUAGE=en`）
- **缓存机制** - `/summary` 秒回缓存结果，零额外 API 消耗

### 快速开始

```bash
git clone https://github.com/wangkayn/stock_monitor.git
cd stock_monitor

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 编辑 .env 填入你的 API Key（参考下方配置说明）

mkdir -p data logs
python main.py
```

### 配置说明

将 `.env.example` 复制为 `.env` 并填写：

#### 必填项

| 变量 | 说明 |
|------|------|
| `TELEGRAM_BOT_TOKEN` | 通过 [@BotFather](https://t.me/BotFather) 创建 |
| `TELEGRAM_CHAT_ID` | 你的 Telegram 聊天 ID |
| `AI_API_KEY` | AI 服务商的 API Key |
| `AI_BASE_URL` | API 地址（见下方 AI 服务商列表） |
| `AI_MODEL` | 模型名称 |

#### AI 服务商

支持任意 OpenAI 兼容 API：

| 服务商 | BASE_URL | MODEL | 费用 |
|--------|----------|-------|------|
| **DeepSeek（推荐）** | `https://api.deepseek.com` | `deepseek-chat` | ~¥0.007/次 |
| OpenAI | _(留空)_ | `gpt-4o-mini` | ~¥0.07/次 |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.1-70b-versatile` | 免费额度 |
| Ollama | `http://localhost:11434/v1` | `llama3` | 免费（本地） |

#### 可选项

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LANGUAGE` | `zh` | 输出语言：`zh`（中文）或 `en`（英文） |
| `FINNHUB_API_KEY` | - | [Finnhub](https://finnhub.io) API Key（免费，推荐） |
| `CHECK_INTERVAL_MINUTES` | `60` | 新闻抓取间隔（分钟） |
| `DAILY_SUMMARY_TIME` | `07:30` | 每日推送时间（美东时间） |

### 机器人命令

| 命令 | 说明 |
|------|------|
| `/add 代码 [优先级]` | 添加股票并可指定优先级（默认为 MEDIUM） |
| `/priority 代码 优先级` | 将优先级修改为 LOW、MEDIUM、HIGH 或 CRITICAL |
| `/remove 代码` | 移除股票 |
| `/list` | 按 CRITICAL 到 LOW 查看关注列表 |
| `/summary` | 获取缓存摘要（点击查看详情） |
| `/health` | 检查机器人运行状态 |
| `/help` | 显示帮助 |

### 工作流程

```
启动 → 首次抓取 → 缓存
          ↓
每 60 分钟 → 抓取新闻 (RSS+API) → AI 分析 → 更新缓存 → 检测突发新闻
          ↓
每日 07:30 → 抓取 + 分析 → 自动推送到 Telegram
          ↓
/summary → 直接返回缓存结果（无 API 调用）
/health → 显示运行状态和上次抓取时间
```

### 新闻源

**免费（无需 API Key）：** Yahoo Finance RSS、Google News RSS、Seeking Alpha RSS、MarketWatch RSS

**API（免费额度）：** Finnhub（60次/分钟）、NewsAPI（100次/天）

### 架构图

查看 [Mermaid 架构图](docs/architecture/README.md)。

---

## License

MIT
