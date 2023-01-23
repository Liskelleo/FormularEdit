from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QTextEdit, QApplication, QAction


class NotepadTextEdit(QTextEdit):
    zoomSignal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.__scale = 100
        self.__min = 50#10
        self.__max = 250#400
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.__initUi()

    def __initUi(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__prepare_menu)

    def __prepare_menu(self, pos):
        menu = self.createStandardContextMenu()
        menu.exec(self.mapToGlobal(pos))

    def wheelEvent(self, e):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if e.angleDelta().y() > 0:
                self.zoomIn(10)
            else:
                self.zoomOut(10)
        return super().wheelEvent(e)

    def zoomInit(self):
        default_scale = 100
        if self.__scale > default_scale:
            while True:
                if self.__scale-10 < default_scale:
                    self.__scale = 100
                    self.zoomSignal.emit(self.__scale)
                    break
                self.zoomOut(10)
        else:
            while True:
                if self.__scale+10 > default_scale:
                    self.__scale = 100
                    self.zoomSignal.emit(self.__scale)
                    break
                self.zoomIn(10)

    def zoomIn(self, range: int = ...) -> None:
        if self.__scale < self.__max:
            super().zoomIn()
            self.__scale += 10
            self.zoomSignal.emit(self.__scale)

    def zoomOut(self, range: int = ...) -> None:
        if self.__scale > self.__min:
            super().zoomOut()
            self.__scale -= 10
            self.zoomSignal.emit(self.__scale)

    def setScale(self, scale):
        scale_diff = self.__scale - scale
        if scale_diff < 0:
            self.zoomIn()
        elif scale_diff > 0:
            self.zoomOut()
        else:
            pass

    def getScale(self):
        return self.__scale
    
    def keyPressEvent(self, e):
        # todo tab/backtab key feature
        tap_key_feature_code = '''
        if e.key() == Qt.Key_Tab:
            print('tab key pressed')
            tc = self.textCursor()
            if tc.hasSelection():
                print('')
            else:
                print('not selected')
        '''
        # zoomin/out with ctrl + numpad plus/minus shortcut feature
        if e.matches(QKeySequence.ZoomIn):
            self.zoomIn()
            return
        elif e.matches(QKeySequence.ZoomOut):
            self.zoomOut()
            return
        elif e.key() in (Qt.Key_Return, Qt.Key_Enter):#, Qt.Key_AsciiCircum, Qt.Key_Less, Qt.Key_Greater):
            return
        return super().keyPressEvent(e)

    def enterEvent(self, e): #mousePressEvent
        self.setReadOnly(False)
