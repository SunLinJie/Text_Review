# 基于敏感词和语义分析的文本审核系统
|  Text_Review   | jasonlbx13  |
|  ----     | ----  |
| Source    | https://github.com/jasonlbx13/Text_Review |
| Keywords  | text review |

### 中文文档

- [简介](#简介)
- [安装](#安装)
- [快速开始](#快速开始)

### 简介

- **快速识别敏感词**

    本项目含约6w左右敏感词库,可识别政治/暴恐/色情/赌博等网络常见敏感词.在使用过程中,可根据用户需要增、改、删、查敏感词.
    
- **fasttext语义分析**

    利用爬虫抓取的贴吧正样本和境外反动网站所爬取的长短预料文本,对fasttext模型进行训练.预训练模型在/ai/flp中,可识别正常涉政,违规涉政和正常.

- **cherry文本分类**
    
    使用cherry文本分类库,对输入语段进行政治/正常/色情/赌博四个类别进行分类.

### 安装
  本项目支持python3.6版本(其他版本未测试,但必须为python3),不需要cuda即可使用
  
    git clone https://github.com/jasonlbx13/Text_Review
    cd Text_Review
    pip install -r requirements.txt
    
### 快速开始

