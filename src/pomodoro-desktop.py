import sys
import threading
import configparser
from os import environ, path, makedirs
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import platform

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

if platform.system() == 'Windows':
    import balloontip as notifier # Windows notifier
    home_dir = environ['USERPROFILE']
else:
    import pynotifier as notifier # Linux notifier
    home_dir = environ['HOME']

config_folder = path.join(path.join(home_dir, ".config/pomo/"))
config_file = path.join(config_folder, "pomo.ini")
config = configparser.ConfigParser(strict=False)
if not path.exists(config_file):
    config['DEFAULT'] = {'pomo_time' : 25,
                         'break_time' : 5,
                         'long_break' : 4,
                         'long_break_time' : 30}

    makedirs(config_folder)
    with open(config_file, 'w') as f:
        config.write(f)
else:
    with open(config_file) as f:
        config.read_file(f)

icons = {icon : path.join(sys.path[0], '../icons', icon + '.png')
            for icon in ['Go', 'Wait', 'Stop']}

pomo_time = config.getint('DEFAULT','pomo_time') 
break_time = config.getint('DEFAULT','break_time')
long_break = config.getint('DEFAULT','long_break')
long_break_time = config.getint('DEFAULT','long_break_time')

pomo_timer = None
counter = 0
started = False

def notify(msg, duration=20, title="Pomodoro"):
    if platform.system() != 'Windows':
        notifier.Notification(
                title=title,
                description=msg,
                duration=duration).send()
    else:
        notifier.balloon_tip(title=title,
            msg=msg)

def end_pomo():
    global started, counter
    counter+=1 
    started = False
    tray.setIcon(QIcon(icons['Stop']))
    if counter % long_break == 0:
        notify(f"Take a break for {long_break_time} minutes.",
            title='LONG BREAK') 
        sleep(long_break_time * 60)
    else:
        notify(f"Take a break for {break_time} minutes.",
            title='SHORT BREAK')
        sleep(break_time * 60)

    if not started:
        tray.setIcon(QIcon(icons['Wait']))
        notify("You should probably get back to work")

def start():
    global started, counter, pomo_timer
    if not started:
        if pomo_timer:
            pomo_timer.cancel()
        tray.setIcon(QIcon(icons['Go']))
        started = True
        notify(f"You got {pomo_time} minutes to work.", title='WORK')
        pomo_timer = threading.Timer(pomo_time * 60, end_pomo)
        pomo_timer.start()
    else:
        notify("Already in the middle of a pomodoro.")

def stop_work():
    global pomo_timer, started
    if pomo_timer:
        started = False
        tray.setIcon(QIcon(icons['Wait']))
        pomo_timer.cancel()
        if started:
            notify("Alright take your unscheduled break...")

def quit():
    global pomo_timer
    if pomo_timer:
        pomo_timer.cancel()
    app.quit()


# Create the icon
icon = QIcon(icons['Wait'])

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# Create the menu
menu = QMenu()
quit_action = QAction("Quit")
quit_action.triggered.connect(quit)

start_action = QAction("Start Pomodoro")
start_action.triggered.connect(start)

stop_action = QAction("End Pomodoro")
stop_action.triggered.connect(stop_work)

# add all actions to menu
menu.addAction(start_action)
menu.addAction(stop_action)

menu.addAction(quit_action)

# Add the menu to the tray
tray.setContextMenu(menu)

app.exec_()

