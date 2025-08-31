import yaml
from typing import Dict, Any
import os
import logging
from dotenv import load_dotenv

class Settings:
    """
    Loads and manages application settings from a YAML file and .env file.
    """
    _config: Dict[str, Any] = {}

    @classmethod
    def load_config(cls, config_path: str = 'config.yaml'):
        """
        Loads configuration from a .env file and then a YAML file.
        If config.yaml is not found, it uses sensible defaults for Anthropic.
        """
        load_dotenv()

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    cls._config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                logging.error(f"Error parsing '{config_path}': {e}. Using default settings.")
                cls._set_default_config()
        else:
            logging.warning(f"'{config_path}' not found. Using default settings for Anthropic.")
            cls._set_default_config()
        
        cls._override_with_env_vars()

    @classmethod
    def _set_default_config(cls):
        """Sets the fallback default configuration."""
        cls._config = {
            'llm': {
                'generation_model': 'claude-3-haiku-20240307',
                'embedding_model': 'all-MiniLM-L6-v2',
                'temperature': 0.1
            },
            'retrieval': {'search_type': 'similarity', 'k_results': 4},
            'chunking': {'chunk_size': 1500, 'chunk_overlap': 200},
            'ui': {'enable_colors': True, 'log_level': 'info'}
        }

    @classmethod
    def _override_with_env_vars(cls):
        """Overrides config values with environment variables for flexibility."""
        llm_temp = os.getenv('LLM_TEMPERATURE')
        if llm_temp:
            try:
                cls._config['llm']['temperature'] = float(llm_temp)
                logging.info(f"Overrode LLM temperature with value from environment: {llm_temp}")
            except (ValueError, KeyError):
                logging.warning("Invalid LLM_TEMPERATURE environment variable.")
        
        gen_model = os.getenv('GENERATION_MODEL')
        if gen_model:
            try:
                cls._config['llm']['generation_model'] = gen_model
                logging.info(f"Overrode generation model with value from environment: {gen_model}")
            except KeyError:
                logging.warning("Could not set generation model from environment variable.")


    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value using dot notation.
        e.g., Settings.get('llm.temperature')
        """
        if not cls._config:
            cls.load_config()
            
        keys = key.split('.')
        value = cls._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

Settings.load_config()
