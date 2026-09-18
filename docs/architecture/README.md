# Stock Monitor architecture

The application is a single long-running Python process. It receives Telegram commands through outbound long polling; it does not expose an HTTP endpoint or webhook.

```mermaid
flowchart LR
    User[Telegram user]
    Telegram[Telegram Bot API]

    subgraph App[Stock Monitor process]
        Adapter[Telegram adapter]
        Monitor[StockMonitor orchestrator]
        Scheduler[Scheduler and watchdog]
        Manager[Stock manager]
        Fetchers[News and social fetchers]
        Analyzer[AI analyzer]
        Cache[In-memory summary cache]
    end

    Stocks[(data/stocks.json)]
    Sources[News and social sources]
    AI[OpenAI-compatible API]

    User -->|Bot commands| Telegram
    Adapter -->|Long polling| Telegram
    Telegram -->|Updates| Adapter
    Adapter -->|Watchlist commands| Manager
    Adapter -->|Summary and health requests| Monitor
    Adapter -->|Replies and alerts| Telegram

    Scheduler -->|Scheduled fetch| Monitor
    Monitor --> Manager
    Manager <--> Stocks
    Monitor --> Fetchers
    Fetchers --> Sources
    Monitor --> Analyzer
    Analyzer --> AI
    Monitor <--> Cache
    Monitor -->|Summaries and breaking alerts| Adapter
```

Priority ranking affects only the watchlist displayed by `/list`. Background fetching continues to use the persisted watchlist order.
