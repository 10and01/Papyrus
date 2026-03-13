import json
import os
import re

class AIConfig:
    """AI配置管理器"""
    def __init__(self, data_dir):
        self.config_file = os.path.join(data_dir, "ai_config.json")
        self.load_config()
    
    def load_config(self):
        default = {
            "providers": {
                "openai": {
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
                },
                "anthropic": {
                    "api_key": "",
                    "base_url": "https://api.anthropic.com/v1",
                    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
                },
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "models": ["llama2", "mistral", "qwen"]
                },
                "custom": {
                    "api_key": "",
                    "base_url": "",
                    "models": []
                }
            },
            "current_provider": "openai",
            "current_model": "gpt-3.5-turbo",
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0
            },
            "features": {
                "auto_hint": False,
                "auto_explain": False,
                "context_length": 10
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.config = {**default, **loaded}
                    # 合并嵌套字典
                    for key in ['providers', 'parameters', 'features']:
                        if key in loaded:
                            self.config[key] = {**default[key], **loaded[key]}
            except:
                self.config = default
        else:
            self.config = default
            self.save_config()
    
    def validate_config(self):
        """验证配置是否包含非法字符"""
        errors = []
        
        # 验证所有提供商的配置
        for provider_name, provider_config in self.config["providers"].items():
            # 验证 API Key（如果存在）
            if "api_key" in provider_config:
                api_key = provider_config["api_key"]
                if api_key and not self._is_valid_ascii(api_key):
                    errors.append(f"{provider_name.upper()} 的 API Key 中包含非法字符（如中文或特殊空格）")
            
            # 验证 Base URL
            if "base_url" in provider_config:
                base_url = provider_config["base_url"]
                if base_url and not self._is_valid_url(base_url):
                    errors.append(f"{provider_name.upper()} 的 Base URL 中包含非法字符")
        
        if errors:
            raise ValueError("\n".join(errors))
    
    def _is_valid_ascii(self, text):
        """检查文本是否只包含 ASCII 字符"""
        try:
            text.encode('ascii')
            return True
        except UnicodeEncodeError:
            return False
    
    def _is_valid_url(self, url):
        """检查 URL 是否有效（只包含 ASCII 字符）"""
        if not url:
            return True
        # URL 应该只包含 ASCII 字符
        return self._is_valid_ascii(url)
    
    def save_config(self):
        # 保存前验证配置
        self.validate_config()
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_provider_config(self):
        """获取当前提供商配置"""
        provider = self.config["current_provider"]
        return self.config["providers"][provider]
    
    def get_current_model(self):
        """获取当前模型"""
        return self.config["current_model"]
    
    def get_parameters(self):
        """获取当前参数"""
        return self.config["parameters"]