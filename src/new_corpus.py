from collections import defaultdict, Counter
from encodings import cp856
from spellwise import CaverphoneOne
import tensorflow as tf
from itertools import *
import numpy as np
import json


from src import CRVDatabase, crv_database
from src.utils import *
from src.crv import *
from src.vectorizer import *


################ The Corpus Class ################
#
# 

# properties, properties, properties

class Corpus:
    def __init__(self, 
                 sentences     = None, 
                 filepath      = None,  
                 dictionary    = None,
                 log           = True):
        
        self.sentences = []
        
        if filepath is not None:
            self.add_sentences(self.load_sentences(filepath))
        elif sentences is not None:
            self.add_sentences(sentences)

        # clean data
        # if dictionary:
        #     self.spell_correcter = CaverphoneOne()
        #     self.spell_correcter.add_from_path(dictionary)
            #sentences equals self.spell_correct()

        if not log: return

        print("Corpus loaded:")
        print(f"    - {str(len(self.sentences))} sentences.")
        print("    - longest sentence: \n")
        print(concat_sentence(max(self.sentences, key = len)))
        print(".    ")
        print("    - shortest sentence: \n")
        print(concat_sentence(min(self.sentences, key = len)))



    def load_sentences(self, filepath):
        if filepath[-5:] != '.json':
            filepath += '.json'

        with open(filepath) as f:
            sentences = json.load(f)
        
        return sentences
    

    def add_sentences(self, sentences):
        """
        Cleans and adds a sentence or sentences to the Corpus
        
        :param self:      
        :param sentences: a sentence string or list of strings to add to the corpus
        """

        if type(sentences) == str:
            sentences = [sentences]

        sentences = [sentence.lower() for sentence in sentences]
        sentences = [split_sentence(sentence) for sentence in sentences]
        
        self.sentences.extend(sentences)
        self.set_dirty()

    def set_dirty(self):
        self._vocab               = None
        self._set_vocab           = None
        self._word_counts         = None
        self._sentence_indices    = None
        self._word_indices        = None
        self._total_word_count    = None
        self._unique_word_count   = None
        self._word_percentages    = None
        self._max_sentence_length = None

    
    #TODO: manage updates to the corpus, a get_dirty? dirty never gets unset....

    @property
    def vocab(self):
        """A list of every word appearing in the Corpus, sorted by low-to-high rarity"""
        if not self._vocab:
            self._vocab = list(self.word_counts.keys())

        return self._vocab
    
    @property
    def set_vocab(self):
        """A set of every word appearing in the Corpus, for quick processing"""#better term than 'rarity'?
        if not self._set_vocab:
            self._set_vocab = set(self.vocab)

        return self._set_vocab
    
    @property
    def word_counts(self):
        """A dict with the number of occurrences of each word in the Corpus"""
        if not self._word_counts:
            self._word_counts = sort_hl(dict(Counter(chain(*self.sentences))))

        return self._word_counts
    
    @property
    def sentence_indices(self):
        """A dict of form word:set, each set being the indices of what sentences that word appears in"""
        if not self._sentence_indices:
            self._sentence_indices = defaultdict(set)

            for i, sentence in enumerate(self.sentences):
                for word in set(sentence):
                    self._sentence_indices[word].add(i)

        return self._sentence_indices
    
    @property
    def word_indices(self):
        """A dict of where each word appears in the vocabulary, more common words having lower indices"""
        if not self._word_indices:
            self._word_indices = {word : i for i, word in enumerate(self.vocab)}

        return self._word_indices
    
    @property
    def total_word_count(self):
        """How many words are in the Corpus"""
        if not self._total_word_count:
            self._total_word_count = sum(self.word_counts.values())

        return self._total_word_count
    
    @property
    def unique_word_count(self):
        """How many unique words are in the Corpus"""
        if not self._unique_word_count:
            self._unique_word_count = len(self.vocab)# a bit simple...

        return self._unique_word_count
    
    @property
    def word_percentages(self):
        """A dict of how often each word appears in the Corpus"""
        if not self._word_percentages:
            self._word_percentages = {word : count / self.total_word_count for word, count in self.word_counts.items()}

        return self._word_percentages
    
    @property
    def max_sentence_length(self):
        """The length of the longest sentence in the Corpus"""
        if not self._max_sentence_length:
            self._max_sentence_length = len(max(self.sentences, key = len))

        return self._max_sentence_length


    def log_properties(self):
        print("Corpus Properties:")
        print(f"    - {str(self.total_word_count)} total words")
        print(f"    - {str(self.unique_word_count)} unique words")
        print(f"    - most common words:  {str(self.vocab[:5])}")
        print(f"    - least common words: {str(self.vocab[-5:])}")
        print('\n')


    # Data cleanup

    def spell_correct(self, sentence):
        # this still operates with the corpus's sentences in mind,
        # and so will not run on the first lap.....
        return self.replace(self.get_correctable_words(), sentence)

    def remove_uncommon(self, n = 0):
        self.replace({word : ['<UNK>'] for word in self.vocab if self.word_counts[word] <= n})

    def get_correctable_words(self, word_set = None):
        possible_corrections = defaultdict(str)

        for word in word_set or (self.set_vocab - set(['<START>', '<END>', '<UNK>'])):
            result = self.get_correction(word)
            if result != word:
                possible_corrections[word] = result

        return possible_corrections
    
    def get_correction(self, word):
        if len(word) <= 3:
            return word

        corrections = self.spell_correcter.get_suggestions(word)
        corrections = {item['word'] : item['distance'] for item in corrections}
        same_keys = set(corrections.keys()).intersection(self.set_vocab)

        if len(same_keys) == 0:
            return word

        if word in same_keys:
            return word

        corrections = {key : self.word_counts[key] for key in same_keys}
        return list(sort_hl(corrections).keys())[0:1]
    

    def spelled_correct(self, word):
        return self.get_correction(word) == word


    def replace(self, replacements):
        replacement_set = set(replacements.keys())

        self.sentences = [self.replace_sentence(sentence, replacements, replacement_set)
                          for sentence in self.sentences]
        self.set_dirty()

    def replace_sentence(self, sentence, replacements, replacement_set):
        for i in range(5):
            output_sentence = []
            edited = False
            for word in sentence:
                if word not in replacement_set:
                    output_sentence.append(word)
                    continue

                edited = True
                output_sentence.extend(replacements[word])

            if not edited:
                break

            sentence = output_sentence
        return output_sentence

                 
    # CRVs

    def create_crvdb(self, window_size = 2, removal_threshold = 0, log = True):

        counts = { word : defaultdict(int) for word in self.vocab }
        
        # collect word counts for each word
        for sentence in self.sentences:
            
            for window_center in range(len(sentence)):

                # the word that we will collect signatures for
                # around it
                center_word = sentence[window_center]

                for word_index in range(max(0, window_center - window_size), min(window_center + window_size + 1, len(sentence))):

                    # while sliding the window, don't include the given word, which will always be in the center of the window
                    if word_index == window_center:
                        continue

                    # add one to the count for that word's occurence next to the given word
                    nearby_word = sentence[word_index]
                    counts[center_word][nearby_word] += 1


        if not log: return CRVDatabase(counts = counts)# one and return
        
        #TODO: refactor
        print("Signatures collected:")
        sorted_best = [[word, list(couts[word].items())[0]] for word in self.vocab]
        highest = max(sorted_best, key = lambda item : item[1][1])
        print("    - highest best signature: " + str(highest) + " & " + str(sorted_best.count(highest) - 1) + " others.")
        lowest = min(sorted_best, key = lambda item : item[1][1])
        print("    - lowest best signature: " + str(lowest) + " & " + str(sorted_best.count(lowest) - 1) + " others.")

        return CRVDatabase(counts = counts)


    # Corpus Search

    def find(self, words, window_size = 3):

        if type(words) == str: words = [words]

        common_sentences = set(self.sentence_indices[words[0]]).union(*[self.sentence_indices[word] for word in words])
        snippets = []

        if len(common_sentences) == 0:
            raise Exception('Words not found')
        
        for i in common_sentences:
            snippets.extend([(i,) + snippet for snippet in self.find_in_sentence(words, self.sentences[i], window_size)])

        print(f"Total Found : {len(snippets)}")
        # print(f"Found in {len(valid_sentences)} sentences")

        return snippets
    

    def find_in_sentence(self, words, sentence, window_size = 3):
        if type(words) == str:  words = [words]
        words = set(words)

        snippets = []

        for i in range(len(sentence)):
            slice = sentence[i:min(len(sentence), i + window_size)]

            if slice[0] not in words:
                continue

            key = slice[0]

            for j, word in enumerate(slice[1:]):
                if word == key:
                    break

                if words.issubset(slice[:j+1]):
                    snippets.append((i, j+1))
                    break

        return snippets
    

    def print_snippets(self, snippets, sentence = None, padding = 4):#padding window
        if sentence:
            [self.print_snippet(snippet, sentence, padding) for snippet in snippets]
        else:
            for snippet in snippets:
                self.print_snippet(snippet, self.sentences[snippet[0]], padding)


    def print_snippet(self, snippet, sentence, padding = 4):
        print(concat_sentence(sentence[snippet[-2]-padding:snippet[-2]+snippet[-1]+padding]))
