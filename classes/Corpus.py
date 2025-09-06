from collections import defaultdict, Counter
from spellwise import CaverphoneOne
import tensorflow as tf
from itertools import *
import numpy as np
import json

from classes.Utils import *
from classes.CRV import *
from classes.Vectorizer import *


################ The Corpus Class ################
#
# -Stores a list of sentences and information about them
# -Loads and cleans data
# -Optionally lemmatizes (cleanliness -> clean ly ness) and corrects spelling errors
# -Splits each sentence into a list of words
# -Collects information
# -Creates CRVs
# -Creates a vectorizer


class Corpus:
    def __init__(self,
                 filepath,               # no need for '.json'
                 file_indexer  = None,   # some jsons have metadata, and so you need to index the actual text
                 text_mode     = 'word', # 'word' or 'char'
                 spell_correct = False,  # spell correct (fails on niche words)
                 lemmatize     = True,   # remove 'er', 'ed', 's', 'ing', etc. to the best of its ability
                 removal_threshold = 0,  # replace a word with <= this many appearences in the corpus with <UNK>
                 log = True):

        # setup
        self.text_mode = text_mode
        self.load_sentences(filepath, file_indexer)

        # clean data
        if spell_correct != False:
            self.spell_correcter = CaverphoneOne()
            self.spell_correcter.add_from_path(spell_correct)
            self.spell_correct()

        self.lemmatize() if lemmatize else None
        self.remove_uncommon(removal_threshold) if removal_threshold >= 1 else None
        
        # post_cleanup regathering
        self.scrape_data()

        # log info
        if not log:
            return

        print("Corpus loaded:")
        print("    - " + str(len(self.sentences)) + " sentences.")
        print("    - longest sentence: \n")
        print(concat_sentence(max(self.sentences, key = len), self.text_mode))
        print(".    ")
        print("    - shortest sentence: \n")
        print(concat_sentence(min(self.sentences, key = len), self.text_mode))


    # Data loading and standardization

    def load_sentences(self, filepath, file_indexer = None):
        if filepath[-5:] != '.json':
            filepath += '.json'

        with open(filepath) as f:
            if file_indexer is None:
                self.sentences = json.load(f)
            else:
                self.sentences = [item[file_indexer] for item in json.load(f)]

        # all lowercase, remove duplicates, split all
        self.sentences = [sentence.lower() for sentence in self.sentences]
        self.sentences = list(set(self.sentences))
        self.sentences = [split_sentence(sentence, self.text_mode) for sentence in self.sentences]

    # data collection

    def get_word_counts_and_vocab(self):
        self.word_counts = sort_hl(dict(Counter(chain(*self.sentences))))
        self.vocab = list(self.word_counts.keys())
        self.set_vocab = set(self.vocab)
        

    def scrape_data(self, log = True):

        self.get_word_counts_and_vocab()

        self.sentence_indices = defaultdict(set)

        for i, sentence in enumerate(self.sentences):
            for word in set(sentence):
                self.sentence_indices[word].add(i)

        self.word_indices = {word : i for i, word in enumerate(self.vocab)}
        self.total_word_count = sum(self.word_counts.values())
        self.total_unique_word_count = len(self.vocab)
        self.word_percentages = {item[0] : item[1] / self.total_word_count for item in self.word_counts.items()}
        self.max_length = len(max(self.sentences, key = len))

        # log info
        if not log:
            return
    
        print("Data collected:")
        print("    - " + str(self.total_unique_word_count) + " unique words found.")
        print("    - most common words: " + str(list(self.word_counts.keys())[:5]))
        print("    - least common words: " + str(list(self.word_counts.keys())[-5:]))
        print('\n')


    # Data cleanup

    def spell_correct(self):
        self.get_word_counts_and_vocab()
        self.replace(self.get_correctable_words())

    def lemmatize(self):
        self.get_word_counts_and_vocab()
        self.replace(self.get_lemmatizable_words())

    def remove_uncommon(self, n = 0):
        self.get_word_counts_and_vocab()
        self.replace({word : ['<UNK>'] for word in self.set_vocab if self.word_counts[word] <= n})        

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



    def get_lemmatizable_words(self, word_set = None):
        lemmatizable_words = defaultdict(str)

        for word in word_set or self.vocab:
            if len(word) <= 4:
                continue

            # word ends in 's'
            if (word[-1] == 's') and (word[-2:] != 'ss') and (word[-3:] != 'ous'):
                # some words with a y change spelling (candy -> candies)
                if word[-3:] == 'ies' and word[:-3] + 'y' in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_ies->_y+s')
                # words that normally end in 's' have 'es' added
                elif word[-3:] == 'ses' and word[:-2] in self.vocab:      
                    lemmatizable_words[word] = lemmatize(word, '_es->_+s')
                # words uses usual 's' rules
                elif word[:-1] in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_s->_+s')

            # word ends in 'ly'
            elif word[-2:] == 'ly':
                if word[:-1] + 'e' in self.set_vocab:
                    lemmatizable_words[word] = lemmatize(word, '_y->_e+ly')# fully
                elif word[:-2] in self.set_vocab:
                    lemmatizable_words[word] = lemmatize(word, '_ly->_+ly')# fully

            # word ends in 'ness'
            elif word[-4:] == 'ness':
                lemmatizable_words[word] = lemmatize(word, '_ness->_+ness')

            elif word[-4:] == 'less' and word != 'less':
                lemmatizable_words[word] = lemmatize(word, '_less->_+less')

            # word ends in 'ing'
            elif word [-3:] == 'ing':
                # putting -> put ing
                if word[-5] == word[-4] and word[:-4] in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_?ing->_+ing')
                # baking -> bake ing
                elif word[:-3] + 'e' in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_ing->_e+ing')
                # working -> work ing
                elif word[:-3] in self.vocab and len(word) > 5:
                    lemmatizable_words[word] = lemmatize(word, '_ing->_+ing')

            # word ends in 'er'
            elif (word != 'er') and (word[-2:] == 'er'):
                # happier -> happy er
                if word[-3:] == 'ier' and word[:-3] + 'y' in self.vocab:
                    lemmatizable_words[word] =  lemmatize(word, '_ier->_y+er')
                # canner -> can er
                elif word[-4] == word[-3] and word[:-3] in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_?er->_+er')
                # baker -> bake er
                elif word[:-1] in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_r->_+er')
                # mixer -> mix er
                elif word[:-2] in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_er->_+er')

            # ord ends in 'ed'
            elif (word != 'ed') and word[-2:] == 'ed':
                # carried -> carry ed
                if word[-3:] == 'ied' and word[:-3] + 'y' in self.vocab:
                    lemmatizable_words[word] =  lemmatize(word, '_ied->_y+ed')
                # canned -> can ed
                elif word[-4] == word[-3] and word[:-3] in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_?ed->_+ed')
                # baked -> bake ed
                elif word[:-1] in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_d->_+ed')
                # mixed -> mix ed
                elif word[:-2] in self.vocab:
                    lemmatizable_words[word] = lemmatize(word, '_ed->_+ed')
        
        return lemmatizable_words


    def replace(self, replacements):
        replacement_set = set(replacements.keys())

        self.sentences = [self.replace_sentence(sentence, replacements, replacement_set)
                          for sentence in self.sentences]

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

    def create_vectorizer(self, window_size = 2, removal_threshold = 0, log = True):
        signatures = self.create_signatures(window_size, log = False)

        if removal_threshold > 0:
            for sig_word in [word for word in self.set_vocab if self.word_counts[word] <= removal_threshold]:
                for word in self.vocab:
                    popped = signatures[word].pop(sig_word)
                    if popped is not None:
                        signatures[word]['<UNK>'] += popped

        encoding_vocab = list(sort_hl({word:self.word_counts[word] for word in self.set_vocab if self.word_counts[word] > removal_threshold}).keys())
        encoding_indices = {word:i for i, word in enumerate(encoding_vocab)}

        try:
            matrix = np.zeros((len(self.vocab), len(encoding_vocab)))# how to do
        except:# could break because vocab doesnt exist yet, and will give wrong message
            raise Exception("Vocab is too big. Consider using create_signatures instead")

        for word in self.vocab:
            for sig_word in signatures[word]:
                matrix[self.word_indices[word], encoding_indices[sig_word]] = signatures[word][sig_word]
        
        if log:
            print("Vectorizer created:")
            print(f"    - {len(self.vocab)} unique words;")
            print(f"    - {len(encoding_vocab)} CRV words")

        return Vectorizer(self.vocab, matrix, encoding_vocab)
        
        
    # a Vectorizer requires a matrix. If it's too large, this makes CRVs instead
    def create_signatures(self, window_size = 2, log = True):

        # setup signatures
        
        signatures = { word : defaultdict(int) for word in self.vocab }
        
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
                    signatures[center_word][nearby_word] += 1


        # divide signatures by counts
        for word in self.vocab:
            total_co_occurences = sum(signatures[word].values())
            signatures[word] = CRV({key: val / total_co_occurences for key, val in signatures[word].items()})

        # log data
        if not log:
            return signatures
        
        print("Signatures collected:")
        sorted_best = [[word, list(signatures[word].items())[0]] for word in self.vocab]
        highest = max(sorted_best, key = lambda item : item[1][1])
        print("    - highest best signature: " + str(highest) + " & " + str(sorted_best.count(highest) - 1) + " others.")
        lowest = min(sorted_best, key = lambda item : item[1][1])
        print("    - lowest best signature: " + str(lowest) + " & " + str(sorted_best.count(lowest) - 1) + " others.")

        return signatures


    # Corpus Search

    def get_ragged_int_tensor(self):
        return tf.ragged.constant([[self.word_indices[word] for word in sentence] for sentence in self.sentences], dtype = tf.int16)

    
    def find(self, words, max_seperation = 3, max_prints = 10, print_size = 20):
        # once you find a set, skip past the first findable word, or you get duplicates
        prints_so_far = 0
        total_found = 0

        if type(words) == str:
            words = [words]

        common_sentences = set(self.sentence_indices[words[0]]).union(*[self.sentence_indices[word] for word in words])
        valid_sentences = set()

        if len(common_sentences) == 0:
            print('None Found')
            return common_sentences
        
        for sentence_index in common_sentences:
            sentence = self.sentences[sentence_index]

            last_index = -100

            for i in range(len(sentence)):

                sentence_slice = sentence[i:min(len(sentence), i + max_seperation)]

                slice_valid = True
                for search_word in words:
                    if search_word not in sentence_slice:
                       slice_valid = False
                       break
                    sentence_slice.remove(search_word)

                if (i - last_index) < max_seperation:
                    slice_valid = False

                if not slice_valid:
                    continue

                if prints_so_far < max_prints:
                    print_center = i + len(sentence_slice) // 2
                    print(concat_sentence(sentence[max(0, print_center - print_size // 2) : min(len(sentence), print_center + print_size // 2)], self.text_mode))
                    print('\n \n')
                    prints_so_far += 1
                    last_index = i

                valid_sentences.add(sentence_index)
                total_found += 1

        print(f"Total Found : {total_found}")
        print(f"Found in {len(valid_sentences)} sentences")

        return valid_sentences