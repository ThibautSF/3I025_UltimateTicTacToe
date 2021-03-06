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
import time
from _ast import While
from builtins import str



    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()
playOn = []
matriceVictoire = []
nbPlayers =0

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
    global playOn,matriceVictoire,nbPlayers;
    #for arg in sys.argv:
    iterations = 750 # default
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
    
    #Creation de la mtrice de test de victoire
    
    for i in range (0,3):
        ligne = []
        for j in range (0,3):
            ligne.append(-1)
        matriceVictoire.append(ligne)
    print(matriceVictoire)
    
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
    
    for i in range(nbPlayers):
        playOn.append((-1,-1))
    
    nextPlay = (-1,-1)
    n,m=1,1
    #variable indiquant la victoire
    gameRun = True
    gagnant = -1
    
    #Un itération = un tour (j1+j2 ont joués)
    #Remplacer condition par test si jeu gagné
    while gameRun :
        fiole_a_ramasser=put_next_fiole(j,tour)
        row,col = posPlayers[j]
        chemin = astar((row,col),fiole_a_ramasser,wallStates)
        
        #Bouger
        while True:
            next_row,next_col = chemin.pop(0)
            
            # and ((next_row,next_col) not in posPlayers)
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)
                game.mainiteration()
    
                col=next_col
                row=next_row
                posPlayers[j]=(row,col)
            
            if (row,col)==fiole_a_ramasser:
                o = players[j].ramasse(game.layers) # on la ramasse
                game.mainiteration()
                break
        
        #Cherche position où jouer
        # Strat possibles : RANDOM / RANDOM2 / GAGNANTE / TERRAIN / TERRAIN2
        if j == 0:
            n,m = jouer(j, playedTicTacToeStates, nextPlay, (n,m), tour, "GAGNANTE")
        else:
            n,m = jouer(j, playedTicTacToeStates, nextPlay, (n,m), tour, "RANDOM")
        
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
                
                #Modifie la matriceVictoire et changeant la valeur si un joueur à gagner dans un carre
                n2 = int(n/3)
                m2 = int(m/3)
                if matriceVictoire[n2][m2] == -1:
                    matriceVictoire[n2][m2]=isVictoire((n2,m2),playedTicTacToeStates)
                    gagnant = isVictoire((0,0),matriceVictoire)
                    
                    if matriceVictoire[n2][m2] != -1:
                        print("\n".join([" ".join([str(matriceVictoire[b][a]) for a in range(3)]) for b in range(3)]))
                                        
                    if gagnant != -1:
                        gameRun = False
                        break
                    
                    flg_continue = False
                    for a in range(0,3):
                        if not flg_continue:
                            for b in range(0,3):
                                if not isPlein((a,b), playedTicTacToeStates):
                                    flg_continue = True
                                    break
                        else:
                            break
                    
                    if not flg_continue:
                        gameRun = False
                                
                #print(playedTicTacToeStates)
                #print(matriceVictoire)
                #Fin des tests de victoire
                
                game.mainiteration()
                break
        
        j = (j+1)%nbPlayers
        if j == 0:
            tour+=1
    if gagnant != -1:
        print('Le joueur '+ str(gagnant) + ' a gagne!')
    else:
        print('Egalité')
    print('Le programme se fermera dans 10 secondes')
    time.sleep(10)
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
            
            new_gScore = gScore[current] + 10
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
    while pos in list(cameFrom.keys()):
        pos = cameFrom[pos]
        chemin.insert(0,pos)
    return chemin

def getChoix(position,wallStates):
    choix = [(0,1),(0,-1),(1,0),(-1,0)]
    frontiere = []
    for one_choix in choix :
        if (position[0]+one_choix[0],position[1]+one_choix[1]) not in wallStates :
            frontiere.append((position[0]+one_choix[0],position[1]+one_choix[1]))
    
    return frontiere

def getCarreDeJeu(playIn,isNaif,playedTicTacToeStates):
    if playIn == (-1,-1):
        carreDeJeu=(random.randint(0,2),random.randint(0,2))
    else:
        carreDeJeu = playIn
        
        if matriceVictoire[playIn[0]][playIn[1]]!=-1:
            if not isNaif:
                carreDeJeu=(random.randint(0,2),random.randint(0,2))
    
    if isPlein((carreDeJeu[0], carreDeJeu[1]),playedTicTacToeStates):
        return getCarreDeJeu(playIn, isNaif, playedTicTacToeStates)
    else:
        return carreDeJeu
    

def jouer(numJ, playedTicTacToeStates, playIn, previousPlay, tour, playerStrat):
    if playerStrat == "RANDOM" :
        return stratAleatoire(numJ,playedTicTacToeStates, playIn)
    if playerStrat == "RANDOM2":
        return stratAleatoire(numJ,playedTicTacToeStates, playIn, False)
    if playerStrat == "GAGNANTE" :
        return stratGagnante(numJ,previousPlay[0],previousPlay[1],tour,playedTicTacToeStates, playIn)
    if playerStrat == "TERRAIN" :
        return stratGainTerrain(numJ, playedTicTacToeStates, playIn, True)
    if playerStrat == "TERRAIN2" :
        return stratGainTerrain(numJ, playedTicTacToeStates, playIn)

#Startegie de jeu aléatoire
def stratAleatoire(numJ,playedTicTacToeStates, playIn, isNaif=True):
    x,y = (-1,-1)
    
    carreDeJeu=getCarreDeJeu(playIn,isNaif,playedTicTacToeStates)
    
    while True:
        x = 3*carreDeJeu[0]+random.randint(0,2)
        y = 3*carreDeJeu[1]+random.randint(0,2)
        
        if playedTicTacToeStates[x][y]==-1:
            break
    
    return (x,y)

#Stratégie de jeu "gagnante" (si le joueur opposé suit les règles de base)
def stratGagnante(numJ,nprec,mprec,tour,playedTicTacToeStates, playIn = (-1,-1)):
    print("Tour "+str(tour))
    
    if tour == 0 or tour == 8:
        if tour == 0:
            #Debut de la partie
            playIn = (1,1)
            coup = (1,1)
        else:
            coup = playIn
            playOn[numJ] = coup
    else:
        if playOn[numJ]!=(-1,-1):
            coup = playOn[numJ]
        else:
            coup = (int(nprec/3),int(mprec/3))
    
    x = 3*playIn[0] + coup[0]
    y = 3*playIn[1] + coup[1]
    
    if playedTicTacToeStates[x][y] != -1:
        #Ici il faut que si on doit aller dans la case du millieu,
        if playIn==(1,1) and tour!=0:
            if not isPlein(playIn, playedTicTacToeStates):
                #x,y = stratAleatoire(numJ,playedTicTacToeStates, playIn)
                x,y = stratGainTerrain(numJ,playedTicTacToeStates, playIn)
            else:
                newPlayIn = (2*1-int(nprec/3),2*1-int(mprec/3))
                x,y = stratGagnante(numJ,nprec,mprec,tour,playedTicTacToeStates,newPlayIn)
        
        else:
            # il faut envoyer vers l'opposé à la meme position
            # si ce n'est pas possible, le mettre a la position oppose dans le carre de cette position
            #x,y = stratAleatoire(tictactoeStates,playedTicTacToeStates, playIn)
            
            x = 2*(3*playIn[0] + 1) - x
            y = 2*(3*playIn[1] + 1) - y
            
            if playedTicTacToeStates[x][y] != -1:
                #x,y = stratAleatoire(numJ,playedTicTacToeStates, playIn)
                x,y = stratGainTerrain(numJ,playedTicTacToeStates, playIn)
    
    return (x,y)

def stratGainTerrain(numJ,playedTicTacToeStates, playIn, isNaif=False):
    if playIn == (-1,-1):
        #Premier Tour
        return (4,4)
    else:
        if not isPlein(playIn, playedTicTacToeStates):
            if matriceVictoire[playIn[0]][playIn[1]]!=-1:
                if not isNaif:
                    #Le terrain est déjà gagné
                    #On cherche un meilleur terrain à gagner
                    newPlayIn = getPlay((0,0), matriceVictoire, numJ)
                    
                    if newPlayIn != (-1,-1):
                        return stratGainTerrain(numJ,playedTicTacToeStates, newPlayIn)
                    
                    return stratAleatoire(numJ, playedTicTacToeStates, playIn, isNaif)
            
            #On joue dans le terrain
            if playedTicTacToeStates[playIn[0]*3+1][playIn[1]*3+1] == -1:
                x = playIn[0]*3+1
                y = playIn[1]*3+1
                return (x,y)
            else:
                x,y = getPlay(playIn, playedTicTacToeStates, numJ)
                
                if (x,y)!=(-1,-1):
                    return (x,y)
                
                return stratAleatoire(numJ, playedTicTacToeStates, playIn, isNaif)
        else:
            #On cherche un meilleur terrain à gagner
            newPlayIn = getPlay((0,0), matriceVictoire, numJ)
            
            if newPlayIn != (-1,-1):
                return stratGainTerrain(numJ,playedTicTacToeStates, newPlayIn)
            
            return stratAleatoire(numJ, playedTicTacToeStates, playIn, isNaif)

def getCorner(pos, matrix):
    goodchoices = []
    n = pos[0]*3
    m = pos[1]*3
    
    corners = [(n,m),(n+2,m),(n,m+2),(n+2,m+2)]
    
    for i in corners:
        k,l = i
        x = 2*(n + 1) - k
        y = 2*(m + 1) - l
        if matrix[k][l] == -1 and matrix[x][y] == -1:
            goodchoices.append(i)
    
    if len(goodchoices)>0 :
        return random.choice(goodchoices)
    
    return (-1,-1)

def getPlay(pos, matrix, numJ):
    n = pos[0]*3
    m = pos[1]*3
    
    lines = [
             [(n,m),(n,m+1),(n,m+2)],[(n+1,m),(n+1,m+1),(n+1,m+2)],[(n+2,m),(n+2,m+1),(n+2,m+2)],
             [(n,m),(n+1,m),(n+2,m)],[(n,m+1),(n+1,m+1),(n+2,m+1)],[(n,m+2),(n+1,m+2),(n+2,m+2)],
             [(n,m),(n+1,m+1),(n+2,m+2)],[(n,m+2),(n+1,m+1),(n+2,m)]
            ]
    
    numO = (numJ+1)%nbPlayers
    
    #Essaie de gagner
    for x in lines:
        if matrix[x[0][0]][x[0][1]] == numJ  and matrix[x[1][0]][x[1][1]] == numJ and matrix[x[2][0]][x[2][1]] == -1:
            return (x[2][0],x[2][1])
        if matrix[x[1][0]][x[1][1]] == numJ and matrix[x[2][0]][x[2][1]] == numJ and matrix[x[0][0]][x[0][1]] == -1:
            return (x[0][0],x[0][1])
        if matrix[x[0][0]][x[0][1]] == numJ and matrix[x[2][0]][x[2][1]] == numJ and matrix[x[1][0]][x[1][1]] == -1:
            return (x[1][0],x[1][1])
    
    #Empêche l'adversaire de gagner le terrain
    for x in lines:
        if matrix[x[0][0]][x[0][1]] == numO  and matrix[x[1][0]][x[1][1]] == numO and matrix[x[2][0]][x[2][1]] == -1:
            return (x[2][0],x[2][1])
        if matrix[x[1][0]][x[1][1]] == numO and matrix[x[2][0]][x[2][1]] == numO and matrix[x[0][0]][x[0][1]] == -1:
            return (x[0][0],x[0][1])
        if matrix[x[0][0]][x[0][1]] == numO and matrix[x[2][0]][x[2][1]] == numO and matrix[x[1][0]][x[1][1]] == -1:
            return (x[1][0],x[1][1])
    
    #Le centre est au joueur on prends un coin
    if matrix[n+1][m+1] == numJ:
        x,y = getCorner(pos, matrix)
        
        if (x,y) != (-1,-1):
            return (x,y)
    
    #Pas de victoire, pas de blocage, pas de coin (si centre appartient au joueur)
    #On essaie les côtés
    sides = [(n,m+1), (n+1,m), (n+1,m+2), (n+2,m+1)]
    goodchoices = []
    nbSides = 0
    for i in sides:
        k,l = i
        if matrix[k][l] == numJ:
            nbSides += 1
        if matrix[k][l] == -1:
            goodchoices.append(i)
    
    if goodchoices == [] or nbSides>1:
        return getCorner(pos, matrix)
    else:
        return random.choice(goodchoices)

#Teste si une matrice est pleine
def isPlein(pos,matrice):
    n = pos[0]*3
    m = pos[1]*3
    
    for i in range(0,3):
        for j in range(0,3):
            if matrice[n+i][m+j] == -1:
                return False
            
    return True

#fonction testant la victoire
def isVictoire(pos,matrice):#+,realTicTacToeStates?
    #l'element que l'on renvoi a la fin: -1: pas de victoire, 0; joueur 0 gagnant et 1: joueur 1 gagnant
    premier = -1
    n = pos[0]*3
    m = pos[1]*3
    
    #Boucle testant les lignes
    for i in range(0,3):
        premier = matrice[n + i][m]
        if premier != -1:
            for j in range(0,3):
                if matrice[n+i][m+j] != premier:
                    premier = -1
                    break
            if  premier != -1:
                print('on trouve une ligne pour le joueur'+str(premier)+'!'+' En position'+str(n/3)+str(m/3))
                return premier
    
    #Boucle testant les colonnes
    for i in range(0,3):
        premier = matrice[n][m + i]
        if matrice[n][m + i] != -1:
            for j in range(0,3):
                if matrice[n + j][m + i] != premier:
                    premier = -1
                    break
            if  premier != -1:
                print('on a trouve une colonne pour le joueur'+str(premier)+'!'+' En position'+str(n/3)+str(m/3))
                return premier
    
    #Boucle testant la diagonale gauche-droite
    premier = matrice[n][m]
    if matrice[n][m] != -1:       
        for i in range(0,3):
            if matrice[n+i][m+i] != premier:
                premier = -1                    
                break
        if premier != -1:
            print('on a trouver une diagonale gauche-droite pour le joueur'+str(premier)+'!'+' En position'+str(n/3)+str(m/3))
            return premier
    
    #Boucle testant la diagonale droite gauche
    premier = matrice[n][m+2] 
    if matrice[n][m+2] != -1:
        for i in range(0,3):
            if matrice[n+i][m+2-i] != premier:
                premier = -1
                break
        if premier != -1:
            print('on a trouve une diagonale droite gauche pour le joueur'+str(premier)+'!'+' En position'+str(n/3)+str(m/3))
            return premier
    
    #si on arrive ici c'est que l'on a pas trouver de victoire
    return -1

if __name__ == '__main__':
    main()
    


