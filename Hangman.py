import pygame
import os, math

from random import choice
from time import thread_time
from typing import List
from dataclasses import dataclass

pygame.init()

# region load
# loading the words from the woerter.txt file.
# have to load above the screen init so you can edit the screen
allWords: List[str] = []
largestWord = 0
with open("woerter.txt", "r") as f:
    allWords = f.read().upper().split(",")
for i in range(len(allWords)):
    allWords[i] = allWords[i].strip()

print(allWords)

# finding the largest word
for w in allWords:
    x = pygame.font.SysFont('comicsans', 60).size(w)
    largestWord = x[0] if largestWord < x[0] else largestWord
# endregion


#* pygame display init. adapting the screen to the longest possible word
screenX, screenY = 800+max(largestWord-500, 0)+100, 500
screen = pygame.display.set_mode((screenX, screenY))
pygame.display.set_caption("Hangman")

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# fonts
BUTTON_FONT = pygame.font.SysFont('comicsans', 40)
WORD_FONT = pygame.font.SysFont('comicsans', 60)
TITLE_FONT = pygame.font.SysFont('comicsans', 70)

# game
hangman_status = 0
word = ""
usedLetters = [] # if letter in usedLetters, it means it was pressed
usedWords = [] # at the start of a round, a new word gets selected and marked as used.

@dataclass
class Button:
    x: int
    y: int
    character: str
    visible: bool

# button variables
buttons: List[Button] = []
RADIUS = 20
SPACE = 15 # between each button
startX = round((screenX - (RADIUS * 2 + SPACE) * 13) / 2)
startY = screenY - 170

# load images.
# orignal image size: 338 | 392 (rel: ~1.2)
hangmanImages: List[pygame.Surface] = []
x = startY-150
for i in range(10):
    image = pygame.image.load(os.path.join("images", "hangman (" + str(i+1) + ").png"))
    image = pygame.transform.scale(image, (x, int(x*1.2))) # resize images
    hangmanImages.append(image)


def setupButtons():
    global buttons
    buttons = []
    perRow = 13 # buttons per row

    for i in range(26):
        x = startX + SPACE * 2 + ((RADIUS * 2 + SPACE) * (i % perRow))
        y = startY + ((i // perRow) * (SPACE + RADIUS * 2))
        buttons.append(Button(x, y, chr(65 + i), True))

def newWord() -> str:
    """Prevent that words wont show up multiple times after each other."""
    global allWords, usedWords
    res = [i for i in allWords if i not in usedWords]

    if len(res) == 0:
        usedWords = []
        usedWords.append(choice(allWords))
        return usedWords[0]

    usedWords.append(choice(res)) 
    return usedWords[len(usedWords)-1]

def reset():
    global hangman_status, usedLetters, word
    usedLetters = []
    word = newWord()
    hangman_status = 0
    setupButtons()

def draw():
    global screenX, screenY
    screen.fill(WHITE)

    # compile guessWord
    guessWord = ""
    for letter in word:
        if letter in usedLetters:
            guessWord += letter + " "
        else:
            # add space
            if ord(letter) not in range(65, 91):
                guessWord += letter + " "
                continue

            guessWord += "_ "


    # draw buttons
    for button in buttons:
        if button.visible:
            rect = pygame.Rect(button.x-RADIUS, button.y-RADIUS, RADIUS*2, RADIUS*2)
            pygame.draw.rect(screen, BLACK, rect, 5)
            t = BUTTON_FONT.render(button.character, True, BLACK)
            screen.blit(t, (int(button.x) - int(t.get_width()/2), int(button.y) - int(t.get_height()/2)))

    # hangman, rendered first, so if the text overlaps it will be more or less visible
    screen.blit(hangmanImages[hangman_status], (25, 50))

    # Title
    t = TITLE_FONT.render("Hangman", True, BLACK)
    screen.blit(t, (int(screenX/2) - int(t.get_width()/2), 20))

    # guessWord
    t = WORD_FONT.render(guessWord, True, BLACK)
    screen.blit(t, (int(screenX/2) - int(t.get_width()/2), int(screenY/2) - int(t.get_height()/2)))

    pygame.display.update()

def display_message(message, waitTime=3):
    """WaitTime in seconds"""
    global run
    tStart = thread_time()
    tEnd = tStart + waitTime + 1

    pygame.time.wait(1000) #wait one second (ns) so the user can see the Hangman when it is complete.

    while thread_time() < tEnd:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                print("exit in wait screen!")
                return
        
        screen.fill(WHITE)
        text = WORD_FONT.render(message, True, BLACK)
        screen.blit(text, (int(screenX/2) - int(text.get_width()/2), int(screenY/2) - int(text.get_height()/2)))

        pygame.display.update()


run = True
def main():
    global hangman_status, run
    
    reset()
    FPS = 60
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                for button in buttons:
                    if button.visible:
                        # calculate the overlap of mouse pos and button
                        distance = math.sqrt((button.x - mouseX)**2 + (button.y - mouseY)**2)
                        if distance <= RADIUS:
                            button.visible = False
                            usedLetters.append(button.character)
                            if button.character not in word:
                                hangman_status += 1
        draw()

        won = True
        for letter in word:
            # only capital letters can be guessed and therefore the win condition is that only these have to be guessed.
            if ord(letter) not in range(65, 91): continue

            if letter not in usedLetters:
                won = False
                break
        
        # game ending conditions
        if won:
            display_message('Gewonnen')
            reset()
            continue
        elif hangman_status == len(hangmanImages)-1:
            display_message('Verloren')
            reset()
            continue
    

main()
pygame.quit()