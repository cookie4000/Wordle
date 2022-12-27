import pandas as pd
from collections import Counter
from itertools import chain
import operator
import string

WORD_LENGTH = 5
MAX_ATTEMPTS = 6

# Import Data
df = pd.read_csv("data/PossibleAnswers.txt",header=None)
df.columns = ['word']
df['word'] = df['word'].str.upper()

# Get a set of the valid words
words = set(df["word"])

# count the letter frequencies in all these words
letterCounter = Counter(chain.from_iterable(words))

# show the letters as a percentage of total letters
letterFreq = {
    character: value / letterCounter.total()
    for character, value in letterCounter.items()
}


def calculateWordScore(word, letterFreq, turn):
    # this method is the algorithm that picks the best word avaiable 
        # We evaluate this on 3 factors;
        #    1. The quanity of vowels in the word (only in the first 2 turns)
        #    2. The distinct letters in the words
        #    3. Letter frequency

        # For example FUZZY would be a bad word - 1 vowel, repeated rare letters
        # AROSE would be a good word - each letter is distinct 3 vowels. letters of high frequency
        
    score = 0.0
    distinctVowelList = ['A','E','I','O','U']

    for char in word.upper():
            score += letterFreq[char]
            # I prefer words which have a lot of vowels in the start of the game
            if char in distinctVowelList and turn <=2:
                score += 0.05*score
                distinctVowelList.remove(char)

    return score * len(set(word))  

def sortByWordScore(words, turn):
    # Generate highest to lowest list of tuples. work / score
    sort_by = operator.itemgetter(1)
    return sorted(
        [(word, calculateWordScore(word,letterFreq,turn)) for word in words],
        key=sort_by,
        reverse=True,
    )

def displayWordScores(wordScores):
    for (word, freq) in wordScores:
        print(f"{word:<10} | {round(freq,3)}")
        
def inputWord():
    while True:
        word = input("Input the word to Help with> ").upper()
        if len(word) == WORD_LENGTH and word in words:
            break
    return word

def match(word_vector, possible_words):
    return [word for word in possible_words if matchWordVector(word, word_vector)]

def matchWordVector(word, word_vector):
    for letter, l in zip(word, word_vector):
        if letter not in l:
            return False
    return True

def inputResponse():
    print("Type the color-coded reply from Wordle:")
    print("  2 for Green")
    print("  1 for Yellow")
    print("  0 for Gray")
    while True:
        response = input("Response from Wordle> ")
        if len(response) == WORD_LENGTH and set(response) <= {"2", "1", "0"}:
            break
        else:
            print(f"Error - invalid answer {response}")
    return response

def solve():
    possibleWords = words.copy()
    wordVector = [set(string.ascii_uppercase) for _ in range(WORD_LENGTH)]
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Attempt {attempt} with {len(possibleWords)} possible words")
        displayWordScores(sortByWordScore(possibleWords, attempt)[:15])

        word = inputWord()
        response = inputResponse()
        if response=="22222":
            print("Wordle Solved!")
            break
        for idx, letter in enumerate(response):
            if letter == "2":
                # it is in the right place - fix it
                wordVector[idx] = {word[idx]}
            elif letter == "1":
                try:
                    # we know this value cant exist in this position remove it
                    wordVector[idx].remove(word[idx])
                except KeyError:
                    pass
            elif letter == "0":
                for vector in wordVector:
                    try:
                        # remove this from all vectors
                        vector.remove(word[idx])
                    except KeyError:
                        pass
                    
        possibleWords = match(wordVector, possibleWords)

        
if __name__ == '__main__':
    solve()