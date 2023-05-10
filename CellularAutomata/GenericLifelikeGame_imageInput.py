#!/usr/bin/env python3

from random import randint
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
from functools import partial
from PIL import Image
import argparse

#Code for this mini-project mainly heavily inspired from this tutorial: https://betterprogramming.pub/how-to-write-conwells-game-of-life-in-python-c6eca19c4676

class Cell:
    """
    Class that contains the status (alive or dead) of the cells.
    """
    def __init__(self):
        #initially, all cells are dead
        self._status = "Dead"

    def setDead(self):
        self._status = "Dead"
    
    def setAlive(self):
        self._status = "Alive"

    def isAlive(self): #check status of cell
        if(self._status == "Alive"):
            return True
        else:
            return False

    def getPrintCharacter(self): #for terminal display
        if(self.isAlive()):
            return "O"
        else:
            return "*"
    
    def getCellPixelColour(self): #for matplotlib animation plottingß
        if(self.isAlive()):
            return 255
        else:
            return 0


class Board:
    def __init__(self, rows, columns, initialStateArray=None):
        try:
            initialStateArray[0][0] #this will fail if initialStateArray = None (you can only index a 2D array this way)
            initStateArrExistence = True
        except:
            initStateArrExistence = False
        if(initStateArrExistence==True):
            shapeOfInitArr = np.shape(initialStateArray)
            self._rows = shapeOfInitArr[0]
            self._columns = shapeOfInitArr[1]
            self._grid = [[Cell() for columnCells in range(self._columns)] for rowCells in range(self._rows)]
            self._generateBoardFromImage(initialStateArray)

        else:
            self._rows = rows
            self._columns = columns
            self._grid = [[Cell() for columnCells in range(self._columns)] for rowCells in range(self._rows)]

            self._generateBoard()

    def _generateBoard(self):
        for row in self._grid:
            for column in row: #this gets a specific Cell object
                chanceNumber = randint(0,2) #inclusive range btw  - can roll 0, 1 and 2
                if(chanceNumber==1):
                    column.setAlive()
    
    def _generateBoardFromImage(self, initArr):
        for i in range(self._rows):
            for j in range(self._columns):
                if(initArr[i][j]==255):
                    self._grid[i][j].setAlive()

    def drawBoard(self): #for terminal display
        print(10*"\n")
        for row in self._grid:
            for column in row: #this gets a specific Cell object
                print(column.getPrintCharacter(), end="") #setting end to a space to print everything in a row on the same row
            print() #new row
    

    def getDataForBoardPlotting(self): #for matplotlib animation plotting - this is the update img func for animation.FuncAnimation from matplotlib
        frame = np.zeros((self._rows, self._columns)) #creating 'blank' 2d array to be able to set values based on Life algorithm for plotting
        for row in range(self._rows):
            for column in range(self._columns):
                frame[row][column] = self._grid[row][column].getCellPixelColour()
        return frame



    def getNeighbourList(self, currentRow, currentColumn): #this function is used on a per cell basis in updateBoard()
        #currentRow and currentColumn are the row and column indices for a given cell
        
        searchDepth = 1 #how far from a given cell am I going to look for neighbours

        #checking the "Moore neighbourhood" of a given cell (I think this phrase is used more commonly in the related game called "Day and Night"), i.e. the cells surroudning a given cell
        neighbourList = []
        for rowDisplacement in range(-searchDepth,searchDepth+1): #the +1 is added since range function uses a half-open interval
            for columnDisplacement in range(-searchDepth,searchDepth+1):
                neighbourRow = currentRow+rowDisplacement
                neighbourColumn = currentColumn+columnDisplacement

                
                validNeighbour = True

                #a cell cannot be its own neighbour
                if(neighbourRow == currentRow and neighbourColumn == currentColumn):
                    validNeighbour = False

                #neighbour row index cannot be negative or greater or equal to the number of rows in the grid (this is to avoid trying to check for neighbours outside the grid) - also remember that index cannot be equal to the no. of rows since arrays in Python are zero-indexed
                if(neighbourRow < 0 or neighbourRow >= self._rows):
                    validNeighbour = False

                #neighbour column index cannot be negative or greater or equal to the number of columns in the grid (this is to avoid trying to check for neighbours outside the grid) - also remember that index cannot be equal to the no. of columns since arrays in Python are zero-indexed
                if(neighbourColumn < 0 or neighbourColumn >= self._columns):
                    validNeighbour = False
                
                if(validNeighbour): #if True
                    neighbourList.append(self._grid[neighbourRow][neighbourColumn])
        
        return neighbourList


    def updateBoard(self, bornRules:list, surviveRules:list):
        goesAlive = [] #list of cells that either get resurrected or continue living
        getsKilled = [] #self-explanatory - this is a cell hit list

        for row in range(len(self._grid)): #will get you the no. of rows
            for column in range(len(self._grid[row])): #will get you the no of columns for a given row
                checkNeighbours = self.getNeighbourList(row, column) #gets neighbours for a given cell

                #saving only the living neighbours
                livingNeighbours = []
                for neighbourCell in checkNeighbours:
                    if(neighbourCell.isAlive()):
                        livingNeighbours.append(neighbourCell)
                
                currentCell = self._grid[row][column]
                statusOfCurrentCell = currentCell.isAlive()

                #if current cell is alive
                if(statusOfCurrentCell == True):
                
                    if(len(livingNeighbours) in surviveRules):
                        goesAlive.append(currentCell)
                    
                    else:
                        getsKilled.append(currentCell)
                
                #if current cell is dead
                else:
                    if(len(livingNeighbours) in bornRules):
                        goesAlive.append(currentCell)
                

        for cells in goesAlive:
            cells.setAlive()
        
        for cells in getsKilled:
            cells.setDead()

                
def mainTerminal(bornRules, surviveRules): #for terminal display
    userSetRows = int(input("How many rows?: "))
    userSetColumns = int(input("How many columns?: "))

    gameOfLifeBoard = Board(userSetRows, userSetColumns)

    gameOfLifeBoard.drawBoard()

    userAction = ""
    while(userAction != "q"):
        userAction = input("Press enter to add a new generation or q to quit: ")

        if(userAction == ""):
            gameOfLifeBoard.updateBoard(bornRules, surviveRules)
            gameOfLifeBoard.drawBoard()

def updateImage(i, boardObject, ax, bornRules, surviveRules, cmap, picPath=None, delay=3, fps=10):
    global frameCounter
    framesToDelay = fps*delay
    if(picPath!=None): #The difference between this and the code after the if statement is this doesn't update the board for however many frames you want to delay by
        if(frameCounter<=framesToDelay):
            frameData = boardObject.getDataForBoardPlotting()
            ax.clear()
            im = ax.imshow(frameData, animated=True, cmap=cmap)
            im.set_array(frameData)
            frameCounter += 1
        else: #this is the same code as for the outer else statement - just running the calculation normally
            frameData = boardObject.getDataForBoardPlotting()
            boardObject.updateBoard(bornRules, surviveRules)
            ax.clear()
            im = ax.imshow(frameData, animated=True, cmap=cmap)
            im.set_array(frameData)

    else:
        frameData = boardObject.getDataForBoardPlotting()
        boardObject.updateBoard(bornRules, surviveRules)
        ax.clear()
        im = ax.imshow(frameData, animated=True, cmap=cmap)
        im.set_array(frameData)


def BorW(luminosity):
    if(luminosity>127):
        return 255
    else:
        return 0


def mainPixelAnimation(rules:str, userSetRows, userSetColumns, pic=None, saveCount=300, cmap="inferno", save=None, delay=3, fps=10): #for matplotlib animation plotting
    
    rules = rules.split("/")
    rules = [list(ruleList)[1:] for ruleList in rules] #taking slice [1:] to remove the B/S chars from lists
    rules = [[int(item) for item in ruleList] for ruleList in rules]

    bornRules=rules[0]
    surviveRules=rules[1]



    if(pic!=None):
        initialState = Image.open(pic).convert("L")
        initialState = np.array([[BorW(i) for i in line] for line in np.array(initialState)])
        gameOfLifeBoard = Board(userSetRows, userSetColumns, initialStateArray=initialState)
    else:
        gameOfLifeBoard = Board(userSetRows, userSetColumns)
    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None) #removes most of the white padding for the animation
    #the following two lines of code remove the axes from the animations
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    global frameCounter
    frameCounter = 0

    if(save!=None):
        ani = animation.FuncAnimation(fig, partial(updateImage, boardObject=gameOfLifeBoard, ax=ax, bornRules=bornRules, surviveRules=surviveRules, cmap=cmap, picPath=pic, delay=delay, fps=fps), interval=50, save_count=saveCount)
        writergif = animation.PillowWriter(fps=fps) 
        ani.save(f"{save}.gif", writer=writergif)
    else:
        ani = animation.FuncAnimation(fig, partial(updateImage, boardObject=gameOfLifeBoard, ax=ax, bornRules=bornRules, surviveRules=surviveRules, cmap=cmap, picPath=pic, delay=delay, fps=fps), interval=50) #this doesn't have save_count set
        plt.show()


parser = argparse.ArgumentParser(prog = 'Game of Life-like program',
                    description = 'This runs GOL-like games, where you can set your own rules.',
                    epilog = 'Hope you have fun with this program :)')
parser.add_argument("-g", "--game", type=str, default="B3678/S34678", help="Defines the rules used for the game in rule notation, e.g. B3/S23 for Conway's Game of Life. The default rules are those for Day and Night, i.e. B3678/S34678.")
parser.add_argument('-r', '--rows', type=int, default=128, help="Defines the number of rows of your game. This is ignored if --pic is set.")
parser.add_argument('-c', '--cols', type=int, default=128, help="Defines the number of columns of your game. This is ignored if --pic is set.")
parser.add_argument("-p", "--pic", type=str, default=None, help="Path to the picture you'd like to use for the initial state of the game.")
parser.add_argument("-d", "--delay", type=int, default=3, help="The amout of time the program lingers on the initial state if the --pic flag is used. Default value is 3 s")
parser.add_argument("-s", "--save", type=str, default=None, help="The name of the .gif file you want to save your animation with.")
parser.add_argument("-f", "--frames", type=int, default=200, help="The number of frames of your game to save to an animated gif. This argument will only be taken into account of --save is set to True. Default value is 200 frames.")
parser.add_argument("-m", "--map", type=str, default="inferno", help="The colour map used for the game. Dead cells use colour value 0, and living cells use value 255.")
args = parser.parse_args()


DandNrules = ([3,6,7,8],[3,4,6,7,8])
DandNrules = "B3678/S34678"
LifeRules = "B3/S23"
newRules = "B27/S247"



mainPixelAnimation(args.game, args.rows, args.cols, pic=args.pic, saveCount=args.frames, save=args.save, cmap=args.map, delay=args.delay)
