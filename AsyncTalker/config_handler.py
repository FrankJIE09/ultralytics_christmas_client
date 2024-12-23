import yaml


def load_config(file_path="./config/config.yaml"):
    """
    加载 YAML 配置文件。

    :param file_path: str，配置文件路径。
    :return: dict，解析后的配置数据。
    """
    with open(file_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


def get_target_points(config, action="default"):
    """
    根据操作从配置文件中获取目标点。

    :param config: dict，配置数据。
    :param action: str，用户操作名称。
    :return: list，目标点位列表。
    """
    return config.get("target_points", {}).get(action, [])
