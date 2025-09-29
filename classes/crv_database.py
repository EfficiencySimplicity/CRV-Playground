from collections import defaultdict
import re

from classes.utils import *
from classes.crv import *

################ CRV Database ################
#
# - Stores a large set of CRVs (for memory efficiency, as full vectors are noit required)
# - Stores these CRVs semi-efficiently in a file

class CRVDatabase:

    def __init__(self, signatures = {}, counts = {}, filepath = ''):
        """
        signatures: a dict of dicts, in the form of
        {word:{co-occurring word: % of occurrences...}...}

        alternatively pass counts, in the form of
        {word:{co-occurring word: # of occurrences...}...}

        alternatively pass a path to a .crvdb file
        """
        
        if signatures == {} and counts == {} and filepath == '':
            raise Exception("You must pass signatures, counts or filepath")
        
        if int(signatures != {}) + int(counts != {}) + int(filepath != '') > 1:
            raise Exception("You must pass only one argument")
        
        if filepath != '':

            if filepath[-6:] != '.crvdb':
                filepath += '.crvdb'#D.R.Y

            self.counts = defaultdict(defaultdict)

            with open(filepath, 'rb') as f:
                saved_string = f.read().decode('utf-8')

            self.vocab = [word[1:-1] for word in re.findall(fr'𘳕[\s\S]+?𘳕', saved_string)]
            self.word_indices = {word: idx for idx, word in enumerate(self.vocab)}
            self.set_vocab = set(self.vocab)

            count_dicts = [d[1:-1] for d in re.findall(
                fr'𘳕[\s\S]+?𘳕',
                saved_string[1:])]
                
            self.counts = {word:{self.vocab[ord(c[0])-1] : ord(c[1]) for c in [(count_dict[i:i+2]) for i in range(0, len(count_dict), 2)]} for word, count_dict in zip(self.vocab, count_dicts)}
            self.signatures = {
                word:
                    {count_word: word_count/sum(word_counts.values()) for count_word, word_count in word_counts.items()}
                for word, word_counts in self.counts.items()
            }

            return
        
        if signatures != {}:
            self.signatures = signatures
            # sneaky way to get at the counts from the signatures?

        if counts != {}:
            self.counts = counts
            self.signatures = {
                word:
                    {count_word: word_count/sum(word_counts.values()) for count_word, word_count in word_counts.items()}
                for word, word_counts in counts.items()
            }

        self.vocab = list(self.signatures.keys())# for indexing words
        self.word_indices = {word: idx for idx, word in enumerate(self.vocab)}
        self.set_vocab = set(self.vocab)# for checking if a word has been seen quickly


    def save(self, filepath):
        save_string = []
        delimiter = chr(101589)
        for word, counts in self.counts.items():
            save_string.append(delimiter)
            save_string.append(word)
            save_string.append(delimiter)

            save_string.extend(
                [(chr(self.word_indices[count_word]+1) + chr(count)) for count_word, count in counts.items()]
                )
            
        save_string.append(delimiter)

        if filepath[-6:] != '.crvdb':
            filepath += '.crvdb'
            
        with open(filepath, 'wb') as f:
            f.write((''.join(save_string)).encode("utf-8"))


    def compare(self, idx, mode = 'min'):
        idx = self[idx]
        return sort_hl({word: idx.compare(signature, mode) for word, signature in self.signatures.items()})


    def __getitem__(self,idx):
        if type(idx) == CRV:
            return idx
        if idx not in self.set_vocab:
            raise Exception(f"Word {idx} of type {type(idx)} never encountered")
        
        return CRV(self.signatures[idx])