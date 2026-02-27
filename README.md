# PDF年报/IPO按章节拆分工具

使用DeepSeek AI智能识别PDF章节结构，自动拆分为独立的PDF文件。

## 功能特点

- 🤖 **AI智能识别**: 使用DeepSeek API自动分析章节结构
- 📁 **批量处理**: 支持递归扫描文件夹处理所有PDF
- 📑 **精准拆分**: 根据AI分析结果精确拆分章节
- 🌐 **中英双语**: 支持中文和英文PDF文档

## 安装依赖

```bash
pip install pypdf requests
# 或者
pip install PyPDF2 requests
```

## 配置

在 `split_pdf_by_chapters.py` 文件中填入你的DeepSeek API Key：

```python
DEEPSEEK_API_KEY = "sk-your-api-key-here"
```

获取API Key: [DeepSeek API](https://platform.deepseek.com/)

## 使用方法

### 扫描目录处理所有PDF

```bash
python split_pdf_by_chapters.py --scan "E:/归档/Annual Report"
```

### 处理单个文件

```bash
python split_pdf_by_chapters.py "LLM/MiniMax_IPO.pdf"
```

### 不使用AI（使用默认规则）

```bash
python split_pdf_by_chapters.py "LLM/MiniMax_IPO.pdf" --no-ai
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `path` | PDF文件路径或目录路径 |
| `--scan` | 递归扫描目录处理所有PDF |
| `--no-ai` | 不使用AI识别章节 |
| `-o, --output` | 指定输出目录 |

## 输出

- 输出目录: `<原文件名>_chapters/`
- 文件命名: `<原文件名>_<章节名>.pdf`

## 示例

处理 `MiniMax_IPO.pdf` (716页) 自动识别为15个章节:

```
MiniMax_IPO_封面及重要提示.pdf    (1-6)
MiniMax_IPO_概要.pdf              (7-24)
MiniMax_IPO_释义.pdf              (25-44)
MiniMax_IPO_风险因素.pdf          (45-54)
MiniMax_IPO_公司资料.pdf          (55-94)
MiniMax_IPO_行业概览.pdf          (95-154)
MiniMax_IPO_历史、重组及公司架构.pdf (155-184)
MiniMax_IPO_业务.pdf             (185-344)
MiniMax_IPO_财务资料.pdf         (345-424)
MiniMax_IPO_未来计划及所得款项用途.pdf (425-434)
MiniMax_IPO_与控股股东的关系.pdf  (435-444)
MiniMax_IPO_股本.pdf             (445-454)
MiniMax_IPO_全球发售的架构.pdf   (455-484)
MiniMax_IPO_附录.pdf             (485-694)
MiniMax_IPO_如何申请香港发售股份.pdf (695-716)
```

## 注意事项

1. API调用会产生费用，请留意使用量
2. 某些加密或扫描版PDF可能无法正确提取文字
3. 首次使用建议先处理单个文件测试

## License

MIT
