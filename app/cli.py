"""Command-line interface for lookup-cli."""

import asyncio
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from langdetect import detect

from .config import Config
from .translator import TranslationService
from .i18n import I18n


console = Console()

# 支持的语言映射
SUPPORTED_LANGUAGES = {
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
    'ru': 'Русský',
    'pt': 'Português',
    'ar': 'العربية'
}


def get_i18n():
    """Get i18n instance based on config."""
    config = Config()
    primary_lang = config.get("primary_language", "zh-cn")
    return I18n(primary_lang)


def validate_language(lang_code, i18n=None):
    """验证语言代码是否受支持"""
    if lang_code and lang_code not in SUPPORTED_LANGUAGES:
        if not i18n:
            i18n = get_i18n()
        console.print(f"[red]{i18n.t('error')}:[/red] {i18n.t('unsupported_language')} '{lang_code}'")
        console.print(f"[yellow]{i18n.t('use_support')}[/yellow]")
        sys.exit(1)


@click.group(invoke_without_command=True)
@click.option('--target', '-t', help='Target language code')
@click.option('--support', '-s', is_flag=True, help='Show supported languages')
@click.option('--help', '-h', is_flag=True, expose_value=False, is_eager=True, help='Show this message and exit.')
@click.argument('text', nargs=-1)
@click.pass_context
def cli(ctx, target, support, text):
    """🔍 Lu - A powerful command-line translation tool with AI support."""
    
    # 显示支持的语言
    if support:
        show_supported_languages()
        return
    
    # 验证目标语言
    i18n = get_i18n()
    validate_language(target, i18n)
    
    # 检查是否有子命令将要被调用
    if ctx.invoked_subcommand is None:
        if text:
            # 如果提供了文本且没有子命令，执行翻译
            text_to_translate = ' '.join(text)
            translate_text_smart(text_to_translate, target, i18n)
        else:
            # 如果没有文本和子命令，显示帮助
            click.echo(ctx.get_help())


def show_supported_languages():
    """显示支持的语言列表"""
    i18n = get_i18n()
    table = Table(title=i18n.t("supported_languages"), show_header=True, header_style="bold magenta")
    table.add_column(i18n.t("language_code"), style="cyan", no_wrap=True)
    table.add_column(i18n.t("language_name"), style="green")
    
    for code, name in SUPPORTED_LANGUAGES.items():
        table.add_row(code, name)
    
    console.print(table)
    console.print(f"\n[yellow]{i18n.t('usage')}:[/yellow] [bold]lu --target zh-cn \"Hello world\"[/bold]")
    console.print(f"[yellow]{i18n.t('usage')}:[/yellow] [bold]lu trans Hello world[/bold]")


def translate_text_smart(text_to_translate, target_lang, i18n):
    """智能翻译函数，根据主语言自动选择目标语言"""
    config = Config()
    primary_lang = config.get("primary_language", "zh-cn")
    
    # 检查配置是否存在
    if not config.config_file.exists():
        console.print(i18n.t("config_not_found"), style="yellow")
        return
    
    # 检查API密钥是否配置
    model_config = config.get_current_model_config()
    if not model_config.get('api_key'):
        console.print(i18n.t("api_key_not_configured"), style="yellow")
        return
    
    # 如果没有指定目标语言，智能判断
    if not target_lang:
        try:
            detected_lang = detect(text_to_translate)
            # 如果检测到的语言是主语言，需要交互式选择目标语言
            if detected_lang == primary_lang or detected_lang.startswith(primary_lang.split('-')[0]):
                target_lang = interactive_select_target_language(i18n, primary_lang)
            else:
                # 非主语言翻译为主语言
                target_lang = primary_lang
        except:
            # 语言检测失败，默认翻译为主语言
            target_lang = primary_lang
    
    # 创建翻译服务
    translator = TranslationService(config)
    
    # 运行翻译
    asyncio.run(_translate_async_smart(translator, text_to_translate, target_lang, i18n))


def interactive_select_target_language(i18n, primary_lang):
    """交互式选择目标语言"""
    console.print(f"\n{i18n.t('select_target_language')}")
    
    # 排除主语言的选项
    options = {}
    for code, name in SUPPORTED_LANGUAGES.items():
        if code != primary_lang:
            options[code] = name
    
    # 显示选项
    choices = list(options.keys())
    for i, (code, name) in enumerate(options.items(), 1):
        console.print(f"{i}. {code} - {name}")
    
    while True:
        try:
            choice = Prompt.ask("选择目标语言编号" if primary_lang.startswith('zh') else "Select target language number", 
                              choices=[str(i) for i in range(1, len(choices) + 1)])
            return choices[int(choice) - 1]
        except (ValueError, IndexError):
            console.print("❌ 无效选择，请重试" if primary_lang.startswith('zh') else "❌ Invalid choice, please try again")


async def _translate_async_smart(translator: TranslationService, text: str, target_lang: str, i18n):
    """Async translation with streaming output and i18n support."""
    
    console.print(f"\n[bold blue]{i18n.t('translating')}:[/bold blue] {text}")
    if target_lang:
        console.print(f"[bold green]{i18n.t('target')}:[/bold green] {target_lang}")
    console.print()
    
    # Create a live display for streaming output
    response_text = ""
    
    with Live(console=console, refresh_per_second=10) as live:
        spinner = Spinner("dots", text=i18n.t("thinking"))
        live.update(spinner)
        
        first_chunk = True
        async for chunk in translator.translate_streaming(text, target_lang):
            if first_chunk:
                live.update(Panel("", title=i18n.t("translation_result"), border_style="blue"))
                first_chunk = False
            
            response_text += chunk
            live.update(Panel(response_text, title=i18n.t("translation_result"), border_style="blue"))
    
    console.print()


@cli.command()
@click.option('--target', '-t', help='Target language code')
@click.argument('text', nargs=-1, required=False)
def trans(target, text):
    """Translate text (all arguments after 'trans' are treated as one text block)."""
    # 如果没有提供文本，显示帮助
    if not text:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        return
    
    # 验证目标语言
    i18n = get_i18n()
    validate_language(target, i18n)
    
    # 将所有参数合并为一个文本
    text_to_translate = ' '.join(text)
    translate_text_smart(text_to_translate, target, i18n)


def show_current_config(config: Config, i18n: I18n) -> None:
    """显示当前配置（不包含API密钥）"""
    console.print(f"\n{i18n.t('current_config')}")
    
    # 获取当前配置
    provider = config.get("provider", "openai")
    primary_lang = config.get("primary_language", "zh-cn")
    model_config = config.get_current_model_config()
    
    # 显示基本信息
    console.print(f"  {i18n.t('provider')} [cyan]{provider}[/cyan]")
    console.print(f"  {i18n.t('primary_language')} [cyan]{SUPPORTED_LANGUAGES.get(primary_lang, primary_lang)}[/cyan]")
    
    # 显示模型信息
    if model_config.get("model"):
        console.print(f"  {i18n.t('model')} [cyan]{model_config.get('model')}[/cyan]")
    
    # 显示基础URL（如果不是默认值）
    base_url = model_config.get("base_url")
    if base_url and base_url != "https://api.openai.com/v1":
        console.print(f"  {i18n.t('base_url')} [cyan]{base_url}[/cyan]")
    
    # 显示API密钥状态（不显示实际密钥）
    api_key = model_config.get("api_key")
    if api_key:
        console.print(f"  [green]{i18n.t('api_key_configured')}[/green]")
    else:
        console.print(f"  [yellow]{i18n.t('api_key_not_set')}[/yellow]")


@cli.command()
def init():
    """Initialize and configure lookup-cli."""
    
    # 首先检查是否已有配置
    config = Config()
    config_exists = config.config_file.exists()
    
    if config_exists:
        # 获取当前主语言以显示提示
        current_primary_lang = config.get("primary_language", "zh-cn")
        temp_i18n = I18n(current_primary_lang)
        
        console.print(f"\n[yellow]{temp_i18n.t('config_exists')}[/yellow]")
        show_current_config(config, temp_i18n)
        console.print(f"\n[yellow]{temp_i18n.t('config_will_overwrite')}[/yellow]")
        
        if not Confirm.ask(temp_i18n.t("continue_init"), default=False):
            console.print("❌ 初始化已取消" if current_primary_lang.startswith('zh') else "❌ Initialization cancelled")
            return
    
    # 主语言选择
    console.print("\n🌍 [bold]Select your primary language / 选择您的主语言:[/bold]")
    console.print("1. 简体中文 (zh-cn)")
    console.print("2. English (en)")
    
    # 如果有现有配置，显示当前值作为默认选项
    default_choice = "1"
    if config_exists:
        current_primary = config.get("primary_language", "zh-cn")
        default_choice = "1" if current_primary == "zh-cn" else "2"
        current_lang_name = "简体中文" if current_primary == "zh-cn" else "English"
        console.print(f"  [dim]当前: {current_lang_name} / Current: {current_lang_name}[/dim]")
    
    primary_choice = Prompt.ask(
        "Select primary language / 选择主语言", 
        choices=["1", "2"], 
        default=default_choice
    )
    
    primary_lang = "zh-cn" if primary_choice == "1" else "en"
    config.set("primary_language", primary_lang)
    
    # 创建i18n实例
    i18n = I18n(primary_lang)
    
    console.print(Panel.fit(
        f"{i18n.t('welcome_title')}\n{i18n.t('welcome_desc')}",
        border_style="blue"
    ))
    
    # Provider selection
    console.print(f"\n{i18n.t('choose_provider')}")
    console.print("1. OpenAI (GPT models)")
    console.print("2. DashScope (Qwen models)")  
    console.print("3. Custom OpenAI-compatible API")
    
    # 显示当前provider（如果存在）
    default_provider_choice = "1"
    if config_exists:
        current_provider = config.get("provider", "openai")
        provider_map_reverse = {"openai": "1", "dashscope": "2", "custom": "3"}
        default_provider_choice = provider_map_reverse.get(current_provider, "1")
        console.print(f"  [dim]{i18n.t('current_config')}: {current_provider}[/dim]")
    
    provider_choice = Prompt.ask(
        i18n.t("select_provider"), 
        choices=["1", "2", "3"], 
        default=default_provider_choice
    )
    
    provider_map = {"1": "openai", "2": "dashscope", "3": "custom"}
    provider = provider_map[provider_choice]
    
    console.print(f"\n{i18n.t('selected')} [bold green]{provider}[/bold green]")
    
    # Configure based on provider
    if provider == "openai":
        _configure_openai(config, i18n, config_exists)
    elif provider == "dashscope":
        _configure_dashscope(config, i18n, config_exists)
    elif provider == "custom":
        _configure_custom(config, i18n, config_exists)
    
    # 显示主语言配置信息
    console.print(f"\n{i18n.t('primary_language_title')}")
    console.print(i18n.t('primary_language_desc'))
    console.print(f"✅ [bold green]{SUPPORTED_LANGUAGES[primary_lang]}[/bold green]")
    
    console.print(f"\n{i18n.t('default_behavior')}")
    console.print(i18n.t('default_behavior_desc'))
    
    # Save configuration
    config.set("provider", provider)
    config.save_config()
    
    console.print(f"\n🎉 [bold green]{i18n.t('config_saved')}[/bold green]")
    console.print(f"📁 {i18n.t('config_file')} {config.config_file}")
    console.print(f"\n💡 [bold]{i18n.t('try_it')}[/bold]")
    for example in i18n.t('usage_examples'):
        console.print(f"  {example}")


def _configure_openai(config: Config, i18n: I18n, config_exists: bool = False):
    """Configure OpenAI settings."""
    console.print("\n🔧 [bold]OpenAI Configuration[/bold]")
    
    # 显示当前配置（如果存在）
    current_config = config.get("models.openai", {})
    if config_exists and current_config:
        console.print(f"\n{i18n.t('current_config')}")
        if current_config.get("model"):
            console.print(f"  {i18n.t('model')} [cyan]{current_config.get('model')}[/cyan]")
        if current_config.get("base_url") and current_config.get("base_url") != "https://api.openai.com/v1":
            console.print(f"  {i18n.t('base_url')} [cyan]{current_config.get('base_url')}[/cyan]")
        if current_config.get("api_key"):
            console.print(f"  [green]{i18n.t('api_key_configured')}[/green]")
        else:
            console.print(f"  [yellow]{i18n.t('api_key_not_set')}[/yellow]")
    
    api_key = Prompt.ask(
        i18n.t("api_key_prompt"),
        password=True,
        default=current_config.get("api_key", "") if config_exists else ""
    )
    
    console.print(f"\n{i18n.t('model_selection')}")
    models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    
    for i, model in enumerate(models, 1):
        console.print(f"{i}. {model}")
    
    # 找到当前模型的索引作为默认值
    default_model_choice = "1"
    if config_exists and current_config.get("model"):
        try:
            current_model_index = models.index(current_config.get("model")) + 1
            default_model_choice = str(current_model_index)
        except ValueError:
            pass
    
    model_choice = Prompt.ask(
        i18n.t("select_model"), 
        choices=[str(i) for i in range(1, len(models) + 1)], 
        default=default_model_choice
    )
    
    selected_model = models[int(model_choice) - 1]
    
    # Custom base URL option
    current_base_url = current_config.get("base_url", "https://api.openai.com/v1")
    use_custom = current_base_url != "https://api.openai.com/v1"
    
    if Confirm.ask(i18n.t("custom_base_url"), default=use_custom):
        base_url = Prompt.ask(i18n.t("enter_base_url"), default=current_base_url)
    else:
        base_url = "https://api.openai.com/v1"
    
    config.update_provider_config("openai", {
        "api_key": api_key,
        "model": selected_model,
        "base_url": base_url
    })


def _configure_dashscope(config: Config, i18n: I18n, config_exists: bool = False):
    """Configure DashScope settings."""
    console.print("\n🔧 [bold]DashScope Configuration[/bold]")
    
    # 显示当前配置（如果存在）
    current_config = config.get("models.dashscope", {})
    if config_exists and current_config:
        console.print(f"\n{i18n.t('current_config')}")
        if current_config.get("model"):
            console.print(f"  {i18n.t('model')} [cyan]{current_config.get('model')}[/cyan]")
        if current_config.get("api_key"):
            console.print(f"  [green]{i18n.t('api_key_configured')}[/green]")
        else:
            console.print(f"  [yellow]{i18n.t('api_key_not_set')}[/yellow]")
    
    api_key = Prompt.ask(
        i18n.t("api_key_prompt"),
        password=True,
        default=current_config.get("api_key", "") if config_exists else ""
    )
    
    console.print(f"\n{i18n.t('model_selection')}")
    models = [
        "qwen-turbo",
        "qwen-plus", 
        "qwen-max",
        "qwen-max-longcontext"
    ]
    
    for i, model in enumerate(models, 1):
        console.print(f"{i}. {model}")
    
    # 找到当前模型的索引作为默认值
    default_model_choice = "1"
    if config_exists and current_config.get("model"):
        try:
            current_model_index = models.index(current_config.get("model")) + 1
            default_model_choice = str(current_model_index)
        except ValueError:
            pass
    
    model_choice = Prompt.ask(
        i18n.t("select_model"),
        choices=[str(i) for i in range(1, len(models) + 1)],
        default=default_model_choice
    )
    
    selected_model = models[int(model_choice) - 1]
    
    config.update_provider_config("dashscope", {
        "api_key": api_key,
        "model": selected_model
    })


def _configure_custom(config: Config, i18n: I18n, config_exists: bool = False):
    """Configure custom OpenAI-compatible API."""
    console.print("\n🔧 [bold]Custom API Configuration[/bold]")
    
    # 显示当前配置（如果存在）
    current_config = config.get("models.custom", {})
    if config_exists and current_config:
        console.print(f"\n{i18n.t('current_config')}")
        if current_config.get("model"):
            console.print(f"  {i18n.t('model')} [cyan]{current_config.get('model')}[/cyan]")
        if current_config.get("base_url"):
            console.print(f"  {i18n.t('base_url')} [cyan]{current_config.get('base_url')}[/cyan]")
        if current_config.get("api_key"):
            console.print(f"  [green]{i18n.t('api_key_configured')}[/green]")
        else:
            console.print(f"  [yellow]{i18n.t('api_key_not_set')}[/yellow]")
    
    base_url = Prompt.ask(
        i18n.t("enter_api_url"),
        default=current_config.get("base_url", "") if config_exists else ""
    )
    
    api_key = Prompt.ask(
        i18n.t("api_key_prompt"),
        password=True,
        default=current_config.get("api_key", "sk-no-key-required") if config_exists else "sk-no-key-required"
    )
    
    model = Prompt.ask(
        i18n.t("enter_model_name"),
        default=current_config.get("model", "gpt-3.5-turbo") if config_exists else "gpt-3.5-turbo"
    )
    
    config.update_provider_config("custom", {
        "api_key": api_key,
        "model": model,
        "base_url": base_url
    })


if __name__ == "__main__":
    cli()
