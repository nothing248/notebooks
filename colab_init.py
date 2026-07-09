import sys
import os

# 仅在 Google Colab 中执行初始化
if 'google.colab' in sys.modules:
    # 1. 基础配置
    GITHUB_USER = "nothing248"
    REPO_NAME = "notebooks"
    
    # 获取 Notebook 全局命名空间中定义的子目录名称
    # 比如在执行此脚本前，Notebook 需声明：COLAB_SUBDIR = "project_analysis_demo"
    subdir = globals().get('COLAB_SUBDIR', '')
    
    COLAB_LOCAL_PATH = f"/content/{REPO_NAME}"
    DRIVE_BASE_PATH = "/content/drive/MyDrive"
    DRIVE_PATH = f"{DRIVE_BASE_PATH}/{REPO_NAME}"
    
    # 2. 尝试挂载 Google Drive
    has_drive = False
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        has_drive = os.path.exists(DRIVE_BASE_PATH)
    except Exception as e:
        print("提示: 未挂载 Google Drive，将使用 Colab 临时虚拟机环境。")
    
    # 3. 决定运行和克隆路径
    from IPython import get_ipython
    ipython = get_ipython()
    
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
            
    # 4. 切换工作路径到当前 Notebook 所在的子项目目录
    if subdir:
        TARGET_SUBDIR = os.path.join(REPO_PATH, "notebooks", subdir)
    else:
        TARGET_SUBDIR = REPO_PATH
        
    os.chdir(TARGET_SUBDIR)
    print(f"工作目录已成功切换至: {os.getcwd()}")
    
    # 5. 自动把项目根目录添加到 sys.path 中，以便直接引用 src.utils
    if REPO_PATH not in sys.path:
        sys.path.append(REPO_PATH)
        print(f"项目根目录已添加至 sys.path: {REPO_PATH}")
        
    # 6. 使用 uv 极速安装子项目专属依赖
    print("正在安装现代包管理器 uv...")
    ipython.system("pip install uv -q")
    
    req_file = os.path.join(TARGET_SUBDIR, "requirements.txt")
    if os.path.exists(req_file):
        print(f"检测到局部依赖文件，正在使用 uv 安装: {req_file}")
        ipython.system(f"uv pip install --system -r {req_file} -q")
    else:
        global_req = os.path.join(REPO_PATH, "requirements.txt")
        if os.path.exists(global_req):
            print(f"正在安装全局依赖: {global_req}")
            ipython.system(f"uv pip install --system -r {global_req} -q")
            
    print("✨ Colab 双端环境一键初始化完成！")
else:
    print("当前为本地开发环境，跳过 Colab 自动初始化配置。")
