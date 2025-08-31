import yaml
from typing import Any

class Settings:
    """A utility class to load and access settings from config.yaml."""
    _config = {}

    @classmethod
    def _load_config(cls):
        """Loads the configuration from the YAML file into a class variable."""
        if not cls._config:
            try:
                with open('config.yaml', 'r') as f:
                    cls._config = yaml.safe_load(f)
            except FileNotFoundError:
                print("Warning: config.yaml not found. Using default settings.")
                # If the file is missing, provide sensible defaults.
                cls._config = {
                    'llm': {
                        'generation_model': 'claude-3-haiku-20240307',
                        'embedding_model': 'all-MiniLM-L6-v2',
                        'temperature': 0.1
                    },
                    'retrieval': { 'search_type': 'mmr', 'k_results': 5 },
                    'chunking': { 'chunk_size': 1500, 'chunk_overlap': 200 },
                    'ui': { 'log_level': 'info' }
                }
            except Exception as e:
                print(f"Warning: Could not load config.yaml: {e}. Using defaults.")
                cls._config = {} # Reset to ensure default fallback in get()

    @classmethod
    def get(cls, key_path: str, default: Any = None) -> Any:
        """
        Retrieves a value from the loaded configuration using dot notation.
        Example: Settings.get('llm.temperature', 0.1)
        """
        cls._load_config()
        keys = key_path.split('.')
        val = cls._config
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return default
        return val
