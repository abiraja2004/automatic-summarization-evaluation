from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as LSA
from sumy.summarizers.lex_rank import LexRankSummarizer as LexRank
from sumy.summarizers.luhn import LuhnSummarizer as Luhn
from sumy.summarizers.random import RandomSummarizer as Random
from sumy.summarizers.sum_basic import SumBasicSummarizer as SumBasic
from sumy.summarizers.text_rank import TextRankSummarizer as TextRank
from sumy.summarizers.kl import KLSummarizer as KL
from pyteaser import Summarize
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import sys
from nltk.tokenize import word_tokenize, sent_tokenize

def baseline(filename):
    summary = []
    f = open(filename)
    text = f.read()
    f.close()
    lines = sent_tokenize(text)
    summary += lines[0:2]
    summary += lines[-2:]
    return ''.join(summary)

if __name__ == '__main__':
    # method_name = sys.argv[1]
    algos = ['LSA',    'LexRank',    'Luhn',    'Random',    'SumBasic',    'TextRank',   'KL']
    filename = "../processed_text_commentaries/doc1.txt"
    parser = PlaintextParser.from_file(filename, Tokenizer('english'))
    stemmer = Stemmer('english')
    print("BASELINE: ")
    summary = baseline(filename)
    print(summary+"\n\n")
    for method_name in algos:
        print('ALGORITHM: '+method_name)
        func = globals()["%s" % method_name]
        # Call appropriate method dynamically
        summarizer = func(stemmer)
        summarizer.stop_words = get_stop_words('english')
        for sentence in summarizer(parser.document, 4):
            print(sentence)
        print("\n\n\n")
