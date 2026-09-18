STRINGS = {
    # Bot commands (autocomplete menu)
    "cmd_summary": "Get market summary for all stocks",
    "cmd_list": "View watchlist",
    "cmd_add": "Add stock to watchlist",
    "cmd_priority": "Change a stock priority",
    "cmd_remove": "Remove stock from watchlist",
    "cmd_help": "Show help",
    "cmd_health": "Check bot health status",

    # /start
    "welcome": (
        "👋 **Welcome to Stock Monitor!**\n\n"
        "I help you track financial news and social media discussions.\n\n"
        "**Commands:**\n"
        "/add <TICKER> [PRIORITY] - Add stock\n"
        "/priority <TICKER> <PRIORITY> - Change priority\n"
        "/remove <TICKER> - Remove stock\n"
        "/list - View watchlist\n"
        "/summary - Get market summary\n"
        "/health - Check bot health status\n"
        "/help - Show help\n\n"
        "📊 **Auto Updates:**\n"
        "• Daily summary before market open (7:30 AM ET)\n"
        "• Real-time breaking news alerts"
    ),

    # /help
    "help": (
        "**Available Commands:**\n\n"
        "📌 **Stock Management:**\n"
        "/add TICKER [PRIORITY] - Add stock (e.g., /add TSLA HIGH)\n"
        "/priority TICKER PRIORITY - Change priority\n"
        "/remove TICKER - Remove stock\n"
        "/list - View watchlist\n\n"
        "📊 **Information:**\n"
        "/summary - Get latest summary (click for details)\n"
        "/health - Check bot health status\n"
        "/help - Show this help\n\n"
        "⏰ **Auto Updates:**\n"
        "• Daily summary: 2h before market open (7:30 AM ET)\n"
        "• Breaking news: checked every hour\n"
        "• Data refreshed hourly\n\n"
        "💡 **Tips:**\n"
        "• Use standard US ticker symbols (AAPL, MSFT, GOOGL, etc.)\n"
        "• /summary returns cached data instantly, click to see details"
    ),

    # /add
    "add_usage": "❌ Usage: /add <TICKER> [PRIORITY]\nExample: /add AAPL HIGH",
    "add_ok": "✅ Added ${ticker} with {priority} priority, fetching data...",
    "add_done": "✅ ${ticker} ready: {brief}",
    "add_fail": "⚠️ ${ticker} fetch failed, will retry on next refresh",
    "add_exists": "⚠️ ${ticker} is already in your watchlist",

    # /priority
    "priority_usage": "❌ Usage: /priority <TICKER> <PRIORITY>\nExample: /priority AAPL CRITICAL",
    "priority_invalid": "❌ Priority must be LOW, MEDIUM, HIGH, or CRITICAL",
    "priority_ok": "✅ ${ticker} priority changed to {priority}",
    "priority_not_found": "⚠️ ${ticker} not found in your watchlist",

    # /remove
    "remove_usage": "❌ Usage: /remove <TICKER>\nExample: /remove AAPL",
    "remove_ok": "✅ Removed ${ticker}",
    "remove_not_found": "⚠️ ${ticker} not found in your watchlist",

    # /list
    "list_empty": "📋 Watchlist is empty\n\nAdd stocks with: /add <TICKER>",
    "list_header": "📊 **Watchlist** ({count} stocks):\n\n",
    "list_btn_remove": "🗑️ Remove",

    # /summary
    "summary_header": "📊 **Stock Summary** | 🕐 {timestamp}\n\n",
    "summary_row": "**${ticker}** | {brief}\n  └ 📰 {news_count} articles\n\n",
    "summary_footer": "_Click buttons below for detailed analysis_",
    "summary_btn": "🔍 ${ticker} Details",
    "summary_empty": "📊 No updates today",
    "summary_fail": "❌ Failed to get summary: {error}",
    "summary_unavailable": "❌ Summary function not available",
    "summary_loading": "⏳ Getting latest summary...",
    "summary_no_cache": "⚠️ No cached data yet, fetching now...",

    # /health
    "health_ok": (
        "✅ Status: {status}\n"
        "🕐 Time: {timestamp}\n"
        "📋 Watchlist: {watchlist_count} stocks\n"
        "🔄 Last fetch: {last_fetch}"
    ),
    "health_never_fetched": "never",
    "health_unavailable": "❌ Health status unavailable",

    # Detail view
    "detail_header": "**💼 ${ticker} Detailed Analysis**\n",
    "detail_link": "[View on Yahoo Finance](https://finance.yahoo.com/quote/{ticker})\n",
    "detail_news_count": "📰 News: {count} articles\n\n",
    "detail_no_data": "⚠️ No data available for ${ticker}",

    # Breaking news
    "breaking_header": "🚨 **BREAKING NEWS** {emoji}\n\n",
    "breaking_impact": "📊 Impact: {impact}\n",
    "breaking_link": "📰 [Read Full Article]({url})",

    # Startup
    "startup": "✅ **Stock Monitor is running!**\n\nFetching initial data...",
    "startup_done": "✅ Initial fetch complete, cached {count} stocks\n\nUse /summary to view latest\nData refreshes every {interval} minutes",

    # Errors
    "fetch_fail_brief": "⚠️ Fetch failed",
    "fetch_fail_detail": "⚠️ Fetch failed: {error}",
    "btn_remove_ok": "✅ Removed ${ticker}",
    "btn_remove_fail": "⚠️ Failed to remove ${ticker}",

    # AI prompts
    "ai_analysis_lang": "IMPORTANT: Output your entire analysis in English.",
    "ai_analysis_brief_example": 'Example BRIEF lines: "📈 iPhone launch boosts outlook" or "📉 Earnings miss pressures stock" or "➡️ Market awaits earnings report"',
    "ai_analysis_format": (
        "BRIEF: [sentiment emoji] [one-line summary under 50 chars]\n\n"
        "**📊 Overall Sentiment:** [Bullish/Bearish/Neutral]\n\n"
        "**🔥 Key Developments:**\n"
        "- [One-line summary per item with source link: summary [Source](url)]\n"
        "- [List top 3-5 most important news]\n\n"
        "**💬 Community Sentiment:**\n"
        "- [Social media discussion summary, 2-3 lines]\n\n"
        "**⚠️ Risk Factors:**\n"
        "- [Any risks or concerns mentioned]\n\n"
        "**📈 Trading Impact:**\n"
        "[1-2 sentences on potential short-term price impact]"
    ),
    "ai_breaking_summary_instruction": "SUMMARY: [one-line summary in English]",
    "ai_no_brief": "📊 No summary",
    "ai_fail_brief": "⚠️ Analysis failed",
}
