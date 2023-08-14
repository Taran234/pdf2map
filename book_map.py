import os
import fitz
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from collections import defaultdict


def summarize_and_map(file_path, map_size=5, min_chunk_len=3, max_chunk_len=5):
    # Extract text from PDF file
    with fitz.open(file_path) as doc:
        text = ''
        for page in doc:
            text += page.get_text()

    # Summarize text using TextRank algorithm
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    sentences = [sent for sent in doc.sents if len(sent) > 10]
    phrase_scores = defaultdict(int)
    for phrase in doc.noun_chunks:
        if min_chunk_len <= len(phrase) <= max_chunk_len and phrase.text.lower() not in STOP_WORDS:
            phrase_scores[phrase.text] += phrase.root.dep_ in {'nsubj', 'dobj', 'pobj'}
    sentence_scores = defaultdict(int)
    for sent in sentences:
        for phrase in sent.noun_chunks:
            if phrase.text in phrase_scores:
                sentence_scores[sent] += phrase_scores[phrase.text]
    summary = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:map_size]

    # Create mind map as HTML file with tree layout
    title = os.path.splitext(os.path.basename(file_path))[0]
    with open('index.html', 'r') as f:
        html_code = f.read()

    mind_map = f'{html_code}\n'
    topics = defaultdict(list)
    included_sentences = set()
    for sentence in summary:
        for phrase in sentence.noun_chunks:
            if min_chunk_len <= len(phrase) <= max_chunk_len:
                topic = phrase.text.capitalize()
                if sentence not in included_sentences:
                    topics[topic].append(sentence)
                    included_sentences.add(sentence)
    for topic, sentences in topics.items():
        mind_map += f'<li><span class="topic">{topic}</span>\n<ul>\n'
        for sent in sentences:
            mind_map += f'<li class="sent">{sent}</li>\n'
        mind_map += '</ul></li>\n'

    mind_map += '</ul>\n</body>\n</html>\n'

    # Save mind map as HTML file
    with open(f'{title}.html', 'w', encoding='utf-8') as f:
        f.write(mind_map)
    print(f'Mind map saved to {os.getcwd()}\\{title}.html')


if __name__ == '__main__':
    file_path = input('Enter file path: ')
    map_size = int(input('Enter maximum summary size (in sentences): '))
    summarize_and_map(file_path, map_size)
