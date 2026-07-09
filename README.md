# Jupyter Notebook 最佳实践项目模板（Colab 同步优化版）

这是一个专为 **Jupyter Notebook 管理** 打造的 Git 仓库模板，特别针对 **Google Colab 同步与协作** 进行了架构优化与最佳实践配置。

---

## 📂 目录结构

```text
.
├── .gitattributes               # 配置 Jupyter 提交过滤器 (自动清理输出)
├── .gitignore                   # 过滤 Python 临时文件与大型数据文件
├── README.md                    # 本说明文档
├── requirements.txt             # 【全局依赖】仅存放通用开发工具 (如 nbstripout)
├── data/                        # 【小额数据】存放配置文件、小测试数据 (< 10MB)
│   └── .gitkeep
├── src/                         # 【复用模块】存放可在多个 Notebook 间共享的 Python 脚本
│   └── utils.py                 # 提供双端挂载、路径智能获取等辅助函数
└── notebooks/                   # 【笔记本库】
    ├── .gitkeep
    └── project_analysis_demo/   # 【子项目示例】
        ├── analysis.ipynb       # 演示 Notebook
        └── requirements.txt     # 【局部依赖】该子项目特有的第三方库 (如 pandas, matplotlib)
```

---

## 🚀 最佳实践 1：版本控制优化 (清除 Notebook 输出)

Jupyter Notebook (`.ipynb`) 文件本质上是 JSON 文件。如果直接将运行后的 Notebook 提交到 Git，会导致：
1. **图片等二进制输出**被写入 Git 历史，使仓库体积迅速膨胀。
2. 每次运行时**执行次数 (Execution Count)** 的变化导致无意义的 Git Diff 冲突。

### 🛠️ 解决方案：`nbstripout`
我们在 `.gitattributes` 中配置了 `filter=nbstripout`。您只需在**本地**执行以下命令一次，此后 `git commit` 时就会自动在后台清除 Notebook 中的输出和执行计数，保持 Git History 绝对干净：

```bash
# 1. 创建并激活您的本地虚拟环境 (推荐)
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装全局依赖
pip install -r requirements.txt

# 3. 在当前 Git 仓库中激活过滤属性
nbstripout --install
```

> [!NOTE]
> 该配置只在您提交时临时过滤，**不会**影响您本地编辑时看到的输出。另外，从 Google Colab 界面直接“保存副本到 GitHub”时不受本地 filter 限制，依然能完整保留输出，提供了完美的平衡。

---

## 📦 最佳实践 2：依赖管理 (全局 vs 局部)

每个 Notebook 的研究主题各不相同（如 NLP、图像处理、金融分析），为了防止库版本冲突和环境臃肿，我们采用**分层维护模式**：

1. **全局依赖 (`./requirements.txt`)**：仅包含开发工具（如 `nbstripout`）。
2. **局部依赖 (`./notebooks/<your_project>/requirements.txt`)**：存放该具体研究项目专用的库。

### 💻 在 Colab 中动态安装子项目依赖
当您在 Colab 中打开某个子项目笔记本时，在 Notebook 首个单元格内运行以下代码，即可快速完成环境配置：

```python
import sys
import os

# 1. 智能检测是否在 Colab 运行
if 'google.colab' in sys.modules:
    # 2. 挂载 Google Drive
    from google.colab import drive
    drive.mount('/content/drive')
    
    # 3. 切换到您在 Drive 中克隆的仓库目录
    REPO_NAME = "notebooks" 
    REPO_PATH = f"/content/drive/MyDrive/{REPO_NAME}"
    os.chdir(REPO_PATH)
    
    # 4. 定位并安装子项目的局部依赖
    %cd {REPO_PATH}/notebooks/project_analysis_demo
    !pip install -r requirements.txt
```

---

## 💾 最佳实践 3：数据存储划分决策

为防止 Git 仓库性能退化，我们建议遵守以下数据划分准则：

```mermaid
graph TD
    Data[需要使用的数据文件] --> Size{文件大小?}
    Size -- 小于 10 MB --> Type{是否属于配置或静态小样本?}
    Type -- 是 --> Git["存放在 data/ 目录<br>(由 Git 追踪)"]
    Type -- 否 --> Drive["存放在 Google Drive<br>(Git 自动忽略)"]
    Size -- 大于 10 MB --> Drive
```

### 🔗 在 Colab 中优雅地跨平台读取数据
无论在本地还是 Colab，我们都推荐使用 `src/utils.py` 中的 `get_data_path()` 函数来规约数据路径，它会自动探测项目根目录：

```python
# 确保项目根目录在 sys.path 中
import sys, os
# ... (具体寻径代码见示例 notebook) ...

from src.utils import get_data_path

# 获取数据路径（本地或 Colab 挂载点）
data_file = get_data_path("my_large_dataset.csv")

# 读写数据
import pandas as pd
df = pd.read_csv(data_file)
```

---

## 🔄 最佳实践 4：Google Colab 同步指南

您有两种方式实现 Colab 与 GitHub 的双向同步：

### 方案 A：通过 GitHub 插件直接同步 (最推荐，适合轻量修改)
1. **打开**：访问 [Google Colab](https://colab.research.google.com/)，选择 **GitHub** 标签页，输入您的仓库地址并选择对应的 `.ipynb` 文件打开。
2. **在 Notebook 中添加快捷打开徽章**：
   在 Notebook 顶部添加如下 Markdown：
   ```markdown
   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<用户名>/<仓库名>/blob/main/notebooks/<项目文件夹>/<文件名>.ipynb)
   ```
3. **保存**：修改完成后，点击 **File -> Save a copy in GitHub**，即可将修改直接提交回 GitHub 仓库（带输出）。

### 方案 B：Google Drive 挂载 + Git 同步 (适合重度开发/大型数据集)
1. 在本地或 Colab 中将仓库克隆至 Google Drive 中的特定目录下：
   ```bash
   # 在 Colab 挂载 Drive 后运行
   %cd /content/drive/MyDrive
   !git clone https://github.com/<用户名>/<仓库名>.git
   ```
2. 在 Colab Notebook 中开发。所有修改会自动实时保存到您的 Google Drive。
3. 当需要将修改推送到 GitHub 时，直接在 Notebook 中运行以下命令：
   ```python
   !git config --global user.name "Your Name"
   !git config --global user.email "your.email@example.com"
   !git add .
   !git commit -m "update: training results"
   !git push
   ```
   *(提示：可配合 SSH 密钥或 GitHub Personal Access Token 进行免密 Push)*
