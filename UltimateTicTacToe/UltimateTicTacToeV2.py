# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys
from _ast import While



    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'tictactoeBis'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 20 # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 500 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    #score = [0]*nbPlayers
    #fioles = {} # dictionnaire (x,y)->couleur pour les fioles
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    #goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    # et la zone de jeu pour le tic-tac-toe
    tictactoeStates = [(x,y) for x in range(3,16) for y in range(3,16)]
    
    realTicTacToeStates = []
    playedTicTacToeStates = []
    for x in range(4,15):
        line = []
        played = []
        for y in range(4,15):
            if (x,y) not in wallStates:
                if not ((x in [5,9,13] and y in [7,11]) or (x in [7,11] and y in [5,9,13])):
                    line.append((x,y))
                    played.append(-1)
        if line != []:
            realTicTacToeStates.append(line)
            playedTicTacToeStates.append(played)
    
    print(realTicTacToeStates)
    print(playedTicTacToeStates)
    #print ("Wall states:", wallStates)
    
    # les coordonnees des tiles dans la fiche
    tile_fiole_jaune = (19,1)
    tile_fiole_bleue = (20,1)
    
    # listes des objets fioles jaunes et bleues
    
    fiolesJaunes = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_jaune]
    fiolesBleues = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_bleue]
    all_fioles = (fiolesJaunes,fiolesBleues) 
    fiole_a_ramasser = (0,0) # servira à repérer la prochaine fiole à prendre
    
    # renvoie la couleur d'une fiole
    # potentiellement utile
    
    def couleur(o):
        if o.tileid==tile_fiole_jaune:
            return 'j'
        elif o.tileid==tile_fiole_bleue:
            return 'b'
    
    
    #-------------------------------
    # Placement aleatoire d'une fioles de couleur 
    #-------------------------------
    
    def put_next_fiole(j,t):
        o = all_fioles[j][t]
    
        # et on met cette fiole qqpart au hasard
    
        x = random.randint(1,19)
        y = random.randint(1,19)
    
        while (x,y) in tictactoeStates or (x,y) in wallStates: # ... mais pas sur un mur
            x = random.randint(1,19)
            y = random.randint(1,19)
        o.set_rowcol(x,y)
        # on ajoute cette fiole dans le dictionnaire
        #fioles[(x,y)]=couleur(o)
        
        game.layers['ramassable'].add(o)
        game.mainiteration()
        return (x,y)
        
        
    
    
    
    #-------------------------------
    # Boucle principale de déplacements, un joueur apres l'autre
    #-------------------------------
    
    posPlayers = initStates

    tour = 0
    j = 0 # le joueur 0 commence
    
    nextPlay = (-1,-1)
    
    #Un itération = un tour (j1+j2 ont joués)
    #Remplacer condition par test si jeu gagné
    while True :
        fiole_a_ramasser=put_next_fiole(j,tour)
        row,col = posPlayers[j]
        chemin = astar((row,col),fiole_a_ramasser,wallStates)
        
        #Bouger
        while True:
            next_row,next_col = chemin.pop(0)
            
            # and ((next_row,next_col) not in posPlayers)
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)
                #print ("pos :", j, next_row,next_col)
                game.mainiteration()
    
                col=next_col
                row=next_row
                posPlayers[j]=(row,col)
            
            if (row,col)==fiole_a_ramasser:
                o = players[j].ramasse(game.layers) # on la ramasse
                game.mainiteration()
                print ("Objet de couleur ", couleur(o), " trouvé par le joueur ", j)
                break
        
        #Cherche position où jouer
        n,m = jouer(j,realTicTacToeStates,playedTicTacToeStates,nextPlay)#+ wallStates?
        nextPlay = (n%3,m%3)
        posjeu = realTicTacToeStates[n][m]
        chemin = astar((row,col),posjeu,wallStates)
        
        #Bouger
        while True:
            next_row,next_col = chemin.pop(0)
            
            # and ((next_row,next_col) not in posPlayers)
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)
                #print ("pos :", j, next_row,next_col)
                game.mainiteration()
                
                col=next_col
                row=next_row
                posPlayers[j]=(row,col)
            
            
            if (row,col)==posjeu:
                #Poser fiole
                players[j].depose(game.layers)
                playedTicTacToeStates[n][m] = j
                game.mainiteration()
                break
        
        j = (j+1)%nbPlayers
        if j == 0:
            tour+=1
        
    pygame.quit()

#Nouvelles Fonctions
def manhattan(position,objectif):
    (x1,y1)=position
    (x2,y2)=objectif
    return abs(x1-x2)+abs(y1-y2)

def astar(depart,objectif,wallStates):
    closedSet = set()
    openSet = {depart}
    
    cameFrom = {}
    
    gScore = {}
    gScore[depart] = 0
    
    fScore = {}
    fScore[depart]=manhattan(depart, objectif)
    
    while openSet!={}:
        current = lowestNode(openSet,fScore)
        
        if current == objectif:
            return getChemin(cameFrom, current)
        
        openSet.remove(current)
        closedSet.add(current)
        
        frontiere = getChoix(current, wallStates)
        for voisin in frontiere:
            if voisin in closedSet:
                continue
            
            if voisin not in openSet:
                openSet.add(voisin)
            
            new_gScore = gScore[current] + 1
            if voisin in gScore:
                if new_gScore >= gScore[voisin]:
                    continue
            
            cameFrom[voisin] = current
            gScore[voisin] = new_gScore
            fScore[voisin] = gScore[voisin]+manhattan(voisin, objectif)
    
    return [];
        
def lowestNode(openSet,fScore):
    noeudMin = (-1,-1)
    for noeud in openSet:
        if noeudMin == (-1,-1):
            noeudMin = noeud
        else:
            if fScore[noeud]<fScore[noeudMin]:
                noeudMin = noeud
    return noeudMin

def getChemin(cameFrom, pos):
    chemin = [pos]
    print(pos)
    print(chemin)
    while pos in list(cameFrom.keys()):
        pos = cameFrom[pos]
        chemin.insert(0,pos)
        #print(chemin)
    return chemin

def getChoix(position,wallStates):
    choix = [(0,1),(0,-1),(1,0),(-1,0)]
    frontiere = []
    for one_choix in choix :
        if (position[0]+one_choix[0],position[1]+one_choix[1]) not in wallStates :
            #choix.pop(choix.index(one_choix))
            frontiere.append((position[0]+one_choix[0],position[1]+one_choix[1]))
    
    return frontiere

def jouer(j,tictactoeStates,playedTicTacToeStates, playIn = (-1,-1)):
    x,y = (-1,-1)
    
    while True:
        if playIn == (-1,-1):
            x = random.randint(0,len(tictactoeStates)-1)
            y = random.randint(0,len(tictactoeStates[0])-1)
        else:
            x = 3*playIn[0]+random.randint(0,2)
            y = 3*playIn[1]+random.randint(0,2)
        
        if playedTicTacToeStates[x][y]==-1:
            break
    
    return (x,y)


if __name__ == '__main__':
    main()
    


