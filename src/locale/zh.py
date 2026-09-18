STRINGS = {
    # Bot commands (autocomplete menu)
    "cmd_summary": "获取所有股票的市场摘要",
    "cmd_list": "查看关注列表",
    "cmd_add": "添加股票到关注列表",
    "cmd_priority": "修改股票优先级",
    "cmd_remove": "从关注列表移除股票",
    "cmd_help": "显示帮助信息",
    "cmd_health": "检查机器人运行状态",

    # /start
    "welcome": (
        "👋 **欢迎使用 Stock Monitor!**\n\n"
        "我帮你追踪股票新闻和社交媒体讨论。\n\n"
        "**命令:**\n"
        "/add <代码> [优先级] - 添加股票\n"
        "/priority <代码> <优先级> - 修改优先级\n"
        "/remove <代码> - 移除股票\n"
        "/list - 查看关注列表\n"
        "/summary - 获取市场摘要\n"
        "/health - 检查机器人运行状态\n"
        "/help - 显示帮助\n\n"
        "📊 **自动推送:**\n"
        "• 每日开盘前摘要 (7:30 AM ET)\n"
        "• 突发新闻实时提醒"
    ),

    # /help
    "help": (
        "**可用命令:**\n\n"
        "📌 **股票管理:**\n"
        "/add 代码 [优先级] - 添加股票 (如 /add TSLA HIGH)\n"
        "/priority 代码 优先级 - 修改优先级\n"
        "/remove 代码 - 移除股票\n"
        "/list - 查看关注列表\n\n"
        "📊 **信息查询:**\n"
        "/summary - 获取最新摘要（点击查看详情）\n"
        "/health - 检查机器人运行状态\n"
        "/help - 显示此帮助\n\n"
        "⏰ **自动更新:**\n"
        "• 每日摘要: 开盘前2小时 (7:30 AM ET)\n"
        "• 突发新闻: 每小时检测\n"
        "• 数据每小时自动刷新\n\n"
        "💡 **提示:**\n"
        "• 支持标准美股代码 (AAPL, MSFT, GOOGL 等)\n"
        "• /summary 秒回缓存数据，点击股票查看详细分析"
    ),

    # /add
    "add_usage": "❌ 用法: /add <代码> [优先级]\n示例: /add AAPL HIGH",
    "add_ok": "✅ 已添加 ${ticker}，优先级为 {priority}，正在抓取数据...",
    "add_done": "✅ ${ticker} 数据就绪: {brief}",
    "add_fail": "⚠️ ${ticker} 抓取失败，下次定时刷新时重试",
    "add_exists": "⚠️ ${ticker} 已在关注列表中",

    # /priority
    "priority_usage": "❌ 用法: /priority <代码> <优先级>\n示例: /priority AAPL CRITICAL",
    "priority_invalid": "❌ 优先级必须为 LOW、MEDIUM、HIGH 或 CRITICAL",
    "priority_ok": "✅ ${ticker} 的优先级已修改为 {priority}",
    "priority_not_found": "⚠️ ${ticker} 不在关注列表中",

    # /remove
    "remove_usage": "❌ 用法: /remove <代码>\n示例: /remove AAPL",
    "remove_ok": "✅ 已移除 ${ticker}",
    "remove_not_found": "⚠️ ${ticker} 不在关注列表中",

    # /list
    "list_empty": "📋 关注列表为空\n\n使用 /add <代码> 添加股票",
    "list_header": "📊 **关注列表** ({count} 只):\n\n",
    "list_btn_remove": "🗑️ 移除",

    # /summary
    "summary_header": "📊 **股票摘要** | 🕐 {timestamp}\n\n",
    "summary_row": "**${ticker}** | {brief}\n  └ 📰 {news_count} 篇新闻\n\n",
    "summary_footer": "_点击下方按钮查看详细分析_",
    "summary_btn": "🔍 ${ticker} 查看详情",
    "summary_empty": "📊 今日暂无更新",
    "summary_fail": "❌ 获取摘要失败: {error}",
    "summary_unavailable": "❌ 摘要功能不可用",
    "summary_loading": "⏳ 正在获取最新摘要...",
    "summary_no_cache": "⚠️ 暂无缓存数据，正在抓取中...",

    # /health
    "health_ok": (
        "✅ 状态: {status}\n"
        "🕐 时间: {timestamp}\n"
        "📋 关注列表: {watchlist_count} 只\n"
        "🔄 上次抓取: {last_fetch}"
    ),
    "health_never_fetched": "尚未抓取",
    "health_unavailable": "❌ 无法获取运行状态",

    # Detail view
    "detail_header": "**💼 ${ticker} 详细分析**\n",
    "detail_link": "[查看行情](https://finance.yahoo.com/quote/{ticker})\n",
    "detail_news_count": "📰 新闻: {count} 篇\n\n",
    "detail_no_data": "⚠️ 暂无 ${ticker} 的数据",

    # Breaking news
    "breaking_header": "🚨 **突发新闻** {emoji}\n\n",
    "breaking_impact": "📊 影响: {impact}\n",
    "breaking_link": "📰 [阅读原文]({url})",

    # Startup
    "startup": "✅ **Stock Monitor 已启动!**\n\n正在进行首次数据抓取...",
    "startup_done": "✅ 首次抓取完成，已缓存 {count} 只股票数据\n\n使用 /summary 查看最新摘要\n数据每 {interval} 分钟自动更新",

    # Errors
    "fetch_fail_brief": "⚠️ 抓取失败",
    "fetch_fail_detail": "⚠️ 抓取失败: {error}",
    "btn_remove_ok": "✅ 已移除 ${ticker}",
    "btn_remove_fail": "⚠️ 移除 ${ticker} 失败",

    # AI prompts
    "ai_analysis_lang": "IMPORTANT: Output your entire analysis in Chinese (简体中文).",
    "ai_analysis_brief_example": 'Example BRIEF lines: "📈 iPhone新品预期推高股价" or "📉 财报不及预期承压" or "➡️ 市场观望等待财报"',
    "ai_analysis_format": (
        "BRIEF: [情绪emoji] [20字以内一句话概括核心动态]\n\n"
        "**📊 整体情绪:** [看涨/看跌/中性]\n\n"
        "**🔥 关键动态:**\n"
        "- [每条用一行总结要点，末尾附上来源链接，格式: 内容摘要 [来源名](url)]\n"
        "- [列出最重要的3-5条新闻]\n\n"
        "**💬 社区舆情:**\n"
        "- [社交媒体讨论概要，2-3行]\n\n"
        "**⚠️ 风险因素:**\n"
        "- [提及的风险或隐患]\n\n"
        "**📈 交易影响:**\n"
        "[1-2句话分析短期价格影响]"
    ),
    "ai_breaking_summary_instruction": "SUMMARY: [用中文写一句话总结]",
    "ai_no_brief": "📊 暂无摘要",
    "ai_fail_brief": "⚠️ 分析失败",
}
