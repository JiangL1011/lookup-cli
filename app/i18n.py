"""Internationalization support for lookup-cli."""

from typing import Dict

class I18n:
    """Internationalization support."""
    
    def __init__(self, primary_language: str = "zh-cn"):
        self.primary_language = primary_language
        self.translations = {
            "zh-cn": {
                "welcome_title": "🚀 欢迎使用 Lu - Lookup CLI 设置",
                "welcome_desc": "让我们来配置您的翻译服务！",
                "choose_provider": "📡 请选择您的AI服务商：",
                "select_provider": "选择服务商",
                "selected": "✅ 已选择：",
                "primary_language_title": "🌍 主语言设置：",
                "primary_language_desc": "请选择您的主语言（界面语言和默认翻译目标）：",
                "select_primary_language": "选择主语言",
                "default_behavior": "🎯 默认翻译行为：",
                "default_behavior_desc": "• 非主语言内容 → 主语言\n• 主语言内容 → 英语（或交互式选择）",
                "config_saved": "🎉 配置已保存！",
                "config_file": "📁 配置文件：",
                "try_it": "💡 试试看：",
                "usage_examples": [
                    "lu Hello world!",
                    "lu --target en \"你好世界\"!"
                ],
                "translating": "🔍 正在翻译：",
                "target": "🎯 目标语言：",
                "translation_result": "🌐 翻译结果",
                "thinking": "🤖 思考中...",
                "supported_languages": "🌍 支持的语言",
                "language_code": "语言代码",
                "language_name": "语言名称",
                "usage": "💡 用法：",
                "error": "❌ 错误：",
                "unsupported_language": "不支持的语言",
                "use_support": "💡 使用 'lu --support' 查看支持的语言",
                "api_key_prompt": "请输入您的 API 密钥",
                "model_selection": "🤖 可用模型：",
                "select_model": "选择模型",
                "custom_base_url": "使用自定义基础URL？（代理/备用端点）",
                "enter_base_url": "输入基础URL",
                "enter_api_url": "输入API基础URL（如：http://localhost:8000/v1）",
                "enter_model_name": "输入模型名称",
                "current_config": "当前配置",
                "config_not_found": "⚠️  找不到配置文件。请先运行 'lu init'。",
                "api_key_not_configured": "⚠️  API密钥未配置。请运行 'lu init' 进行设置。",
                "select_target_language": "🎯 请选择目标语言：",
                "config_exists": "⚠️  检测到现有配置",
                "config_will_overwrite": "重新初始化将覆盖您当前的所有配置。",
                "continue_init": "您确定要继续吗？",
                "current_config": "📋 当前配置：",
                "provider": "服务商：",
                "model": "模型：",
                "primary_language": "主语言：",
                "base_url": "基础URL：",
                "api_key_configured": "API密钥：已配置",
                "api_key_not_set": "API密钥：未设置"
            },
            "en": {
                "welcome_title": "🚀 Welcome to Lu - Lookup CLI Setup",
                "welcome_desc": "Let's configure your translation service!",
                "choose_provider": "📡 Choose your AI provider:",
                "select_provider": "Select provider",
                "selected": "✅ Selected:",
                "primary_language_title": "🌍 Primary Language Settings:",
                "primary_language_desc": "Please select your primary language (interface language and default translation target):",
                "select_primary_language": "Select primary language",
                "default_behavior": "🎯 Default Translation Behavior:",
                "default_behavior_desc": "• Non-primary language content → Primary language\n• Primary language content → English (or interactive selection)",
                "config_saved": "🎉 Configuration saved!",
                "config_file": "📁 Config file:",
                "try_it": "💡 Try it out:",
                "usage_examples": [
                    "lu Hello world!",
                    "lu --target zh-cn \"Hello world!\""
                ],
                "translating": "🔍 Translating:",
                "target": "🎯 Target:",
                "translation_result": "🌐 Translation Result",
                "thinking": "🤖 Thinking...",
                "supported_languages": "🌍 Supported Languages",
                "language_code": "Language Code",
                "language_name": "Language Name",
                "usage": "💡 Usage:",
                "error": "❌ Error:",
                "unsupported_language": "Unsupported language",
                "use_support": "💡 Use 'lu --support' to see supported languages",
                "api_key_prompt": "Enter your API key",
                "model_selection": "🤖 Available models:",
                "select_model": "Select model",
                "custom_base_url": "Use custom base URL? (for proxies/alternative endpoints)",
                "enter_base_url": "Enter base URL",
                "enter_api_url": "Enter API base URL (e.g., http://localhost:8000/v1)",
                "enter_model_name": "Enter model name",
                "current_config": "Current Configuration",
                "config_not_found": "⚠️  Configuration not found. Please run 'lu init' first.",
                "api_key_not_configured": "⚠️  API key not configured. Please run 'lu init' to setup.",
                "select_target_language": "🎯 Please select target language:",
                "config_exists": "⚠️  Existing configuration detected",
                "config_will_overwrite": "Re-initialization will overwrite all your current settings.",
                "continue_init": "Are you sure you want to continue?",
                "current_config": "📋 Current Configuration:",
                "provider": "Provider:",
                "model": "Model:",
                "primary_language": "Primary Language:",
                "base_url": "Base URL:",
                "api_key_configured": "API Key: Configured",
                "api_key_not_set": "API Key: Not set"
            }
        }
    
    def t(self, key: str, **kwargs) -> str:
        """Get translated string."""
        lang_dict = self.translations.get(self.primary_language, self.translations["en"])
        text = lang_dict.get(key, self.translations["en"].get(key, key))
        if kwargs:
            return text.format(**kwargs)
        return text
    
    def get_language_options(self) -> Dict[str, str]:
        """Get language options for selection."""
        if self.primary_language == "zh-cn":
            return {
                'zh-cn': '简体中文',
                'zh-tw': '繁体中文（台湾）',
                'zh-hk': '繁体中文（香港）',
                'en': 'English',
                'de': 'Deutsch',
                'fr': 'Français',
                'ja': '日本語',
                'es': 'Español',
                'ko': '한국어',
                'nl': 'Nederlands',
                'pl': 'Polski',
                'ru': 'Русский',
                'pt': 'Português',
                'ar': 'العربية'
            }
        else:
            return {
                'en': 'English',
                'zh-cn': 'Simplified Chinese',
                'zh-tw': 'Traditional Chinese (Taiwan)',
                'zh-hk': 'Traditional Chinese (Hong Kong)',
                'de': 'German',
                'fr': 'French',
                'ja': 'Japanese',
                'es': 'Spanish',
                'ko': 'Korean',
                'nl': 'Dutch',
                'pl': 'Polish',
                'ru': 'Russian',
                'pt': 'Portuguese',
                'ar': 'Arabic'
            }
