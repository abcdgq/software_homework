# pip install sumy gensim
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

from langdetect import detect

def detect_language(text):
    lang = detect(text)
    if lang == 'zh-cn':
        return 'chinese'
    else:
        return 'english'

def text_summarizer(text, sentences_count=3):
    """基于TextRank的摘要生成"""
    language = detect_language(text)
    print("language:", language)
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer = TextRankSummarizer()
    summary = summarizer(parser.document, sentences_count)
    # for s in summary:
    #     print(s)
    #     print("len:", len(str(s)))
    return " ".join([str(s) for s in summary])


if __name__ == '__main__':
    # 示例：处理API返回的论文摘要
    nltk.download('punkt_tab')
    api_response = "Hello, i m  soce"
    print("api_response len:", len(api_response))
    summary = text_summarizer(api_response, sentences_count=5)
    print("summary:", summary)
    print("summary len:", len(summary))