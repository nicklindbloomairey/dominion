import curses
import curses.textpad
import os

users = {'foo':'bar', 'guest':'secret'}

#globals
loggedin = False
user = None

def login(sc):
    global loggedin
    global user
    sc.clear()
    sc.addstr(1,1,'##')
    sc.addstr(1,4,' pythonlaunch', curses.color_pair(2) | curses.A_BOLD)
    sc.addstr(2,1,'##')
    sc.addstr(3,1,'## written by nicolas lindbloom airey')
    while True:
        sc.addstr(5, 3, 'enter username (blank line aborts)')
        sc.addstr(7, 3, '=> ')
        curses.echo()
        username = sc.getstr().decode('utf-8') 
        curses.noecho()
        if username == '':
            menu(sc)
            return
        if username in users:
            break
        sc.clear()
        sc.addstr(4, 3, 'user does not exist')
    sc.move(5,1)
    sc.clrtobot()
    while True:
        sc.addstr(5, 3, 'enter password (blank line aborts)')
        sc.addstr(7, 3, '=> ')
        curses.echo()
        password = sc.getstr().decode('utf-8')
        curses.noecho()
        if password == '':
            menu(sc)
            return
        if users[username] == password:
            loggedin = True
            user = username
            menu_loggedin(sc)
        sc.clear()
        sc.addstr(4, 3, password+' incorrect password')

    return

def menu(sc):
    global loggedin
    global user
    sc.clear()
    if loggedin:
        return menu_loggedin(sc)
    sc.addstr(1,1,'##')
    sc.addstr(1,4,' pythonlaunch', curses.color_pair(2) | curses.A_BOLD)
    sc.addstr(2,1,'##')
    sc.addstr(3,1,'## written by nicolas lindbloom airey')
    if not loggedin:
        sc.addstr(5,3,'Not logged in.')
    sc.addstr(7,3,'l) Login')
    sc.addstr(8,3,'r) Register new user')
    sc.addstr(9,3,'p) play as guest')

    #sc.addstr(10,3,'s) server info')

    sc.addstr(12,3,'q) Quit')

    sc.addstr(16, 3, '=> ')
    while True:
        option = sc.getch()
        if option == ord('l'):
            login(sc)
        if option == ord('p'):
            loggedin = True
            user = 'guest'
            menu_play(sc)
        elif option == ord('q'):
            exit()
    return

def menu_loggedin(sc):
    sc.clear()
    sc.addstr(1,1,'##')
    sc.addstr(1,4,' pythonlaunch', curses.color_pair(2) | curses.A_BOLD)
    sc.addstr(2,1,'##')
    sc.addstr(3,1,'## written by nicolas lindbloom airey')
    sc.addstr(5,3,'Logged in as: ')
    sc.addstr(5,17,user, curses.A_BOLD)
    sc.addstr(7,3,'c) change password')
    sc.addstr(8,3,'p) play')
    sc.addstr(10,3,'s) server info')
    sc.addstr(12,3,'q) Quit')
    sc.addstr(16, 3, '=> ')
    while True:
        option = sc.getch()
        if option == ord('p'):
            menu_play(sc)
        elif option == ord('c'):
            pass
        elif option == ord('q'):
            exit()
    return

def menu_play(sc):
    sc.move(6,1)
    sc.clrtobot()
    if loggedin:
        sc.addstr(5,3,'Logged in as: ')
        sc.addstr(5,17,user, curses.A_BOLD)
    sc.addstr(7,3,'a) hello world')
    sc.addstr(8,3,'b) dominion text 1.0')
    sc.addstr(9,3,'c) dominion curses 1.1')
    sc.addstr(12,3,'q) Quit')
    sc.addstr(16, 3, '=> ')
    while True:
        option = sc.getch()
        curses.endwin() #options that end the window
        if option == ord('q'):
            exit()
        elif option == ord('a'):
            os.execvp('python3', ['python3', 'hello.py'])
        elif option == ord('b'):
            os.execvp('python3', ['python3', 'dominion1.0.py'])
        elif option == ord('c'):
            os.execvp('python3', ['python3', 'dominion_curses1.1.py'])

def main(sc):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    while True:
        menu(sc)
    
if __name__ == '__main__':
    curses.wrapper(main)
