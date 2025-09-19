import matplotlib.pyplot as plt
from itertools import *
import numpy as np
import random

from classes.Utils import *
from classes.CRV import *


class Vectorizer:
    def __init__(self, vocab, matrix, embedding_vocab = None):
        self.vocab = vocab
        self.embedding_vocab = embedding_vocab or vocab

        self.matrix = matrix
        self.vsize, self.csize = self.matrix.shape

        self.indices = {word : i for i, word in enumerate(self.vocab)}
        self.embedding_indices = {word : i for i, word in enumerate(self.embedding_vocab)}

    @argmap
    def vectorize(self, word, mode = 'vec'):
        if mode == 'vec':
            return self.to_vector(word)
        
        elif mode == 'int':
            return self.to_int(word)
        
        elif mode == 'str':
            return self.to_str[word]
        
        elif mode == '1hot':
            return self.one_hot(word)
        
        elif mode == 'CRV':
            return self.to_CRV(word)
        
    
    def to_int(self, item):
        if type(item) not in (int, str):
            raise Exception(f'Invalid type to be int, was {type(item)}')
        return item if type(item) == int else self.indices[item]
    
    def to_str(self, item):
        if type(item) not in (int, str):
            raise Exception(f'Invalid type to be str, was {type(item)}')
        return item if type(item) == str else self.vocab[item]

    
    def to_vector(self, item):
        if type(item) not in (int, str, np.ndarray, CRV):
            raise Exception(f'Invalid type to be vector, was {type(item)}')
        
        if type(item) == np.ndarray:
            if item.shape == (self.csize,):
                return item
            else:
                raise Exception(f'Cannot convert array of shape {item.shape} into a vector with this Vectorizer')
            
        elif type(item) in (str, int):
            return self[self.to_int(item)]
        
        elif type(item) == CRV:
            result = np.zeros(self.csize)
            for word, val in item.items():
                result[self.embedding_indices[word]] = val

            return result
   
    def to_CRV(self, item):
        if type(item) not in (int, str, np.ndarray, CRV):
            raise Exception(f'Invalid type to be vector, was {type(item)}')
        
        if type(item) == CRV:
            return item
        
        item = self.to_vector(item)
        return CRV({word : val for word, val in zip(self.embedding_vocab, item) if val != 0})
    

    # Vector Creation

    def one_hot(self, item):
        result = np.zeros(self.vsize)
        result[self.to_int(item)] = 1
        return result

    def average(self, *args):
        if len(args) == 0 and type(args[0]) == list:
            args = args[0]
        result = np.zeros(self.csize)
        for arg in args:
            result += self.to_vector(arg)

        return result / len(args)
    

    # Different methods of comparison of a word to all others
    def rate_words(self, vector, mode = 'min'):
        vector = self.to_vector(vector)

        if mode == 'min':
            ratings = np.sum(np.minimum(self.matrix, vector), axis = 1)
        elif mode == 'diff':
            ratings = 1 - np.sum(abs(self.matrix - vector), axis = 1)
        elif mode == 'mult':
            ratings = np.einsum('wv,v->w', self.matrix, vector)
        elif mode == 'min/max':
            max_vals = np.maximum(self.matrix, vector) 
            ratings = np.divide(np.minimum(self.matrix, vector), max_vals, out = np.zeros_like(max_vals), where = max_vals!=0)
            ratings = np.sum(ratings, axis = 1)
        elif mode == 'sqrt':
            ratings = np.sqrt(self.matrix * vector)
            ratings = np.sum(ratings, axis = -1)
            ratings *= ratings
            
        return sort_hl({word : i for word, i in zip(self.vocab, list(ratings))})
    
    # Different methods of comparison of a word to a sequence of words
    # return values should be printed with print_scanned_text()
    def rate_sequence(self, vector, word_sequence, mode = 'min'):
        vector = self.to_vector(vector)
        sequence = self.vectorize(word_sequence)

        if type(sequence) == list:
            sequence = np.array(sequence)

        try:
            if mode == 'min':
                ratings = np.sum(np.minimum(sequence, vector), axis = 1)
            elif mode == 'diff':
                ratings = 1 - np.sum(abs(sequence - vector), axis = 1)
            elif mode == 'mult':
                ratings = np.einsum('wv,v->w', sequence, vector)
            elif mode == 'sqrt':
                ratings = np.sqrt(sequence * vector)
                ratings = np.sum(ratings, axis = -1)
                ratings *= ratings

        except Exception as error:
            print(type(vector), type(sequence))
            print(sequence.shape, vector.shape)
            print(sequence.dtype, vector.dtype)
            raise error

        return [(word, i) for word, i in zip(word_sequence, list(ratings))]
    

    def __getitem__(self, idx):
        return self.matrix[self.to_int(idx)]
