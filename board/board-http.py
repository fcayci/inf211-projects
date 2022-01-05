# -*- coding: utf-8 -*-
""" Sliding Game
Created on Thu Oct 28 11:48:26 2021

@author: AsL
"""

import random
import socket
import os

import flask
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect, url_for

# -------------Generating matrix------------
def test_generate(row,column):
    board_ana = list(range(row*column))
    board=[board_ana[i:i+column] for i in range(0, len(board_ana), column)]
    return board


def test_get_board_size(board):
    row=len(board)
    column=len(board[0])
    return row, column

# -------------Shuffling matrix------------ w.r.t zero
def test_shuffle(board, times=20):
    for i in range (times):
        test_move_random(board)
    return board

# -------------Reset matrix------------
def test_reset(board):
    board_ana = list(range(len(board)*len(board[0])))
    board=[board_ana[i:i+len(board[0])] for i in range(0, len(board_ana), len(board[0]))]
    return board

# -------------Validty of movements------------
def test_is_valid(board):
    blist = sum(board,[])
    blist.sort()
    blist2 = list(range(len(board)*len(board[0])))
    if blist==blist2:
        valid = True
    else:
        valid = False
    return valid

# -------------Control------------
def test_is_solved(board):
    blist = sum(board,[])
    blist2 = list(range(len(board)*len(board[0])))
    if blist==blist2:
        result = True
    else:
        result = False
    return result

# -------------Rotate matrix------------
def test_rotate(board):
    board_tp = [[0 for a in range(len(board))] for y in range(len(board[0]))]
    board_rt=[]
    for i in range(len(board[0])): #transpose
            for j in range(len(board)):
                board_tp[i][j] = board[j][i]
    for i in range(len(board[0])): #reverse
        board_rt.append(board_tp[i][::-1])
    return board_rt

# -------------Movements-----------------
def test_move(board, moves):
    for num2 in moves:
        for rowx in range(len(board)):
            for coly in range(len(board[rowx])):
                if board[rowx][coly] == 0:
                    x=rowx
                    y=coly
        if num2 in 'lL': #left
            if y-1<0:
                continue
            else:
                board[x][y], board[x][y - 1] = board[x][y - 1], board[x][y]

        elif num2 in 'rR': #right
            if y+1>len(board[0])-1:
                continue
            else:
                board[x][y], board[x][y + 1] = board[x][y + 1], board[x][y]

        elif num2 in 'uU': # up
            if x-1<0:
                continue
            else:
                board[x][y], board[x - 1][y] = board[x - 1][y], board[x][y]

        elif num2 in 'dD':  #down
            if x+1>len(board)-1:
                continue
            else:
                board[x][y], board[x + 1][y] = board[x + 1][y], board[x][y]
                continue
    return board

#-------------Right movements--------------
def test_move_right(board, allmove):
    for rowx in range (len(board)):
        for coly in range(len(board[rowx])):
            if board[rowx][coly] == 0:
                x=rowx
                y=coly

    if y+1>len(board[0])-1:
        allmove = allmove
        # print('you have made an invalid movement')
    else:
        board[x][y], board[x][y + 1] = board[x][y + 1], board[x][y]
        allmove = allmove+1
    return board, allmove

#-------------Left movements--------------
def test_move_left(board,allmove):
    for rowx in range (len(board)):
        for coly in range(len(board[rowx])):
            if board[rowx][coly] == 0:
                x=rowx
                y=coly
    if y-1<0:
        allmove = allmove
        # print('you have made an invalid movement')
    else:
        board[x][y], board[x][y - 1] = board[x][y - 1], board[x][y]
        allmove = allmove+1
    return board, allmove

#-------------Up movements--------------
def test_move_up(board,allmove):
    for rowx in range (len(board)):
        for coly in range(len(board[rowx])):
            if board[rowx][coly] == 0:
                x=rowx
                y=coly
    if x-1<0:
        allmove = allmove
        # print('you have made an invalid movement')
    else:
        board[x][y], board[x - 1][y] = board[x - 1][y], board[x][y]
        allmove = allmove+1
    return board, allmove

#-------------Down movements--------------
def test_move_down(board,allmove):
    for rowx in range (len(board)):
        for coly in range(len(board[rowx])):
            if board[rowx][coly] == 0:
                x=rowx
                y=coly
    if x+1>len(board)-1:
        allmove = allmove
        # print('you have made an invalid movement')
    else:
        board[x][y], board[x + 1][y] = board[x + 1][y], board[x][y]
        allmove = allmove+1
    return board, allmove

#-------------Random movements--------------
def test_move_random(board):
    alist=['R','L','U','D']
    for rowx in range(len(board)):
        for coly in range(len(board[rowx])):
            if board[rowx][coly] == 0:
                x=rowx
                y=coly
    if y-1<0:
        alist.remove('L')
    if y+1>len(board[0])-1:
        alist.remove('R')
    if x-1<0:
        alist.remove('U')
    if x+1>len(board)-1:
        alist.remove('D')

    moves=random.choice(alist)
    test_move(board,moves)
    return board

# -------------Design matrix--------------
def test_print_board(board):
    from colorama import Fore
    from colorama import Style
    a2=len(board[0])
    strlev='<code><br />&nbsp;&nbsp;&nbsp;+'+a2*'-------+'
    s = ''
    s += strlev + '<br />'
    for xx in range (len(board)):
        strprt=''
        for yy in range(len(board[xx])):
            if board[xx][yy] == 0:
                strprt=strprt+'&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;<b style="color:red">00</b>'
            else:
                strprt=strprt+'&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;' + '{:02d}' .format(board[xx][yy])
        s += strprt + '&nbsp;&nbsp;&nbsp;|'
        s += strlev + '<br />'
    s += '</code>'
    return s

# -------------Board Playing--------------
def test_play(board,moves):
    count=0
    valid=test_is_valid(board)
    if valid:#==True:
        result = test_is_solved(board)
        if result:#==True:
            conn.sendall(b"\n\rThe given puzzle is already solved.")
            return board,count

        for num3 in moves:
            test_move(board, num3)
            result = test_is_solved(board)
            count+=1
            if result:#==True:
                conn.sendall(b"\n\rCongrulations!! You solved the puzzle.")
                return board,count

        conn.sendall(b"\n\t Sorry!! \n\t The puzzle could not be solved with the given movements.")
        print( test_print_board(board) )
        count=-1
    else:
        conn.sendall(b"\n\t Please enter the puzzle board again. \n\t The board matrix elements must be between [0:1:(row*column-1)])")
    return board,count

# -------------Self Playing--------------
def test_play_interactive1():
    Play_on = True
    while Play_on:
        Game_on = True
        row = int(input("\n Please type the puzzle size number. \n"" Row number:"))
        column = int(input("\n Column number:"))
        board = test_generate(row,column)
        board = test_shuffle(board, times=20)
        print( test_print_board(board) )
        allmove=0
        while Game_on==True:
            num = input('\n Please type the move (Left:L, Right:R, Up:U, Down:D): \n Press ( q ) to quit.')

            while True:
                if (num!="Q") and (num!="q") and (num!="r") and (num!="R") and (num!="l") \
                    and (num!="L") and (num!="d") and (num!="D") and (num!="u") and (num!="U"):
                    print('\n You typed wrong key. Please type again.')
                    num = input('\n Please type the move (Left:L, Right:R, Up:U, Down:D): \n Press ( q ) to quit. ')
                else:
                    break
            if num in ['q','Q']:
                print('\n\nGame over.')
                Play_on=False
                break
            else:
                if num in ['l','L']:
                    board, allmove = test_move_left(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['r','R']:
                    board, allmove = test_move_right(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['u','U']:
                    board, allmove = test_move_up(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['d','D']:
                    board, allmove = test_move_down(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:' )

            result = test_is_solved(board)
            print( test_print_board(board) )

            if result==True:
                Game_on = False
                print('\n Congrulations!! \n You solved the puzzle making' ,allmove,'movement.')
                again = input('\n To play again please press the key A: \n Press ( q ) to quit.')
                if again in ['q','Q']:
                    print('\n\n Game over.')
                    Play_on=False
                    break
                else:
                    board = test_reset(board)

    return board,allmove

# -------------Self Playing--------------
def test_play_interactive1():
    Play_on = True
    while Play_on:
        Game_on = True
        row = int(input("\n Please type the puzzle size number. \n"" Row number:"))
        column = int(input("\n Column number:"))
        board = test_generate(row,column)
        board = test_shuffle(board, times=20)
        print( test_print_board(board) )
        allmove=0
        while Game_on==True:
            num = input('\n Please type the move (Left:L, Right:R, Up:U, Down:D): \n Press ( q ) to quit.')

            while True:
                if (num!="Q") and (num!="q") and (num!="r") and (num!="R") and (num!="l") \
                    and (num!="L") and (num!="d") and (num!="D") and (num!="u") and (num!="U"):
                    print('\n You typed wrong key. Please type again.')
                    num = input('\n Please type the move (Left:L, Right:R, Up:U, Down:D): \n Press ( q ) to quit. ')
                else:
                    break
            if num in ['q','Q']:
                print('\n\nGame over.')
                Play_on=False
                break
            else:
                if num in ['l','L']:
                    board, allmove = test_move_left(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['r','R']:
                    board, allmove = test_move_right(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['u','U']:
                    board, allmove = test_move_up(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['d','D']:
                    board, allmove = test_move_down(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:' )

            result = test_is_solved(board)
            print( test_print_board(board) )
            if result==True:
                Game_on = False
                print('\n Congrulations!! \n You solved the puzzle making' ,allmove,'movement.')
                again = input('\n To play again please press the key A: \n Press ( q ) to quit.')
                if again in ['q','Q']:
                    print('\n\n Game over.')
                    Play_on=False
                    break
                else:
                    board = test_reset(board)
    return board,allmove


def test_play_interactive(board=None):
    Play_on = True
    while Play_on:
        Game_on = True

        if board is None:
            row = int(input("Please type the puzzle size number. \n""Row number:"))
            column = int(input("Column number:"))
            board = test_generate(row,column)
            board = test_shuffle(board, times=20)

        print( test_print_board(board) )
        allmove=0
        while Game_on==True:
            num = input('\n Please type the move (Left:L, Right:R, Up:U, Down:D, Random:M): \n Press ( q ) to quit.')

            while True:
                if (num!="Q") and (num!="q") and (num!="r") and (num!="R") and (num!="l") \
                    and (num!="L") and (num!="d") and (num!="D") and (num!="u") and (num!="U")and (num!="m") and (num!="M"):
                    print('\n You typed wrong key. Please type again.')
                    num = input('\n Please type the move (Left:L, Right:R, Up:U, Down:D, Random:M): \n Press ( q ) to quit. ')
                else:
                    break
            if num in ['q','Q']:
                print('\n\nGame over.')
                Play_on=False
                break
            else:
                if num in ['l','L']:
                    board, allmove = test_move_left(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['r','R']:
                    board, allmove = test_move_right(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['u','U']:
                    board, allmove = test_move_up(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:')
                elif num in ['d','D']:
                    board, allmove = test_move_down(board,allmove)
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:' )
                elif num in ['m','M']:
                    board = test_move_random(board)
                    allmove = allmove+1
                    print('\n you have made ', allmove , 'moves so far.\n Current board is:' )
            result = test_is_solved(board)
            print( test_print_board(board) )
            if result==True:
                Game_on = False
                print('\n Congrulations!! \n You solved the puzzle making' ,allmove,'movement.')
                again = input('\n To play again please press the key A: \n Press ( q ) to quit.')
                if again in ['q','Q']:
                    print('\n\n Game over.')
                    Play_on=False
                    break
                else:
                    board = test_reset(board)
    return board,allmove


#####################################
### This is where the magic happens #
#####################################
def test_play_network(conn):
    while True:
        conn.sendall(b'Welcome to the game of sliders.\n\r')
        conn.sendall(b'Row and Column sizes should be greater than 1.\n\r')

        while True:
            try:
                conn.sendall(b'Enter row size: ')
                row = int(conn.recv(20))
            except ValueError:
                row = 0

            if row > 1:
                break

        while True:
            try:
                conn.sendall(b'Enter column size: ')
                column = int(conn.recv(20))
            except ValueError:
                column = 0

            if column > 1:
                break

        board = test_generate(row, column)
        board = test_shuffle(board, times=20)

        s = test_print_board(board)
        conn.sendall(str.encode(s))
        allmove=0

        while True:
            while True:
                num = 'zzz'
                conn.sendall(b'\n\rLRUD, Random (M) or Quit (Q): ')
                num = conn.recv(10).decode("utf-8").strip().lower()

                if num not in 'qrudlm':
                    conn.sendall(b'\n\rWrong input, try again.')
                else:
                    break

            if num == 'q':
                conn.sendall(b'\n\rQuiting. Bye Bye.')
                return board, allmove, 0

            elif num == 'l':
                board, allmove = test_move_left(board,allmove)

            elif num == 'r':
                board, allmove = test_move_right(board,allmove)

            elif num == 'u':
                board, allmove = test_move_up(board,allmove)

            elif num == 'd':
                board, allmove = test_move_down(board,allmove)

            elif num == 'm':
                board = test_move_random(board)
                allmove += 1

            conn.sendall(str.encode(f'\n\ryou have made {allmove} moves so far.\n\rCurrent board is:'))

            s = test_print_board(board)
            conn.sendall(str.encode(s))

            if test_is_solved(board):
                conn.sendall(str.encode(f'\n\rCongrulations!! \n\rYou solved the puzzle making {allmove} movement.'))

                while True:
                    try:
                        again = 'zzz'
                        conn.sendall(b'\n\rPlay again (a) or Quit game (q):')

                        again = conn.recv(10).decode('utf-8').strip().lower()
                    except UnicodeError:
                        conn.sendall(b'Wrong key, try again')

                    if again == 'q' or again == 'a':
                        break
                    else:
                        conn.sendall(b'Wrong key, try again')


                if again == 'q':
                    conn.sendall(b'\n\rGame over. Bye Bye')
                    return board, allmove, 1
                elif again == 'a':
                    board = test_reset(board)
                    board = test_shuffle(board, times=20)
                    allmove = 0
                    break


        b, m, s = test_play_network(conn)


app = Flask(__name__)

@app.route('/')
def start():
    return render_template('board-start.html')


@app.route('/congrats')
def congrats():
    if 'board' not in session:
        return redirect(url_for('start'))
    else:
        a = session['allmove']
        b = session['board']
        r = len(b)
        c = len(b[0])
        del session['board']
        del session['allmove']
        return f"<h1>Congrats, you solved {r}x{c} board in {a} moves!</h1>"

@app.route('/board', methods=['POST'])
def initialize_board():
    if 'board' not in session:
        r = int(request.form['row'])
        c = int(request.form['column'])
        board = test_generate(r, c)
        t = r * c * 5
        board = test_shuffle(board, times=t)
        session['board'] = board
        session['allmove'] = 0

    return redirect(url_for('play_board'))

@app.route('/play', methods=['POST', 'GET'])
def play_board():
    if request.method == 'POST':

        comm = request.form['command']

        if comm == 'Go Left':
            session['board'], session['allmove'] = test_move_left(session['board'], session['allmove'])

        elif comm == 'Go Right':
            session['board'], session['allmove'] = test_move_right(session['board'], session['allmove'])

        elif comm == 'Go Up':
            session['board'], session['allmove'] = test_move_up(session['board'], session['allmove'])

        elif comm == 'Go Down':
            session['board'], session['allmove'] = test_move_down(session['board'], session['allmove'])

        elif comm == 'Go Random':
            session['board'] = test_move_random(session['board'])
            session['allmove'] += 1

        elif comm == 'Restart':
            del session['board']
            del session['allmove']
            return redirect(url_for('start'))

        session.modified = True

        if test_is_solved(session['board']):
            return redirect(url_for('congrats'))

        s = test_print_board(session['board'])

        s += f"<br />You made {session['allmove']} moves. <br />"

        return render_template('board-play-header.html') + s + render_template('board-play.html')

    elif request.method == 'GET':
        if 'board' in session:
            s = test_print_board(session['board'])
            return render_template('board-play-header.html') + s + render_template('board-play.html')
        else:
            return redirect(url_for('start'))


if __name__ == "__main__":
    app.secret_key = '12345'
    app.run(host="0.0.0.0", port=5000, debug=False)
