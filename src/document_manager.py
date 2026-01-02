"""
智能文献管理模块
支持PDF文件的语义搜索、自动分类和整理
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
import pdfplumber
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np


class DocumentManager:
    """文献管理器"""
    
    def __init__(self, data_dir: str = "data/documents", db_path: str = "data/chroma_db"):
        """
        初始化文献管理器
        
        Args:
            data_dir: 文献存储目录
            db_path: 向量数据库路径
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化文本嵌入模型
        print("正在加载文本嵌入模型...")
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 初始化向量数据库
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        print("文献管理器初始化完成")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        从PDF文件中提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本内容
        """
        text = ""
        try:
            # 使用pdfplumber提取文本（更准确）
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"使用pdfplumber提取失败，尝试PyPDF2: {e}")
            # 备用方案：使用PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"PDF文本提取失败: {e2}")
                return ""
        
        return text.strip()
    
    def add_document(self, pdf_path: str, topics: Optional[List[str]] = None) -> Dict:
        """
        添加并索引单个PDF文档
        
        Args:
            pdf_path: PDF文件路径
            topics: 主题列表（用于分类）
            
        Returns:
            包含文档信息的字典
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"文件不存在: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"仅支持PDF文件: {pdf_path}")
        
        print(f"正在处理文档: {pdf_path.name}")
        
        # 提取文本
        text = self.extract_text_from_pdf(str(pdf_path))
        if not text:
            raise ValueError(f"无法从PDF中提取文本: {pdf_path}")
        
        # 生成嵌入向量
        embedding = self.text_model.encode(text).tolist()
        
        # 生成文档ID
        doc_id = f"doc_{pdf_path.stem}_{hash(str(pdf_path))}"
        
        # 存储到向量数据库
        self.collection.add(
            embeddings=[embedding],
            documents=[text[:10000]],  # ChromaDB有长度限制，截取前10000字符
            metadatas=[{
                "file_path": str(pdf_path),
                "file_name": pdf_path.name,
                "topics": ",".join(topics) if topics else ""
            }],
            ids=[doc_id]
        )
        
        # 如果指定了主题，进行自动分类
        if topics:
            self._classify_and_move(pdf_path, topics, text)
        
        print(f"文档已添加: {pdf_path.name}")
        return {
            "doc_id": doc_id,
            "file_name": pdf_path.name,
            "file_path": str(pdf_path),
            "text_length": len(text)
        }
    
    def _classify_and_move(self, pdf_path: Path, topics: List[str], text: str):
        """
        根据主题分类并移动文件
        
        Args:
            pdf_path: PDF文件路径
            topics: 主题列表
            text: 文档文本内容
        """
        # 使用简单的关键词匹配进行分类（可以改进为使用LLM）
        text_lower = text.lower()
        matched_topics = []
        
        for topic in topics:
            if topic.lower() in text_lower:
                matched_topics.append(topic)
        
        # 如果没有匹配，使用第一个主题作为默认
        if not matched_topics:
            matched_topics = [topics[0]]
        
        # 创建主题目录并移动文件
        for topic in matched_topics:
            topic_dir = self.data_dir / topic.strip()
            topic_dir.mkdir(parents=True, exist_ok=True)
            
            # 移动文件到对应主题目录
            dest_path = topic_dir / pdf_path.name
            if pdf_path != dest_path:  # 避免移动到自身
                shutil.copy2(pdf_path, dest_path)
                print(f"文件已分类到: {topic}/{pdf_path.name}")
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        语义搜索文档
        
        Args:
            query: 搜索查询（自然语言）
            top_k: 返回最相关的k个结果
            
        Returns:
            相关文档列表
        """
        print(f"正在搜索: {query}")
        
        # 生成查询向量
        query_embedding = self.text_model.encode(query).tolist()
        
        # 在向量数据库中搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # 格式化结果
        documents = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                doc = {
                    "file_name": results['metadatas'][0][i]['file_name'],
                    "file_path": results['metadatas'][0][i]['file_path'],
                    "topics": results['metadatas'][0][i].get('topics', ''),
                    "distance": results['distances'][0][i] if 'distances' in results else None,
                    "snippet": results['documents'][0][i][:200] + "..." if len(results['documents'][0][i]) > 200 else results['documents'][0][i]
                }
                documents.append(doc)
        
        return documents
    
    def batch_organize(self, source_dir: str, topics: List[str]):
        """
        批量整理文件夹中的PDF文件
        
        Args:
            source_dir: 源文件夹路径
            topics: 主题列表
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            raise FileNotFoundError(f"目录不存在: {source_dir}")
        
        pdf_files = list(source_path.glob("*.pdf"))
        print(f"找到 {len(pdf_files)} 个PDF文件")
        
        for pdf_file in pdf_files:
            try:
                self.add_document(str(pdf_file), topics)
            except Exception as e:
                print(f"处理文件 {pdf_file.name} 时出错: {e}")
        
        print(f"批量整理完成，共处理 {len(pdf_files)} 个文件")
    
    def list_files(self, query: Optional[str] = None) -> List[str]:
        """
        列出相关文件（仅返回文件列表）
        
        Args:
            query: 可选的搜索查询，如果提供则返回相关文件
            
        Returns:
            文件路径列表
        """
        if query:
            results = self.search_documents(query, top_k=10)
            return [doc['file_path'] for doc in results]
        else:
            # 返回所有已索引的文件
            all_docs = self.collection.get()
            return [meta['file_path'] for meta in all_docs['metadatas']]

