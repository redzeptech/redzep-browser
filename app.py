import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QMessageBox, QTabWidget, QWidget, QVBoxLayout
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class BrowserTab(QWidget):
    def __init__(self, url: str = "https://www.example.com"):
        super().__init__()
        self.view = QWebEngineView()
        self.view.setUrl(QUrl(url))

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)


class TabbedBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redzep Browser (Tabs)")
        self.resize(1200, 800)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)

        # Toolbar
        tb = QToolBar("Navigation")
        self.addToolBar(tb)

        back_action = QAction("←", self)
        back_action.setStatusTip("Geri")
        back_action.triggered.connect(self.go_back)
        tb.addAction(back_action)

        forward_action = QAction("→", self)
        forward_action.setStatusTip("İleri")
        forward_action.triggered.connect(self.go_forward)
        tb.addAction(forward_action)

        reload_action = QAction("⟳", self)
        reload_action.setStatusTip("Yenile")
        reload_action.triggered.connect(self.reload_page)
        tb.addAction(reload_action)

        home_action = QAction("🏠", self)
        home_action.setStatusTip("Ana sayfa")
        home_action.triggered.connect(self.go_home)
        tb.addAction(home_action)

        newtab_action = QAction("＋", self)
        newtab_action.setStatusTip("Yeni sekme")
        newtab_action.setShortcut(QKeySequence("Ctrl+T"))
        newtab_action.triggered.connect(lambda: self.add_tab("https://www.example.com", switch=True))
        tb.addAction(newtab_action)

        closetab_action = QAction("✕", self)
        closetab_action.setStatusTip("Sekmeyi kapat")
        closetab_action.setShortcut(QKeySequence("Ctrl+W"))
        closetab_action.triggered.connect(self.close_current_tab)
        tb.addAction(closetab_action)

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("example.com veya https://example.com")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        tb.addWidget(self.urlbar)

        # First tab
        self.add_tab("https://www.example.com", switch=True)

    # --- Helpers ---
    def current_view(self) -> QWebEngineView | None:
        w = self.tabs.currentWidget()
        if isinstance(w, BrowserTab):
            return w.view
        return None

    def add_tab(self, url: str, switch: bool = False):
        tab = BrowserTab(url)
        i = self.tabs.addTab(tab, "Yeni Sekme")
        tab.view.urlChanged.connect(lambda qurl, tab=tab: self.on_url_changed(qurl, tab))
        tab.view.titleChanged.connect(lambda title, idx=i: self.tabs.setTabText(idx, title[:30] if title else "Sekme"))
        if switch:
            self.tabs.setCurrentIndex(i)

    def close_tab(self, index: int):
        if self.tabs.count() <= 1:
            # Son sekmeyi kapatmayalım; yerine boş sekme açalım
            self.tabs.removeTab(index)
            self.add_tab("https://www.example.com", switch=True)
            return
        self.tabs.removeTab(index)

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def on_tab_changed(self, _index: int):
        v = self.current_view()
        if v:
            self.urlbar.setText(v.url().toString())

    def on_url_changed(self, qurl: QUrl, tab: BrowserTab):
        # URL bar sadece aktif tab için güncellensin
        if tab == self.tabs.currentWidget():
            self.urlbar.setText(qurl.toString())
            self.urlbar.setCursorPosition(0)

    # --- Navigation actions ---
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
        v = self.current_view()
        if v:
            v.setUrl(url)

    def go_home(self):
        v = self.current_view()
        if v:
            v.setUrl(QUrl("https://www.example.com"))

    def go_back(self):
        v = self.current_view()
        if v:
            v.back()

    def go_forward(self):
        v = self.current_view()
        if v:
            v.forward()

    def reload_page(self):
        v = self.current_view()
        if v:
            v.reload()


def main():
    app = QApplication(sys.argv)
    win = TabbedBrowser()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
