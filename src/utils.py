import os
import sys

def setup_colab(repo_name=""):
    """
    智能检测当前是否运行在 Google Colab 环境中。
    如果是，则引导挂载 Google Drive，并协助将工作路径切换到该 Git 仓库下。
    
    参数:
    repo_name (str): Google Drive 中你克隆的 Git 仓库文件夹名称。
    """
    if 'google.colab' in sys.modules:
        print("检测到正在 Google Colab 环境中运行。正在准备挂载 Google Drive...")
        from google.colab import drive
        drive.mount('/content/drive')
        
        if repo_name:
            # 通常克隆在 'My Drive' 下对应的项目目录
            target_path = f"/content/drive/MyDrive/{repo_name}"
            if os.path.exists(target_path):
                os.chdir(target_path)
                print(f"成功切换工作目录至 Google Drive 仓库路径: {target_path}")
            else:
                print(f"警告: 路径 {target_path} 不存在。请确认你在 Google Drive 中的仓库文件夹名称。")
        else:
            print("提示: 未指定 repo_name。您可以挂载 Drive 后手动切换工作目录。")
    else:
        print("检测到为本地开发环境，无需挂载 Google Drive。")


def get_data_path(filename=""):
    """
    智能获取数据文件的路径。
    自动检测项目根目录（基于当前文件位置或工作目录），返回相对于项目根目录的 'data/' 文件夹的绝对路径。
    
    参数:
    filename (str): 数据文件名（可选）
    
    返回:
    str: 对应数据文件的绝对路径
    """
    # 递归向上寻找项目根目录的标志文件/文件夹（如 .git 或 requirements.txt）
    current_dir = os.path.abspath(os.getcwd())
    root_dir = current_dir
    
    for _ in range(5):  # 最多向上查找 5 级
        if os.path.exists(os.path.join(root_dir, '.git')) or os.path.exists(os.path.join(root_dir, 'requirements.txt')):
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
