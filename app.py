import sys
import json
import os
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QMessageBox,
    QTabWidget, QWidget, QVBoxLayout
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
        self.setWindowTitle("Redzep Browser")
        self.resize(1200, 800)

        self.bookmarks_file = "bookmarks.json"
        self.bookmarks = self.load_bookmarks()

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
        back_action.triggered.connect(self.go_back)
        tb.addAction(back_action)

        forward_action = QAction("→", self)
        forward_action.triggered.connect(self.go_forward)
        tb.addAction(forward_action)

        reload_action = QAction("⟳", self)
        reload_action.triggered.connect(self.reload_page)
        tb.addAction(reload_action)

        home_action = QAction("🏠", self)
        home_action.triggered.connect(self.go_home)
        tb.addAction(home_action)

        newtab_action = QAction("＋", self)
        newtab_action.setShortcut(QKeySequence("Ctrl+T"))
        newtab_action.triggered.connect(lambda: self.add_tab("https://www.example.com", switch=True))
        tb.addAction(newtab_action)

        closetab_action = QAction("✕", self)
        closetab_action.setShortcut(QKeySequence("Ctrl+W"))
        closetab_action.triggered.connect(self.close_current_tab)
        tb.addAction(closetab_action)

        bookmark_action = QAction("★", self)
        bookmark_action.setStatusTip("Yer imlerine ekle")
        bookmark_action.triggered.connect(self.add_bookmark)
        tb.addAction(bookmark_action)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        tb.addWidget(self.urlbar)

        self.add_tab("https://www.example.com", switch=True)

    # ---------------- BOOKMARK ----------------

    def load_bookmarks(self):
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w", encoding="utf-8") as f:
            json.dump(self.bookmarks, f, indent=2)

    def add_bookmark(self):
        v = self.current_view()
        if not v:
            return
        title = v.title()
        url = v.url().toString()
        self.bookmarks.append({"title": title, "url": url})
        self.save_bookmarks()
        QMessageBox.information(self, "Bookmark", "Yer imi eklendi!")
        self.refresh_bookmark_menu()
    def refresh_bookmark_menu(self):
        self.bookmark_menu.clear()
        for bm in self.bookmarks:
            action = QAction(bm["title"], self)
            action.triggered.connect(lambda checked=False, url=bm["url"]: self.add_tab(url, switch=True))
            self.bookmark_menu.addAction(action)

    # ---------------- TAB SYSTEM ----------------

    def current_view(self):
        w = self.tabs.currentWidget()
        if isinstance(w, BrowserTab):
            return w.view
        return None

    def add_tab(self, url, switch=False):
        tab = BrowserTab(url)
        i = self.tabs.addTab(tab, "Yeni Sekme")
        tab.view.urlChanged.connect(lambda qurl, tab=tab: self.on_url_changed(qurl, tab))
        tab.view.titleChanged.connect(lambda title, idx=i: self.tabs.setTabText(idx, title[:30] if title else "Sekme"))
        if switch:
            self.tabs.setCurrentIndex(i)

    def close_tab(self, index):
        if self.tabs.count() <= 1:
            self.tabs.removeTab(index)
                   # Menu bar
        menubar = self.menuBar()
        self.bookmark_menu = menubar.addMenu("Yer İmleri")
        self.refresh_bookmark_menu()

            self.add_tab("https://www.example.com", switch=True)
            return
        self.tabs.removeTab(index)

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def on_tab_changed(self, _index):
        v = self.current_view()
        if v:
            self.urlbar.setText(v.url().toString())

    def on_url_changed(self, qurl, tab):
        if tab == self.tabs.currentWidget():
            self.urlbar.setText(qurl.toString())

    # ---------------- NAVIGATION ----------------

    def navigate_to_url(self):
        text = self.urlbar.text().strip()
        if not text:
            return
        if "://" not in text:
            text = "https://" + text
        v = self.current_view()
        if v:
            v.setUrl(QUrl(text))

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
