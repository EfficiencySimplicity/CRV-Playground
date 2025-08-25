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

That's all there is to it! It may seem overly simple, but CRVs can produce surprising results. 

### Some notes on generating CRVs:

- For smaller datasets, a window of 2 on each side of the word seems to give most consistent results, and different windows
  reveal different representations of a word.

  A whole-document window will produce the 'theme' of the word, i.e, whether is is in mostly recipes, news articles, etc.,
  while a smaller window will be more inclined towards the "meaning" of the word

- It is recommended that you use the tally - and divide method above, as simply dividing by the number of appearences of "was" will
  not take into account the varying window size (sometimes clipped by the end of the document)
  
# CRV Operations

#### Similarity:

The best discovered methods for finding the similarity of 2 CRVs (and thus 2 ideas) are min() and absolute difference.
Both of these methods produce nearly identical ordering of words according to similarity, but have differing values.
Minimum is preferred because:

- It is always normalized
- It is quick to compute bitwise
- It is always positive.

Since a CRV's values all sum to 1, the largest value that min() can reach is 1; this is where the two CRVs are 
exactly equal, so the minimum is exactly the same as either one, and summed up, is one. Any increase in one of a CRV's
values results in a decrease in others.

similarity of 'chicken' (recipe corpus):

<img width="1601" height="659" alt="image" src="https://github.com/user-attachments/assets/635f381c-3d0d-4fff-8cc4-e0e655d6ce03" />

similarity of 'hi' (diplomacy corpus):

<img width="1601" height="659" alt="image" src="https://github.com/user-attachments/assets/916c7c19-8e94-4435-a557-3f13e1681147" />

similarity of '2' (recipe corpus):

<img width="1601" height="659" alt="image" src="https://github.com/user-attachments/assets/906278c0-2f58-493b-81b4-f190b2afcaa4" />

similarity of 'betray' (diplomacy corpus):

<img width="1601" height="659" alt="image" src="https://github.com/user-attachments/assets/1205f907-fb14-4f80-87b1-6b4b05ea93b0" />

similarity of '🥳' (diplomacy corpus):

<img width="1601" height="659" alt="image" src="https://github.com/user-attachments/assets/fceb27ba-bbd2-4a85-96dd-8c3ecf6884cf" />


#### Difference

Suppose you want to know how two words are different (i.e. how are they used differently?). CRVs make inspecting a word's particular
attributes incredibly simple.

For example, here from the diplomacy corpus (a strategy game where country leaders sent chat messages asking for alliances and so on)
is 'hi' and 'greetings':

'hi':

{ + 0.32⋅<START> + 0.13⋅, + 0.1⋅! + 0.04⋅there + 0.04⋅.  
  + 0.03⋅germany + 0.03⋅russia + 0.03⋅austria + 0.03⋅england
  + 0.03⋅france + 0.02⋅turkey + 0.02⋅— + 0.02⋅i + 0.02⋅italy
  + 0.01⋅- + 0.01⋅and + 0.01⋅queen + 0.01⋅: + 0.01⋅<END>
  + 0.01⋅fellow + 38 others}

'greetings':

{ + 0.3⋅<START> + 0.14⋅! + 0.13⋅, + 0.04⋅germany + 0.03⋅\n  
  + 0.03⋅<UNK> + 0.03⋅from + 0.03⋅russia + 0.02⋅austria
  + 0.02⋅england + 0.02⋅italy + 0.02⋅my + 0.02⋅queen
  + 0.01⋅and + 0.01⋅good + 0.01⋅her + 0.01⋅hope + 0.01⋅how
  + 0.01⋅i + 0.01⋅kaiser + 6 others}

How *specifically* are 'hi' and 'greetings' different?
By subtracting 'greetings' from 'hi', we get this:

{ - 0.04⋅! + 0.04⋅there + 0.04⋅. - 0.03⋅\n - 0.03⋅from  
  - 0.03⋅<UNK> + 0.03⋅france + 0.02⋅turkey - 0.02⋅my  
  + 0.02⋅— + 0.02⋅<START> - 0.01⋅queen - 0.01⋅good - 0.01⋅her  
  - 0.01⋅hope - 0.01⋅how - 0.01⋅neighbor - 0.01⋅the - 0.01⋅to  
  - 0.01⋅we + 50 others}

separating nefative values as 'more like "greetings"', we get these:

##### more like 'hi':

{ + 0.04⋅there + 0.04⋅. + 0.03⋅france + 0.02⋅turkey + 0.02⋅—  
  + 0.02⋅<START>}

##### more like 'greetings':

{ + 0.04⋅! + 0.03⋅\n + 0.03⋅from + 0.03⋅<UNK> + 0.02⋅my 
  + 0.01⋅queen + 0.01⋅good + 0.01⋅her  
  + 0.01⋅hope + 0.01⋅how + 0.01⋅neighbor + 0.01⋅the + 0.01⋅to  
  + 0.01⋅we}

From these two CRVs, we can gain quite a lot of information:

- 'hi' is more often used to greet a country.
- 'greetings' is most often to greet a queen, and its tone is more formal overall.
- 'hi' appears next to the <START> of a chat message more often, and is the more common greeting.
- 'greetings' is more often near a new line, meaning 'greetings' is on it's own line, like the greeting in a letter.

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

It appears (and I have learned many other things from my CRVs) that
the standard measurement of a casserole is in *quarts*,
which was certainly unexpected for me. I'd expect the measurement to be in pan-inches.

Diplomacy hi greetings



