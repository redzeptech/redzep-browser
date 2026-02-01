import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QLineEdit, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView


class MiniBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redzep Browser (Mini)")
        self.resize(1200, 800)

        self.view = QWebEngineView()
        self.setCentralWidget(self.view)
        self.view.setUrl(QUrl("https://www.example.com"))

        tb = QToolBar("Navigation")
        self.addToolBar(tb)

        back_action = QAction("←", self)
        back_action.setStatusTip("Geri")
        back_action.triggered.connect(self.view.back)
        tb.addAction(back_action)

        forward_action = QAction("→", self)
        forward_action.setStatusTip("İleri")
        forward_action.triggered.connect(self.view.forward)
        tb.addAction(forward_action)

        reload_action = QAction("⟳", self)
        reload_action.setStatusTip("Yenile")
        reload_action.triggered.connect(self.view.reload)
        tb.addAction(reload_action)

        home_action = QAction("🏠", self)
        home_action.setStatusTip("Ana sayfa")
        home_action.triggered.connect(self.go_home)
        tb.addAction(home_action)

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("example.com veya https://example.com")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        tb.addWidget(self.urlbar)

        self.view.urlChanged.connect(self.update_urlbar)

    def go_home(self):
        self.view.setUrl(QUrl("https://www.example.com"))

    def navigate_to_url(self):
        text = self.urlbar.text().strip()
        if not text:
            return

        if "://" not in text:
            text = "https://" + text

        url = QUrl(text)
        if not url.isValid():
            QMessageBox.warning(self, "Hata", "Geçersiz URL.")
            return

        self.view.setUrl(url)

    def update_urlbar(self, qurl: QUrl):
        self.urlbar.setText(qurl.toString())
        self.urlbar.setCursorPosition(0)


def main():
    app = QApplication(sys.argv)
    win = MiniBrowser()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
