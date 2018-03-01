# Sujet de mini-projet (2018)

## Environnement
Vous utiliserez le module `PySpriteWorld` qui élabore pygame et permet de manipuler simplement des personnages, cartes, et autres objets à l'écran. Ce module a été développé par Yann Chevaleyre. Une version plus complète se trouve ici: https://github.com/yannche/pySpriteWorld, mais la version disponible dans ce répertoire suffit a priori pour faire tout ce dont vous avez besoin.

Notez que vous pourrez ensuite éditer vos propres cartes à l'aide de l'éditeur [Tiled](http://www.mapeditor.org/), et exporter ces cartes au format `.json`.
Il faut utiliser au moins trois calques lors de la création de votre carte: 
* un calque **joueur**, où seront les personnages 
* un calque **ramassable**, qui contient les objets que les personnages peuvent ramasser
* un calque **obstacles**, pour les murs, les arbres, etc.

**Note**: on fait ici l'hypothèse que toutes les informations (positions des agents et des trésors sont disponibles pour tous les agents, i.e. on ne se pose pas de problème de communication)

Une difficulté pour le sujet de projet concerne le fait que les joueurs doivent pouvoir identifier quel type de fiole est à quel endroit, or le calque ramassable ne les distingue pas a priori. 
Il est possible d'utiliser `o.tileid` qui donne la coordonnée du symbole dans la fiche `tiny_complete`, et de là vous pouvez déduire la couleur de la fiole (voir pour un exemple le code `UltimateTicTacToe.py`).

## 1: Echauffement

Vous coderez grâce à l'algorithme A\* un calcul de plus court chemin permettant à votre personnage d'atteindre une fiole, puis de la porter au centre du terrain. 
Vous pouvez utiliser comme squelette de code le fichier `PySpriteWorld.py`. 

## 2-3: Mini-Projet

Dans ce projet, on met en compétition deux personnages dans un monde labyrinthique.
Les deux joueurs vont s'affronter en jouant à une partie de Ultimate TicTacToe. 
Les règles de base sont les suivantes: 
* le terrain de TicTacToe consiste en 9 terrains "classiques" de TicTacToe (les "petits terrains"), chacun de 3x3. 
* chaque joueur, à son tour, ramasse une fiole de sa couleur et l'utilise comme un pion pour jouer sur un petit terrain de TicTacToe
* en jouant sur une case donnée de son terrain, le joueur contraint le terrain sur lequel l'autre joueur pourra jouer. 
* lorsqu'un joueur gagne une partie sur un petit terrain, il gagne ce terrain
* lorsqu'un joueur aligne trois petits terrains victorieux, il gagne globalement la partie

En cas d'égalité, vous pourrez tester les variantes suivantes: 
* le terrain est gagné par les deux joueurs
* le terrain est gagné par le joueur qui a parcouru le moins 



### Travail demandé: 
Proposer au minimum deux IAs permettant de simuler un match entre deux joueurs. 
Pour comparer vos IAs, vous pourrez répéter plusieurs matchs. Si vous proposez, vous pourrez organiser la compétition sous forme d'un tournoi au cours duquel tous les joueurs se rencontrent. 
Vous pouvez utiliser toutes les notions qui vous semblent pertinentes vues en cours-TDs. 

