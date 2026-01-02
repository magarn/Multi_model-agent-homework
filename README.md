# 本地 AI 智能文献与图像管理助手 (Local Multimodal AI Agent)

## 1. 项目简介 (Project Introduction)
本项目是一个基于 Python 的本地多模态 AI 智能助手，旨在解决本地大量文献和图像素材管理困难的问题。不同于传统的文件名搜索，本项目利用多模态神经网络技术，实现对内容的**语义搜索**和**自动分类**。本项目可以帮助各位同学理解多模态大模型的实际应用，并且可以在实际日常学习生活中帮助各位同学管理自己的本地知识库。希望各位同学可以不局限于本次作业规定的内容，通过自己的构建、扩展和维护实现自己的本地AI助手。

项目可使用本地化部署，也可以调用云端大模型 API 以获得更强的性能。

## 2. 核心功能要求 (Core Features)

### 2.1 智能文献管理
*   **语义搜索**: 支持使用自然语言提问（如“Transformer 的核心架构是什么？”）。系统需基于语义理解返回最相关的论文文件，进阶要求可返回具体的论文片段或页码。
*   **自动分类与整理**:
    *   **单文件处理**: 添加新论文时，根据指定的主题（如 "CV, NLP, RL"）自动分析内容，将其归类并移动到对应的子文件夹中。
    *   **批量整理**: 支持对现有的混乱文件夹进行“一键整理”，自动扫描所有 PDF，识别主题并归档到相应目录。
*   **文件索引**: 支持仅返回相关文件列表，方便快速定位所需文献。

### 2.2 智能图像管理
*   **以文搜图**: 利用多模态图文匹配技术，支持通过自然语言描述（如“海边的日落”）来查找本地图片库中最匹配的图像。

## 3. 技术选型与模型建议 (Technical Stack)

本项目采用模块化设计，支持替换不同的后端模型。学生可根据自身硬件条件选择本地部署或调用云端 API（如 Gemini, GPT-4o 等）。

### 3.1 推荐配置 (轻量级/本地化)
*   **文本嵌入**: `SentenceTransformers` (如 `all-MiniLM-L6-v2`) —— 速度快，内存占用小。
*   **图像嵌入**: `CLIP` (如 `ViT-B-32`) —— OpenAI 开源的经典图文匹配模型。
*   **向量数据库**: `ChromaDB` —— 无需服务器，开箱即用的嵌入式数据库。

### 3.2 进阶配置建议 (高性能/多功能)
如果您拥有较好的硬件资源（如 NVIDIA GPU），可以尝试以下方案：

*   **图像描述与问答**:
    *   **Florence-2 (Microsoft)**: 轻量级全能视觉模型，支持 OCR、检测、描述。
    *   **Moondream**: 专为边缘设备设计的小型视觉语言模型。
    *   **LLaVA**: 开源多模态大模型，支持复杂的图文对话。
*   **文本理解**:
    *   **本地 LLM**: 如 `Llama-3` 或 `Qwen-2` (通过 Ollama 部署)，实现更精准的分类。

## 4. 环境要求 (Environment)

*   **操作系统**: Windows / macOS / Linux
*   **Python 版本**: 建议 Python 3.8 及以上
*   **内存**: 建议 8GB 及以上

## 5. 安装与配置 (Installation & Configuration)

### 5.1 依赖安装

1. 克隆或下载项目到本地：
```bash
git clone <your-repo-url>
cd agent
```

2. 创建虚拟环境（推荐）：
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

**注意**: 首次运行时，程序会自动下载所需的模型文件（约几百MB），请确保网络连接正常。

### 5.2 项目结构

```
agent/
├── main.py                 # 统一入口文件
├── requirements.txt        # 依赖包列表
├── README.md              # 项目说明文档
├── src/                   # 源代码目录
│   ├── __init__.py
│   ├── document_manager.py    # 文献管理模块
│   └── image_manager.py       # 图像管理模块
└── data/                  # 数据目录（自动创建）
    ├── documents/         # 文献存储目录
    ├── images/            # 图像存储目录
    └── chroma_db/         # 向量数据库存储目录
```

## 6. 使用说明 (Usage)

### 6.1 文献管理功能

#### 6.1.1 添加并分类单个论文

添加一个PDF文件，并根据指定主题自动分类：

```bash
python main.py add-paper paper.pdf --topics "CV,NLP,RL"
```

**参数说明**:
- `paper.pdf`: PDF文件路径（可以是相对路径或绝对路径）
- `--topics`: 主题列表，用逗号分隔，如 "CV,NLP,RL"

**功能**: 
- 提取PDF文本内容
- 生成语义嵌入向量并存储到向量数据库
- 根据主题关键词自动分类并移动到对应子文件夹（`data/documents/CV/`、`data/documents/NLP/` 等）

**示例**:
```bash
# 添加一篇关于计算机视觉的论文
python main.py add-paper transformer.pdf --topics "CV,DeepLearning"

# 添加一篇关于自然语言处理的论文
python main.py add-paper bert.pdf --topics "NLP,Transformer"
```

#### 6.1.2 语义搜索论文

使用自然语言查询搜索相关论文：

```bash
python main.py search-paper "What is the core architecture of a Transformer?"
```

**参数说明**:
- `"What is the core architecture of a Transformer?"`: 搜索查询（自然语言）

**可选参数**:
- `--top-k` 或 `-k`: 返回最相关的k个结果（默认5个）

**示例**:
```bash
# 搜索关于注意力机制的论文
python main.py search-paper "The Principles and Applications of Attention Mechanisms"

# 返回前10个最相关的结果
python main.py search-paper "Deep Learning" --top-k 10
```

**输出格式**:
```
找到 5 篇相关论文:

1. transformer.pdf
   路径: data/documents/CV/transformer.pdf
   主题: CV,DeepLearning
   相似度: 0.856
   摘要: Transformer is a model architecture eschewing recurrence and relying entirely on attention mechanisms...

2. bert.pdf
   ...
```

#### 6.1.3 批量整理文件夹

对现有文件夹中的所有PDF文件进行批量整理和分类：

```bash
python main.py organize-papers ./paper --topics "CV,NLP,RL"
```

**参数说明**:
- `./paper`: 源文件夹路径（包含待整理的PDF文件）
- `--topics`: 主题列表，用逗号分隔

**功能**:
- 扫描指定文件夹中的所有PDF文件
- 自动提取文本并生成索引
- 根据内容匹配主题并分类到对应目录

**示例**:
```bash
# 整理当前目录下的papers文件夹
python main.py organize-papers ./paper --topics "CV,NLP,RL,ML"

# 整理绝对路径的文件夹
python main.py organize-papers "C:\Users\Documents\Papers" --topics "CV,NLP"
```

#### 6.1.4 列出论文文件

列出所有已索引的论文文件，或根据查询返回相关文件列表：

```bash
# 列出所有文件
python main.py list-papers

# 根据查询列出相关文件
python main.py list-papers --query "deep learning"
```

**参数说明**:
- `--query` 或 `-q`: 可选的搜索查询，如果提供则只返回相关文件

**示例**:
```bash
# 列出所有已索引的论文
python main.py list-papers

# 列出与"Transformer"相关的论文
python main.py list-papers --query "Transformer"
```

### 6.2 图像管理功能

#### 6.2.1 添加并索引图像

添加单个图像文件到索引库：

```bash
python main.py add-image photo.jpg
```

**参数说明**:
- `photo.jpg`: 图像文件路径（支持 jpg, jpeg, png, bmp, gif, webp 格式）

**功能**:
- 加载图像并生成CLIP嵌入向量
- 存储到向量数据库以供后续搜索

**示例**:
```bash
# 添加单张图片
python main.py add-image sunset.jpg

# 添加PNG格式图片
python main.py add-image landscape.png
```

#### 6.2.2 以文搜图

通过自然语言描述搜索相关图像：

```bash
python main.py search-image "海边的日落"
```

**参数说明**:
- `"海边的日落"`: 文本查询（自然语言描述）

**可选参数**:
- `--top-k` 或 `-k`: 返回最相关的k个结果（默认5个）

**示例**:
```bash
# 搜索日落相关的图片
python main.py search-image "Sunset by the Sea"

# 搜索动物相关的图片
python main.py search-image "tiger"
python main.py search-image "The Snake by the Sea"

# 返回前10个最相关的结果
python main.py search-image "Landscape" --top-k 10
```

**输出格式**:
```
找到 5 张相关图像:

1. sunset.jpg
   路径: data/images/sunset.jpg
   相似度: 0.923

2. beach.jpg
   ...
```

#### 6.2.3 批量索引图像

批量索引文件夹中的所有图像：

```bash
python main.py index-images ./images
```

**参数说明**:
- `./images`: 源文件夹路径（包含待索引的图像文件）

**功能**:
- 扫描指定文件夹中的所有图像文件（jpg, jpeg, png, bmp, gif, webp）
- 自动生成嵌入向量并存储到向量数据库

**示例**:
```bash
# 索引当前目录下的photos文件夹
python main.py index-images ./images

# 索引绝对路径的文件夹
python main.py index-images "C:\Users\Pictures\Vacation"
```

#### 6.2.4 批量处理 data/images 目录

批量处理 `./images` 目录中的所有图像文件（包括子目录）：

```bash
python main.py process-images
```

**参数说明**:
- `--recursive` 或 `-r`: 是否递归处理子目录（默认启用）
- `--no-recursive`: 只处理根目录，不递归子目录

**功能**:
- 自动扫描 `./images` 目录下的所有图像文件
- 自动跳过已经索引的文件，只处理新文件
- 支持递归处理所有子目录
- 自动生成嵌入向量并存储到向量数据库

**示例**:
```bash
# 批量处理 ./images 目录中的所有图像（递归子目录）
python main.py process-images

# 只处理 ./images 根目录，不递归子目录
python main.py process-images --no-recursive

# 使用短参数
python main.py process-images -r
```

**使用场景**:
- 当你将图像文件直接放入 `data/images` 目录后，可以使用此命令批量索引
- 适合定期批量处理新增的图像文件
- 自动跳过已索引的文件，避免重复处理

### 6.3 查看帮助信息

查看所有可用命令：

```bash
python main.py --help
```

查看特定命令的详细帮助：

```bash
python main.py add-paper --help
python main.py search-paper --help
python main.py search-image --help
```

## 7. 技术选型说明 (Technical Stack Details)

本项目采用以下技术栈：

### 7.1 文本处理
- **SentenceTransformers (all-MiniLM-L6-v2)**: 
  - 轻量级文本嵌入模型，速度快，内存占用小
  - 支持多语言，适合中文和英文文献
  - 模型大小约80MB，首次运行会自动下载

### 7.2 图像处理
- **CLIP (ViT-B-32)**: 
  - OpenAI开源的经典图文匹配模型
  - 支持通过文本描述搜索图像
  - 模型大小约600MB，首次运行会自动下载

### 7.3 向量数据库
- **ChromaDB**: 
  - 嵌入式向量数据库，无需单独部署服务器
  - 支持持久化存储，数据保存在本地
  - 使用余弦相似度进行语义搜索

### 7.4 PDF处理
- **pdfplumber**: 主要PDF文本提取工具，提取准确度高
- **PyPDF2**: 备用PDF处理库，作为fallback方案

### 7.5 命令行接口
- **Click**: Python命令行工具库，提供友好的CLI界面

## 8. 注意事项 (Notes)

1. **首次运行**: 首次运行时会自动下载模型文件，请确保网络连接正常，下载时间取决于网络速度。

2. **存储空间**: 
   - 模型文件约占用700MB磁盘空间
   - 向量数据库会根据索引的文件数量增长

3. **性能优化**:
   - 如果有NVIDIA GPU，可以安装GPU版本的PyTorch以加速模型推理
   - 对于大量文件，建议分批处理

4. **文件格式支持**:
   - 文献: 仅支持PDF格式
   - 图像: 支持 jpg, jpeg, png, bmp, gif, webp 格式

5. **数据安全**: 所有数据（文献、图像、向量索引）都存储在本地，不会上传到云端。

## 9. 作业提交要求 (Submission Guidelines)

为规范作业提交与评测流程，请严格按照以下要求提交：

### 5.1 代码提交
*   **GitHub 仓库**: 将完整项目代码上传至 GitHub 个人仓库，并提交仓库链接。
*   **README 文档**: 仓库首页必须包含详细的 `README.md`，内容包括：
    *   项目简介与核心功能列表。
    *   环境配置与依赖安装说明。
    *   **详细的使用说明**（包含具体的命令行示例）。
    *   技术选型说明（使用了哪些模型、数据库等）。

### 5.2 评测接口规范
*   **统一入口**: 项目根目录下必须包含 `main.py` 文件。
*   **一键调用**: 必须支持通过命令行参数调用核心功能。参考格式如下（不仅限于此）：
    *   添加/分类论文: `python main.py add-paper <path> --topics "Topic1,Topic2"`
    *   搜索论文: `python main.py search-paper <query>`
    *   以文搜图: `python main.py search-image <query>`

### 5.3 演示文档
请提交一份 PDF 格式的演示报告（或直接包含在 README 中），内容需包括：
*   **运行截图**: 关键功能的运行结果截图（如搜索结果、分类后的文件夹结构）。
*   **演示视频 (可选)**: 录制一段屏幕录像，演示从环境启动到功能使用的全过程。

---

# Local Multimodal AI Agent (English Version)

## 1. Project Introduction
This project is a Python-based local multimodal AI assistant designed to solve the difficulty of managing large collections of local documents and images. Unlike traditional filename-based searches, this project utilizes multimodal neural network technology to achieve **semantic search** and **automatic classification** of content.

The project is designed to be flexible, supporting both fully offline local deployment (for privacy) and cloud-based large model API integration for enhanced performance.

## 2. Core Features

### 2.1 Intelligent Document Management
*   **Semantic Search**: Supports natural language queries (e.g., "What is the core architecture of Transformer?"). The system should return the most relevant paper documents based on semantic understanding. Advanced implementations can return specific snippets or page numbers.
*   **Automatic Classification & Organization**:
    *   **Single File Processing**: When adding a new paper, the system automatically analyzes the content based on specified topics (e.g., "CV, NLP, RL") and moves it to the corresponding subfolder.
    *   **Batch Organization**: Supports "one-click organization" for existing messy folders, automatically scanning all PDFs, identifying topics, and archiving them into appropriate directories.
*   **File Indexing**: Supports returning only a list of relevant files for quick location.

### 2.2 Intelligent Image Management
*   **Text-to-Image Search**: Utilizes multimodal text-image matching technology to allow users to find the best-matching images in the local library using natural language descriptions (e.g., "sunset by the sea").

## 3. Technical Stack & Recommendations

This project adopts a modular design, allowing for the replacement of different backend models. Students can choose between local deployment or calling cloud APIs (such as Gemini, GPT-4o) based on their hardware conditions.

### 3.1 Recommended Configuration (Lightweight/Local)
*   **Text Embedding**: `SentenceTransformers` (e.g., `all-MiniLM-L6-v2`) — Fast speed, low memory usage.
*   **Image Embedding**: `CLIP` (e.g., `ViT-B-32`) — OpenAI's classic open-source text-image matching model.
*   **Vector Database**: `ChromaDB` — Serverless, out-of-the-box embedded database.

### 3.2 Advanced Configuration (High Performance)
If you have better hardware resources (such as NVIDIA GPUs), consider the following options:

*   **Image Captioning & QA**:
    *   **Florence-2 (Microsoft)**: Lightweight yet powerful vision model supporting OCR, detection, and captioning.
    *   **Moondream**: Small vision-language model designed for edge devices.
    *   **LLaVA**: Open-source multimodal large model supporting complex image-text dialogue.
*   **Text Understanding**:
    *   **Local LLM**: Such as `Llama-3` or `Qwen-2` (deployed via Ollama) for more precise classification.

## 4. Environment Requirements

*   **OS**: Windows / macOS / Linux
*   **Python Version**: Recommended Python 3.8+
*   **Memory**: Recommended 8GB+ (for loading basic Embedding models)

## 10. Submission Guidelines

To standardize the submission and evaluation process, please strictly follow these requirements:

### 5.1 Code Submission
*   **GitHub Repository**: Upload the complete project code to a personal GitHub repository and submit the link.
*   **README**: The repository homepage must include a detailed `README.md` containing:
    *   Project introduction and core feature list.
    *   Environment configuration and dependency installation instructions.
    *   **Detailed usage instructions** (including specific command-line examples).
    *   Technical stack explanation (models, databases used, etc.).

### 5.2 Evaluation Interface Specification
*   **Unified Entry Point**: The project root directory must contain a `main.py` file.
*   **One-Click Execution**: Core features must be callable via command-line arguments. Reference format (not limited to):
    *   Add/Classify Paper: `python main.py add-paper <path> --topics "Topic1,Topic2"`
    *   Search Paper: `python main.py search-paper <query>`
    *   Search Image: `python main.py search-image <query>`

### 5.3 Demonstration Documentation
Please submit a PDF demonstration report (or include it in the README), which must include:
*   **Screenshots**: Screenshots of key function results (e.g., search results, folder structure after classification).
*   **Demo Video (Optional)**: Record a screen capture video demonstrating the entire process from environment startup to feature usage.
