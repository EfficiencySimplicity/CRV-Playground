# CRV-Playground

###### "You shall know a word by the company it keeps" - J. R. Firth

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

# CRV Operations

# CRV Interpretation

CRVs are not like ordinary vector representations, which combine meaning spread out across many values, and are not oriented 
towards being easy for humans to understand, instead being optimized for efficiency. The fact that CRVs are made by a fixed
process allows for inspection into the meaning of their values.

Consider the CRV of "bake", obtained from a corpus of recipes:  
  { + 0.17⋅\n + 0.16⋅- + 0.1⋅at + 0.1⋅3 + 0.04⋅and + 0.04⋅.   
    + 0.03⋅for + 0.03⋅1 + 0.03⋅in + 0.02⋅4 + 0.02⋅0 + 0.02⋅2  
    + 0.02⋅5 + 0.01⋅, + 0.01⋅a + 0.01⋅uncovered + 0.01⋅pan   
    + 0.01⋅until + 0.01⋅about + 0.01⋅cover + 352 others}  

Here we see, *as expected*, words that would be around the word 'bake'.
This may be the first time you have seen a word vector that is what you *expect*!

These representations can even be guessed at; take for example this CRV, from the same corpus:

  { + 0.24⋅\n + 0.09⋅. + 0.07⋅dish + 0.05⋅- + 0.04⋅<START>   
    + 0.04⋅in + 0.04⋅quart + 0.02⋅a + 0.02⋅and + 0.01⋅,   
    + 0.01⋅into + 0.01⋅greased + 0.01⋅of + 0.01⋅broccoli   
    + 0.01⋅chicken + 0.01⋅with + 0.01⋅potato   
    + 0.01⋅large + 0.01⋅put + 0.01⋅buttered + 237 others}  

This is an example of one that is harder to guess, but you can get at the *mood* of the word.
It has to do with brocolli, chicken, butter and grease, and it is a 'dish'.
The word happens to be 'casserole', and the CRV above probably makes more sense in light of that information.

But why is "quart" so common next to 'casserole'? I certainly don't see the connection. And this is where the trail would stop
for most types of word vectors. Maybe you'd check to see what activates parts of it, maybe you'd check similarity. Those would
both be approximations, however. With CRVs, we can plainly see, by *looking into the corpus*, where this came from, and have it then
*make sense to us*.

A quick search reveals:

'all ingredients in 3 quart casserole . cover'

'cheese into 2 - quart casserole dish .'

'a greased 3 - quart casserole at 4'

'1 / 2 - quart casserole , pyrex'

'1 / 2 - quart casserole dish ,'

'1 / 2 - quart casserole . '

It appears (and I have just learned many other things from my CRVs) that
the standard measurement of a casserole is in *quarts*, which was certainly unexpected for me.



