"""
-raté : si la torpille est tombée dans l'eau ; et on change de joueur sauf dans le mode solo.
-touché : si la torpille est tombée sur un bâtiment ; le même joueur continue.
-coulé : si la torpille est tombée sur la dernière case non touchée d'un bâtiment ; le même joueur continue.

Exemples de fonctionnalités à mettre en place (les premières sont les plus simples) :

•on peut jouer en mode solo dans la console (même si la phase de placement n'est pas encore implémentée, on peut imaginer qu'on définit une grille fixe dans un premier temps)

•on peut jouer à deux joueurs dans la console

•à chaque tour de jeu, les grilles du joueur, et de l'adversaire (sauf en mode solo), sont mises à jour et affichées

•la phase de placement des bateaux est implémentée

•on peut jouer contre l'ordinateur

On peut avoir la totalité des points sans forcément répondre à toutes les exigences 
précédentes, tout dépend de la qualité globable du travail.
"""

#import des modules nécessaires pour faire fonctionner le jeu
import pygame, sys
from pygame.locals import *

from button import Button #module qui est dans le zip que j'ai trouvé pour faire des boutons sur pygame

import tkinter as tk #servira (pour l'instant) à demander le(s) pseudo(s)
from tkinter import messagebox

import json

import os

import random

#initialisation de pygame et pour l'affichage
pygame.init()
clock = pygame.time.Clock()

#setup de l'affichage
width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Menu")

#set up des background
bgMenu = pygame.image.load("assets/images/background.jpg")
bgPlay = pygame.image.load("assets/images/background play.jpg")
bgGame = pygame.image.load("assets/images/background game.jpg")
bgPos = pygame.image.load("assets/images/background pos.jpg")

#set up des musiques du jeu
menuMusic = pygame.mixer.Sound("assets/musiques/Menu Music.mp3")
gameMusic = pygame.mixer.Sound("assets/musiques/Game Music.mp3")
positioningMusic = pygame.mixer.Sound("assets/musiques/Positioning Music.mp3")

#son lors du jeu
explosion = pygame.mixer.Sound("assets/musiques/Explosion.mp3")
plop = pygame.mixer.Sound("assets/musiques/plop.mp3")

#volume du jeu
volume = 1.0


#pour la police d'écriture
def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

#pour "ajouter" le score du joueur dans le mode jeu
def add_score(scores, user, score):
    if not user in scores:
        scores[user] = {}
        scores[user]= 0
    scores[user] += score


def solo():
    
    menuMusic.stop()
    gameMusic.play()

    #pour avoir le nom d'utilisateur du joueur pour faire les scores
    root= tk.Tk()

    canvas1 = tk.Canvas(root, width=400, height=300, relief='raised')
    canvas1.pack()

    label1 = tk.Label(root, text='Votre pseudo')
    label1.config(font=('assets/font.ttf', 14))
    canvas1.create_window(200, 25, window=label1)

    label2 = tk.Label(root, text='votre pseudo :')
    label2.config(font=('assets/font.ttf', 10))
    canvas1.create_window(200, 100, window=label2)

    entry1 = tk.Entry(root) 
    canvas1.create_window(200, 140, window=entry1)
    
    def get_username():
        global username # je dois mettre ça comme ça car sinon ça ne fonction pas
        username = entry1.get()
        root.destroy()
        
    button1 = tk.Button(text='valider', command=get_username, bg='brown', fg='white', font=('assets/font.ttf', 9, 'bold'))
    canvas1.create_window(200, 180, window=button1)
    
    root.mainloop()

    score = 0

    failedShoots = [] #pour mettre les tirs ratés
    successfulShoots = [] #tirs réussis

    columns = ["0","1","2","3","4","5","6","7","8","9"] # colonnes
    rows = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9} # donne l'index de la lettre essentiel pour la suite
        
    buttons = {} # dictionnaire avec tous les boutons
    grid = [] # pour la grille

    y = 90 #pour les lignes des boutons sachant que ma fenetre = 720 de large et les 10 boutons prennent 600 de large (60px par bouton) je ne sais comment expliquer mais (720 -600) / 2 = 60 sauf qu'avec 90 ça à l'air un peu près centré
        
    #création des boutons
    for row in rows:
        x = 340
        gridRow = []
        for column in columns:
            buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color="#d7fcd4", hovering_color="White")
            x += 60
            gridRow.append({row+column : 0})
        grid.append(gridRow)
        y += 60
    
    """
        Les bâtiments ne doivent jamais se toucher

        Voici la liste des bâtiments disponibles pour chaque joueur :
        -1 porte-avions : 5 cases (affiche 5)
        -1 croiseur : 4 cases (affiche 4)
        -2 contre-torpilleurs : 3 cases (affiche 3 et 6)
        -1 sous-marin : 2 cases (affiche 2)
    """

    ships = {2 : ["E0", "F0"], 3 : ["C2", "C3", "C4"], "3" : ["B7", "C7", "D7"], 4 : ["E3", "E4", "E5", "E6"], 5 : ["G3", "G4", "G5", "G6", "G7"]} # dictionnaire contenant la localisation des bateaux
        
    for ship in ships:
        for cases in ships[ship]:
            gridCase = [*cases]
            grid[rows[gridCase[0]]][int(gridCase[1])][cases] = ship
    
    numbShips = 0
    
    for i in ships.values():
        numbShips += len(i)
    
    playing = True

    while playing:
        screen.fill((0,0,0))
        screen.blit(bgGame, (0,0))

        #pour avoir la position de la souris
        game_mouse_pos = pygame.mouse.get_pos()
        
        #pour changer la couleur du bouton quand on passe dessus
        for button in buttons:
            buttons[button].changeColor(game_mouse_pos)
            buttons[button].update(screen)
        
        #pour les events bouton et quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameMusic.stop()
                pygame.quit()
                sys.exit()
            
                #pour check si un des 100 boutons est pressé
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if buttons[button].checkForInput(game_mouse_pos):
                        Gridcase = [*button] # sépare "A0" pour après qu'on puisse utiliser les valeur pour chercher dans la grille 
                        #pour voir si il y a un bateau sur la case ou non
                        if int(grid[rows[Gridcase[0]]][int(Gridcase[1])][button]) >= 2: # vérifie si il y a un bateau sur la case
                            if button in ships[grid[rows[Gridcase[0]]][int(Gridcase[1])][button]]: # verifie si il y a bel et bien le bateau
                                if button in successfulShoots: #vérifie si la case à déjà été torpillée
                                    messagebox.showwarning("torpille", "ATTENTION VOUS AVEZ DEJA TORPILLE ICI") # mettre un message si déjà torpilée autre que dans la console
                                
                                else:
                                    successfulShoots.append(button)
                                    score += 15 # ajoute 15 au score car on a deviné qu'il y avait un bateau
                                    explosion.play() # joue le son de l'explosion
                                    buttons[button].changeImage(image=pygame.image.load("assets/images/explosion.png"), screen=screen) # change l'image en explosion car il y a un bateau qui a été touché par la torpille
                        else:
                            if button in failedShoots:
                                messagebox.showwarning("torpille", "ATTENTION VOUS AVEZ DEJA TORPILLE ICI")
                            else:
                                failedShoots.append(button) #ajouts des cases où le tir est raté
                                plop.play() # joue le son d'un objet tombant dans l'eau comme la torpille
                                buttons[button].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)
                                score -= 3 # enlève 3 de score si la case est vide
                                #afficher tirs ratés
                        

                #pour quitter avec echap
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameMusic.stop()
                    pygame.quit()
                    sys.exit()

            #pour actualiser l'affichage
        pygame.display.flip()
        clock.tick(60) #nombre d'image par seconde

        if len(successfulShoots) == numbShips:
            with open("score.json", "ab+") as ab:
                ab.close()
                f = open('score.json','r+')
                f.readline()
                if os.stat("score.json").st_size == 0:
                    f.write("{}")
                    f.close()
                else:
                    pass
            #pour ouvrir le fichier pour ajouter le score
            with open("score.json", 'r') as f:
                scores = json.load(f)
            add_score(scores, user=username, score=score)
            #pour ajouter réellement le score dans le fichier de sauvegarde
            with open('score.json', 'w') as f:
                json.dump(scores, f)

            main_menu()

def ordi():
    menuMusic.stop()
    positioningMusic.play()
    
    screen.fill((0,0,0))
    screen.blit(bgPos, (0,0))

    columns = ["0","1","2","3","4","5","6","7","8","9"] # colonnes
    rows = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9}
    
    global userbutton
    global userGrid
    userButtons = {}
    userGrid = []

    y = 90 #pour les lignes des boutons sachant que ma fenetre = 720 de large et les 10 boutons prennent 600 de large (60px par bouton) je ne sais comment expliquer mais (720 -600) / 2 = 60 sauf qu'avec 90 ça à l'air un peu près centré
        
    #création des boutons
    for row in rows:
        x = 340
        gridRow = []
        for column in columns:
            userButtons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color="#d7fcd4", hovering_color="White")
            x += 60
            gridRow.append({row+column : 0})
        userGrid.append(gridRow)
        y += 60
    
    userShips = []

    while len(userShips) <= 17:

        ordi1_mouse_pos = pygame.mouse.get_pos()
        
        for userbutton in userButtons:
            userButtons[userbutton].changeColor(ordi1_mouse_pos)   
            userButtons[userbutton].update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menuMusic.stop()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in userButtons:
                    if userButtons[button].checkForInput(ordi1_mouse_pos):
                        if button in userShips:
                            print("coucou")
                        else:
                            userShips.append(button)
                            userButtons[button].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)
                
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameMusic.stop()
                    pygame.quit()
                    sys.exit()

                #pour actualiser l'affichage
            pygame.display.flip()
            clock.tick(60) #nombre d'image par seconde
    
    positioningMusic.stop()
    gameMusic.play()

    screen.fill((0,0,0))
    screen.blit(bgPlay, (0,0))

    columns = ["0","1","2","3","4","5","6","7","8","9"] # colonnes
    rows = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9}
    
    failedUserShoots = [] #pour mettre les tirs ratés du joueur
    successfulUserShoots = [] #tirs réussis du joueur

    FailedOrdiShoots = []
    successfulOrdiShoots = []
        
    buttons = {} # dictionnaire avec tous les boutons
    grid = [] # pour la grille

    y = 90 #pour les lignes des boutons sachant que ma fenetre = 720 de large et les 10 boutons prennent 600 de large (60px par bouton) je ne sais comment expliquer mais (720 -600) / 2 = 60 sauf qu'avec 90 ça à l'air un peu près centré
        
    #création des boutons
    for row in rows:
        x = 340
        gridRow = []
        for column in columns:
            buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color="#d7fcd4", hovering_color="White")
            x += 60
            gridRow.append({row+column : 0})
        grid.append(gridRow)
        y += 60

    while True:

        ordi2_mouse_pos = pygame.mouse.get_pos()

        for button in buttons:
            buttons[button].changeColor(ordi2_mouse_pos)
            buttons[button].update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameMusic.stop()
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    pass
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameMusic.stop()
                    pygame.quit()
                    sys.exit()

            #pour actualiser l'affichage
            pygame.display.flip()
            clock.tick(60) #nombre d'image par seconde


def play_menu():
    while True:
        screen.fill((0,0,0))
        screen.blit(bgPlay, (0,0))

        #pour avoir la position de la souris
        play_mouse_pos = pygame.mouse.get_pos()

        playSolo = Button(image=pygame.image.load("assets/images/Solo Rect.png"), pos=(640,150), text_input="SOLO", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        playOrdi = Button(image=pygame.image.load("assets/images/Solo Rect.png"), pos=(640,275), text_input="VS ORDI", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        playLocal = Button(image=pygame.image.load("assets/images/Solo Rect.png"), pos=(640,400), text_input="VS LOCAL", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        playBack = Button(image=pygame.image.load("assets/images/Solo Rect.png"), pos=(640,525), text_input="BACK", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        #pour changer la couleur du bouton quand on passe dessus
        for button in [playSolo, playOrdi, playLocal, playBack]:
            button.changeColor(play_mouse_pos)
            button.update(screen)
        # 
        #pour les events bouton et quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if playBack.checkForInput(play_mouse_pos):
                    main_menu()
                
                elif playSolo.checkForInput(play_mouse_pos):
                    solo()

                elif playOrdi.checkForInput(play_mouse_pos):
                    ordi()
            
            #pour actualiser l'affichage
            pygame.display.flip()
            clock.tick(60) #nombre d'image par seconde

def option_menu():
    
    menuMusic.stop()
    positioningMusic.play()
    

    master = tk.Tk()
    
    canvas10 = tk.Canvas(master, width=400, height=300, relief='raised')
    canvas10.pack()

    label10 = tk.Label(master, text='volume :')
    label10.config(font=('assets/font.ttf', 10))
    canvas10.create_window(200, 100, window=label10)

    w = tk.Scale(master, from_=0, to=100, tickinterval=50, orient="horizontal")
    canvas10.create_window(300, 150, window=w)
    w.set(50)
    
    def volume_value():
        global volume
        volume = float(w.get() /100)
        menuMusic.set_volume(volume)
        gameMusic.set_volume(volume)
        positioningMusic.set_volume(volume)
        positioningMusic.stop()
        master.destroy()
        main_menu()

    button10 = tk.Button(text="Appliquer", command=volume_value).pack()
    canvas10.create_window(200, 180, window=button10)

    master.mainloop()

def main_menu():
    
    menuMusic.play()
    while True:
        screen.blit(bgMenu, (0,0))

        #pour avoir la position de la souris
        menu_mouse_pos = pygame.mouse.get_pos()

        playButton = Button(image=pygame.image.load("assets/images/Play Rect.png"), pos=(640,250), text_input="JOUER", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        optButton = Button(image=pygame.image.load("assets/images/Option Rect.png"), pos=(640, 400), text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        quitButton = Button(image=pygame.image.load("assets/images/Quit Rect.png"), pos=(640, 550), text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        #pour changer la couleur du bouton quand on passe dessus
        for button in [playButton, quitButton, optButton]:
            button.changeColor(menu_mouse_pos)
            button.update(screen)

        #pour les events bouton et quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menuMusic.stop()
                pygame.quit()
                sys.exit()
            #pour checker si un bouton est cliqué
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #pour quitter
                if quitButton.checkForInput(menu_mouse_pos):
                    menuMusic.stop()
                    pygame.quit()
                    sys.exit()
                
                #pour aller sur le "menu" de sélection du mode de jeu
                if playButton.checkForInput(menu_mouse_pos):
                    play_menu()
                
                #pour aller dans les paramètres du jeu
                if optButton.checkForInput(menu_mouse_pos):
                    option_menu()
                
            #pour quitter avec echap
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    menuMusic.stop()
                    pygame.quit()
                    sys.exit()

            #pour actualiser l'affichage
            pygame.display.flip()
            clock.tick(60) #nombre d'image par seconde

main_menu()