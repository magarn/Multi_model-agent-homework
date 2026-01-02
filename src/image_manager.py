"""
智能图像管理模块
支持以文搜图功能
"""
import os
from pathlib import Path
from typing import List, Dict
from PIL import Image
import torch
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np


class ImageManager:
    """图像管理器"""
    
    def __init__(self, image_dir: str = "data/images", db_path: str = "data/chroma_db"):
        """
        初始化图像管理器
        
        Args:
            image_dir: 图像存储目录
            db_path: 向量数据库路径
        """
        self.image_dir = Path(image_dir)
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化CLIP模型
        print("正在加载CLIP模型...")
        try:
            # 使用sentence-transformers的CLIP模型
            self.model = SentenceTransformer('clip-ViT-B-32')
            print("CLIP模型加载完成")
        except Exception as e:
            print(f"CLIP模型加载失败: {e}")
            print("尝试使用备用模型...")
            # 备用方案：使用中文CLIP或其他模型
            self.model = SentenceTransformer('sentence-transformers/clip-ViT-B-32')
        
        # 初始化向量数据库
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="images",
            metadata={"hnsw:space": "cosine"}
        )
        
        print("图像管理器初始化完成")
    
    def add_image(self, image_path: str) -> Dict:
        """
        添加并索引单个图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            包含图像信息的字典
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"文件不存在: {image_path}")
        
        # 支持的图像格式
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        if image_path.suffix.lower() not in valid_extensions:
            raise ValueError(f"不支持的图像格式: {image_path.suffix}")
        
        print(f"正在处理图像: {image_path.name}")
        
        try:
            # 加载图像
            image = Image.open(image_path).convert('RGB')
            
            # 生成图像嵌入向量
            image_embedding = self.model.encode(image).tolist()
            
            # 生成图像ID
            img_id = f"img_{image_path.stem}_{hash(str(image_path))}"
            
            # 存储到向量数据库
            self.collection.add(
                embeddings=[image_embedding],
                documents=[str(image_path)],  # 存储文件路径作为文档
                metadatas=[{
                    "file_path": str(image_path),
                    "file_name": image_path.name,
                    "file_size": os.path.getsize(image_path)
                }],
                ids=[img_id]
            )
            
            print(f"图像已添加: {image_path.name}")
            return {
                "img_id": img_id,
                "file_name": image_path.name,
                "file_path": str(image_path)
            }
        except Exception as e:
            raise ValueError(f"处理图像时出错: {e}")
    
    def search_images(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        以文搜图：通过自然语言描述搜索图像
        
        Args:
            query: 文本查询（自然语言描述）
            top_k: 返回最相关的k个结果
            
        Returns:
            相关图像列表
        """
        print(f"正在搜索图像: {query}")
        
        # 生成文本查询的嵌入向量
        query_embedding = self.model.encode(query).tolist()
        
        # 在向量数据库中搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # 格式化结果
        images = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                img = {
                    "file_name": results['metadatas'][0][i]['file_name'],
                    "file_path": results['metadatas'][0][i]['file_path'],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                }
                images.append(img)
        
        return images
    
    def batch_index(self, source_dir: str):
        """
        批量索引文件夹中的所有图像
        
        Args:
            source_dir: 源文件夹路径
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            raise FileNotFoundError(f"目录不存在: {source_dir}")
        
        # 支持的图像格式
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        image_files = []
        for ext in valid_extensions:
            image_files.extend(source_path.glob(f"*{ext}"))
            image_files.extend(source_path.glob(f"*{ext.upper()}"))
        
        print(f"找到 {len(image_files)} 个图像文件")
        
        success_count = 0
        for image_file in image_files:
            try:
                self.add_image(str(image_file))
                success_count += 1
            except Exception as e:
                print(f"处理文件 {image_file.name} 时出错: {e}")
        
        print(f"批量索引完成，共处理 {success_count}/{len(image_files)} 个文件")
    
    def batch_process_images_dir(self, recursive: bool = True, source_dir: str = "images"):
        """
        批量处理 ./images 目录中的所有图像
        
        Args:
            recursive: 是否递归处理子目录（默认True）
            source_dir: 源目录路径（默认 "images"，与 data 目录同级）
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            raise FileNotFoundError(f"图像目录不存在: {source_path}")
        
        # 支持的图像格式
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        image_files = []
        
        if recursive:
            # 递归搜索所有子目录
            for ext in valid_extensions:
                image_files.extend(source_path.rglob(f"*{ext}"))
                image_files.extend(source_path.rglob(f"*{ext.upper()}"))
        else:
            # 只搜索当前目录
            for ext in valid_extensions:
                image_files.extend(source_path.glob(f"*{ext}"))
                image_files.extend(source_path.glob(f"*{ext.upper()}"))
        
        # 过滤掉已经索引的文件（通过检查向量数据库）
        existing_files = set()
        try:
            all_docs = self.collection.get()
            existing_files = {meta['file_path'] for meta in all_docs['metadatas']}
        except:
            pass
        
        # 只处理未索引的文件
        new_files = [f for f in image_files if str(f) not in existing_files]
        
        print(f"在 {source_path} 目录中找到 {len(image_files)} 个图像文件")
        if existing_files:
            print(f"其中 {len(new_files)} 个文件尚未索引，将进行批量处理")
        
        if not new_files:
            print("所有文件已索引，无需处理")
            return
        
        success_count = 0
        for image_file in new_files:
            try:
                self.add_image(str(image_file))
                success_count += 1
            except Exception as e:
                print(f"处理文件 {image_file.name} 时出错: {e}")
        
        print(f"批量处理完成，共处理 {success_count}/{len(new_files)} 个文件")

