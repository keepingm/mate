import yaml

# 全局配置变量
config = None

def load_config(filename='/home/mgh/dev/projects/python_projects/mate/config.yaml'):
    global config
    if config is None:  # 只在第一次调用时加载配置
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)  # 使用 safe_load 来避免不安全的数据
    return config

# 载入配置
load_config()  # 可以在模块初始化时加载配置
