import pandas as pd
from random import *
from rich.prompt import Prompt
from rich.console import Console

NO_OF_GUESSES = 6

# Import the total word list
dfWordList = pd.read_csv("data/WordList.txt",header=None)
dfWordList.columns = ['word']
dfWordList['word'] = dfWordList['word'].str.upper()

# Import the Possible answer list
dfPossibleAnswers = pd.read_csv("data/PossibleAnswers.txt",header=None)
dfPossibleAnswers.columns = ['word']
dfPossibleAnswers['word'] = dfPossibleAnswers['word'].str.upper()

SQUARES = {
    'correct': '🟩',
    'contains': '🟨',
    'wrong': '⬛'
}

# Return the letter formatted
def correct(letter):
    return f'[black on green]{letter}[/]'

def contains(letter):
    return f'[black on yellow]{letter}[/]'

def wrong(letter):
    return f'[black on white]{letter}[/]'

def checkAnswer(guess, answer):
    guessed = []
    pattern = []

    # for each letter in the guess 
    for i, letter in enumerate(guess):

        if answer[i] == guess[i]:
            # the letter is right
            guessed += correct(letter)
            pattern.append(SQUARES['correct'])
        elif letter in answer:
            # the letter exists in the word but not in this space
            guessed += contains(letter)
            pattern.append(SQUARES['contains'])
        else:
            # the letter doesnt exist
            guessed += wrong(letter)
            pattern.append(SQUARES['wrong'])
    
    # the method returns the 2 strings (rich formatted guess and the related coloured squares)
    return ''.join(guessed), ''.join(pattern)

def isWordActualWord(guess):
    if guess in dfWordList['word'].values:
        return True
    return False

def pickWord():

    # Pick a 5 letter word from the possible answers
    wordleDict = dfPossibleAnswers[dfPossibleAnswers['word'].str.len()==5] 
    wordArr = wordleDict['word'].to_numpy()
    max = wordArr.size -1
    rand = randint(1, max)
    selectedWord = wordArr[rand]
    return selectedWord

def game(console, answer):
    endOfGame = False
    alreadyGuessed = []
    FullPattern = []
    allGuesses = []

    while not endOfGame:

        guess = Prompt.ask("Enter your Answer").upper()

        # Validate Input - is the word 5 letters, have you already entered it, is it actually a word?
        while len(guess) != 5 or guess in alreadyGuessed or isWordActualWord(guess) == False:
            if guess in alreadyGuessed:
                console.print("[red]You've already guessed this word\n[/]")
            elif (len(guess) != 5):
                console.print('[red]You need to enter a 5 letter word\n[/]')
            else:
                isWordActualWord(guess) == False
                console.print("[red]This is not a dictionary word\n[/]")
            guess = Prompt.ask("Enter your Answer").upper()

        # Add to the array of previous guesses
        alreadyGuessed.append(guess)

        # Check the answer and add to the pattern grid
        guessed, pattern = checkAnswer(guess, answer)

        # Add the formatting to all the letters guessed
        allGuesses.append(guessed)

        # add to the total pattern
        FullPattern.append(pattern)

        console.print(*allGuesses, sep="\n")
        if guess == answer or len(alreadyGuessed) == NO_OF_GUESSES:
            endOfGame = True

    if len(alreadyGuessed) == NO_OF_GUESSES and guess != answer:
        console.print(f'\n[green]Correct Word: {answer}[/]')
    else:
        console.print(f"\n[green]WORDLE {len(alreadyGuessed)}/{NO_OF_GUESSES}[/]\n")

    console.print(*FullPattern, sep="\n")

if __name__ == '__main__':
    answer = pickWord()
    console = Console()
    
    console.print(f'\n[white on blue] WELCOME TO WORDLE [/]\n')
    console.print("Start Guessing\n")
    game(console, answer)
