import os
import pygame
import math
import sys
import random
import time

from typing import List
from dataclasses import dataclass

# setup display
pygame.init()
WIDTH, HEIGHT = 1100, 700 # minimum: 700, 450, perfect: 1200 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman")

@dataclass
class Button:
    x: int
    y: int
    character: str
    visible: bool

# colors
WHITE = (255,255,255)
BLACK = (0,0,0)

# fonts
LETTER_FONT = pygame.font.SysFont('comicsans', 40)
WORD_FONT = pygame.font.SysFont('comicsans', 60)
TITLE_FONT = pygame.font.SysFont('comicsans', 70)

# button variables
buttons: List[Button] = []
RADIUS = 20
SPACE = 15 # between each button
startx = round((WIDTH - (RADIUS * 2 + SPACE) * 13) / 2)
starty = HEIGHT - 170

# game
hangman_status = 0
word = ""
guessed = []

def setupButtons():
    global buttons
    buttons = []

    for i in range(26):
        # 13 pro zeile
        x = startx + SPACE * 2 + ((RADIUS * 2 + SPACE) * (i % 13))
        y = starty + ((i // 13) * (SPACE + RADIUS * 2))
        buttons.append(Button(x, y, chr(65 + i), True))

# load images.
images = []
for i in range(10):
    image = pygame.image.load(os.path.join("src", "backdrop" + str(i) + ".png"))
    images.append(image)

# game variables
words = []
with open("woerter.txt", "r") as f:
    words = f.read().upper().replace(" ", "").split(",")

wordsString = " ".join(words)

def reset():
    global hangman_status, guessed, word
    guessed = []
    word = random.choice(words)
    hangman_status = 0
    setupButtons()


def draw():
    win.fill(WHITE)
    # draw title
    text = TITLE_FONT.render("Hangman", True, BLACK)
    win.blit(text, (int(WIDTH/2) - int(text.get_width()/2), 20)) # titel

    # draw word
    display_word = ""
    for letter in word:
        # if letter in guessed, it means it was pressed
        if letter in guessed:
            display_word += letter + " "
        else:
            display_word += "_ "
    text = WORD_FONT.render(display_word, True, BLACK)
    win.blit(text, (int(WIDTH/2) - int(text.get_width()/2), int(HEIGHT/2) - int(text.get_height()/2)))# lösung

    # draw buttons
    for button in buttons:
        if button.visible:
            r = pygame.Rect(button.x-RADIUS, button.y-RADIUS, RADIUS*2, RADIUS*2)
            pygame.draw.rect(win, BLACK, r, 5)
            text = LETTER_FONT.render(button.character, True, BLACK)
            win.blit(text, (int(button.x) - int(text.get_width()/2), int(button.y) - int(text.get_height()/2)))

    win.blit(images[hangman_status], (150, 100))
    pygame.display.update()


def display_message(message, waitTime=3):
    """WaitTime in sekunden angeben"""
    global run
    tStart = time.thread_time()
    tEnd = tStart + waitTime

    while time.thread_time() < tEnd:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                print("break?")
                return
        
        win.fill(WHITE)
        text = WORD_FONT.render(message, True, BLACK)
        win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))

        pygame.display.update()


reset()
run = True

def main():
    global hangman_status, run
    
    FPS = 60
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                for button in buttons:
                    if button.visible:
                        #calculate the overlap point of mouse pos and button
                        distance = math.sqrt((button.x - m_x)**2 + (button.y - m_y)**2)
                        if distance < RADIUS:
                            button.visible = False
                            guessed.append(button.character)
                            if button.character not in word:
                                hangman_status += 1

        draw()

        won = True
        for letter in word:
            if letter not in guessed:
                won = False
                break
        
        if won:
            display_message('Gewonnen')
            reset()
        if hangman_status == 9:
            display_message('Verloren')
            reset()
    

main()
pygame.quit()