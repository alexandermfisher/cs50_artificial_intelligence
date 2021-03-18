import nltk
import sys
from nltk.tokenize import word_tokenize
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1



def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)
    

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    # initialise dictionay to be returned
    files_dictionary = dict()
    
    # read in file names into a list:
    file_names = [file_name for file_name in os.listdir(directory) if file_name.endswith('.txt')]
    
    # read file_name and file contents into dictinoary:
    for file_name in file_names:
        with open(os.path.join(directory, file_name), 'r', encoding='UTF-8') as file:
                files_dictionary[file_name] = file.read()
    
    return files_dictionary


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # tokenize document and remove stops words and punctuation.
    document_tokens = word_tokenize(document.lower())
    
    formatted_tokens = list()
    for token in document_tokens:
        # check to see word isn't a stop word
        if token not in nltk.corpus.stopwords.words("english"):
            # removing any char in token that is punctuation
            formatted_token = token
            for char in token:
                if char in string.punctuation:
                    formatted_token = formatted_token.replace(char, "")
            
            # if formatted_token is not empty string append to formatted_tokens
            if formatted_token != ("" or "/n"): 
                formatted_tokens.append(formatted_token)

    
    return formatted_tokens


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    num_docs = len(documents)
    idf_values_dict = dict()
    seen_words = set()

    # read in all words looping over each document
    # and store count in a dict.
    for document in documents:
        for word in documents[document]:
            # add unseen words to dict for counting and add 1 to count.
            if word not in seen_words:
                seen_words.add(word)
                idf_values_dict[word] = 1
            else:
                idf_values_dict[word] += 1
    # create dict that maps word to idf value for all seen words.
    return {word: math.log(num_docs)/count for word, count in idf_values_dict.items()}


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # calculate the sum of tf-idf values (corresponding to each word in query) for each document.
    document_scores = dict()
    for file_name, file_words in files.items():
        document_scores[file_name] = 0
        for word in query:
            if word in file_words:
                document_scores[file_name] +=  idfs[word] * file_words.count(word)
    
    # rank the documents in descending order and return top n files from ranked list 
    ranked_files = list(dict(sorted(document_scores.items(), key=lambda item: item[1], reverse=True)).keys())
    return ranked_files[:n]
            

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_scores = dict()
    for sentence, sentences_words in sentences.items():
        sentence_scores[sentence] = [0,0]
        for word in query:
            if word in sentences_words:
                sentence_scores[sentence][0] += idfs[word]
                sentence_scores[sentence][1] += sentences_words.count(word) / len(sentences_words)

    ranked_sentences = list(dict(sorted(sentence_scores.items(), key=lambda item: (item[1][0], item[1][1]), reverse=True)).keys())
    return ranked_sentences[:n]

if __name__ == "__main__":
    main()
