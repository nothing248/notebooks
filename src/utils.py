import os
import sys

def get_data_path(filename=""):
    """
    智能获取数据文件的绝对路径。
    自动向上递归寻找项目根目录（基于 .git 或 requirements.txt），返回相对根目录下 'data/' 文件夹的绝对路径。
    这保证了代码在本地（Local）和 Google Colab 上均可使用相同的相对结构直接读写数据。
    
    参数:
    filename (str): 数据文件名（可选）
    
    返回:
    str: 对应数据文件或数据文件夹的绝对路径
    """
    current_dir = os.path.abspath(os.getcwd())
    root_dir = current_dir
    
    # 递归向上寻找项目根目录的标志文件/文件夹，最多向上查找 5 级
    for _ in range(5):
        if os.path.exists(os.path.join(root_dir, '.git')):
            break
        parent_dir = os.path.dirname(root_dir)
        if parent_dir == root_dir:
            break
        root_dir = parent_dir
        
    data_dir = os.path.join(root_dir, 'data')
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        
    if filename:
        return os.path.join(data_dir, filename)
    return data_dir
