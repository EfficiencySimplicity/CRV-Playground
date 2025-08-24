# CRV-Playground
Composite Representation Vectors (CRVs) are a type of human-understandable word embedding developed with the intent of creating explainable AI models. This repository includes tools for explaining and working with them. 


# CRVs:

CRVs are an effective, simple, human-understandable word vector representation (although they are not limited to simply words!) that
store words as frequency tables. They are made by a fixed, logical process that allows inspection of *why* a value is the way it is.

To generate a CRV for a specific word, take every appearance of that word in a corpus / dataset, along with
the words around it:

"and there **was** a        new"
"so  I     **was** starting to"
",   it    **was** soon     apparent"

The CRV for "was" is a table of words to percentages. More specifically:

- Every word that "was" appears next to (within the chosen context window) is tallied in the table:

  | Word     | Tally   |
  | -------- | ------- |
  | the      | 11800   |
  | in       | 5920    |
  | starting | 94765   |

- Every word's tally is divided by the sum of all the tallies,
  resulting in a normalized value representing the percentage of times that "was" is paired with that word.

  | Word     | Tally   |
  | -------- | ------- |
  | the      | .1049   |
  | in       | .0526   |
  | starting | .8425   |

That's all there is to it! It may seem overly simple, but CRVs can procuce surprising results. 

### Some notes on generating CRVs:

- For smaller datasets, a window of 2 on each side of the word seems to give most consistent results, and different windows
  reveal different representations of a word.

  A whole-document window will produce the 'theme' of the word, i.e, whether is is in mostly recipes, news articles, etc.,
  while a smaller window will be more inclined towards the "meaning" of the word

- It is recommended that you use the tally - and divide method above, as simply dividing by the number of appearences of "was" will
  not take into account the varying window size (sometimes clipped by the end of the document)



