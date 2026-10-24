import numpy
import matplotlib.pyplot
import time
import os
import json
import _tkinter

empty = [120]
Boards = []
for e in empty:
    with open('sudoku' + str(e) + '_16_2' + '.json', 'r') as f: Boards.append(json.load(f))

#check which values 1-9 do not conflict with the starting board
def makeDomain(board):
    domains = []
    for i in range(len(board)):
        domains.append([])
        for j in range(len(board)):
            domains[i].append([])   
            for k in range(1, len(board)+1):
                if allowed(board, i, j, k):
                    domains[i][j].append(k)
    return domains


def solve(board, MRV, MAC, LCV):
        if complete(board): 
            return
        board = backtracking(board, makeDomain(board), MRV, MAC, LCV)[1]
        printBoard(board)

def complete(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 0: return False
    return True

def printBoard(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            print(" ", board[i][j], " ", end="")
        print()
    print()

def backtracking(board, domains, MRV, MAC, LCV):
    return backtrack(board, domains, 0, 0, MRV, MAC, LCV)

def backtrack(board, domains, r, c, MRV, MAC, LCV):
    if complete(board): 
        return True, board
    if (not MRV):
        #find the next open position in column major order
        while(board[r][c] != 0): #find next unfilled position (random select unassigned value)
            r = r+1
            if r > len(board)-1:
                r = 0
                c = c + 1
    else:
        #find the open position on the board with the smallest current domain
        minRemainValues = (9, 0, 0) #9 values at pos 0, 0
        for i in range(len(domains)):
            for j in range(len(domains[i])):
                if board[i][j] == 0 and len(domains[i][j]) < minRemainValues[0]:
                    minRemainValues = (len(domains[i][j]), i, j)
        r = minRemainValues[1]
        c = minRemainValues[2]
    
    if(LCV):
        orderByLeastConstraining(board, domains, r, c)
    for value in domains[r][c]:
        if (allowed(board, r, c, value)):
            #change a temporary copy of the board and domain so we can backtrack later
            bd = copy(board)
            bd[r][c] = value
            d = []
            for i in range(len(domains)):
                d.append(copy(domains[i])) #I think this will work since domains has three levels
            d[r][c] = [value] #imagine we've placed value, ac3 will check if it works
            if(MAC):
                if not AC3(bd, d, r, c):
                    continue
            else:
                if not inference(bd, d, r, c):
                    continue #don't backtrack, go find the next number instead
            #move to the next position on the board (open or not)
            prevr = r
            prevc = c
            r = r+1
            if r > len(bd)-1:
                r = 0
                c = c + 1 
            #go fill that position
            res = backtrack(bd, d, r, c, MRV, MAC, LCV)
            if (res[0]):
                return True, res[1]
            else:
                r = prevr #we moved to the next position before we recursed, so now we need to go back one
                c = prevc
                board[r][c] = 0      
    return False, None

def orderByLeastConstraining(board, domains, r, c):
    #count the number of neighbor domains that would have to change if we put each value in that position
    nbs = neighbors(board, r, c)
    order = []
    for i in range(len(domains[r][c])):
        #the number of other places the first domain value constrains starts at 0 
        numConstraints = 0
        for n in nbs:
            if board[n[0]][n[1]] == 0 and domains[r][c][i] in domains[n[0]][n[1]]:
                numConstraints = numConstraints + 1
        order.append((numConstraints, domains[r][c][i]))
    #rearrange the domain values so the least affecting ones are in the beginning
    order.sort() 
    domains[r][c] = []
    for value in order:
        domains[r][c].append(value[1])

def allowed(board, r, c, value):
    for n in neighbors(board, r, c):
        if board[n[0]][n[1]] == value:
            return False
    return True

def inference(board, domain, r, c):
    #remove the value we just placed from our neighbors domains
    nbs = neighbors(board, r, c)
    for n in nbs:
        try:
            domain[n[0]][n[1]].remove(board[r][c])
        except ValueError:
            pass
        if len(domain[n[0]][n[1]]) == 0:
            return False
    return True

'''Maintaining Arc Consistency (MAC): after a variable Xi is assigned a value, the inference calls AC-3,
which starts its queue only with the arcs (Xj, Xi), where Xj’s are the unassigned neighbors of Xi.'''
def AC3(board, domains, r, c):
    queue = []
    for n in neighbors(board, r, c):
        if board[n[0]][n[1]] == 0 and ((n[0], n[1], r, c) not in queue):
            queue.append((n[0], n[1], r, c))

    #if we have changed a neighbor's domain, add all the other neighbors back to the queue to check again
    while len(queue) != 0:
        r1, c1, _, _ = queue.pop(0) #we want the second two values to always be r, c
        if revise(board, domains, r1, c1, r, c):
            if len(domains[r1][c1]) == 0: return False
            for n in neighbors(board, r, c): 
                if (n[0] != r1 and n[1] != c1) and board[n[0]][n[1]] == 0 and ((n[0], n[1], r, c) not in queue):
                    queue.append((n[0], n[1], r, c)) 
    return True
        
def revise(board, domains, r1, c1, r2, c2):
    revised = False
    i = 0
    while i < len(domains[r1][c1]): 
        bd = copy(board)
        bd[r1][c1] = domains[r1][c1][i]
        numAllowed = 0
        for y in domains[r2][c2]:
            if allowed(bd, r2, c2, y): 
                numAllowed = numAllowed + 1
                break
        if numAllowed == 0:
            try:
                domains[r1][c1].pop(i)
                i = i - 1
            except ValueError:
                pass
            revised = True #can't return yet, need to keep shrinking the domain
        i = i + 1
    return revised

def neighbors(board, r, c):
    neighbor = []
    for i in range(len(board[r])):
        if i != c and (r, i) not in neighbor:
            neighbor.append((r , i))
    for j in range(len(board)):
        if j != r and (j, c) not in neighbor:
            neighbor.append((j, c))
    size = int(numpy.sqrt(len(board)))
    quadrow = r // size
    quadcol = c // size
    for qr in range(quadrow * size, quadrow * size + size):
        for qc in range(quadcol * size, quadcol * size + size):
            if (qr != r and qc != c) and (qr, qc) not in neighbor:
                neighbor.append((qr , qc))
    return neighbor

def copy(board):
    bd = []
    for i in range(len(board)):
        bd.append([])
        for j in range(len(board[i])):
            bd[i].append(board[i][j])
    return bd

with open("sudoku size results", "a") as f:
    for i in range(len(Boards)):
        start = time.time()
        solve(Boards[i], True, False, True)
        print(str(time.time() - start) + " " + str(i) + " TFT")
        '''
        start = time.time()
        solve(Boards[i], False, False, False)
        f.write(str(time.time() - start) + " " + str(i) + " FFF")
        print(i)
        start = time.time()
        solve(Boards[i], True, False, False)
        f.write(str(time.time() - start) + " " + str(i) + " TFF")
        print(i)
        start = time.time()
        solve(Boards[i], False, True, False)
        f.write(str(time.time() - start) + " " + str(i) + " FTF")
        print(i)
        start = time.time()
        solve(Boards[i], False, False, True)
        f.write(str(time.time() - start) + " " + str(i) + " FFT")
        print(i)
        start = time.time()
        solve(Boards[i], True, True, False)
        f.write(str(time.time() - start) + " " + str(i) + " TTF")
        print(i)
        start = time.time()
        solve(Boards[i], True, False, True)
        f.write(str(time.time() - start) + " " + str(i) + " TFT")
        print(i)
        start = time.time()
        solve(Boards[i], False, True, True)
        f.write(str(time.time() - start) + " " + str(i) + " FTT")
        print(i)
        start = time.time()
        solve(Boards[i], True, True, True)
        f.write(str(time.time() - start) + " " + str(i) + " TTT")
        '''