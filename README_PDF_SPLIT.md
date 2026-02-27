# PDF年报/IPO按章节拆分工具

根据PDF中的章节标题自动识别拆分点，生成独立的PDF文件。

## 功能特点

- **自动检测**: 尝试从目录页(TOC)自动解析章节
- **多种输入方式**: 支持命令行参数、配置文件、章节定义文件
- **通用设计**: 可处理中文和英文年报/IPO文档

## 安装依赖

```bash
pip install pypdf
# 或者
pip install PyPDF2
```

## 使用方法

### 1. 扫描PDF查看章节候选

```bash
python split_pdf_by_chapters.py <pdf文件> --scan
```

这会扫描PDF并显示检测到的章节候选，帮助你了解文档结构。

### 2. 自动检测并拆分

```bash
python split_pdf_by_chapters.py <pdf文件>
```

工具会尝试自动检测章节并拆分。适用于目录结构清晰的PDF。

### 3. 手动指定章节拆分

如果自动检测效果不佳，可以手动指定章节：

```bash
# 命令行格式
python split_pdf_by_chapters.py <pdf文件> --chapters "Cover:1,Summary:10,Business:50,Financial:200"

# 或从JSON文件读取
python split_pdf_by_chapters.py <pdf文件> --chapters-file chapters.json
```

### 4. 使用配置文件

```bash
python split_pdf_by_chapters.py <pdf文件> --config config.json
```

## 章节配置格式

### 命令行格式

```
章节名1:起始页1,章节名2:起始页2,...
```

例如: `Cover:1,Summary:10,Business:50,Financial:200,Risk:350`

### JSON文件格式

```json
{
  "chapters": [
    {"name": "Cover", "start_page": 1},
    {"name": "Summary", "start_page": 10},
    {"name": "Business", "start_page": 50},
    {"name": "Financial", "start_page": 200}
  ]
}
```

注意: 起始页从1开始计算

## 配置文件说明

### split_config.json

用于自定义关键词和章节识别规则:

```json
{
  "keywords": {
    "zh": ["业务", "财务", "风险", ...],
    "en": ["Business", "Financial", "Risk", ...]
  },
  "custom_keywords": [],
  "ipo_chapters": ["Cover", "Summary", "Business", ...]
}
```

## 示例

### 拆分MiniMax IPO文档

```bash
# 先扫描了解结构
python split_pdf_by_chapters.py LLM/MiniMax_IPO.pdf --scan

# 根据扫描结果创建章节配置文件，然后拆分
python split_pdf_by_chapters.py LLM/MiniMax_IPO.pdf --chapters-file LLM/MiniMax_IPO_chapters.json
```

## 输出

- 输出目录: `<原文件名>_chapters/`
- 文件命名: `<原文件名>_<章节名>.pdf`

## 常见问题

### PDF文字提取失败

某些PDF(特别是扫描版或加密的PDF)可能无法正确提取文字。可以尝试:

1. 使用PDF阅读器将PDF转换为文字版
2. 手动指定章节拆分点
3. 使用OCR版本的PDF

### 章节检测不准确

1. 使用 `--scan` 参数查看检测结果
2. 根据实际情况调整章节配置
3. 使用 `--chapters` 手动指定章节

## 文件列表

- `split_pdf_by_chapters.py` - 主程序
- `split_config.json` - 默认配置文件
- `chapters_template.json` - 章节配置模板
