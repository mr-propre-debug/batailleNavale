#import des modules nécessaires pour faire fonctionner le jeu
import pygame, sys
from pygame.locals import *

from button import Button #module qui est dans le zip que j'ai trouvé pour faire des boutons sur pygame

import tkinter as tk #servira (pour l'instant) à demander le(s) pseudo(s)
from tkinter import messagebox # sert à afficher des boite d'alerte mais ceci rends très instable le jeu

import json

import os

import random

from time import sleep

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
    
    menuMusic.stop()
    gameMusic.play()

    pygame.display.set_caption("solo mode")

    score = 0

    failedShoots = [] #pour mettre les tirs ratés
    successfulShoots = [] #tirs réussis

    columns = ["0","1","2","3","4","5","6","7","8","9"] # colonnes
    rows = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9} # donne l'index de la lettre essentiel pour la suite

    buttons = {} # dictionnaire avec tous les boutons
    grid = [] # pour la grille
    gridForPosBoat = []

    y = 90 #pour les lignes des boutons sachant que ma fenetre = 720 de large et les 10 boutons prennent 600 de large (60px par bouton) je ne sais comment expliquer mais (720 -600) / 2 = 60 sauf qu'avec 90 ça à l'air un peu près centré

    #création des boutons
    for row in rows:
        x = 340
        gridRow = []
        gridRowSpé = []
        for column in columns:
            buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color=(215, 252, 212), hovering_color=(255, 255, 255))
            x += 60
            gridRow.append({row+column : 0})
            gridRowSpé.append({row+column : 999})
        gridForPosBoat.append(gridRowSpé)
        grid.append(gridRow)
        y += 60

    """
        pour générer une grille randint et positionner la 1ère et vérifier si pas en bout de grille

        Les bâtiments ne doivent jamais se toucher
    """

    ships = {2 : [], 3 : [], 6 : [], 4 : [], 5 : []} # liste contenant la localisation des bateaux
    shipSize = {"2": 2, "3" : 3, "6" : 3,  "4" : 4, "5" : 5} #pour la taille des bateau vu qu'il y a 2 fois un bateau de 3 cases
    sunkShips = {2 : [], 3 : [], 6 : [], 4 : [], 5 : []} #pour les bateaux coulés

    for bat in ships: #pour chaque bateau
        shipRow = random.sample(gridForPosBoat, 1) # séléctionne une ligne au hasard
        shipCase = random.sample(shipRow[0], 1) #selectionne une case au hasard
        boatCase1st = list(shipCase[0]) # pour prendre que la key du dict de la case
        boatPlace1st = [*boatCase1st[0]] # sépare la case en liste

        remainingSpace = 0 #sert à voir si l'espace est suffisant
        remainingSpace += int(boatPlace1st[1]) #colonne du bateau
        remainingSpace += shipSize[str(bat)] # taille du bateau
        remainingSpace = int(remainingSpace)
        print(remainingSpace)
        
        if int(remainingSpace) < int(8):
            is_not_boat_in_ships = True

            for b in ships:
                if boatCase1st in ships[b]:
                    is_not_boat_in_ships = False
            
            if is_not_boat_in_ships == True:
                caseAvant = int(boatPlace1st[1])
                if caseAvant == 0:
                    gridForPosBoat[rows[boatPlace1st[0]]].remove({str(boatCase1st[0]) : 999}) #enlève la case de la grille pour la position des bateaux
                    ships[bat].append(str(boatCase1st[0]))
                    for i in range(shipSize[str(bat)]-1): # pour placer le bateau
                        boatCase = list(shipCase[0]) # pour prendre que la key du dict de la case
                        boatPlace = [*boatCase[0]] # sépare la case en liste
                        columnBoat = boatPlace[1] # prendre le chiffre de la case
                        columnBoat = int(columnBoat)
                        columnBoat += i # pour mettre le bateau
                        columnBoat += 1
                        boatPos = boatPlace[0] + str(columnBoat) # pour ajouter les cases où est le bateau
                        print(gridForPosBoat[rows[boatPlace[0]]])
                        print(boatPos)
                        ships[bat].append(boatPos)
                        gridForPosBoat[rows[boatPlace[0]]].remove({boatPos : 999})
                else:
                    caseAvant -= 1
                    removedCase = boatPlace1st[0] + str(caseAvant)
                    gridForPosBoat[rows[boatPlace1st[0]]].remove({str(removedCase) : 999}) #enlève la case de la grille pour la position des bateaux
                    ships[bat].append(str(boatCase1st[0]))
                    for i in range(shipSize[str(bat)] - 1):
                        boatCase = list(shipCase[0]) # pour prendre que la key du dict de la case
                        boatPlace = [*boatCase[0]] # sépare la case en liste
                        columnBoat = boatPlace[1] # prendre le chiffre de la case
                        columnBoat = int(columnBoat)
                        columnBoat += i # pour mettre le bateau
                        if columnBoat == 9:
                            break
                        columnBoat += 1
                        boatPos = boatPlace[0] + str(columnBoat) # pour ajouter les cases où est le bateau
                        print(gridForPosBoat[rows[boatPlace[0]]])
                        print(boatPos)
                        ships[bat].append(boatPos)
                        gridForPosBoat[rows[boatPlace[0]]].remove({boatPos : 999})
        
        else:
            shipRow = random.sample(gridForPosBoat, 1) # séléctionne une ligne au hasard
            shipCase = random.sample(shipRow[0], 1)
            boatCase2nd = list(shipCase[0]) # pour prendre que la key du dict de la case
            boatPlace2nd = [*boatCase2nd[0]] # sépare la case en liste
            remainingSpace = 0 #sert à voir si l'espace est suffisant
            remainingSpace += int(boatPlace2nd[1])
            remainingSpace += shipSize[str(bat)]
            remainingSpace = int(remainingSpace)
            
            is_not_boat_in_ships2 = True

            for b in ships:
                if boatCase1st in ships[b]:
                    is_not_boat_in_ships2 = False

            while remainingSpace > 8 and is_not_boat_in_ships2 == False:
                shipRow = random.sample(gridForPosBoat, 1) # séléctionne une ligne au hasard
                shipCase = random.sample(shipRow[0], 1)
                boatCase2nd = list(shipCase[0]) # pour prendre que la key du dict de la case
                boatPlace2nd = [*boatCase2nd[0]] # sépare la case en liste
                remainingSpace = 0 #sert à voir si l'espace est suffisant
                remainingSpace += int(boatPlace2nd[1])
                remainingSpace += shipSize[str(bat)]
                remainingSpace = int(remainingSpace)
            
            
            print(boatCase2nd[0], "else 207")
            caseAvant = int(boatPlace2nd[1])
            if caseAvant == 0:
                gridForPosBoat[rows[boatPlace2nd[0]]].remove({str(boatCase2nd[0]) : 999}) #enlève la case de la grille pour la position des bateaux
                ships[bat].append(str(boatCase2nd[0]))
                
                for j in range(shipSize[str(bat)]-1): # pour placer le bateau
                    boatCase = list(shipCase[0]) # pour prendre que la key du dict de la case
                    boatPlace = [*boatCase[0]] # sépare la case en liste
                    columnBoat = boatPlace[1] # prendre le chiffre de la case
                    columnBoat = int(columnBoat)
                    columnBoat += j # pour mettre le bateau
                    if columnBoat == 9:
                        break
                    columnBoat += 1
                    boatPos = boatPlace[0] + str(columnBoat) # pour ajouter les cases où est le bateau
                    print(boatPos, "else 223")
                    print(gridForPosBoat[rows[boatPlace[0]]], "else 224")
                    ships[bat].append(boatPos)
                    gridForPosBoat[rows[boatPlace[0]]].remove({boatPos : 999})
            else:
                caseAvant -= 1
                removedCase = boatPlace2nd[0] + str(caseAvant)
                print(removedCase, "else 230")
                print(gridForPosBoat[rows[boatPlace2nd[0]]], "else 231")
                gridForPosBoat[rows[boatPlace2nd[0]]].remove({str(removedCase) : 999})
                
                gridForPosBoat[rows[boatPlace2nd[0]]].remove({str(boatCase2nd[0]) : 999}) #enlève la case de la grille pour la position des bateaux
                ships[bat].append(str(boatCase2nd[0]))
                
                for j in range(shipSize[str(bat)]-1): # pour placer le bateau
                    boatCase = list(shipCase[0]) # pour prendre que la key du dict de la case
                    boatPlace = [*boatCase[0]] # sépare la case en liste
                    columnBoat = boatPlace[1] # prendre le chiffre de la case
                    columnBoat = int(columnBoat)
                    columnBoat += j # pour mettre le bateau
                    if columnBoat == 9:
                        break
                    columnBoat += 1
                    boatPos = boatPlace[0] + str(columnBoat) # pour ajouter les cases où est le bateau
                    print(boatPos, "else 247")
                    print(gridForPosBoat[rows[boatPlace[0]]], "else 248")
                    ships[bat].append(boatPos)
                    gridForPosBoat[rows[boatPlace[0]]].remove({boatPos : 999})
            
    print(ships)

    # ships = {2 : ["E0", "F0"], 3 : ["C2", "C3", "C4"], 6 : ["B7", "C7", "D7"], 4 : ["E3", "E4", "E5", "E6"], 5 : ["G3", "G4", "G5", "G6", "G7"]} # lsite contenant la localisation des bateaux

    for ship in ships:
        for cases in ships[ship]:
            gridCase = [*cases]
            grid[rows[gridCase[0]]][int(gridCase[1])][cases] = ship
    
    numbShips = 0
    
    for i in ships.values():
        numbShips += len(i)
    
    while True:
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
                        if grid[rows[Gridcase[0]]][int(Gridcase[1])][button] >= 2: # vérifie si il y a un bateau sur la case
                            if button in ships[grid[rows[Gridcase[0]]][int(Gridcase[1])][button]]: # verifie si il y a bel et bien le bateau
                                if button in successfulShoots: #vérifie si la case à déjà été torpillée
                                    print("case déja devinée") # mettre un message si déjà torpilée autre que dans la console
        
                                else:
                                    successfulShoots.append(button)
                                    ships[grid[rows[Gridcase[0]]][int(Gridcase[1])][button]].remove(button)
                                    sunkShips[grid[rows[Gridcase[0]]][int(Gridcase[1])][button]].append(button)
                                    score += 15 # ajoute 15 au score car on a deviné qu'il y avait un bateau
                                    explosion.play() # joue le son de l'explosion
                                    buttons[button].changeImage(image=pygame.image.load("assets/images/explosion.png"), screen=screen) # change l'image en explosion car il y a un bateau qui a été touché par la torpille
                                    if ships[grid[rows[Gridcase[0]]][int(Gridcase[1])][button]] == []:
                                        ships[grid[rows[Gridcase[0]]][int(Gridcase[1])][button]] = "coulé"
                                        for but in sunkShips[grid[rows[Gridcase[0]]][int(Gridcase[1])][button]]:
                                            buttons[but].changeImage(image=pygame.image.load("assets/images/wood.png"), screen=screen)                
                        else:
                            if button in failedShoots:
                                print("case déja devinée")
                            else:
                                failedShoots.append(button) #ajouts des cases où le tir est raté
                                plop.play() # joue le son d'un objet tombant dans l'eau comme la torpille
                                buttons[button].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)
                                score -= 3 # enlève 3 de score si la case est vide

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

            gameMusic.stop()
            main_menu()

def ordi():
    menuMusic.stop()
    positioningMusic.play()

    pygame.display.set_caption("placement des bateaux")

    screen.fill((0,0,0))
    screen.blit(bgPos, (0,0))

    columns = ["0","1","2","3","4","5","6","7","8","9"] # colonnes
    rows = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9}

    userButtons = {}
    userGrid = []

    y = 90 #pour les lignes des boutons sachant que ma fenetre = 720 de large et les 10 boutons prennent 600 de large (60px par bouton) je ne sais comment expliquer mais (720 -600) / 2 = 60 sauf qu'avec 90 ça à l'air un peu près centré

    #création des boutons
    for row in rows:
        x = 340
        for column in columns:
            userButtons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color=(215, 252, 212), hovering_color=(255, 255, 255))
            x += 60
            userGrid.append(row+column)
        y += 60

    userShips = []

    while len(userShips) < 17:

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
                            print("BATEAU DEJA PLACE ICI")
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

    comptShips = ["E0", "F0", "C2", "C3", "C4", "B7", "C7", "D7", "E3", "E4", "E5", "E6", "G3", "G4", "G5", "G6", "G7"] # lsite contenant la localisation des bateaux

    failedUserShoots = [] #pour mettre les tirs ratés du joueur
    successfulUserShoots = [] #tirs réussis du joueur

    FailedOrdiShoots = []
    successfulOrdiShoots = []

    buttons = {} # dictionnaire avec tous les boutons
    grid = [] # pour la grille

    y = 90 #pour les lignes des boutons sachant que ma fenetre = 720 de large et les 10 boutons prennent 600 de large (60px par bouton) je ne sais comment expliquer mais (720 -600) / 2 = 60 sauf qu'avec 90 ça à l'air un peu près centré

    ships = {2 : [], 3 : [], 6 : [], 4 : [], 5 : []} # liste contenant la localisation des bateaux
    shipSize = {"2": 2, "3" : 3, "6" : 3,  "4" : 4, "5" : 5} #pour la taille des bateau vu qu'il y a 2 fois un bateau de 3 cases
    sunkShips = {2 : [], 3 : [], 6 : [], 4 : [], 5 : []} #pour les bateaux coulés
    gridForPosBoat = []


    for row in rows:
        x = 340
        gridRow = []
        gridRowSpé = []
        for column in columns:
            buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color=(215, 252, 212), hovering_color=(255, 255, 255))
            x += 60
            gridRow.append({row+column : 0})
            gridRowSpé.append({row+column : 999})
        gridForPosBoat.append(gridRowSpé)
        grid.append(gridRow)
        y += 60


    for bat in ships: #pour chaque bateau
        shipRow = random.sample(gridForPosBoat, 1) # séléctionne une ligne au hasard
        shipCase = random.sample(shipRow[0], 1) #selectionne une case au hasard
        boatCase1st = list(shipCase[0]) # pour prendre que la key du dict de la case
        boatPlace1st = [*boatCase1st[0]] # sépare la case en liste

        remainingSpace = 0 #sert à voir si l'espace est suffisant
        remainingSpace += int(boatPlace1st[1]) #colonne du bateau
        remainingSpace += shipSize[str(bat)] # taille du bateau
        remainingSpace = int(remainingSpace)
        print(remainingSpace)
        
        if int(remainingSpace) < int(8):
            is_not_boat_in_ships = True

            for b in ships:
                if boatCase1st in ships[b]:
                    is_not_boat_in_ships = False
            
            if is_not_boat_in_ships == True:
                caseAvant = int(boatPlace1st[1])
                if caseAvant == 0:
                    gridForPosBoat[rows[boatPlace1st[0]]].remove({str(boatCase1st[0]) : 999}) #enlève la case de la grille pour la position des bateaux
                    ships[bat].append(str(boatCase1st[0]))
                    for i in range(shipSize[str(bat)]-1): # pour placer le bateau
                        boatCase = list(shipCase[0]) # pour prendre que la key du dict de la case
                        boatPlace = [*boatCase[0]] # sépare la case en liste
                        columnBoat = boatPlace[1] # prendre le chiffre de la case
                        columnBoat = int(columnBoat)
                        columnBoat += i # pour mettre le bateau
                        columnBoat += 1
                        boatPos = boatPlace[0] + str(columnBoat) # pour ajouter les cases où est le bateau
                        print(gridForPosBoat[rows[boatPlace[0]]])
                        print(boatPos)
                        ships[bat].append(boatPos)
                        gridForPosBoat[rows[boatPlace[0]]].remove({boatPos : 999})
                else:
                    caseAvant -= 1
                    removedCase = boatPlace1st[0] + str(caseAvant)
                    gridForPosBoat[rows[boatPlace1st[0]]].remove({str(removedCase) : 999}) #enlève la case de la grille pour la position des bateaux
                    ships[bat].append(str(boatCase1st[0]))
                    for i in range(shipSize[str(bat)] - 1):
                        boatCase = list(shipCase[0]) # pour prendre que la key du dict de la case
                        boatPlace = [*boatCase[0]] # sépare la case en liste
                        columnBoat = boatPlace[1] # prendre le chiffre de la case
                        columnBoat = int(columnBoat)
                        columnBoat += i # pour mettre le bateau
                        if columnBoat == 9:
                            break
                        columnBoat += 1
                        boatPos = boatPlace[0] + str(columnBoat) # pour ajouter les cases où est le bateau
                        print(gridForPosBoat[rows[boatPlace[0]]])
                        print(boatPos)
                        ships[bat].append(boatPos)
                        gridForPosBoat[rows[boatPlace[0]]].remove({boatPos : 999})
        
        else:
            shipRow = random.sample(gridForPosBoat, 1) # séléctionne une ligne au hasard
            shipCase = random.sample(shipRow[0], 1)
            boatCase2nd = list(shipCase[0]) # pour prendre que la key du dict de la case
            boatPlace2nd = [*boatCase2nd[0]] # sépare la case en liste
            remainingSpace = 0 #sert à voir si l'espace est suffisant
            remainingSpace += int(boatPlace2nd[1])
            remainingSpace += shipSize[str(bat)]
            remainingSpace = int(remainingSpace)
            
            is_not_boat_in_ships2 = True

            for b in ships:
                if boatCase1st in ships[b]:
                    is_not_boat_in_ships2 = False

            while remainingSpace > 8 and is_not_boat_in_ships2 == False:
                shipRow = random.sample(gridForPosBoat, 1) # séléctionne une ligne au hasard
                shipCase = random.sample(shipRow[0], 1)
                boatCase2nd = list(shipCase[0]) # pour prendre que la key du dict de la case
                boatPlace2nd = [*boatCase2nd[0]] # sépare la case en liste
                remainingSpace = 0 #sert à voir si l'espace est suffisant
                remainingSpace += int(boatPlace2nd[1])
                remainingSpace += shipSize[str(bat)]
                remainingSpace = int(remainingSpace)
            
            
            print(boatCase2nd[0], "else 207")
            caseAvant = int(boatPlace2nd[1])
            if caseAvant == 0:
                gridForPosBoat[rows[boatPlace2nd[0]]].remove({str(boatCase2nd[0]) : 999}) #enlève la case de la grille pour la position des bateaux
                ships[bat].append(str(boatCase2nd[0]))
                
                for j in range(shipSize[str(bat)]-1): # pour placer le bateau
                    boatCase = list(shipCase[0]) # pour prendre que la key du dict de la case
                    boatPlace = [*boatCase[0]] # sépare la case en liste
                    columnBoat = boatPlace[1] # prendre le chiffre de la case
                    columnBoat = int(columnBoat)
                    columnBoat += j # pour mettre le bateau
                    if columnBoat == 9:
                        break
                    columnBoat += 1
                    boatPos = boatPlace[0] + str(columnBoat) # pour ajouter les cases où est le bateau
                    print(boatPos, "else 223")
                    print(gridForPosBoat[rows[boatPlace[0]]], "else 224")
                    ships[bat].append(boatPos)
                    gridForPosBoat[rows[boatPlace[0]]].remove({boatPos : 999})
            else:
                caseAvant -= 1
                removedCase = boatPlace2nd[0] + str(caseAvant)
                print(removedCase, "else 230")
                print(gridForPosBoat[rows[boatPlace2nd[0]]], "else 231")
                gridForPosBoat[rows[boatPlace2nd[0]]].remove({str(removedCase) : 999})
                
                gridForPosBoat[rows[boatPlace2nd[0]]].remove({str(boatCase2nd[0]) : 999}) #enlève la case de la grille pour la position des bateaux
                ships[bat].append(str(boatCase2nd[0]))
                
                for j in range(shipSize[str(bat)]-1): # pour placer le bateau
                    boatCase = list(shipCase[0]) # pour prendre que la key du dict de la case
                    boatPlace = [*boatCase[0]] # sépare la case en liste
                    columnBoat = boatPlace[1] # prendre le chiffre de la case
                    columnBoat = int(columnBoat)
                    columnBoat += j # pour mettre le bateau
                    if columnBoat == 9:
                        break
                    columnBoat += 1
                    boatPos = boatPlace[0] + str(columnBoat) # pour ajouter les cases où est le bateau
                    print(boatPos, "else 247")
                    print(gridForPosBoat[rows[boatPlace[0]]], "else 248")
                    ships[bat].append(boatPos)
                    gridForPosBoat[rows[boatPlace[0]]].remove({boatPos : 999})
            
    print(ships)

    # ships = {2 : ["E0", "F0"], 3 : ["C2", "C3", "C4"], 6 : ["B7", "C7", "D7"], 4 : ["E3", "E4", "E5", "E6"], 5 : ["G3", "G4", "G5", "G6", "G7"]} # lsite contenant la localisation des bateaux

    for ship in ships:
        for cases in ships[ship]:
            gridCase = [*cases]
            grid[rows[gridCase[0]]][int(gridCase[1])][cases] = ship
    
    numbShips = 0
    
    for i in ships.values():
        numbShips += len(i)


    #création des boutons
    for row in rows:
        x = 340
        for column in columns:
            buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color=(215, 252, 212), hovering_color=(255, 255, 255))
            x += 60
            grid.append(row+column)
        y += 60

    def ordiTurn():
        sleep(1.0)
        shoot = random.choice(userGrid)

        if shoot in userShips:
            userGrid.remove(shoot)
            explosion.play()
            sleep(2.0)
            print("Votre bateau en", shoot, "a été touché")
            ordiTurn()
        else:
            userGrid.remove(shoot)
            FailedOrdiShoots.append(shoot)
            plop.play()
            print("Une torpille a été envoyée en", shoot, "mais hereusement rien a été touché")

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
                    if buttons[button].checkForInput(ordi2_mouse_pos):
                        if button in comptShips:
                            if button in successfulUserShoots:
                                print("TU AS DEJA TORPILLE ICI")
                            else:
                                successfulUserShoots.append(button)
                                explosion.play()
                                buttons[button].changeImage(image=pygame.image.load("assets/images/explosion.png"), screen=screen) # change l'image en explosion car il y a un bateau qui a été touché par la torpille
                        else:
                            if button in failedUserShoots:
                                print("TU AS DEJA TORPILLE ICI")
                            else:
                                failedUserShoots.append(button)
                                buttons[button].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)
                                plop.play()
                                ordiTurn()

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameMusic.stop()
                    pygame.quit()
                    sys.exit()

            #pour actualiser l'affichage
            pygame.display.flip()
            clock.tick(60) #nombre d'image par seconde

        if len(successfulOrdiShoots) == 17 or len(successfulUserShoots) == 17:
            if len(successfulOrdiShoots) == 17:
                print("Faut vraiment le faire car il tirait aléatoirement !")
                gameMusic.stop()
                main_menu()
            elif len(successfulUserShoots) == 17:
                print("Vous avez gagné contre l'ordi qui tirait aléatoirement")
                gameMusic.stop()
                main_menu()
            else:
                print("comment en êtes-vous arrivé là ?")
                gameMusic.stop()
                main_menu()

def multiLocal():
    menuMusic.stop()
    positioningMusic.play()
    
    screen.fill((0,0,0))
    screen.blit(bgPos, (0,0))

    columns = ["0","1","2","3","4","5","6","7","8","9"] # colonnes
    rows = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9}

    failedPlayer1Shoots = [] #pour mettre les tirs ratés du joueur
    successfulPlayer1Shoots = [] #tirs réussis du joueur

    failedPlayer2Shoots = []
    successfulPlayer2Shoots = []

    player1Buttons = {}
    player1Grid = []

    y = 90 #pour les lignes des boutons sachant que ma fenetre = 720 de large et les 10 boutons prennent 600 de large (60px par bouton) je ne sais comment expliquer mais (720 -600) / 2 = 60 sauf qu'avec 90 ça à l'air un peu près centré
        
    #création des boutons
    for row in rows:
        x = 340
        for column in columns:
            player1Buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color="#d7fcd4", hovering_color="White")
            x += 60
            player1Grid.append(row+column)
        y += 60
    
    player1Ships = []

    while len(player1Ships) < 17:

        player1_mouse_pos = pygame.mouse.get_pos()
        
        for userbutton in player1Buttons:
            player1Buttons[userbutton].changeColor(player1_mouse_pos)   
            player1Buttons[userbutton].update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menuMusic.stop()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in player1Buttons:
                    if player1Buttons[button].checkForInput(player1_mouse_pos):
                        if button in player1Ships:
                            print("BATEAU DEJA PLACE ICI")
                        else:
                            player1Ships.append(button)
                            player1Buttons[button].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)
                
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameMusic.stop()
                    pygame.quit()
                    sys.exit()

                #pour actualiser l'affichage
            pygame.display.flip()
            clock.tick(60) #nombre d'image par seconde
    
    screen.fill((0,0,0))
    screen.blit(bgPos, (0,0))

    player2Buttons = {}
    player2Grid = []

    y = 90 #pour les lignes des boutons sachant que ma fenetre = 720 de large et les 10 boutons prennent 600 de large (60px par bouton) je ne sais comment expliquer mais (720 -600) / 2 = 60 sauf qu'avec 90 ça à l'air un peu près centré
        
    #création des boutons
    for row in rows:
        x = 340
        for column in columns:
            player2Buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color="#d7fcd4", hovering_color="White")
            x += 60
            player2Grid.append(row+column)
        y += 60
    
    player2Ships = []

    while len(player2Ships) < 17:

        player2_mouse_pos = pygame.mouse.get_pos()
        
        for userbutton in player2Buttons:
            player2Buttons[userbutton].changeColor(player2_mouse_pos)   
            player2Buttons[userbutton].update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menuMusic.stop()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in player2Buttons:
                    if player2Buttons[button].checkForInput(player2_mouse_pos):
                        if button in player2Ships:
                            print("BATEAU DEJA PLACE ICI")
                        else:
                            player2Ships.append(button)
                            player2Buttons[button].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)
                
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameMusic.stop()
                    pygame.quit()
                    sys.exit()

            #pour actualiser l'affichage
            pygame.display.flip()
            clock.tick(60) #nombre d'image par seconde
    
    screen.fill((0,0,0))
    screen.blit(bgGame, (0,0))

    positioningMusic.stop()
    gameMusic.play()

    player1Buttons = {}
    player2Buttons = {}

    y = 90

    for row in rows:
        x = 340
        for column in columns:
            player2Buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color="#d7fcd4", hovering_color="White")
            x += 60
        y += 60

    def player2turn():
        screen.fill((0,0,0))
        screen.blit(bgGame, (0,0))

        y = 90
        for row in rows:
            x = 340
            for column in columns:
                player1Buttons[row+column] = Button(image=pygame.image.load("assets/images/Game Square.png"), pos=(x,y), text_input=row+column, font=get_font(25), base_color="#d7fcd4", hovering_color="White")
                x += 60
            y += 60
        
        for explo in successfulPlayer2Shoots:
            player1Buttons[explo].changeImage(image=pygame.image.load("assets/images/explosion.png"), screen=screen)
        
        for plouf in failedPlayer2Shoots:
            player1Buttons[plouf].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)

        playing = True

        while playing:
            player2_mouse_pos = pygame.mouse.get_pos()

            for userbutton in player1Buttons:
                player1Buttons[userbutton].changeColor(player2_mouse_pos)   
                player1Buttons[userbutton].update(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameMusic.stop()
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in player1Buttons:
                        if player1Buttons[button].checkForInput(player2_mouse_pos):
                            if button in player1Ships:
                                if button in successfulPlayer2Shoots:
                                    print("Tu as déjà torpillé ici")
                                        
                                else:
                                    successfulPlayer2Shoots.append(button)
                                    explosion.play()
                                    player1Buttons[button].changeImage(image=pygame.image.load("assets/images/explosion.png"), screen=screen)
                                    if len(successfulPlayer2Shoots) == 17:
                                        print("Le joueur 2 a gagné !")

                            else:
                                if button in failedPlayer2Shoots:
                                    print("tu as déjà torpillé ici")
                                else:
                                    player1Buttons[button].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)
                                    failedPlayer2Shoots.append(button)
                                    plop.play()
                                    playing = False
                
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        gameMusic.stop()
                        pygame.quit()
                        sys.exit()

                #pour actualiser l'affichage
                pygame.display.flip()
                clock.tick(60) #nombre d'image par seconde

    while True:
        player1_mouse_pos = pygame.mouse.get_pos()
        
        for userbutton in player2Buttons:
            player2Buttons[userbutton].changeColor(player1_mouse_pos)   
            player2Buttons[userbutton].update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameMusic.stop()
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in player2Buttons:
                    if player2Buttons[button].checkForInput(player1_mouse_pos):
                        if button in player2Ships:
                            if button in successfulPlayer1Shoots:
                                print("Tu as déjà torpillé ici")

                            else:
                                successfulPlayer1Shoots.append(button)
                                explosion.play()
                                player2Buttons[button].changeImage(image=pygame.image.load("assets/images/explosion.png"), screen=screen)
                        else:
                            if button in failedPlayer1Shoots:
                                print("tu as déjà torpillé ici")
                            else:
                                failedPlayer1Shoots.append(button)
                                player2Buttons[button].changeImage(image=pygame.image.load("assets/images/rate.png"), screen=screen)
                                plop.play()
                                player2turn()
            
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

        playSolo = Button(image=pygame.image.load("assets/images/Solo Rect.png"), pos=(640,150), text_input="SOLO", font=get_font(75), base_color=(215, 252, 212), hovering_color=(255, 255, 255))

        playOrdi = Button(image=pygame.image.load("assets/images/Solo Rect.png"), pos=(640,275), text_input="VS ORDI", font=get_font(75), base_color=(215, 252, 212), hovering_color=(255, 255, 255))

        playLocal = Button(image=pygame.image.load("assets/images/Solo Rect.png"), pos=(640,400), text_input="VS LOCAL", font=get_font(75), base_color=(215, 252, 212), hovering_color=(255, 255, 255))

        playBack = Button(image=pygame.image.load("assets/images/Solo Rect.png"), pos=(640,525), text_input="BACK", font=get_font(75), base_color=(215, 252, 212), hovering_color=(255, 255, 255))

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

                elif playLocal.checkForInput(play_mouse_pos):
                    multiLocal()

            #pour actualiser l'affichage
            pygame.display.flip()
            clock.tick(60) #nombre d'image par seconde

def option_menu():

    menuMusic.stop()
    positioningMusic.play()

    sleep(2.0)

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
    screen.fill((0,0,0))
    while True:
        screen.blit(bgMenu, (0,0))

        #pour avoir la position de la souris
        menu_mouse_pos = pygame.mouse.get_pos()

        playButton = Button(image=pygame.image.load("assets/images/Play Rect.png"), pos=(640,250), text_input="JOUER", font=get_font(75), base_color=(215, 252, 212), hovering_color=(255, 255, 255))

        optButton = Button(image=pygame.image.load("assets/images/Option Rect.png"), pos=(640, 400), text_input="OPTIONS", font=get_font(75), base_color=(215, 252, 212), hovering_color=(255, 255, 255))

        quitButton = Button(image=pygame.image.load("assets/images/Quit Rect.png"), pos=(640, 550), text_input="QUIT", font=get_font(75), base_color=(215, 252, 212), hovering_color=(255, 255, 255))

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