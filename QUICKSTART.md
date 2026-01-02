# 快速开始指南 (Quick Start Guide)

## 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 2. 快速测试

### 测试文献管理功能

1. **准备测试文件**: 将一些PDF论文文件放在一个文件夹中，例如 `test_papers/`

2. **批量整理论文**:
```bash
python main.py organize-papers test_papers --topics "CV,NLP,ML"
```

3. **搜索论文**:
```bash
python main.py search-paper "深度学习"
```

### 测试图像管理功能

**方法一：处理外部文件夹**
1. **准备测试文件**: 将一些图片文件放在一个文件夹中，例如 `test_images/`

2. **批量索引图像**:
```bash
python main.py index-images test_images
```

**方法二：处理 data/images 目录（推荐）**
1. **准备测试文件**: 将图片文件直接放入 `data/images/` 目录（可包含子目录）

2. **批量处理图像**:
```bash
python main.py process-images
```

3. **以文搜图**:
```bash
python main.py search-image "风景"
```

## 3. 查看所有命令

```bash
python main.py --help
```

## 4. 常见问题

**Q: 首次运行很慢？**  
A: 首次运行需要下载模型文件（约700MB），请耐心等待。

**Q: 如何查看已索引的文件？**  
A: 使用 `python main.py list-papers` 查看所有已索引的论文。

**Q: 数据存储在哪里？**  
A: 所有数据存储在 `data/` 目录下，包括文献、图像和向量数据库。

**Q: 如何删除索引？**  
A: 删除 `data/chroma_db/` 目录即可清除所有索引数据。


