import reflex as rx
from typing import TypedDict


class Tab(TypedDict):
    id: int
    title: str
    url: str
    content_url: str
    history: list[str]
    history_index: int


class Bookmark(TypedDict):
    title: str
    url: str
    icon: str


class BrowserState(rx.State):
    tabs: list[Tab] = [
        {
            "id": 1,
            "title": "New Tab",
            "url": "",
            "content_url": "about:blank",
            "history": ["about:blank"],
            "history_index": 0,
        }
    ]
    active_tab_id: int = 1
    next_tab_id: int = 2
    homepage: str = rx.Cookie("https://google.com", name="browser_homepage")
    search_engine: str = rx.Cookie("Google", name="browser_search_engine")
    show_settings: bool = False
    search_engines: list[str] = ["Google", "DuckDuckGo", "Bing"]
    bookmarks: list[Bookmark] = [
        {"title": "Reflex", "url": "https://reflex.dev", "icon": "box"},
        {"title": "GitHub", "url": "https://github.com", "icon": "github"},
        {"title": "Google", "url": "https://google.com", "icon": "search"},
        {
            "title": "Docs",
            "url": "https://reflex.dev/docs/getting-started/introduction/",
            "icon": "book-open",
        },
    ]
    show_bookmark_manager: bool = False
    show_dev_tools: bool = False
    show_statistics: bool = False

    @rx.var
    def active_tab(self) -> Tab | None:
        for tab in self.tabs:
            if tab["id"] == self.active_tab_id:
                return tab
        return None

    @rx.var
    def active_tab_url(self) -> str:
        tab = self.active_tab
        return tab["url"] if tab else ""

    @rx.var
    def can_go_back(self) -> bool:
        active_tab = self.active_tab
        return active_tab is not None and active_tab["history_index"] > 0

    @rx.var
    def can_go_forward(self) -> bool:
        active_tab = self.active_tab
        return (
            active_tab is not None
            and active_tab["history_index"] < len(active_tab["history"]) - 1
        )

    @rx.event
    def add_tab(self):
        new_tab = {
            "id": self.next_tab_id,
            "title": "New Tab",
            "url": "",
            "content_url": self.homepage,
            "history": [self.homepage],
            "history_index": 0,
        }
        self.tabs.append(new_tab)
        self.active_tab_id = self.next_tab_id
        self.next_tab_id += 1

    @rx.event
    def close_tab(self, tab_id: int):
        self.tabs = [tab for tab in self.tabs if tab["id"] != tab_id]
        if self.active_tab_id == tab_id and self.tabs:
            self.active_tab_id = self.tabs[-1]["id"]
        elif not self.tabs:
            self.add_tab()

    @rx.event
    def switch_tab(self, tab_id: int):
        self.active_tab_id = tab_id

    @rx.event
    def navigate(self, form_data: dict[str, str]):
        url = form_data.get("url", "")
        if not url:
            return
        tab_index = -1
        for i, tab in enumerate(self.tabs):
            if tab["id"] == self.active_tab_id:
                tab_index = i
                break
        if tab_index != -1:
            search_urls = {
                "Google": "https://www.google.com/search?q=",
                "DuckDuckGo": "https://duckduckgo.com/?q=",
                "Bing": "https://www.bing.com/search?q=",
            }
            url_to_load = url
            if ("." not in url or " " in url) and (not url.startswith("http")):
                url_to_load = (
                    f"{search_urls[self.search_engine]}{url.replace(' ', '+')}"
                )
            elif not url_to_load.startswith("http://") and (
                not url_to_load.startswith("https://")
            ):
                url_to_load = f"https://{url_to_load}"
            current_history = self.tabs[tab_index]["history"]
            current_index = self.tabs[tab_index]["history_index"]
            if current_index < len(current_history) - 1:
                self.tabs[tab_index]["history"] = current_history[: current_index + 1]
            self.tabs[tab_index]["history"].append(url_to_load)
            self.tabs[tab_index]["history_index"] += 1
            self.tabs[tab_index]["url"] = url
            self.tabs[tab_index]["content_url"] = url_to_load
            self.tabs[tab_index]["title"] = self._get_domain(url)

    def _get_domain(self, url: str) -> str:
        if "//" in url:
            domain = url.split("//")[1].split("/")[0]
        else:
            domain = url.split("/")[0]
        return domain.replace("www.", "")

    @rx.event
    def go_home(self):
        return BrowserState.navigate({"url": self.homepage})

    @rx.event
    def refresh(self):
        active_tab = self.active_tab
        if active_tab:
            current_content_url = active_tab["content_url"]
            active_tab["content_url"] = "about:blank"
            yield
            active_tab["content_url"] = current_content_url

    @rx.event
    def go_back(self):
        tab_index = -1
        for i, tab in enumerate(self.tabs):
            if tab["id"] == self.active_tab_id:
                tab_index = i
                break
        if tab_index != -1 and self.tabs[tab_index]["history_index"] > 0:
            self.tabs[tab_index]["history_index"] -= 1
            url = self.tabs[tab_index]["history"][self.tabs[tab_index]["history_index"]]
            self.tabs[tab_index]["content_url"] = url
            self.tabs[tab_index]["url"] = url
            self.tabs[tab_index]["title"] = self._get_domain(url)

    @rx.event
    def go_forward(self):
        tab_index = -1
        for i, tab in enumerate(self.tabs):
            if tab["id"] == self.active_tab_id:
                tab_index = i
                break
        if (
            tab_index != -1
            and self.tabs[tab_index]["history_index"]
            < len(self.tabs[tab_index]["history"]) - 1
        ):
            self.tabs[tab_index]["history_index"] += 1
            url = self.tabs[tab_index]["history"][self.tabs[tab_index]["history_index"]]
            self.tabs[tab_index]["content_url"] = url
            self.tabs[tab_index]["url"] = url
            self.tabs[tab_index]["title"] = self._get_domain(url)

    @rx.event
    def handle_key_down(self, key: str):
        meta = self.get_client_meta()
        ctrl_key = meta.get("ctrlKey", False)
        meta_key = meta.get("metaKey", False)
        if (meta_key or ctrl_key) and key == "t":
            return BrowserState.add_tab
        if (meta_key or ctrl_key) and key == "w":
            if self.active_tab:
                return BrowserState.close_tab(self.active_tab_id)

    @rx.event
    def navigate_to_bookmark(self, url: str):
        return BrowserState.navigate({"url": url})

    @rx.event
    def toggle_dev_tools(self):
        self.show_dev_tools = not self.show_dev_tools

    @rx.event
    def toggle_statistics(self):
        self.show_statistics = not self.show_statistics

    @rx.event
    def add_bookmark(self):
        active_tab = self.active_tab
        if active_tab and (
            not any((b["url"] == active_tab["url"] for b in self.bookmarks))
        ):
            new_bookmark = {
                "title": active_tab["title"],
                "url": active_tab["url"],
                "icon": "file-text",
            }
            self.bookmarks.append(new_bookmark)

    @rx.event
    def remove_bookmark(self, url: str):
        self.bookmarks = [b for b in self.bookmarks if b["url"] != url]

    @rx.event
    def edit_bookmark(self, old_url: str, new_title: str, new_url: str):
        for bookmark in self.bookmarks:
            if bookmark["url"] == old_url:
                bookmark["title"] = new_title
                bookmark["url"] = new_url
                break