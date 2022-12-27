import pandas as pd
from collections import Counter
from itertools import chain
import string
import operator
from random import *

WORD_LENGTH = 5
NO_OF_TURNS = 6

class WordleHelper:
    
    def __init__(self):
        self.possibleWords = self.__getWordList()
        self.letterFrequency = self.__getLetterFrequency()
        # A list of all alphabet characters repeated each time for each of the 5 letters
        self.wordVector =  [set(string.ascii_uppercase) for _ in range(WORD_LENGTH)]
        self.turn = 0

    def __getWordList(self):
        # Get the list of words which we consider as valid guesses
        df = pd.read_csv("data/PossibleAnswers.txt",header=None)
        df.columns = ['word']
        df['word'] = df['word'].str.upper()
        wordleDict = df[df['word'].str.len()==5] 

        output = set(wordleDict["word"])

        return output
    
    def __getLetterFrequency(self):

        # Look at the frequency of each letter
        letterCounter = Counter(chain.from_iterable(self.possibleWords))
        
        # show the letters as a percentage of total letters
        letterFreq = {
            character: value / letterCounter.total()
            for character, value in letterCounter.items()
        }

        return letterFreq

    def __calculateWordScore(self, word):
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
            score += self.letterFrequency[char]
            # I prefere words which have a lot of vowels in the start of the game
            if char in distinctVowelList and self.turn <=2:
                score += 0.05*score
                distinctVowelList.remove(char)

        # the score is multiplied by the number of distinct letters in the word 
        outputVal = score * len(set(word))  
        return outputVal

    def updateWordList(self,wordEntered, pattern):
        if pattern!="22222":
            ##########################
            # Update the word Vectors
            ##########################

            for idx, letter in enumerate(pattern):
                if letter == "2":
                    # letter is in the right place. the vector becomes the correct letter
                    self.wordVector[idx] = {wordEntered[idx]}
                elif letter == "1":
                    try:
                        # we know this value cant exist in this position - remove the value
                        self.wordVector[idx].remove(wordEntered[idx])
                    except KeyError:
                        # Its possible we have already removed it
                        pass
                elif letter == "0":
                    # this letter doesnt exist in the word - remove it from all vectors
                    for v in self.wordVector:
                        try:
                            v.remove(wordEntered[idx])
                        except KeyError:
                            pass

            ###############################################
            # Use the vectors to update the possible words
            ###############################################
            newPossibleWords = [word for word in self.possibleWords if self.__matchWordVector(word)]
            self.possibleWords = newPossibleWords

    def __matchWordVector(self,word):
        for letter, l in zip(word, self.wordVector):
            if letter not in l:
                return False
        return True

    def pickTopAnswer(self):
        self.turn+=1
        
        sort_by = operator.itemgetter(1)
        sortedScores =  sorted(
            [(word, self.__calculateWordScore(word)) for word in self.possibleWords],
            key=sort_by,
            reverse=True,
        )
        output = sortedScores[0][0]
        score = sortedScores[0][1]
        print(f"Selected Word: {output} | Score: {score}")

        return output

class WordleGame:

    def __init__(self):
        self.answer = self.__getAnswer()

    def __getAnswer(self):

        # Import the data and pick a random answer
        df = pd.read_csv("data/PossibleAnswers.txt",header=None)
        df.columns = ['word']
        df['word'] = df['word'].str.upper()
        wordleDict = df[df['word'].str.len()==5] 
        wordArr = wordleDict['word'].to_numpy()
        max = wordArr.size - 1
        rand = randint(1, max)
        selectedWord = wordArr[rand]

        return selectedWord

    def getPatternFromGuess(self,guess):
        
        pattern = ""

        for i,letter in enumerate(guess):
            if self.answer[i] == guess[i]:
                # the letter is right
                pattern+="2"
            elif letter in self.answer:
                # the letter exists in the word but not in this space
                pattern+="1"
            else:
                # the letter doesnt exist    
                pattern+="0"

        return pattern



if __name__ == '__main__':

    noOfGames = 1000
    countWins = 0
    countLose = 0
    wordsThatLose = []

    for game in range(1,noOfGames+1):
        
        # Play the game
        outcome = False
        print("")
        print(f"Game: {game}")
        
        wordle = WordleGame()
        helper = WordleHelper()

        print(f"Answer: {wordle.answer}")

        for turn in range(1,NO_OF_TURNS+1):    
            # Guess - Get the Pattern - Update the list 
            guess = helper.pickTopAnswer()
            pattern = wordle.getPatternFromGuess(guess)

            if pattern == "22222": 
                outcome = True
                break
            helper.updateWordList(guess,pattern)

        if outcome==True:
            print("Outcome: Win")
            countWins+=1
        else: 
            print("Outcome: Lose")
            countLose+=1
            wordsThatLose.append(wordle.answer)

    winPercent = (countWins/noOfGames) * 100
    print("")
    print(f"Total Wins: {countWins}")
    print(f"Total Losses: {countLose}")
    print(f"Win %: {winPercent}")
    
    print("")
    print("Failures:")
    print(*wordsThatLose, sep = "\n") 