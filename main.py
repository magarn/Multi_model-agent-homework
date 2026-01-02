#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地 AI 智能文献与图像管理助手
统一入口文件，支持命令行参数调用
"""
import click
import sys
from pathlib import Path
from src.document_manager import DocumentManager
from src.image_manager import ImageManager


# 全局管理器实例
doc_manager = None
img_manager = None


def init_managers():
    """初始化管理器"""
    global doc_manager, img_manager
    if doc_manager is None:
        doc_manager = DocumentManager()
    if img_manager is None:
        img_manager = ImageManager()


@click.group()
def cli():
    """本地 AI 智能文献与图像管理助手"""
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--topics', '-t', help='主题列表，用逗号分隔，如: "CV,NLP,RL"')
def add_paper(path, topics):
    """添加并分类论文文件
    
    PATH: PDF文件路径
    
    示例:
        python main.py add-paper paper.pdf --topics "CV,NLP"
    """
    init_managers()
    
    topics_list = None
    if topics:
        topics_list = [t.strip() for t in topics.split(',')]
    
    try:
        result = doc_manager.add_document(path, topics_list)
        click.echo(f"✓ 论文已添加: {result['file_name']}")
        if topics_list:
            click.echo(f"  主题: {', '.join(topics_list)}")
    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--top-k', '-k', default=5, help='返回最相关的k个结果')
def search_paper(query, top_k):
    """语义搜索论文
    
    QUERY: 搜索查询（自然语言）
    
    示例:
        python main.py search-paper "Transformer的核心架构是什么"
    """
    init_managers()
    
    try:
        results = doc_manager.search_documents(query, top_k=top_k)
        
        if not results:
            click.echo("未找到相关论文")
            return
        
        click.echo(f"\n找到 {len(results)} 篇相关论文:\n")
        for i, doc in enumerate(results, 1):
            click.echo(f"{i}. {doc['file_name']}")
            click.echo(f"   路径: {doc['file_path']}")
            if doc.get('topics'):
                click.echo(f"   主题: {doc['topics']}")
            if doc.get('distance') is not None:
                click.echo(f"   相似度: {1 - doc['distance']:.3f}")
            click.echo(f"   摘要: {doc.get('snippet', '')[:100]}...")
            click.echo()
    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--topics', '-t', required=True, help='主题列表，用逗号分隔，如: "CV,NLP,RL"')
def organize_papers(source_dir, topics):
    """批量整理文件夹中的PDF文件
    
    SOURCE_DIR: 源文件夹路径
    
    示例:
        python main.py organize-papers ./papers --topics "CV,NLP,RL"
    """
    init_managers()
    
    topics_list = [t.strip() for t in topics.split(',')]
    
    try:
        click.echo(f"开始批量整理文件夹: {source_dir}")
        doc_manager.batch_organize(source_dir, topics_list)
        click.echo("✓ 批量整理完成")
    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--query', '-q', help='可选的搜索查询')
def list_papers(query):
    """列出论文文件（仅返回文件列表）
    
    示例:
        python main.py list-papers
        python main.py list-papers --query "深度学习"
    """
    init_managers()
    
    try:
        files = doc_manager.list_files(query)
        
        if not files:
            click.echo("未找到论文文件")
            return
        
        click.echo(f"\n找到 {len(files)} 个文件:\n")
        for file_path in files:
            click.echo(f"  {file_path}")
    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--top-k', '-k', default=5, help='返回最相关的k个结果')
def search_image(query, top_k):
    """以文搜图：通过自然语言描述搜索图像
    
    QUERY: 文本查询（自然语言描述）
    
    示例:
        python main.py search-image "海边的日落"
    """
    init_managers()
    
    try:
        results = img_manager.search_images(query, top_k=top_k)
        
        if not results:
            click.echo("未找到相关图像")
            return
        
        click.echo(f"\n找到 {len(results)} 张相关图像:\n")
        for i, img in enumerate(results, 1):
            click.echo(f"{i}. {img['file_name']}")
            click.echo(f"   路径: {img['file_path']}")
            if img.get('distance') is not None:
                click.echo(f"   相似度: {1 - img['distance']:.3f}")
            click.echo()
    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
def add_image(image_path):
    """添加并索引图像文件
    
    IMAGE_PATH: 图像文件路径
    
    示例:
        python main.py add-image photo.jpg
    """
    init_managers()
    
    try:
        result = img_manager.add_image(image_path)
        click.echo(f"✓ 图像已添加: {result['file_name']}")
    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False))
def index_images(source_dir):
    """批量索引文件夹中的所有图像
    
    SOURCE_DIR: 源文件夹路径
    
    示例:
        python main.py index-images ./photos
    """
    init_managers()
    
    try:
        click.echo(f"开始批量索引文件夹: {source_dir}")
        img_manager.batch_index(source_dir)
        click.echo("✓ 批量索引完成")
    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--recursive/--no-recursive', '-r', default=True, help='是否递归处理子目录（默认递归）')
def process_images(recursive):
    """批量处理 ./images 目录中的所有图像
    
    该命令会自动扫描 ./images 目录下的所有图像文件（包括子目录），
    并对尚未索引的图像进行批量处理和索引。
    
    示例:
        python main.py process-images
        python main.py process-images --no-recursive  # 只处理根目录，不递归子目录
    """
    init_managers()
    
    try:
        click.echo(f"开始批量处理 ./images 目录中的图像...")
        if recursive:
            click.echo("  模式: 递归处理所有子目录")
        else:
            click.echo("  模式: 仅处理根目录")
        img_manager.batch_process_images_dir(recursive=recursive)
        click.echo("✓ 批量处理完成")
    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()

