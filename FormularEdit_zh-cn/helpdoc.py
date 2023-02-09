import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, \
    QToolBar, QStatusBar, QAction, QProgressBar, QSizePolicy, \
    QHBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize, QUrl

from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtPrintSupport import QPrinter, QPrinterInfo, QPageSetupDialog, QPrintDialog

from qt_sass_theme.qtSassTheme import QtSassTheme


class WebView(QWebEngineView):

    def __init__(self, WebMain, parent=None):
        super(WebView, self).__init__(parent)
        self.channel = QWebChannel()
        self.page().setWebChannel(self.channel)
    

class WebMain(QMainWindow):
    def __init__(self):
        super().__init__()
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.pageload = True
        self.themeflag = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Help')
        self.setWindowIcon(QIcon('./icons/document.svg'))

        self.progressBar = QProgressBar()
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.urlprogress = QLabel()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.addPermanentWidget(self.urlprogress)
        self.statusBar.addPermanentWidget(self.progressBar)

        navigation_bar = self.addToolBar('Navigation')
        navigation_bar.setIconSize(QSize(16, 16))
        navigation_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        theme_button = QAction(QIcon('icons/theme.svg'), 'Theme', self)
        theme_button.setShortcut('F1')
        self.back_button = QAction(QIcon('icons/back.svg'), 'Back', self)
        self.back_button.setShortcut('F2')
        self.next_button = QAction(QIcon('icons/forward.svg'), 'Forward', self)
        self.next_button.setShortcut('F3')
        stop_button = QAction(QIcon('icons/stop.svg'), 'Stop', self)
        stop_button.setShortcut('F4')
        reload_button = QAction(QIcon('icons/reload.svg'), 'Reload', self)
        reload_button.setShortcut('F5')
        print_button = QAction(QIcon('icons/print.svg'), 'Print', self)
        print_button.setShortcut('F6')

        navigation_bar.addAction(theme_button)
        navigation_bar.addAction(self.back_button)
        navigation_bar.addAction(self.next_button)
        navigation_bar.addAction(stop_button)
        navigation_bar.addAction(reload_button)
        navigation_bar.addAction(print_button)


        self.next_button.setEnabled(False)
        self.back_button.setEnabled(False)

        self.webview = WebView(self)
        self.back_button.triggered.connect(self.webview.back)
        self.next_button.triggered.connect(self.webview.forward)
        stop_button.triggered.connect(self.webview.stop)
        reload_button.triggered.connect(self.webview.reload)
        theme_button.triggered.connect(self.Changetheme)
        print_button.triggered.connect(self.print)

        self.urlbar = QLabel()
        self.textbar = QLabel(' Current URL>>>  ')
        navigation_bar.addSeparator()
        navigation_bar.addWidget(self.textbar)
        navigation_bar.addWidget(self.urlbar)

        self.page = QWebEnginePage(self)
        self.webview.setPage(self.page)
        self.page.printRequested.connect(self.printRequested)

        self.webview.page().linkHovered.connect(self.showUrl)
        self.webview.urlChanged.connect(self.renew_urlbar)
        self.webview.loadProgress.connect(self.webProgress)
        self.webview.loadFinished.connect(self.webProgressEnd)
        self.webview.titleChanged.connect(self.Begin2Change)

        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./doc/help.html"))
        local_url = QUrl.fromLocalFile(file_path)

        self.webview.load(local_url)
        self.setCentralWidget(self.webview)
        for i in [navigation_bar, self.textbar]:i.setFont(QFont("Arial"))
        self.urlbar.setStyleSheet("color:gray")
        self.urlbar.setFont(QFont("Consolas"))

        t = QtSassTheme()
        t.getThemeFiles(theme='#ffffff')
        t.setThemeFiles(main_window=self)

    def showUrl(self, url):
        self.statusBar.showMessage(url)

    def renew_urlbar(self, q):
        self.urlbar.setText(q.toString())
        history = self.webview.history()
        if history.count() > 1:
            if history.currentItemIndex() == history.count()-1:
                self.back_button.setEnabled(True)
                self.next_button.setEnabled(False)
            elif history.currentItemIndex() == 0:
                self.back_button.setEnabled(False)
                self.next_button.setEnabled(True)
            else:
                self.back_button.setEnabled(True)
                self.next_button.setEnabled(True)

    def Begin2Change(self):
        self.pageload = True
        if self.themeflag is not None:
            if self.themeflag:
                cmd = "location.reload(true)"
                self.webview.page().runJavaScript(cmd)
            else:
                cmd = "document.documentElement.style.filter='invert(85%) hue-rotate(180deg)'"
                self.webview.page().runJavaScript(cmd)

    def webProgress(self, progress):
        if self.pageload:
            self.urlprogress.setText("loading...")
            self.urlprogress.show()
            self.progressBar.show()
            self.progressBar.setValue(progress)
    
    def webProgressEnd(self, isFinished):
        self.pageload = False
        if isFinished:
            self.progressBar.setValue(100)
            self.progressBar.hide()
            self.urlprogress.hide()
            self.progressBar.setValue(0)

    def Changetheme(self):
        if self.themeflag or self.themeflag is None:
            cmd = "document.documentElement.style.filter='invert(80%) hue-rotate(180deg)'"
            self.webview.page().runJavaScript(cmd)
            t = QtSassTheme()
            t.getThemeFiles(theme='dark_gray')
            t.setThemeFiles(main_window=self)
            self.themeflag = False
        else:
            cmd = "location.reload(true)"
            self.webview.page().runJavaScript(cmd)
            t = QtSassTheme()
            t.getThemeFiles(theme='#ffffff')
            t.setThemeFiles(main_window=self)
            self.themeflag = True

    def print(self):
        cmd = 'print()'
        self.webview.page().runJavaScript(cmd)
    
    def printRequested(self):
        defaultPrinter = QPrinter(QPrinterInfo.defaultPrinter())
        dialog = QPrintDialog(defaultPrinter, self)
        settingsDialog = QPageSetupDialog(defaultPrinter, self)
        if settingsDialog.exec():
            pass
        if dialog.exec():
            self._printer = dialog.printer()
            self.page.print(self._printer, self.printResult)
            self.urlprogress.setText("printing...")
            self.urlprogress.show()
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(0)
            self.progressBar.show()

    def printResult(self, success):
        if self._printer.paperSource() and self._printer.printerName() != 'pdfFactory Pro':
            #if self._printer.printerName() == 'Adobe PDF':
            if self._printer.outputFileName() == '':
                if success:
                    QMessageBox.information(self, 'Print Canceled', 
                        'Printing has been canceled!', QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, 'Print Failed', 
                        'Printing has failed!', QMessageBox.Ok)
            else:
                if success:
                    QMessageBox.information(self, 'Print Completed', 
                        'Printing has been completed!', QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, 'Print Failed', 
                        'Printing has failed!', QMessageBox.Ok)
        else:
            if success:
                QMessageBox.information(self, 'Print Completed', 
                    'Printing has been completed!', QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'Print Failed', 
                    'Printing has failed!', QMessageBox.Ok)
        self.progressBar.hide()
        self.urlprogress.hide()
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        del self._printer

        
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ex = WebMain()
    ex.show()
    sys.exit(app.exec_())
