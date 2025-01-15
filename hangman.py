import random
import time
from typing import Callable, Optional
from IPython.display import clear_output

def load_word_counts(file_path: str) -> dict[str, int]:
    word_counts = {}
    with open(file_path, 'r') as f:
        for line in f:
            word, count = line.strip().split()
            word_counts[word] = int(count)
    return word_counts

def draw_hangman(tries: int) -> None:
    '''
    Draws the hangman output.
    
    :param tries: The number of failed tries.
    :type tries: int
    '''
    assert 0 <= tries <= 6, 'Invalid try number!'
    stages = [
        """\n  +---+\n      |\n      |\n      |\n     ===\n""",
        """\n  +---+\n  O   |\n      |\n      |\n     ===\n""",
        """\n  +---+\n  O   |\n  |   |\n      |\n     ===\n""",
        """\n  +---+\n  O   |\n /|   |\n      |\n     ===\n""",
        """\n  +---+\n  O   |\n /|\  |\n      |\n     ===\n""",
        """\n  +---+\n  O   |\n /|\  |\n /    |\n     ===\n""",
        """\n  +---+\n  O   |\n /|\  |\n / \  |\n     ===\n""",
    ]
    print(stages[tries])

def hangman_game(
    inference: Optional[Callable] = None,
    word_file_path: str = "hw1_word_counts_05.txt",
    interactive: bool = True,
    seed: Optional[int] = None
) -> None:
    '''
    Engine for running the hangman game.
    
    :param inference: The function which predicts the next letter given the game state. Leave empty
                      for an interactive game.
    :type inference: Optional[Callable]
    :param word_file_path: The path to the word counts file.
    :type word_file_path: str
    :param interactive: Set to true if the game should be interactive, false otherwise.
    :type interactive: bool
    :param seed: Set to an int for random seeding.
    :type seed: Optional[int]
    '''
    if seed is not None:
        random.seed(seed)
    if not interactive and not inference:
        raise ValueError('Hangman without an algorithm function cannot be run in noninteractive mode.')
    word_counts = load_word_counts(word_file_path)
    all_words = []
    for word, freq in word_counts.items():
        all_words += [word] * freq
    word = random.choice(all_words)
    word_pattern: list[str] = ['_'] * len(word)
    letters_tried: set[str] = set()
    max_tries: int = 6
    tries: int = 0
    message: str = ''

    while tries < max_tries and '_' in word_pattern:
        if interactive:
            clear_output(wait=True)
            time.sleep(0.5)
            print(message)
            draw_hangman(tries)
            print(f"Word: {' '.join(word_pattern)}\nTried letters: {', '.join(sorted(letters_tried))}")
        message = ''

        try:
            if inference:
                guess = inference(letters_tried, word_pattern, word_counts)
                if not isinstance(guess, str):
                    raise ValueError(f'Model prediction returned type {type(guess)}, not str')
                guess = guess.upper()
            else:
                guess = input("Choose a letter (type 'exit' to exit): ").upper()
                if 'EXIT' == guess:
                    break
        except Exception as e:
            message = f"Inference error: {e}"
            raise ValueError(message)
        if not guess or not guess.isalpha() or len(guess) != 1:
            if inference:
                raise ValueError(f'Your code predicted an invalid guess: {guess}')
            message = "Invalid input. Please enter a single letter."
            continue
        if guess in letters_tried:
            if inference:
                raise ValueError(f'Your code predicted a letter that has already been attempted: {guess}')
            message = "You've already tried that letter. Try again."
            continue

        letters_tried.add(guess)

        if guess in word:
            for i, letter in enumerate(word):
                if letter == guess:
                    word_pattern[i] = guess
        else:
            tries += 1
    if interactive:
        clear_output(wait=True)
        time.sleep(0.5)
        print(message)
        draw_hangman(tries)
        print(f"Word: {' '.join(word_pattern)}\nTried letters: {', '.join(sorted(letters_tried))}")
    if '_' not in word_pattern:
        if interactive:
            print("Congratulations! You guessed the word: ", word)
        return 1
    if interactive:
        print("Game over! The word was: ", word)
    return 0