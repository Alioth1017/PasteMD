"""Configuration loading and saving."""

import json
import os

from .defaults import DEFAULT_CONFIG
from .paths import get_config_path
from ..core.types import ConfigDict
from ..core.errors import ConfigError
from ..utils.logging import log


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self):
        self.config_path = get_config_path()
    
    def load(self) -> ConfigDict:
        """加载配置文件"""
        config = DEFAULT_CONFIG.copy()
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                
                # 合并用户配置
                for key, value in user_config.items():
                    config[key] = value
                    
            except Exception as e:
                config = DEFAULT_CONFIG.copy()
                log(f"Load config error: {e}")
                raise ConfigError(f"Failed to load config: {e}")

        # 深度合并 HTML 格式化配置，便于向后兼容
        default_html_formatting = DEFAULT_CONFIG.get("html_formatting", {})
        user_html_formatting = config.get("html_formatting", {})
        if isinstance(user_html_formatting, dict):
            merged_html_formatting = {**default_html_formatting, **user_html_formatting}
        else:
            merged_html_formatting = default_html_formatting.copy()
        config["html_formatting"] = merged_html_formatting

        # 展开环境变量
        config["save_dir"] = os.path.expandvars(config["save_dir"])
        
        return config
    
    def save(self, config: ConfigDict) -> None:
        """保存配置文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log(f"Save config error: {e}")
            raise ConfigError(f"Failed to save config: {e}")
