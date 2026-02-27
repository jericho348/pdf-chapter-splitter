#!/usr/bin/env python3
"""
PDF年报/IPO按章节拆分工具 - AI增强版
使用DeepSeek AI智能识别PDF章节结构
"""

import os
import re
import json
import argparse
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests

# 使用pypdf库
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        print("请安装pypdf库: pip install pypdf")
        exit(1)


# ==================== 配置区域 ====================
# 在这里直接填写你的DeepSeek API Key
DEEPSEEK_API_KEY = "YOUR API KEY HERE"

# API配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
# ==================== 配置结束 ====================


class DeepSeekChapterAnalyzer:
    """使用DeepSeek API分析PDF章节结构"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def analyze_chapters(self, pdf_path: str, total_pages: int) -> List[Dict]:
        """调用DeepSeek API分析章节结构"""
        if not self.api_key:
            print("  错误: API Key未配置")
            return []

        print(f"  正在调用DeepSeek API分析章节结构...")

        # 提取PDF前几页的文本作为上下文
        sample_text = self._extract_sample_text(pdf_path)

        prompt = f"""你是一个专业的PDF文档分析助手。我有一个PDF文件需要按章节拆分成独立的文件。

PDF文件信息:
- 文件路径: {pdf_path}
- 总页数: {total_pages}

PDF前几页内容预览:
{sample_text[:3000]}

请分析这个PDF的章节结构，返回JSON格式的章节列表。

要求:
1. 根据PDF内容判断这是什么类型的文档（年报、IPO招股书等）
2. 识别主要的章节标题和起始页码
3. 页码从1开始计算（不是0）
4. 只返回主要章节，不要返回过于细分的子章节
5. 返回5-15个主要章节即可

请严格按照以下JSON格式返回，不要包含任何其他内容:
{{
  "chapters": [
    {{"name": "章节名称", "start_page": 页码}},
    ...
  ]
}}

只返回JSON，不要有任何其他文字。"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"  API返回结果")
                return self._parse_json_response(content)
            else:
                print(f"  API调用失败: {response.status_code}")
                return []

        except Exception as e:
            print(f"  API调用出错: {e}")
            return []

    def _extract_sample_text(self, pdf_path: str) -> str:
        """提取PDF前几页的样本文本"""
        try:
            reader = PdfReader(pdf_path)
            text_parts = []

            # 提取前10页
            for i in range(min(10, len(reader.pages))):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    text_parts.append(f"[第{i+1}页]\n{text[:500]}")

            return "\n\n".join(text_parts)
        except Exception as e:
            return f"无法提取文本: {e}"

    def _parse_json_response(self, content: str) -> List[Dict]:
        """解析API返回的JSON"""
        try:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                if 'chapters' in data:
                    chapters = data['chapters']
                    valid_chapters = []
                    for ch in chapters:
                        if isinstance(ch, dict) and 'name' in ch and 'start_page' in ch:
                            try:
                                page = int(ch['start_page'])
                                if page > 0:
                                    valid_chapters.append({
                                        'name': ch['name'],
                                        'start_page': page
                                    })
                            except:
                                continue
                    return valid_chapters
            return []
        except json.JSONDecodeError:
            return []


class PDFChapterSplitter:
    """PDF章节拆分器"""

    def __init__(self, api_key: str = None):
        self.analyzer = DeepSeekChapterAnalyzer(api_key) if api_key else None

    def split_pdf(self, pdf_path: str, output_dir: str = None) -> List[str]:
        """拆分PDF文件"""
        print(f"\n{'='*60}")
        print(f"正在处理: {pdf_path}")

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"总页数: {total_pages}")

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]

        # 在同层级创建输出目录
        if output_dir is None:
            output_dir = f"{pdf_path}_chapters"

        os.makedirs(output_dir, exist_ok=True)
        print(f"输出目录: {output_dir}")

        # 使用AI分析
        chapters = []
        if self.analyzer:
            chapters = self.analyzer.analyze_chapters(pdf_path, total_pages)

        if not chapters:
            print("  AI分析失败，使用默认章节")
            chapters = self._get_default_chapters(total_pages)

        print(f"\n检测到的章节 ({len(chapters)}个):")
        for i, ch in enumerate(chapters):
            print(f"  {i+1}. {ch['name']} (起始页: {ch['start_page']})")

        # 确认拆分
        print("\n确认拆分? (y/n): ", end='')
        response = input().strip().lower()
        if response not in ['y', 'yes', '是', '']:
            print("已取消")
            return []

        # 生成PDF
        ranges = self._determine_ranges(chapters, total_pages)
        output_files = []

        print("\n正在生成章节PDF文件...")
        for start_page, end_page, chapter_name in ranges:
            if start_page > end_page:
                continue

            print(f"  [{chapter_name}] 页 {start_page} - {end_page}")

            writer = PdfWriter()
            for page_num in range(start_page - 1, min(end_page, total_pages)):
                writer.add_page(reader.pages[page_num])

            safe_name = re.sub(r'[<>:"/\\|?*]', '_', chapter_name)[:50]
            output_file = os.path.join(output_dir, f"{base_name}_{safe_name}.pdf")

            # 处理重名
            counter = 1
            original = output_file
            while os.path.exists(output_file):
                name, ext = os.path.splitext(original)
                output_file = f"{name}_{counter}{ext}"
                counter += 1

            with open(output_file, 'wb') as f:
                writer.write(f)
            output_files.append(output_file)

        print(f"\n拆分完成! 共生成 {len(output_files)} 个文件")
        return output_files

    def _get_default_chapters(self, total_pages: int) -> List[Dict]:
        """生成默认章节配置"""
        chapters = [
            {"name": "Cover", "start_page": 1},
            {"name": "Summary", "start_page": max(1, total_pages // 15)},
            {"name": "TOC", "start_page": max(1, total_pages // 12)},
            {"name": "Business", "start_page": max(1, total_pages // 8)},
            {"name": "Financial", "start_page": max(1, total_pages * 2 // 5)},
            {"name": "Management", "start_page": max(1, total_pages * 3 // 5)},
            {"name": "Risk", "start_page": max(1, total_pages * 4 // 5)},
        ]
        chapters.sort(key=lambda x: x['start_page'])
        return chapters

    def _determine_ranges(self, chapters: List[Dict], total_pages: int) -> List[Tuple[int, int, str]]:
        """确定章节范围"""
        ranges = []
        for i, ch in enumerate(chapters):
            start = ch['start_page']
            if i + 1 < len(chapters):
                end = chapters[i + 1]['start_page'] - 1
            else:
                end = total_pages
            ranges.append((start, end, ch['name']))
        return ranges


def scan_and_select_files(root_dir: str = None):
    """扫描目录，列出所有PDF文件，让用户选择"""
    if root_dir is None:
        # 默认扫描脚本所在目录
        root_dir = os.path.dirname(os.path.abspath(__file__))
        if not root_dir:
            root_dir = "."

    # 收集所有PDF文件，排除已处理的_chapters文件夹
    pdf_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 跳过_chapters结尾的目录
        dirnames[:] = [d for d in dirnames if not d.endswith('_chapters')]

        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(dirpath, filename))

    if not pdf_files:
        print("没有找到PDF文件")
        return None

    # 按文件路径排序
    pdf_files.sort()

    print(f"\n找到 {len(pdf_files)} 个PDF文件:\n")
    for i, f in enumerate(pdf_files, 1):
        print(f"  {i}. {f}")
    print()

    return pdf_files


def select_and_process(pdf_files: list, api_key: str):
    """让用户选择文件并处理"""
    if not pdf_files:
        return

    splitter = PDFChapterSplitter(api_key)

    while True:
        print("请输入要处理的文件序号（输入0退出）: ", end='')
        try:
            choice = input().strip()
        except EOFError:
            break

        if not choice:
            continue

        try:
            idx = int(choice)
        except ValueError:
            print("请输入有效的数字")
            continue

        if idx == 0:
            print("退出")
            break
        elif 1 <= idx <= len(pdf_files):
            pdf_path = pdf_files[idx - 1]
            print(f"\n{'#'*60}")
            print(f"选择: {pdf_path}")
            print(f"{'#'*60}")

            # 在同层级创建输出目录
            output_dir = f"{pdf_path}_chapters"

            # 直接使用AI处理
            splitter.split_pdf(pdf_path, output_dir)
        else:
            print(f"序号无效，请输入1-{len(pdf_files)}")


def main():
    parser = argparse.ArgumentParser(
        description='PDF年报/IPO按章节拆分工具 - AI增强版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方法:
  # 扫描当前目录，列出所有PDF文件
  python split_pdf_by_chapters.py

  # 扫描指定目录
  python split_pdf_by_chapters.py "E:/归档/Annual Report/LLM"
        """
    )

    parser.add_argument('path', nargs='?', help='PDF文件路径或目录路径')

    args = parser.parse_args()

    api_key = DEEPSEEK_API_KEY

    if args.path:
        # 检查是否是单个文件
        if os.path.isfile(args.path) and args.path.lower().endswith('.pdf'):
            splitter = PDFChapterSplitter(api_key)
            output_dir = f"{args.path}_chapters"
            splitter.split_pdf(args.path, output_dir)
        else:
            # 扫描目录
            pdf_files = scan_and_select_files(args.path)
            if pdf_files:
                select_and_process(pdf_files, api_key)
    else:
        # 默认扫描当前目录
        pdf_files = scan_and_select_files(None)
        if pdf_files:
            select_and_process(pdf_files, api_key)


if __name__ == '__main__':
    main()
