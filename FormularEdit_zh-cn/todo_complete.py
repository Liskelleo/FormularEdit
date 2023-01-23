import json, os, sys

from PyQt5.QtCore import QAbstractListModel, Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QImage, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QStatusBar

from todolist import Ui_MainWindow

basedir = os.path.dirname(__file__)
tick = QImage(os.path.join(basedir, r"icon\tick.png"))


class TodoModel(QAbstractListModel):
    def __init__(self, todos=None):
        super().__init__()
        self.todos = todos or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            status, text = self.todos[index.row()]
            return text
        if role == Qt.DecorationRole:
            status, text = self.todos[index.row()]
            if status:
                return tick

    def rowCount(self, index):
        return len(self.todos)


class MainWin(QMainWindow, Ui_MainWindow):
    shutdownValue2 = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('./icon/history.svg'))
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.model = TodoModel()
        self.load()
        self.todoView.setModel(self.model)
        self.deleteButton.pressed.connect(self.delete)
        self.todoView.clicked.connect(self.clicked)
        self.todoView.installEventFilter(self)

    def delete(self):
        length = len(self.model.todos)
        x, count = 0, 0
        while x < length:
            if self.model.todos[x][0]:
                del self.model.todos[x]
                count += 1
                x -= 1
                length -= 1
            x += 1
        self.model.layoutChanged.emit()
        self.todoView.clearSelection()
        self.save()
        self.statusBar.showMessage(u'已删除{}项!'.format(count), 0)

    def complete(self):
        indexes = self.todoView.selectedIndexes()
        index = [i.data() for i in indexes]
        if indexes:
            for index in indexes:
                status, text = self.model.todos[index.row()]
                if status:
                    self.model.todos[index.row()] = (False, text)
                else:
                    self.model.todos[index.row()] = (True, text)
                self.model.dataChanged.emit(index, index)
            self.todoView.clearSelection()
            self.save()

    def clicked(self,index):
        len_indexes = 0
        self.complete()
        for i in self.model.todos:
            if i[0]:
                len_indexes += 1
        self.statusBar.showMessage(u'已选中{}项!'.format(len_indexes), 0)

    def load(self):
        with open(r"./output/data.json", "r") as f:
            self.model.todos = json.load(f)
        if not len(self.model.todos):
            self.statusBar.showMessage(u'当前无保存的历史记录!', 0)

    def save(self):
        with open(r"./output/data.json", "w") as f:
            data = json.dump(self.model.todos, f)

    def closeEvent(self, event):
        self.shutdownValue2.emit(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWin()
    window.show()
    app.exec_()
