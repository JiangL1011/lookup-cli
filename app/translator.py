"""Translation services for lookup-cli."""

import asyncio
import json
import httpx
from typing import Dict, Any, AsyncGenerator, Optional
from langdetect import detect
import dashscope
from openai import AsyncOpenAI

from .config import Config


class TranslationService:
    """Handles translation requests to various AI providers."""

    def __init__(self, config: Config):
        self.config = config
        self.model_config = config.get_current_model_config()
        self.provider = config.get("provider", "openai")

    async def translate_streaming(
        self,
        text: str,
        target_lang: str = None,
        source_lang: str = None
    ) -> AsyncGenerator[str, None]:
        """Translate text with streaming response."""

        # Auto-detect source language if not provided
        if not source_lang:
            try:
                source_lang = detect(text)
            except:
                source_lang = "auto"

        # Set target language based on auto-detection
        if not target_lang:
            target_lang = "zh-cn" if source_lang == "en" else "en"

        # Determine if input is word, phrase, or sentence
        text_type = self._classify_text(text)

        # Create appropriate prompt
        prompt = self._create_prompt(text, source_lang, target_lang, text_type)

        # Route to appropriate provider
        if self.provider == "openai":
            async for chunk in self._translate_openai(prompt):
                yield chunk
        elif self.provider == "dashscope":
            async for chunk in self._translate_dashscope(prompt):
                yield chunk
        elif self.provider == "custom":
            async for chunk in self._translate_custom(prompt):
                yield chunk

    def _classify_text(self, text: str) -> str:
        """Classify text as word, phrase, or sentence."""
        text = text.strip()

        # Simple classification logic
        if len(text.split()) == 1 and text.isalpha():
            return "word"
        elif len(text.split()) <= 5 and not any(p in text for p in '.!?'):
            return "phrase"
        else:
            return "sentence"

    def _create_prompt(self, text: str, source_lang: str, target_lang: str, text_type: str) -> str:
        """Create appropriate prompt based on text type."""

        # 获取用户配置的主语言
        primary_lang = self.config.get("primary_language", "zh-cn")

        lang_names = {
            "en": "English",
            "zh-cn": "Simplified Chinese",
            "zh-tw": "Traditional Chinese (Taiwan)",
            "zh-hk": "Traditional Chinese (Hong Kong)",
            "zh": "Chinese",
            "de": "German",
            "fr": "French",
            "ja": "Japanese",
            "es": "Spanish",
            "ko": "Korean",
            "nl": "Dutch",
            "pl": "Polish",
            "ru": "Russian",
            "pt": "Portuguese",
            "ar": "Arabic"
        }

        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        primary_name = lang_names.get(primary_lang, primary_lang)

        if text_type == "word":
            return f"""
            将单词 "{text}" 从 {source_name} 翻译到 {target_name}。输出以下内容：
            翻译结果
            读音和词性
            例句

            要求：
            1. 输出的内容要适合在命令行中展示并且要美观，适当的可以加入一些表情符号或者颜色；
            2. 说明性的内容使用{primary_name}语言回复。
            3. 输出内容不要用markdown格式
            4. 如果有多个含义，请列出所有常见含义并提供对应的翻译和用法，并且其他用法也要遵循之前的输出格式。
            """

        elif text_type == "phrase":
            return f"""
            将短语 "{text}" 从 {source_name} 翻译到 {target_name}。输出以下内容：
            翻译结果
            简要上下文说明（如果需要）
            使用示例

            要求：
            1. 输出的内容要适合在命令行中展示并且要美观，适当的可以加入一些表情符号或者颜色；
            2. 说明性的内容使用{primary_name}语言回复。
            3. 输出内容不要用markdown格式
            4. 如果有多个含义，请列出所有常见含义并提供对应的翻译和用法，并且其他用法也要遵循之前的输出格式。
            """

        else:  # sentence
            return f"""
            将句子 "{text}" 从 {source_name} 翻译到 {target_name}。输出以下内容：
            准确翻译然后对原句内容做语法分析，并展示一些使用示例

            要求：
            1. 输出的内容要适合在命令行中展示并且要美观，适当的可以加入一些表情符号或者颜色；
            2. 说明性的内容使用{primary_name}语言回复。
            3. 输出内容不要用markdown格式
            4. 不要包含代码块或其他格式化内容
            5. 语法分析要准确且格式清晰
            """

    async def _translate_openai(self, prompt: str) -> AsyncGenerator[str, None]:
        """Translate using OpenAI API."""
        client = AsyncOpenAI(
            api_key=self.model_config.get("api_key"),
            base_url=self.model_config.get(
                "base_url", "https://api.openai.com/v1")
        )

        try:
            stream = await client.chat.completions.create(
                model=self.model_config.get("model", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a professional translator and language teacher. Provide detailed, accurate translations with educational context."},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                temperature=0.3
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"❌ Error: {str(e)}"

    async def _translate_dashscope(self, prompt: str) -> AsyncGenerator[str, None]:
        """Translate using DashScope API."""
        dashscope.api_key = self.model_config.get("api_key")

        try:
            responses = dashscope.Generation.call(
                model=self.model_config.get("model", "qwen-turbo"),
                messages=[
                    {"role": "system", "content": "You are a professional translator and language teacher. Provide detailed, accurate translations with educational context."},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                result_format='message'
            )

            previous_content = ""
            for response in responses:
                if response.status_code == 200:
                    current_content = response.output.choices[0]['message']['content']
                    # 只yield新增的内容部分
                    if current_content and current_content != previous_content:
                        delta = current_content[len(previous_content):]
                        if delta:
                            yield delta
                        previous_content = current_content
                else:
                    yield f"❌ Error: {response.message}"

        except Exception as e:
            yield f"❌ Error: {str(e)}"

    async def _translate_custom(self, prompt: str) -> AsyncGenerator[str, None]:
        """Translate using custom OpenAI-compatible API."""
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.model_config.get('base_url')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.model_config.get('api_key')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_config.get("model", "gpt-3.5-turbo"),
                        "messages": [
                            {"role": "system", "content": "You are a professional translator and language teacher. Provide detailed, accurate translations with educational context."},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": True,
                        "temperature": 0.3
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if chunk["choices"][0]["delta"].get("content"):
                                    yield chunk["choices"][0]["delta"]["content"]
                            except:
                                continue

            except Exception as e:
                yield f"❌ Error: {str(e)}"
