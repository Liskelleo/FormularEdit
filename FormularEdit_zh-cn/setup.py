#-*- coding: utf-8                  -*-
#-*- author: liskelleo              -*-
#-*- update: 2023.1.23              -*-
#-*- email:  liskello_o@outlook.com -*-


import datetime
import os, re, sys, json
import subprocess, traceback

from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread, QThreadPool, \
     QRunnable, QEvent, QSize
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QMenuBar, QTextEdit, \
     QGridLayout, QAction, QStatusBar, QWidgetAction, QMessageBox, QTreeWidgetItem, \
     QLabel, QSlider, QPushButton, QLineEdit, QHBoxLayout, QWidget, QActionGroup
from PyQt5.QtWebEngineWidgets import QWebEngineView

from pyqt5ui import Ui_FormularEdit
from pyqt_instant_search_bar import InstantSearchBar
from pyqt_hidable_menubar import HidableMenuBar
from qt_sass_theme.qtSassTheme import QtSassTheme


class Flag:
    flag = False


class Hook:
    app = QApplication(sys.argv)
    def __init__(self, logdir=None):
        self.logdir = logdir

    def __call__(self, etype, evalue, etb):
        info = (etype, evalue, etb)
        doc = ''.join(traceback.format_exception(*info))
        with open(os.path.join(os.path.dirname(__file__),self.logdir,'error.log'),'a') as ed:
            ed.write('{0} {1}\n{2}{3}'.format(os.getlogin(),
                                    datetime.datetime.now(), doc, '\n'))
        Flag.flag = True
        self.app.quit()

sys.excepthook = Hook(logdir='output')

import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['axes.spines.left'] = False
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False
matplotlib.rcParams['axes.spines.bottom'] = False
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

text_kwargs = 50
last_speres, vflag = None, None
sflag, cflag, cflag2, fflag = False, False, False, False


class MainDegbug(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui()

    def ui(self):
        self.setWindowTitle('出现错误')
        self.setFixedSize(self.width(),self.height())
        self.setWindowIcon(QIcon('./icon/debug.svg'))
        label = QLabel(self)
        label.setText("'setup.exe'因发生致命错误而终止运行!")
        label.setStyleSheet("font-family:'Arial';font-size:23px")
        label.resize(550,28)
        label.move(70,25)
        pic = QPixmap('./icon/error.svg')
        label2 = QLabel(self)
        label2.setPixmap(pic)
        label2.resize(32,32)
        label2.setScaledContents(True)
        label2.move(25,23)
        textedit = QTextEdit(self)
        with open('./output/error.log','r',encoding='utf-8') as readError:
            error = readError.read()
        textedit.setPlainText(error)
        textedit.setReadOnly(True)
        textedit.resize(590,330)
        textedit.move(25,80)
        textedit.setLineWrapMode(True)
        pic2 = QIcon('./icon/help.svg')
        button = QPushButton(self)
        button.setText('出现了bug? 反馈给作者!')
        button.setIcon(pic2)
        button.resize(300,35)
        button.move(315,428)
        button.show()
        button.pressed.connect(self.sendmail)
    
    def sendmail(self):
        import webbrowser
        webbrowser.open('https://github.com/liskelleo/FormularEdit/issues/new')


class createFormula_Thread(QThread):

    def __init__(self):
        super().__init__()

    def setCmd(self, speres, widget):
        self.speres = speres
        self.F = widget

    def run(self):
        self.speres = MainDialogImgBW.check(self.speres)
        try:
            if cflag2:
                self.speres = MainDialogImgBW.s_filter(self.speres)
            if cflag:
                self.speres = MainDialogImgBW.exp_filter(self.speres)
            self.F.axes.cla()
            self.F.axes.text(0.5,0.5,'${}$'.format(self.speres),ha='center',va='center',fontsize=text_kwargs)
            self.F.draw()
        except:
            self.F.axes.cla()
            pass
        
    def __del__(self):
        self.quit()
        self.requestInterruption()
        self.wait()


class WorkerSignals(QObject):
    result = pyqtSignal(str)
    finished = pyqtSignal()


class SubProcessWorker(QRunnable):

    def __init__(self, command):
        super().__init__()
        self.signals = WorkerSignals()
        self.command = command

    @pyqtSlot()
    def run(self):
        output = subprocess.getoutput(self.command)
        self.signals.result.emit(output)
        self.signals.finished.emit()


class MyFigure(FigureCanvas):
    changeValue = pyqtSignal(bool)
    def __init__(self, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MyFigure, self).__init__(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.axes.axes.xaxis.set_visible(False)
        self.axes.axes.yaxis.set_visible(False)
        
    def wheelEvent(self, event):
        global text_kwargs
        angle = event.angleDelta() / 8
        angleY = angle.y()
        if angleY > 0:
            text_kwargs += 5
        else:
            text_kwargs -= 5
        self.changeValue.emit(True)


class SearchBarMenu(QMenu):
    changeValue = pyqtSignal(str)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.searchBar = InstantSearchBar()
        self.__actions = []
        self.text_list = []
        self.__initUi()

    def __initUi(self):
        self.searchLineEdit = self.searchBar.getSearchBar()
        self.searchLineEdit.setPlaceholderText("此处搜索更多...")
        self.searchLineEdit.textChanged.connect(self.__searchLineEditTextChanged)
        self.searchAction = QWidgetAction(self)
        self.searchAction.setDefaultWidget(self.searchBar)
        self.addAction(self.searchAction)
        
    def addAction(self, action: QAction) -> None:
        super().addAction(action)
        if action in self.__actions:
            pass
        else:
            self.__actions.append(self.actions()[-1])
            self.text_list.append(action)
            self.actions()[-1].triggered.connect(self.lineedit_set_text)
        for action in self.__actions[1:-5]:
            action.setVisible(False)
    
    def clear(self):
        for action in self.__actions[1:]:
            self.removeAction(action)
                
    def __searchLineEditTextChanged(self, text):
        actions = self.__actions[1:]
        if text.strip() != '':
            for action in actions:
                action_text = action.text()
                if action_text.startswith(text):
                    if action.isVisible():
                        pass
                    else:
                        action.setVisible(True)
                else:
                    action.setVisible(False)
        else:
            for action in actions:
                action.setVisible(True)
            for action in actions[:-5]:
                action.setVisible(False)
        
    def lineedit_set_text(self):
        actions = [str(x) for x in self.__actions[:]]
        btn = str(self.sender())
        text = self.text_list[actions.index(btn)]
        try:
            self.searchLineEdit.setText(text)
            self.changeValue.emit(str(self.searchLineEdit.text()))
        except:
            pass


class MainDialogImgBW(QMainWindow, Ui_FormularEdit):
    shutdownValue = pyqtSignal(tuple)
    def __init__(self):
        super(MainDialogImgBW, self).__init__() 
        self.setWindowIcon(QIcon('./icon/FormularEdit.svg'))
        self.setMinimumSize(600,525)
        self.setMaximumSize(600,525)
        self.resize(605, 525)
        self.setupUi(self)

        try:
            with open(r"./output/data.json", "r") as fr:
                self.todo = json.load(fr)
        except:
            self.todo = []
        self.sbm = SearchBarMenu('搜索记录', self)
        self.sbm.installEventFilter(self)
        self.initMenu()

        self.textEdit.setAcceptRichText(False)
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.zoomSignal.connect(self.__zoomByWheel)
        
        self.F = MyFigure(width=5, height=4, dpi=100)
        self.gridlayout = QGridLayout(self.groupBox)
        self.gridlayout.addWidget(self.F,0,1)

        self.F.changeValue.connect(self.result)
        
        self.threadpool = QThreadPool()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setSizeGripEnabled(False)

        self.__zoomScaleText = '字体大小: {0}% '
        self.__charsLinesCountText = '字符数: {0}'
        self.__charsLinesCountLabel = QLabel('字符数: 0')

        text = self.__zoomScaleText.format(self.textEdit.getScale())
        self.__zoomScaleLabel = QLabel()
        self.__zoomScaleLabel.setText(text)

        self.__zoomScaleSlider = QSlider()
        self.__zoomScaleSlider.setOrientation(Qt.Horizontal)
        self.__zoomScaleSlider.setRange(50, 250)
        self.__zoomScaleSlider.setValue(self.textEdit.getScale())
        self.__zoomScaleSlider.valueChanged.connect(self.__zoomScaleSliderValueChanged)

        self.__zoomScaleSlider.setTickInterval(10)
        self.__zoomScaleSlider.setSingleStep(10)
        self.__zoomScaleSlider.setMaximumWidth(self.__zoomScaleSlider.sizeHint().width())

        self.statusBar.addPermanentWidget(self.__zoomScaleLabel)
        self.statusBar.addPermanentWidget(self.__zoomScaleSlider)
        self.statusBar.addPermanentWidget(self.__charsLinesCountLabel)
        
        self.location = None
        self.dockWidget.setVisible(False)
        self.dockWidget.setFeatures(self.dockWidget.DockWidgetClosable|self.dockWidget.DockWidgetFloatable)
        self.dockWidget.topLevelChanged.connect(self.windowchange)
        self.dockWidget.visibilityChanged.connect(self.HideTool)

        t = QtSassTheme()
        t.getThemeFiles(theme='light_gray', font_size=10)
        t.setThemeFiles(main_window=self)
        self.show()

    def initMenu(self):
        self.sbm.changeValue.connect(self.getValue)

        hidableMenuBar = HidableMenuBar()
        hidableMenuBar.hideSignal.connect(self.changeHeight)
        
        self.filemenu = QMenu('文件(&F)', self)
        self.save_action = QAction(self)
        self.save_action.setCheckable(False)
        self.save_action.setObjectName('saveAction')
        self.save_action.triggered.connect(self.save_history)
        self.save_action.setText('保存公式')
        self.save_action.setShortcut('Ctrl+S')
        
        self.savefig_action = QAction(self)
        self.savefig_action.setCheckable(False)
        self.savefig_action.setObjectName('savefigAction')
        self.savefig_action.triggered.connect(self.SaveFig)
        self.savefig_action.setText('保存图片')
        self.savefig_action.setShortcut('Alt+S')

        self.quit_action = QAction(self)
        self.quit_action.setCheckable(False)
        self.quit_action.setObjectName('quitAction')
        self.quit_action.triggered.connect(self.quit)
        self.quit_action.setText('快捷退出')
        self.quit_action.setShortcut('Esc')

        self.filemenu.addAction(self.save_action)
        self.filemenu.addAction(self.savefig_action)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.quit_action)

        self.filemenu1 = QMenu('历史(&R)', self)
        self.filemenu1.installEventFilter(self)
        
        for i in self.todo:
            action = self.sbm.addAction(f'{i[1]}')

        self.manage_action = QAction(self)
        self.manage_action.setCheckable(False)
        self.manage_action.setObjectName('manageAction')
        self.manage_action.triggered.connect(self.manage_history)
        self.manage_action.setText('管理记录')

        self.clear_action = QAction(self)
        self.clear_action.setCheckable(False)
        self.clear_action.setObjectName('clearAction')
        self.clear_action.triggered.connect(self.clear_history)
        self.clear_action.setText('清除缓存')

        self.filemenu1.addMenu(self.sbm)
        self.filemenu1.addAction(self.manage_action)
        self.filemenu1.addAction(self.clear_action)

        self.filemenu2 = QMenu("工具", self)
        self.left_action = QAction(self)
        self.left_action.setCheckable(False)
        self.left_action.setObjectName('leftAction')
        self.left_action.triggered.connect(self.ShowLeftTool)
        self.left_action.setText('左栏显示')
        self.left_action.setCheckable(True)

        self.right_action = QAction(self)
        self.right_action.setCheckable(False)
        self.right_action.setObjectName('rightAction')
        self.right_action.triggered.connect(self.ShowRightTool)
        self.right_action.setText('右栏显示')
        self.right_action.setCheckable(True)

        self.filemenu2.addAction(self.left_action)
        self.filemenu2.addAction(self.right_action)

        self.filemenu3 = QMenu("设置(&S)", self)
        self.filemenu3_1 = QMenu("格式", self)
        self.subscript_action = QAction(self)
        self.subscript_action.setCheckable(False)
        self.subscript_action.setObjectName('subscriptAction')
        self.subscript_action.triggered.connect(self.subscript)
        self.subscript_action.setText('自由下标')
        self.subscript_action.setCheckable(True)
        self.subscript_action.setChecked(False)

        self.superscript_action = QAction(self)
        self.superscript_action.setCheckable(False)
        self.superscript_action.setObjectName('superscriptAction')
        self.superscript_action.triggered.connect(self.superscript)
        self.superscript_action.setText('特殊上标')
        self.superscript_action.setCheckable(True)
        self.superscript_action.setChecked(False)

        self.phy_action = QAction(self)
        self.phy_action.setCheckable(False)
        self.phy_action.setObjectName('phyAction')
        self.phy_action.triggered.connect(self.replacephy)
        self.phy_action.setText('物理常量识别')
        self.phy_action.setCheckable(True)
        self.phy_action.setChecked(False)

        self.filemenu3_2 = QMenu("主题(&T)", self)
        self.light_action = QAction(self)
        self.light_action.setObjectName('lightAction')
        self.light_action.triggered.connect(self.__themeToggled)
        self.light_action.setText('明亮模式')
        self.light_action.setCheckable(True)
        self.light_action.setChecked(True)

        self.dark_action = QAction(self)
        self.dark_action.setObjectName('darkAction')
        self.dark_action.triggered.connect(self.__themeToggled1)
        self.dark_action.setText('暗黑模式')
        self.dark_action.setCheckable(True)
        self.dark_action.setChecked(False)

        self.darkblue_action = QAction(self)
        self.darkblue_action.setObjectName('darkblueAction')
        self.darkblue_action.triggered.connect(self.__themeToggled2)
        self.darkblue_action.setText('深蓝模式')
        self.darkblue_action.setCheckable(True)
        self.darkblue_action.setChecked(False)

        self.blue_action = QAction(self)
        self.blue_action.setObjectName('blueAction')
        self.blue_action.triggered.connect(self.__themeToggled3)
        self.blue_action.setText('浅蓝模式')
        self.blue_action.setCheckable(True)
        self.blue_action.setChecked(False)

        self.filemenu3.addMenu(self.filemenu3_1)
        self.filemenu3_1.addAction(self.subscript_action)
        self.filemenu3_1.addAction(self.superscript_action)
        self.filemenu3_1.addAction(self.phy_action)
        self.filemenu3.addMenu(self.filemenu2)
        self.filemenu3_2.addAction(self.light_action)
        self.filemenu3_2.addAction(self.dark_action)
        self.filemenu3_2.addAction(self.darkblue_action)
        self.filemenu3_2.addAction(self.blue_action)
        self.action_group = QActionGroup(self)
        self.action_group.addAction(self.light_action)
        self.action_group.addAction(self.dark_action)
        self.action_group.addAction(self.darkblue_action)
        self.action_group.addAction(self.blue_action)

        self.filemenu4 = QMenu("帮助(&H)", self)
        self.doc_action = QAction(self)
        self.doc_action.setCheckable(False)
        self.doc_action.setObjectName('docAction')
        self.doc_action.triggered.connect(self.DocHelp)
        self.doc_action.setText('帮助文档')

        self.aboutus_action = QAction(self)
        self.aboutus_action.setCheckable(False)
        self.aboutus_action.setObjectName('aboutusAction')
        self.aboutus_action.triggered.connect(self.AboutUs)
        self.aboutus_action.setText('关于')
        
        self.filemenu4.addAction(self.doc_action)        
        self.filemenu4.addAction(self.aboutus_action)

        hidableMenuBar.addMenu(self.filemenu)
        hidableMenuBar.addMenu(self.filemenu1)
        hidableMenuBar.addMenu(self.filemenu3)
        hidableMenuBar.addMenu(self.filemenu3_2)
        hidableMenuBar.addMenu(self.filemenu4)
        
        self.setMenuBar(hidableMenuBar)
            
    def getValue(self, val):
        self.textEdit.setText(val)
        self.sbm.searchLineEdit.clear()

    def __themeToggled(self):
        t = QtSassTheme()
        t.getThemeFiles(theme='light_gray', font_size=10)
        t.setThemeFiles(main_window=self)

    def __themeToggled1(self):
        t = QtSassTheme()
        t.getThemeFiles(theme='dark_gray', font_size=10)
        t.setThemeFiles(main_window=self)
    
    def __themeToggled2(self):
        t = QtSassTheme()
        t.getThemeFiles(theme='dark_blue', font_size=10)
        t.setThemeFiles(main_window=self)
    
    def __themeToggled3(self):
        t = QtSassTheme()
        t.getThemeFiles(theme='light_blue', font_size=10)
        t.setThemeFiles(main_window=self)
    
    @staticmethod
    def check(key):
        key = str(key)
        if '\\ll' not in key and '\\gg' not in key and '\\oplus' not in key:
            rule = r"(?<=[})\w\|])\s+?(?={\d|\d})"
            pattern1 = re.compile(rule)
            newKey = re.sub(rule, "×", key)
            return newKey
        else:
            return key

    @staticmethod
    def check2(key):
        key = str(key)
        rule = r"(?<=\d|\d)[e]+?(?=\d|\-)"
        pattern = re.compile(rule)
        newKey = re.sub(rule, "*10**", key)
        return newKey
    
    @staticmethod
    def check3(key, *rep):
        key = str(key)
        for i in rep:
            rule = r"{}([^)]+)".format(i)
            pattern = re.compile(rule)
            new_key = re.sub(rule, '$', key)
            mat_str = re.findall(rule, key)
            for x in mat_str:
                new_key = new_key.replace('$)', '{}({}))'.format(i,x), 1)
            key = new_key
        newKey = new_key
        return newKey
        
    @staticmethod
    def s_filter(exp):
        exp = str(exp)
        if '_bar' in exp:
            c = exp.count('_bar')
            for _ in range(c):
                beg = exp.index('_bar')
                if exp[beg-1].isalpha():
                    mod = exp[beg-1:beg+4]
                    modf = r'\bar{' + exp[beg-1] + '}'
                try:
                    exp = exp.replace(mod,modf,1)
                except:
                    exp = exp.replace('_bar','',1)
        if '_tilde' in exp:
            c = exp.count('_tilde')
            for _ in range(c):
                beg = exp.index('_tilde')
                if exp[beg-1].isalpha():
                    mod = exp[beg-1:beg+6]
                    modf = r'\tilde{' + exp[beg-1] + '}'
                try:
                    exp = exp.replace(mod,modf,1)
                except:
                    exp = exp.replace('_tilde','',1)
        if '_dot' in exp:
            c = exp.count('_dot')
            for _ in range(c):
                beg = exp.index('_dot')
                if exp[beg-1].isalpha():
                    mod = exp[beg-1:beg+4]
                    modf = r'\dot{' + exp[beg-1] + '}'
                try:
                    exp = exp.replace(mod,modf,1)
                except:
                    exp = exp.replace('_dot','',1)
        if '_hat' in exp:
            c = exp.count('_hat')
            for _ in range(c):
                beg = exp.index('_hat')
                if exp[beg-1].isalpha():
                    mod = exp[beg-1:beg+4]
                    modf = r'\hat{' + exp[beg-1] + '}'
                try:
                    exp = exp.replace(mod,modf,1)
                except:
                    exp = exp.replace('_hat','',1)
        return exp

    @staticmethod
    def exp_filter(exp):
        exp = str(exp)
        explst = exp.split()
        fname = explst[0]
        if '_' in fname:
            fname = fname.replace('_', '_{')
            n = fname.count('_')
            try:
                k = fname.index('(')
                for _ in range(n):
                    fname = fname[:k] + '}' + fname[k:]
            except:
                for _ in range(n):
                    fname = fname + '}'
            exp = exp.replace(explst[0],fname)
        for x, y in zip(explst[1:], range(1,len(explst))):
            if '_' in x and '{' not in x and ']' not in x:
                x = '{' + x
                x = x.replace('_', '_{')
                n = x.count('_')
                for _ in range(n+1):
                    x = x + '}'
                exp = exp.replace(explst[y],x)
        return exp

    @staticmethod
    def formula_filter(exp):
        exp = str(exp)
        if "(e)" in exp:
            exp = exp.replace("(e)", "1.602176565e-19")
        elif "(c)" in exp: 
            exp = exp.replace("(c)", "2.99792458e8")
        elif "(h)" in exp:
            exp = exp.replace("(h)", "6.62606957e-34")
        elif "(G)" in exp:
            exp = exp.replace("(G)", "6.67384e-11")
        elif "(N_A)" in exp:
            exp = exp.replace("(N_A)", "6.02214129e23")
        elif "(R)" in exp:
            exp = exp.replace("(R)", "8.3144621")
        elif "(k)" in exp:
            exp = exp.replace("(k)", "1.3806488e-23")
        elif "(epsilon)" in exp:
            exp = exp.replace("(epsilon)", "8.85418781762e-12")
        elif "(mu)" in exp:
            exp = exp.replace("(mu)", "4*pi*e-7")
        elif "(e_m)" in exp:
            exp = exp.replace("(e_m)", "9.10938291e-31")
        return exp

    def eventFilter(self, obj, event):
        if obj is self.sbm and event.type() == QEvent.Move:
            self.textEdit.setReadOnly(True)
            return True
        if obj is self.filemenu1 and event.type() == QEvent.Enter:
            self.textEdit.setReadOnly(True)
            return True
        if obj is self.filemenu1 and event.type() == QEvent.Close:
            self.sbm.searchLineEdit.clear()
            self.textEdit.setReadOnly(False)
            return False
        return False

    @pyqtSlot()
    def on_textEdit_textChanged(self):
        global last_formular
        formular = self.textEdit.toPlainText()
        if len(formular) <= 150:
            self.__charsLinesCountLabel.setText(self.__charsLinesCountText.format(len(formular)))
            formular = self.check2(formular)
            with open('./background.py','r') as f_read:
                content = f_read.read()
            if '=' not in formular:
                content = content.replace('formular_to_be_replaced', formular)
                content = content.replace('delete_functionName_and_eq',
                "formular = formular.replace('\\mathrm{functionName}() =','')")
                content = content.replace('delete_bracket',"")
            else:
                content = content.replace('delete_functionName_and_eq',"")
                formular_name = formular.split('=')[0]
                formular_content = formular.split('=')[1]
                if '(' not in formular_name:
                    content = content.replace('functionName',formular_name)
                    content = content.replace('formular_to_be_replaced',formular_content)
                    content = content.replace('delete_bracket',
                    "formular = formular.replace('()','')")
                else:
                    formular_name_wo_bracket = formular_name.split('(')[0]
                    content = content.replace('functionName()',formular_name)
                    content = content.replace('functionName',formular_name_wo_bracket)
                    content = content.replace('formular_to_be_replaced',formular_content)
                    content = content.replace('delete_bracket',
                    "formular = formular.replace('()','')")
            with open('run_cache','w') as f_write:
                try:
                    f_write.write(content)
                except:
                    self.statusBar.showMessage(u'输入非法字符!', 1000)
            self.runner = SubProcessWorker("python run_cache")
            self.runner.signals.result.connect(self.result)
            self.threadpool.start(self.runner)
        else:
            self.statusBar.showMessage(u'超出了字数限制150!', 1000)

    def result(self, signal):
        global last_speres, text_kwargs
        if self.sender() is self.F and last_speres is not None:
            self.statusBar.showMessage(u'当前缩放比例:{}%'.format(text_kwargs+50), 500)
            speres = last_speres
            self.xxx = createFormula_Thread()
            self.xxx.setCmd(speres, self.F)
            self.xxx.start()
        else:
            try:
                if 'Error' not in signal:
                    if 'SyntaxWarning' in signal:
                        self.statusBar.showMessage(u'下标用法错误!', 1000)
                        self.F.axes.cla()
                        self.F.draw()
                    else:
                        speres = signal
                        last_speres = speres
                        self.xxx = createFormula_Thread()
                        self.xxx.setCmd(speres, self.F)
                        self.xxx.start()
                elif 'NoneType' in signal:
                    self.statusBar.showMessage(u'输入为空!', 1000)
                    self.F.axes.cla()
                    self.F.draw()
                    last_speres = None
                elif 'Non-UTF-8' in signal:
                    self.statusBar.showMessage(u'输入了非法字符!', 1000)
                    self.F.axes.cla()
                    self.F.draw()
                elif "SyntaxError" in signal:
                    if 'unmatched' in signal:
                        self.statusBar.showMessage(u'请补全括号!', 1000)
                        self.F.axes.cla()
                        self.F.draw()
                        last_speres = None
                    elif 'invalid syntax' in signal:
                        self.statusBar.showMessage(u'用法错误!', 1000)
                        self.F.axes.cla()
                        self.F.draw()
            except:
                self.F.axes.cla()
                self.F.draw()
                pass

    def __zoomByWheel(self, n):
        self.__zoomScaleLabel.setText(self.__zoomScaleText.format(n))
        self.__zoomScaleSlider.setValue(n)

    def __zoomIn(self):
        self.textEdit.zoomIn(10)
        self.__zoomScaleLabel.setText(self.__zoomScaleText.format(self.textEdit.getScale()))
        self.__zoomScaleSlider.setValue(self.textEdit.getScale())

    def __zoomOut(self):
        self.textEdit.zoomOut(10)
        self.__zoomScaleLabel.setText(self.__zoomScaleText.format(self.textEdit.getScale()))
        self.__zoomScaleSlider.setValue(self.textEdit.getScale())

    def __zoomReset(self):
        self.textEdit.zoomInit()
        self.__zoomScaleLabel.setText(self.__zoomScaleText.format(100))
        self.__zoomScaleSlider.setValue(self.textEdit.getScale())

    def __zoomScaleSliderValueChanged(self, v):
        v = v - v % 10
        self.textEdit.setScale(v)
        text = self.__zoomScaleText.format(self.textEdit.getScale())
        self.__zoomScaleLabel.setText(text)
        self.__zoomScaleLabel.setMaximumWidth(self.__zoomScaleLabel.fontMetrics().boundingRect(text).width()+5)

    def clear_history(self,event):
        reply = QMessageBox.question(self,"提示","是否清空所有历史记录?",QMessageBox.Yes,QMessageBox.No)
        if reply == QMessageBox.Yes:
            with open('./output/data.json', 'w') as fx:
                fx.truncate(0)
                data = json.dump([], fx)
            self.sbm.clear()
            self.statusBar.showMessage(u'已清空历史记录!', 1000)
    
    def save_history(self):
        global sflag, fflag
        reply = QMessageBox.question(self,"提示","是否保存到历史记录?",QMessageBox.Yes,QMessageBox.No)
        if reply == QMessageBox.Yes:
            close_flag = True
            cmd = os.popen('python run_cache')
            flag_str = cmd.read().rstrip()
            flag = bool(flag_str)
            cmd.close()
            try:
                with open('run_cache','r') as wp:
                    reslst = wp.readlines()
                funcname = reslst[4]
                last_formular = reslst[5].split()[1]
            except FileNotFoundError:
                close_flag = False
                last_formular = None
            except IndexError:
                last_formular = None
            if last_formular is None:
                QMessageBox.warning(self,"警告","输入为空!",QMessageBox.Yes)
            elif not flag:
                QMessageBox.warning(self,"警告","存在错误, 请检查输入的表达式!",QMessageBox.Yes)
            else:
                if 'functionName' not in funcname:
                    funcname = funcname[4:]
                    funcname = funcname.split('(')[0]
                    with open(r"./output/data.json", "w") as f:
                        fml = '{}={}'.format(funcname, last_formular)
                        self.sbm.addAction(fml)
                        self.todo.append([False, fml])
                        data = json.dump(self.todo, f)
                    if fflag:
                        emitformula = self.formula_filter(self.check3(last_formular,'max','min','sum','prod'))
                    else:
                        emitformula = self.check3(last_formular,'max','min','sum','prod')
                    self.shutdownValue.emit(((funcname, emitformula), 0))
                    if close_flag:os.remove('run_cache')
                    sflag = True
                    self.setWindowTitle("公式编辑器")
                else:
                    QMessageBox.warning(self,"警告","请输入含有新变量的表达式!",QMessageBox.Yes)
        else:
            self.shutdownValue.emit((False, 0))
    
    def SaveFig(self):
        pixmap = self.F.grab()
        QApplication.clipboard().setPixmap(pixmap)
        self.statusBar.showMessage(u'图片已保存到剪贴板!', 1000)

    def closeEvent(self, event):
        global sflag, fflag
        if not sflag:
            close_flag = True
            cmd = os.popen('python run_cache')
            flag_str = cmd.read().rstrip()
            flag = bool(flag_str)
            cmd.close()
            try:
                with open('run_cache','r') as wp:
                    reslst = wp.readlines()
                funcname = reslst[4]
                last_formular = reslst[5].split()[1]
            except FileNotFoundError:
                close_flag = False
                last_formular = None
            except IndexError:
                last_formular = None
            reply = QMessageBox.question(self,"提示","是否保存本次编辑?",QMessageBox.Yes,QMessageBox.No)
            if reply == QMessageBox.Yes:
                if last_formular is None:
                    QMessageBox.warning(self,"警告","输入为空!",QMessageBox.Yes)
                    event.ignore()
                elif not flag:
                    QMessageBox.warning(self,"警告","存在错误, 请检查输入的表达式!",QMessageBox.Yes)
                    event.ignore()
                else:
                    if 'functionName' not in funcname:
                        funcname = funcname[4:]
                        funcname = funcname.split('(')[0]
                        with open(r"./output/data.json", "w") as f:
                            fml = '{}={}'.format(funcname, last_formular)
                            self.todo.append([False, fml])
                            data = json.dump(self.todo, f)
                        event.accept()
                        if fflag:
                            emitformula = self.formula_filter(self.check3(last_formular,'max','min','sum','prod'))
                        else:
                            emitformula = self.check3(last_formular,'max','min','sum','prod')
                        self.dockWidget.setVisible(False)
                        self.shutdownValue.emit(((funcname, emitformula), 1))
                        if close_flag:os.remove('run_cache')
                    else:
                        QMessageBox.warning(self,"警告","请输入含有新变量的表达式!",QMessageBox.Yes)
                        event.ignore()
            else:
                event.accept()
                self.dockWidget.setVisible(False)
                self.shutdownValue.emit((False, 1))
        else:
            self.dockWidget.setVisible(False)
            self.shutdownValue.emit(((True, False), 1))
        
    def manage_history(self):
        from todo_complete import MainWin
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMaximizeButtonHint)
        self.setEnabled(False)
        self.show()
        self.demo = MainWin()
        self.demo.show()
        self.demo.shutdownValue2.connect(self.getValue2)

    def getValue2(self, bool):
        if bool:
            self.setWindowFlags(self.windowFlags() | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint)
            self.setEnabled(True)
            self.show()
            self.sbm.clear()
            try:
                with open(r"./output/data.json", "r") as fr:
                    self.todo = json.load(fr)
                for i in self.todo:
                    action = self.sbm.addAction(f'{i[1]}')
            except:
                self.todo = []
                pass

    def ShowLeftTool(self):
        if self.dockWidget.isVisible() and self.location == 'left':
            self.left_action.setChecked(True)
        else:
            self.dockWidget.setFloating(False)
            self.addDockWidget(Qt.DockWidgetArea(1), self.dockWidget)
            self.location = 'left'
            self.setMinimumSize(1205, 525)
            self.setMaximumSize(1205, 525)
            self.resize(1205, 525)
            self.dockWidget.setVisible(True)
            self.left_action.setChecked(True)
            self.right_action.setChecked(False)

    def ShowRightTool(self):
        if self.dockWidget.isVisible() and self.location == 'right':
            self.right_action.setChecked(True)
        else:
            self.dockWidget.setFloating(False)
            self.addDockWidget(Qt.DockWidgetArea(2), self.dockWidget)
            self.location = 'right'
            self.setMinimumSize(1205, 525)
            self.setMaximumSize(1205, 525)
            self.resize(1205, 525)
            self.dockWidget.setVisible(True)
            self.right_action.setChecked(True)
            self.left_action.setChecked(False)

    def HideTool(self):
        global vflag
        self.location = None
        self.left_action.setChecked(False)
        self.right_action.setChecked(False)
        if not self.dockWidget.isVisible():
            self.dockWidget.setVisible(False)
            if vflag:
                self.setMinimumSize(600, 475)
                self.setMaximumSize(600, 475)
                self.resize(605, 475)
            else:
                self.setMinimumSize(600, 525)
                self.setMaximumSize(600, 525)
                self.resize(605, 525)
    
    def windowchange(self):
        global vflag
        if vflag:
            if self.dockWidget.isFloating():
                self.dockWidget.setMaximumSize(QSize(524287, 524287))
                self.setMinimumSize(600, 475)
                self.setMaximumSize(600, 475)
                self.resize(605, 475)
            else:
                self.dockWidget.setMaximumSize(QSize(600, 450))
                self.showNormal()
                self.setMinimumSize(1205, 475)
                self.setMaximumSize(1205, 475)
                self.resize(1205, 475)
        else:
            if self.dockWidget.isFloating():
                self.dockWidget.setMaximumSize(QSize(524287, 524287))
                self.setMinimumSize(600, 525)
                self.setMaximumSize(600, 525)
                self.resize(605, 525)
            else:
                self.dockWidget.setMaximumSize(QSize(600, 450))
                self.showNormal()
                self.setMinimumSize(1205, 525)
                self.setMaximumSize(1205, 525)
                self.resize(1205, 525)
    
    def changeHeight(self, bool):
        global vflag
        if bool:
            if (not self.dockWidget.isFloating()) and self.dockWidget.isVisible():
                self.setMinimumSize(1205, 475)
                self.setMaximumSize(1205, 475)
                self.resize(1205, 475)
            else:
                self.setMinimumSize(600, 475)
                self.setMaximumSize(600, 475)
                self.resize(605, 475)
            vflag = True
        else:
            if (not self.dockWidget.isFloating()) and self.dockWidget.isVisible():
                self.setMinimumSize(1205, 525)
                self.setMaximumSize(1205, 525)
                self.resize(1205, 525)
            else:
                self.setMinimumSize(600, 525)
                self.setMaximumSize(600, 525)
                self.resize(605, 525)
            vflag = False

    def quit(self):
        try:
            global sflag
            sflag = True
            self.close()
            self.dockWidget.setVisible(False)
            os.remove('run_cache')
        except:
            pass
        self.shutdownValue.emit(((True, False), 1))
    
    def subscript(self):
        global cflag, cflag2
        if cflag2:
            if cflag:
                cflag = False
                self.F.axes.cla()
                if last_speres is not None:
                    self.F.axes.text(0.5,0.5,'${}$'.format(self.s_filter(self.check(last_speres))),ha='center',va='center',fontsize=text_kwargs)
                try:
                    self.F.draw()
                except:
                    self.F.axes.cla()
                    self.F.draw()
            else:
                cflag = True
                self.F.axes.cla()
                if last_speres is not None:
                    self.F.axes.text(0.5,0.5,'${}$'.format(self.exp_filter(self.s_filter(self.check(last_speres)))),ha='center',va='center',fontsize=text_kwargs)
                try:
                    self.F.draw()
                except:
                    self.F.axes.cla()
                    self.F.draw()
        else:
            if cflag:
                cflag = False
                self.F.axes.cla()
                if last_speres is not None:
                    self.F.axes.text(0.5,0.5,'${}$'.format(self.check(last_speres)),ha='center',va='center',fontsize=text_kwargs)
                try:
                    self.F.draw()
                except:
                    self.F.axes.cla()
                    self.F.draw()
            else:
                cflag = True
                self.F.axes.cla()
                if last_speres is not None:
                    self.F.axes.text(0.5,0.5,'${}$'.format(self.exp_filter(self.check(last_speres))),ha='center',va='center',fontsize=text_kwargs)
                try:
                    self.F.draw()
                except:
                    self.F.axes.cla()
                    self.F.draw()

    def superscript(self):
        global cflag, cflag2
        if cflag:
            if cflag2:
                cflag2 = False
                self.F.axes.cla()
                if last_speres is not None:
                    self.F.axes.text(0.5,0.5,'${}$'.format(self.exp_filter(self.check(last_speres))),ha='center',va='center',fontsize=text_kwargs)
                try:
                    self.F.draw()
                except:
                    self.F.axes.cla()
                    self.F.draw()
            else:
                cflag2 = True
                self.F.axes.cla()
                if last_speres is not None:
                    self.F.axes.text(0.5,0.5,'${}$'.format(self.exp_filter(self.s_filter(self.check(last_speres)))),ha='center',va='center',fontsize=text_kwargs)
                try:
                    self.F.draw()
                except:
                    self.F.axes.cla()
                    self.F.draw()
        else:
            if cflag2:
                cflag2 = False
                self.F.axes.cla()
                if last_speres is not None:
                    self.F.axes.text(0.5,0.5,'${}$'.format(self.check(last_speres)),ha='center',va='center',fontsize=text_kwargs)
                try:
                    self.F.draw()
                except:
                    self.F.axes.cla()
                    self.F.draw()
            else:
                cflag2 = True
                self.F.axes.cla()
                if last_speres is not None:
                    self.F.axes.text(0.5,0.5,'${}$'.format(self.s_filter(self.check(last_speres))),ha='center',va='center',fontsize=text_kwargs)
                try:
                    self.F.draw()
                except:
                    self.F.axes.cla()
                    self.F.draw()

    def replacephy(self):
        global fflag
        if fflag:
            fflag = False
        else:
            fflag = True

    @pyqtSlot(QTreeWidgetItem, int)
    def on_treeFiles_itemClicked(self, item, column):
        clipboard = QApplication.clipboard()
        if item.parent():
            if item.text(0) == "电子质量":  
                clipboard.setText("9.10938291e-31")
                self.textEdit.paste()
            elif item.text(0) == "真空中光速":  
                clipboard.setText("2.99792458e8")
                self.textEdit.paste()
            elif item.text(0) == "普朗克常数":  
                clipboard.setText("6.62606957e-34")
                self.textEdit.paste()
            elif item.text(0) == "万有引力常数":  
                clipboard.setText("6.67384e-11")
                self.textEdit.paste()
            elif item.text(0) == "阿伏伽德罗常数":  
                clipboard.setText("6.02214129e23")
                self.textEdit.paste()
            elif item.text(0) == "气体常数":  
                clipboard.setText("8.3144621")
                self.textEdit.paste()
            elif item.text(0) == "玻尔兹曼常数":  
                clipboard.setText("1.3806488e-23")
                self.textEdit.paste()
            elif item.text(0) == "真空电容率":  
                clipboard.setText("8.85418781762e-12")
                self.textEdit.paste()
            elif item.text(0) == "真空磁导率":  
                clipboard.setText("4*pi*e-7")
                self.textEdit.paste()
            elif item.text(0) == "电子电荷量":  
                clipboard.setText("1.602176565e-19")
                self.textEdit.paste()
            elif item.text(0) == "Lambda":
                clipboard.setText("Lambda")
                self.textEdit.paste()
            elif item.text(0) == "Omicron":  
                pass       
            else:
                clipboard.setText(item.text(2))
                self.textEdit.paste()

    def AboutUs(self):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon('./icon/AboutUs.svg'))
        msg.setWindowTitle("关于")
        msg.setText('''<font size='3'>
        <p align="center">公式编辑&检查工具</p>
        <table>
            <tr>
                <td>当前版本: </td>
                <td>ver.1.1 (2023.1.9)</td>
            </tr>
            <tr>
                <td>历史版本: </td>
                <td>ver.1.0 (2022.12.18)</td>
            </tr>
            <tr>
            <td></td>
                <td>ver.0.0 (2022.11.3)</td>
            </tr>
        </table>
        </font>''')
        msg.setIcon(QMessageBox.Information)
        msg.setDetailedText('''软件作者: Liskelleo; WaleYu\n联系我们: liskello_o@outlook.com;
                 chuanqi_yu2021@126.com''')
        msg.exec_()

    def DocHelp(self):
        from helpdoc import WebMain
        self.demo = WebMain()
        self.demo.show()


if __name__ == "__main__":
    main = MainDialogImgBW()
    main.show()
    Hook.app.exec_()
    if Flag.flag:
        app = QApplication(sys.argv)
        main.quit()
        main = MainDegbug()
        main.show()
        sys.exit(app.exec_())
