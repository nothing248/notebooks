import sys
import os
from IPython import get_ipython
ipython = get_ipython()

# 1. 检测是否处于 Colab 环境
IN_COLAB = 'google.colab' in sys.modules

# 2. 寻找项目根目录 (本地寻径逻辑)
current_dir = os.path.abspath(os.getcwd())
root_dir = current_dir
for _ in range(5):
    # 向上寻找含有 .git 或 requirements.txt 的项目根目录
    if os.path.exists(os.path.join(root_dir, '.git')):
        break
    parent_dir = os.path.dirname(root_dir)
    if parent_dir == root_dir:
        break
    root_dir = parent_dir


# 3. 针对 Colab 的专属挂载、同步和重置根目录逻辑
if IN_COLAB:
    GITHUB_USER = "nothing248"
    REPO_NAME = "notebooks"
    
    subdir = globals().get('COLAB_SUBDIR', '')
    COLAB_LOCAL_PATH = f"/content/{REPO_NAME}"
    DRIVE_BASE_PATH = "/content/drive/MyDrive"
    DRIVE_PATH = f"{DRIVE_BASE_PATH}/{REPO_NAME}"
    
    # 尝试挂载 Google Drive
    has_drive = False
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        has_drive = os.path.exists(DRIVE_BASE_PATH)
    except Exception as e:
        print("提示: 未挂载 Google Drive，将使用 Colab 临时虚拟机环境。")
        

    
    if has_drive:
        REPO_PATH = DRIVE_PATH
        if not os.path.exists(REPO_PATH):
            print(f"Google Drive 中未检测到仓库。正在自动克隆至 Drive 中永久保留...")
            os.chdir(DRIVE_BASE_PATH)
            ipython.system(f"git clone https://github.com/{GITHUB_USER}/{REPO_NAME}.git")
        else:
            print(f"检测到 Google Drive 中已存在仓库，直接使用并拉取 GitHub 最新代码...")
            os.chdir(REPO_PATH)
            ipython.system("git pull")
    else:
        REPO_PATH = COLAB_LOCAL_PATH
        if not os.path.exists(REPO_PATH):
            print("正在自动将 GitHub 仓库克隆到 Colab 临时虚拟机环境中...")
            ipython.system(f"git clone https://github.com/{GITHUB_USER}/{REPO_NAME}.git {REPO_PATH}")
        else:
            print(f"Colab 临时虚拟机环境中已存在仓库，正在自动拉取 GitHub 最新代码...")
            os.chdir(REPO_PATH)
            ipython.system("git pull")
            
    # Colab 端的根目录重定向为克隆的仓库路径
    root_dir = REPO_PATH  
    
    # 切换 Colab 下的工作路径到子项目目录
    if subdir:
        TARGET_SUBDIR = os.path.join(REPO_PATH, "notebooks", subdir)
    else:
        TARGET_SUBDIR = REPO_PATH
    os.chdir(TARGET_SUBDIR)
    print(f"工作目录已成功切换至: {os.getcwd()}")

# 4. 将项目根目录（不管是本地寻得的，还是 Colab 定位的）加入 sys.path
if root_dir not in sys.path:
    sys.path.append(root_dir)
    print(f"项目根目录已添加至 sys.path: {root_dir}")

# 5. 自动配置并安装依赖
req_file = os.path.join(os.getcwd(), "requirements.txt")
global_req = os.path.join(root_dir, "requirements.txt")

if IN_COLAB:
    print("正在安装现代包管理器 uv...")
    ipython.system("pip install uv -q")
    
    if os.path.exists(req_file):
        print(f"检测到局部依赖文件，正在使用 uv 安装: {req_file}")
        ipython.system(f"uv pip install --system -r {req_file} -q")
    elif os.path.exists(global_req):
        print(f"正在安装全局依赖: {global_req}")
        ipython.system(f"uv pip install --system -r {global_req} -q")
            
    print("✨ Colab 双端环境一键初始化完成！")
else:
    # 本地环境下的依赖同步 (智能检测 uv 并利用 sys.executable 确保安装至当前 Kernel 虚拟环境中)
    target_req = req_file if os.path.exists(req_file) else (global_req if os.path.exists(global_req) else None)
    if target_req:
        print(f"检测到本地依赖文件，正在自动同步安装: {target_req}")
        try:
            import subprocess
            subprocess.run(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            # 使用 --python 参数将依赖精准安装到当前 Jupyter 运行的虚拟环境解释器中
            ipython.system(f'uv pip install --python "{sys.executable}" -r {target_req}')
        except Exception:
            print("本地未检测到 uv 命令，将使用当前环境的 pip 进行安装...")
            # 使用 sys.executable -m pip 确保安装到对应的运行环境，防止全局污染
            ipython.system(f'"{sys.executable}" -m pip install -r {target_req}')
            
    print("✨ 本地开发环境：一键初始化及依赖同步完成！")
