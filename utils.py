from configparser import ConfigParser


def load_config(config_path: str) -> ConfigParser:
    """
    Load from config file
    """
    configuration = ConfigParser()
    configuration.read(config_path)
    return configuration