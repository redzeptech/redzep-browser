import re
from urllib.parse import urlparse

import sys
import json
import os

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QLineEdit,
    QTabWidget,
    QWidget,
    QVBoxLayout,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

HOME_URL = "https://www.google.com"


class BrowserTab(QWidget):
    def __init__(self, url: str = HOME_URL):
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

        # State
        self.bookmarks_file = "bookmarks.json"
        self.bookmarks = self.load_bookmarks()
        self.secure_mode = False  # True => JS OFF

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
        newtab_action.triggered.connect(lambda: self.add_tab(HOME_URL, switch=True))
        tb.addAction(newtab_action)

        closetab_action = QAction("✕", self)
        closetab_action.setStatusTip("Sekmeyi kapat")
        closetab_action.setShortcut(QKeySequence("Ctrl+W"))
        closetab_action.triggered.connect(self.close_current_tab)
        tb.addAction(closetab_action)

        bookmark_action = QAction("★", self)
        bookmark_action.setStatusTip("Yer imlerine ekle")
        bookmark_action.triggered.connect(self.add_bookmark)
        tb.addAction(bookmark_action)

        secure_action = QAction("🛡", self)
        secure_action.setStatusTip("Güvenli Mod (JavaScript Aç/Kapat)")
        secure_action.setCheckable(True)
        secure_action.triggered.connect(self.toggle_secure_mode)
        self.secure_action = secure_action
        tb.addAction(secure_action)

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("example.com veya https://example.com")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        tb.addWidget(self.urlbar)

        # Menu bar (Bookmarks)
        menubar = self.menuBar()
        self.bookmark_menu = menubar.addMenu("Yer İmleri")
        self.refresh_bookmark_menu()

        # Status bar
        self.statusBar().showMessage("Hazır", 1500)

        # First tab
        self.add_tab(HOME_URL, switch=True)

    # ---------------- BOOKMARKS ----------------

    def load_bookmarks(self):
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    # Minimal validation
                    cleaned = []
                    for bm in data:
                        if isinstance(bm, dict) and "url" in bm:
                            cleaned.append(
                                {
                                    "title": str(bm.get("title", "Yer imi")),
                                    "url": str(bm.get("url", HOME_URL)),
                                }
                            )
                    return cleaned
            except Exception:
                pass
        return []

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w", encoding="utf-8") as f:
            json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)

    def add_bookmark(self):
        v = self.current_view()
        if not v:
            return

        title = v.title() or "Yer imi"
        url = v.url().toString()

        # Duplicate prevent (by URL)
        if any(bm.get("url") == url for bm in self.bookmarks):
            self.statusBar().showMessage("Zaten kayıtlı: " + url, 2500)
            return

        self.bookmarks.append({"title": title, "url": url})
        self.save_bookmarks()
        self.refresh_bookmark_menu()
        self.statusBar().showMessage("Yer imi eklendi", 2000)

    def delete_bookmark(self, index: int):
        if 0 <= index < len(self.bookmarks):
            self.bookmarks.pop(index)
            self.save_bookmarks()
            self.refresh_bookmark_menu()
            self.statusBar().showMessage("Yer imi silindi", 2000)

    def clear_bookmarks(self):
        self.bookmarks = []
        self.save_bookmarks()
        self.refresh_bookmark_menu()
        self.statusBar().showMessage("Tüm yer imleri temizlendi", 2500)

    def refresh_bookmark_menu(self):
        self.bookmark_menu.clear()

        if not self.bookmarks:
            empty = QAction("(Boş)", self)
            empty.setEnabled(False)
            self.bookmark_menu.addAction(empty)
            return

        # Open bookmarks
        for bm in self.bookmarks:
            title = bm.get("title", "Yer imi")
            url = bm.get("url", HOME_URL)
            action = QAction(title, self)
            action.triggered.connect(lambda checked=False, u=url: self.add_tab(u, switch=True))
            self.bookmark_menu.addAction(action)

        # Management
        self.bookmark_menu.addSeparator()

        clear_action = QAction("🗑 Tüm yer imlerini temizle", self)
        clear_action.triggered.connect(self.clear_bookmarks)
        self.bookmark_menu.addAction(clear_action)

        delete_menu = self.bookmark_menu.addMenu("🧹 Yer imi sil")
        for idx, bm in enumerate(self.bookmarks):
            title = bm.get("title", "Yer imi")
            del_action = QAction(title, self)
            del_action.triggered.connect(lambda checked=False, i=idx: self.delete_bookmark(i))
            delete_menu.addAction(del_action)

    # ---------------- SECURE MODE ----------------

    def apply_js_setting_all_tabs(self):
        js_enabled = not self.secure_mode
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if isinstance(tab, BrowserTab):
                tab.view.settings().setAttribute(
                    QWebEngineSettings.WebAttribute.JavascriptEnabled,
                    js_enabled,
                )

    def toggle_secure_mode(self):
        self.secure_mode = not self.secure_mode
        self.secure_action.setChecked(self.secure_mode)
        self.apply_js_setting_all_tabs()
        self.statusBar().showMessage(
            "Secure Mode: " + ("ON (JavaScript OFF)" if self.secure_mode else "OFF (JavaScript ON)"),
            3000,
        )

    # ---------------- TABS ----------------
    def is_suspicious_domain(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()

            # IP adresi mi?
            if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
                return True

            # Çok uzun domain
            if len(host) > 40:
                return True

            # Çok fazla tire
            if host.count("-") >= 3:
                return True

            # Şüpheli kelimeler
            suspicious_words = ["secure", "verify", "update", "account", "login"]
            if any(word in host for word in suspicious_words):
                return True

        except Exception:
            pass

        return False

    
    def current_view(self):
        w = self.tabs.currentWidget()
        if isinstance(w, BrowserTab):
            return w.view
        return None

    def add_tab(self, url: str, switch: bool = False):
        tab = BrowserTab(url)

        # Ensure secure mode applies to new tab too
        tab.view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled,
            not self.secure_mode,
        )

        idx = self.tabs.addTab(tab, "Yeni Sekme")

        tab.view.urlChanged.connect(lambda qurl, t=tab: self.on_url_changed(qurl, t))
        tab.view.titleChanged.connect(
            lambda title, i=idx: self.tabs.setTabText(i, (title[:30] if title else "Sekme"))
        )

        if switch:
            self.tabs.setCurrentIndex(idx)

    def close_tab(self, index: int):
        if self.tabs.count() <= 1:
            self.tabs.removeTab(index)
            self.add_tab(HOME_URL, switch=True)
            return
        self.tabs.removeTab(index)

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def on_tab_changed(self, _index: int):
        v = self.current_view()
        if v:
            self.urlbar.setText(v.url().toString())
            self.urlbar.setCursorPosition(0)

    def on_url_changed(self, qurl: QUrl, tab: BrowserTab):
        if tab == self.tabs.currentWidget():
            self.urlbar.setText(qurl.toString())
            self.urlbar.setCursorPosition(0)
      
        # Phishing kontrolü
                # HTTPS kontrolü
        if self.is_insecure_http(current_url):
            self.statusBar().showMessage(
                "⚠️ This site is not using HTTPS (connection not secure)", 4000
            )

        current_url = qurl.toString()
        if self.is_suspicious_domain(current_url):
                def is_insecure_http(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme == "http"
        except Exception:
            return False

            self.statusBar().showMessage(
                "⚠️ Warning: Suspicious domain detected!", 4000
            )

    
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
            v.setUrl(QUrl(HOME_URL))

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
