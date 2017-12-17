import argparse
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
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from sumy.models import TfDocumentModel
from sumy.evaluation import precision, recall, f_score, cosine_similarity, unit_overlap, rouge_1, rouge_2, rouge_l_sentence_level, rouge_l_summary_level
from itertools import chain

def baseline(filename):
    summary = []
    f = open(filename)
    text = f.read()
    f.close()
    lines = sent_tokenize(text)
    summary += lines[0:2]
    summary += lines[-2:]
    return ''.join(summary)

all_scores = (
    ("Precision", False, 'precision'),
    ("Recall", False, 'recall'),
    ("F-score", False, 'f_score'),
    ("Cosine similarity", False, 'evaluate_cosine_similarity'),
    ("Cosine similarity (document)", True, 'evaluate_cosine_similarity'),
    ("Unit overlap", False, 'evaluate_unit_overlap'),
    ("Unit overlap (document)", True, 'evaluate_unit_overlap'),
    ("Rouge-1", False, 'rouge_1'),
    ("Rouge-2", False, 'rouge_2'),
    ("Rouge-L (Sentence Level)", False, 'rouge_l_sentence_level'),
    ("Rouge-L (Summary Level)", False, 'rouge_l_summary_level')
)

def evaluate_cosine_similarity(evaluated_sentences, reference_sentences):
    evaluated_words = tuple(chain(*(s.words for s in evaluated_sentences)))
    reference_words = tuple(chain(*(s.words for s in reference_sentences)))
    evaluated_model = TfDocumentModel(evaluated_words)
    reference_model = TfDocumentModel(reference_words)

    return cosine_similarity(evaluated_model, reference_model)

def evaluate_unit_overlap(evaluated_sentences, reference_sentences):
    evaluated_words = tuple(chain(*(s.words for s in evaluated_sentences)))
    reference_words = tuple(chain(*(s.words for s in reference_sentences)))
    evaluated_model = TfDocumentModel(evaluated_words)
    reference_model = TfDocumentModel(reference_words)

    return unit_overlap(evaluated_model, reference_model)

def get_summary(sum_sentences):
    return ' '.join(map(str,sum_sentences))

def score_summaries(orig_text, summary_sentences, extractive_sentences):
    try:
        extractive_bleu_score = nltk.translate.bleu_score.sentence_bleu([get_summary(extractive_sentences)], get_summary(summary_sentences))
        print 'Bleu Score: '+str(extractive_bleu_score)
        for name, score_against_orig, score_method in all_scores:
            score = globals()["%s" % score_method]
            if score_against_orig:
                result = score(summary_sentences, orig_text)
            else:
                result = score(summary_sentences, extractive_sentences)
            print("%s: %f" % (name, result))
    except ZeroDivisionError as e:
        print('Skipping because: '+str(e))

if __name__ == '__main__':
    algos = ['LSA',    'LexRank',    'Luhn',    'Random',    'SumBasic',    'TextRank',   'KL']
    inparse = argparse.ArgumentParser(description='Extractive Summarization Algorithm')
    inparse.add_argument('-f','--textfile', nargs=1, help='input commentary file',required=True)
    inparse.add_argument('-o','--out', nargs=1, help='output file to dump summaries',required=True)
    inparse.add_argument('-r','--ref', nargs=1, help='reference summary file',required=True)
    args = inparse.parse_args()

    input_filename = args.textfile[0]
    output_filename = args.out[0]
    reference_filename = args.ref[0]

    with open(reference_filename) as fref:
        refs = fref.read()
        extractive_references = ' '.join(sent_tokenize(refs)[0:5])
        abstractive_references = ' '.join(sent_tokenize(refs)[-4:])
        ex_reference_document = PlaintextParser.from_string(extractive_references, Tokenizer('english'))
        abs_reference_document = PlaintextParser.from_string(abstractive_references, Tokenizer('english'))
        ex_reference_sentences = ex_reference_document.document.sentences
        abs_reference_sentences = abs_reference_document.document.sentences

    # Read input file to be summarized
    comm_parser = PlaintextParser.from_file(input_filename, Tokenizer('english'))
    stemmer = Stemmer('english')

    # Get list of sentences in the original commentary
    orig_text = comm_parser.document.sentences

    # Open output file for writing
    fout = open(output_filename,'w')

    # Make baseline summary
    baseline_summary = baseline(input_filename)
    fout.write("BASELINE: \n")
    fout.write(baseline_summary+"\n\n")
    print("Summarizing using Algorithm: Baseline \n")

    base_summary_sentences = PlaintextParser.from_string(baseline_summary, Tokenizer('english')).document.sentences
    score_summaries(orig_text, base_summary_sentences, ex_reference_sentences)

    # Generate all other summaries
    for method_name in algos:
        print('Summarizing using Algorithm: '+method_name+'\n')
        fout.write('ALGORITHM: '+method_name+'\n')
        func = globals()["%s" % method_name]

        # Call appropriate method dynamically
        summarizer = func(stemmer)
        summarizer.stop_words = get_stop_words('english')

        # Summary has 4 sentences
        sums = summarizer(comm_parser.document, 4)
        summary = ' '.join(map(str,sums))
        fout.write(summary)
        fout.write("\n\n\n")

        # Evaluate each summary
        score_summaries(orig_text, sums, ex_reference_sentences)
        print("\n\n")

    fout.close()
