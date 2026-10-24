import numpy
import matplotlib.pyplot
import time
import os
import json
import _tkinter #is this the same?
#import Pygame

class Node:
    C = 3.5

    def __init__(self, p, bd, win=0, myTurn=True):
        self.children = [None] * 7
        self.playout = 1 #TODO: this makes head have one too many, but i think thats the only problem
        self.parent = p
        self.board = bd
        self.win = win
        self.myTurn = myTurn

board = []
for i in range(6):
    board.append([None, None, None, None, None, None, None])

turnLengths = []

def play(board):
    print("H = Human, C = Computer")
    myTurn = True #give the computer the first turn
    for i in range(100): 
        if hasWinner(board): 
            return myTurn
        if myTurn:
            #computer turn
            start = time.time()
            col = alphaBetaSearch(board, myTurn) #monteCarlo also returns head now
            end = time.time()
            turnLengths.append(end - start)
            board = place(board, col, myTurn) 
        else:
            #human turn
            col = input("enter column number 1-7: ") 
            board = place(board, int(col)-1, myTurn)
        myTurn = not myTurn
        printBoard(board)

def place(board, col, mt):
    #place mt player's piece in the column in a copy of board, and return the copy. If the column is full, return None
    b = []
    for r in range(len(board)):
        b.append([])
        for c in range(len(board[0])):
            b[r].append(board[r][c])
    i = 5
    while(i >= 0):
        if(b[i][col]) == None: 
            b[i][col] = mt
            return b
        i = i-1
    return None

def printBoard(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == False: print(" H ", end="")
            elif board[i][j] == True: print(" C ", end="")
            else: print(" . ", end="")
        print()
    print(" 1  2  3  4  5  6  7")
    print()

def hasWinner(board):
    #check horizontal
    for i in range(len(board)):
        consecutive = 0
        for j in range(1, len(board[0])):
            if(board[i][j] == None or board[i][j] != board[i][j-1]):
                consecutive = 0
            else:
                consecutive = consecutive + 1
            if consecutive == 3:
                return True
    #check vertical
    for j in range(len(board[0])):
        consecutive = 0
        for i in range(1, len(board)):
            if(board[i][j] == None or board[i][j] != board[i-1][j]):
                consecutive = 0
            else:
                consecutive = consecutive + 1
            if consecutive == 3:
                return True
    #check negative diagonal
    for k in range(3): #to check diagonals that don't start in the first row
        for i in range(len(board[0])):
            consecutive = 0
            for j in range(len(board)):
                if(not (j+k+2 > len(board)) and not(i+j+2 > len(board[0]))):
                    if(board[j+k][i+j] == None or board[j+k][i+j] != board[j+1+k][i+j+1]):
                        consecutive = 0
                    else:
                        consecutive = consecutive + 1
                    if consecutive == 3:
                        return True
                else: break
    #check negative diagonal
    for k in range(3): #to check diagonals that don't start in the first row
        for i in range(len(board[0])):
            consecutive = 0
            for j in range(len(board)):
                if(not (5-j-k-1 < 0) and not(i+j+2 > len(board[0]))):
                    if(board[5-j-k][i+j] == None or board[5-j-k][i+j] != board[5-j-1-k][i+j+1]):
                        consecutive = 0
                    else:
                        consecutive = consecutive + 1
                    if consecutive == 3:
                        return True
                else: break
    return False

def alphaBetaSearch(board, myTurn):
    value, move = maxValue(board, -2, 2, myTurn, 0)
    return move

def maxValue(board, a, b, mt, cutoff):
    if hasWinner(board):
        return -2, None 
    elif complete(board) or cutoff > 5:
        return evaluate(board, True), None 
    v = -2
    move = 0
    for col in range(0,7): 
        #place a piece and send the result down the tree
        bd = place(board, col, True) 
        if bd == None: 
            continue
        v2, _ = minValue(bd, a, b, mt, cutoff+1)
        #when min returns its evaluation, compare it to our current value and see if we like it better (and it is within the range our parent will accept)
        if v2 > v:
            v = v2
            move = col
            a = max(a, v)
        if v >= b:
            return v, move
    return v, move

def minValue(board, a, b, mt, cutoff):
    if hasWinner(board):
        return 2, None 
    elif complete(board) or cutoff > 5:
        return evaluate(board, False), None
    v = 2
    move = 0
    for col in range(0,7): 
        #place a piece and send the result down the tree
        bd = place(board, col, False)
        if bd == None: continue
        v2, _ = maxValue(bd, a, b, mt, cutoff+1) 
        #when min returns its evaluation, compare it to our current value and see if we like it better (and it is within the range our parent will accept)
        if v2 < v:
            v = v2
            move = col
            b = min(b, v)
        if v <= a: 
            return v, move
    return v, move 

def monteCarlo(board, myTurn):
    head = Node(None, board, 0, myTurn)
    #check for a game-ending move
    for col in range(len(board[0])): 
        b = place(board, col, myTurn)
        if b != None and hasWinner(b):
            return col, head
    for col in range(len(board[0])): #its better if it checks for a winning move for itself first, then for my win
        b = place(board, col, not myTurn)
        if b != None and hasWinner(b):
            return col, head
    #simulate nodes 300 times
    for i in range(300):
        MCTS(head, myTurn, 0)
    #find the most popular node to playout, this is the best one 
    col = 0
    max = 0
    for i in range(len(head.children)):
        if head.children[i] != None:
            playout = head.children[i].playout
            if playout > max:
                max = playout
                col = i
    return col, head

def MCTS(node, mt, cutoff):
        #if we haven't played out all the columns at least once, do that
        if None in node.children:
            unvisitedChild = node.children.index(None)
            bd = place(node.board, unvisitedChild, mt)
            if bd != None:
                win = simulateRandom(bd, node)
                node.children[unvisitedChild] = Node(node, bd, win, not mt)
                pNode = node
                while(True):
                    pNode.playout = pNode.playout + 1
                    if pNode.myTurn == mt:
                        pNode.win = pNode.win + (not win)
                    else:
                        pNode.win = pNode.win + win #TODO: what if they tied?
                    pNode = pNode.parent
                    if pNode == None:
                        break
            else: #if the column was full
                return
        #compare all the children and pick the best one
        else:
            best = node.children[0] 
            v = 0
            for child in node.children: 
                #UCB function
                v2 = (child.win/child.playout) + node.C * numpy.sqrt(numpy.log(node.playout) / child.playout)
                if v2 > v:
                    v = v2
                    best = child
            mt = not mt 
            MCTS(best, mt, cutoff+1) 
        return

def simulateRandom(board, node):
    mt = node.myTurn
    while not complete(board):
        #place the next player's piece in a random column
        bd = place(board, numpy.random.randint(7), mt)
        if bd == None:
            continue
        else:
            board = bd
            if (hasWinner(board)):
                if(mt == False):
                    return 0 #lose
                else:
                    return 1 #win
            elif complete(board):
                return 0.5 #tie
            mt = not mt
    return 0.5

def simulateWCheck(board, node):
    mt = node.myTurn
    while not complete(board):
        for col in range(len(board[0])): 
            #check if either player can win on their next turn, and act on that they can
            b1 = place(board, col, mt)
            b2 = place(board, col, not mt)
            if b1 != None and hasWinner(b1):
                board = b1
                mt = not mt
                return 1
            elif b2 != None and hasWinner(b2):
                board = place(board, col, mt)
                mt = not mt
                break 
        #if no one is about to win, just pick a random column
        b3 = place(board, numpy.random.randint(7), mt)
        if b3 != None:
            board = b3
            if (hasWinner(board)):
                if(mt == False):
                    return 0
                else:
                    return 1
            elif complete(board):
                return 0.5
            mt = not mt
    return 0.5

#sum of consecutive pieces
def evaluate(board, myTurn):
    b = []
    for r in range(len(board)):
        b.append([])
        for c in range(len(board[0])):
            b[r].append(board[r][c])
    retMine = 0
    retTheirs = 0
    #check horizontal
    for i in range(len(b)):
        mine = 0
        theirs = 0
        for j in range(1, len(b[0])):
            if(b[i][j] == None or b[i][j] != b[i][j-1]):
                mine = 0
                theirs = 0
            elif (b[i][j] == myTurn):
                mine = mine + 1
            elif (b[i][j] != myTurn):
                theirs = theirs + 1
            if mine == 3: #TODO: my report wants to know i did this
                return 1 #TODO: this should be a 2? or is this breaking everything?
            if theirs == 3: 
                return -1
            retMine = retMine + mine
            retTheirs = retTheirs + theirs
    #check vertical
    for j in range(len(b[0])):
        mine = 0
        theirs = 0
        for i in range(1, len(b)):
            if(b[i][j] == None or b[i][j] != b[i-1][j]):
                mine = 0
                theirs = 0
            elif (b[i][j] == myTurn):
                mine = mine + 1
            elif (b[i][j] != myTurn):
                theirs = theirs + 1
            if mine == 3: #TODO: my report wants to know i did this
                return 1
            if theirs == 3: 
                return -1
            retMine = retMine + mine
            retTheirs = retTheirs + theirs
    #check negative diagonal
    for k in range(3): #to check diagonals that don't start in the first row
        for i in range(len(b[0])):
            mine = 0
            theirs = 0
            for j in range(len(b)):
                if(not (j+k+2 > len(b)) and not(i+j+2 > len(b[0]))):
                    if(b[j+k][i+j] == None or b[j+k][i+j] != b[j+1+k][i+j+1]):
                        mine = 0
                        theirs = 0
                    elif (b[i][j] == myTurn):
                        mine = mine + 1
                    elif (b[i][j] != myTurn):
                        theirs = theirs + 1
                    if mine == 3: #TODO: my report wants to know i did this
                        return 1
                    if theirs == 3: 
                        return -1
                    retMine = retMine + mine
                    retTheirs = retTheirs + theirs
                else: break
    #check negative diagonal
    for k in range(3): #to check diagonals that don't start in the first row
        for i in range(len(b[0])):
            mine = 0
            theirs = 0
            for j in range(len(b)):
                if(not (5-j-k-1 < 0) and not(i+j+2 > len(b[0]))):
                    if(b[5-j-k][i+j] == None or b[5-j-k][i+j] != b[5-j-1-k][i+j+1]):
                        mine = 0
                        theirs = 0
                    elif (b[i][j] == myTurn):
                        mine = mine + 1
                    elif (b[i][j] != myTurn):
                        theirs = theirs + 1
                    if mine == 3: #TODO: my report wants to know i did this
                        return 1
                    if theirs == 3: 
                        return -1
                    retMine = retMine + mine
                    retTheirs = retTheirs + theirs
                else: break
    ret = (retMine - retTheirs)/42 #TODO is this backward?
    if ret > 1 or ret < -1:
        pass
    return ret

def complete(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == None: return False
    return True

printBoard(board)
print(hasWinner(board))
print(1 + (not False))
iwon = play(board)
tie = complete(board)
print(numpy.average(turnLengths))
if tie: 
    print("we all win!")
elif iwon: #its opposite bc at the end of every turn, we flip the variable
    print("human wins!")
else:
    print("computer wins!")