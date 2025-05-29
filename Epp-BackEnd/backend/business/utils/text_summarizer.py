import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

from langdetect import detect

#一个简单的文本总结方法，用于缩短输入文本的长度，在scripts/text_summary.py文件中进行测试

def detect_language(text):
    lang = detect(text)
    if lang == 'zh-cn':
        return 'chinese'
    else:
        return 'english'

def text_summarizer(text, sentences_count=3):
    """基于TextRank的摘要生成"""
    language = detect_language(text)
    # print("language:", language)
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer = TextRankSummarizer()
    summary = summarizer(parser.document, sentences_count)
    # for s in summary:
    #     print(s)
    #     print("len:", len(str(s)))
    return " ".join([str(s) for s in summary])