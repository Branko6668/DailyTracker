import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "database": {
                "host": "localhost",
                "database": "daily_tracker",
                "user": "root",
                "password": ""
            },
            "ui": {
                "theme": "default",
                "window_size": "1200x800",
                "auto_refresh": True
            },
            "chart": {
                "default_chart": "weight",
                "date_format": "%m-%d",
                "chart_colors": ["#1f77b4", "#ff7f0e", "#2ca02c"]
            }
        }
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_config.copy()
        else:
            self.save_config(self.default_config)
            return self.default_config.copy()

    def save_config(self, config=None):
        """保存配置文件"""
        if config is None:
            config = self.config

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False

    def get(self, key_path, default=None):
        """获取配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path, value):
        """设置配置值"""
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self.save_config()

    def get_database_config(self):
        """获取数据库配置"""
        return self.get('database', self.default_config['database'])
