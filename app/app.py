import reflex as rx
from app.state import BrowserState
from app.states.download_state import DownloadState


def browser_tab(tab: dict) -> rx.Component:
    is_active = BrowserState.active_tab_id == tab["id"]
    return rx.el.div(
        rx.el.span(tab["title"], class_name="truncate max-w-[120px]"),
        rx.el.button(
            rx.icon("x", size=14),
            on_click=lambda: BrowserState.close_tab(tab["id"]),
            class_name=rx.cond(
                is_active,
                "ml-2 text-gray-700 hover:text-black",
                "ml-2 text-gray-500 hover:text-gray-800",
            ),
            size="1",
        ),
        on_click=lambda: BrowserState.switch_tab(tab["id"]),
        class_name=rx.cond(
            is_active,
            "flex items-center justify-between h-10 px-4 cursor-pointer bg-white border-t-2 border-blue-500 rounded-t-lg shadow-sm",
            "flex items-center justify-between h-10 px-4 cursor-pointer text-gray-600 bg-gray-100 hover:bg-gray-200 border-b rounded-t-lg",
        ),
        style={"minWidth": "180px"},
    )


def navigation_controls() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("arrow-left", size=20),
            on_click=BrowserState.go_back,
            disabled=~BrowserState.can_go_back,
            class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed",
        ),
        rx.el.button(
            rx.icon("arrow-right", size=20),
            on_click=BrowserState.go_forward,
            disabled=~BrowserState.can_go_forward,
            class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed",
        ),
        rx.el.button(
            rx.icon("rotate-cw", size=20),
            on_click=BrowserState.refresh,
            class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200",
        ),
        rx.el.button(
            rx.icon("home", size=20),
            on_click=BrowserState.go_home,
            class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200",
        ),
        class_name="flex items-center space-x-2",
    )


def address_bar() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.input(
                name="url",
                key=BrowserState.active_tab_url,
                default_value=BrowserState.active_tab_url,
                placeholder="Search Google or type a URL",
                class_name="w-full h-10 px-4 bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white",
            ),
            on_submit=BrowserState.navigate,
            width="100%",
            reset_on_submit=True,
        ),
        class_name="flex-grow mx-4",
    )


def browser_header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.foreach(BrowserState.tabs, browser_tab),
            rx.el.button(
                rx.icon("plus", size=16),
                on_click=BrowserState.add_tab,
                class_name="h-10 w-10 flex items-center justify-center bg-gray-200 hover:bg-gray-300 rounded-t-lg",
            ),
            class_name="flex items-end space-x-1",
        ),
        rx.el.div(
            navigation_controls(),
            address_bar(),
            rx.el.div(
                rx.el.button(
                    rx.icon("star", size=20),
                    on_click=BrowserState.add_bookmark,
                    class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200 transition-colors",
                ),
                downloads_popover(),
                bookmark_manager_modal(),
                rx.el.button(
                    rx.icon("bar-chart-2", size=20),
                    on_click=BrowserState.toggle_statistics,
                    class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200 transition-colors",
                ),
                rx.el.button(
                    rx.icon("code", size=20),
                    on_click=BrowserState.toggle_dev_tools,
                    class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200 transition-colors",
                ),
                settings_modal(),
                rx.image(
                    src="https://api.dicebear.com/9.x/initials/svg?seed=Taviad",
                    class_name="w-8 h-8 rounded-full",
                ),
                class_name="flex items-center space-x-2",
            ),
            class_name="flex items-center h-14 bg-white px-4 border-b border-gray-200",
        ),
        class_name="bg-gray-100",
    )


def bookmark_bar() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            BrowserState.bookmarks,
            lambda bookmark: rx.el.button(
                rx.icon(bookmark["icon"], size=16, class_name="mr-2"),
                rx.el.span(bookmark["title"]),
                on_click=lambda: BrowserState.navigate_to_bookmark(bookmark["url"]),
                class_name="flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white rounded-md hover:bg-gray-100 border border-gray-200 shadow-sm",
            ),
        ),
        class_name="flex items-center px-4 py-2 space-x-3 bg-white border-b border-gray-200",
    )


def browser_content() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.iframe(
                src=BrowserState.active_tab.get("content_url", "about:blank"),
                key=BrowserState.active_tab_id.to_string(),
                class_name="w-full h-full border-0 transition-all duration-300",
                style={
                    "height": rx.cond(
                        BrowserState.show_dev_tools | BrowserState.show_statistics,
                        "60%",
                        "100%",
                    )
                },
            ),
            rx.cond(BrowserState.show_statistics, statistics_panel(), rx.fragment()),
            rx.cond(BrowserState.show_dev_tools, dev_tools_panel(), rx.fragment()),
            class_name="flex-grow flex flex-col bg-white",
        ),
        class_name="flex-grow bg-white overflow-hidden",
    )


def settings_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(
            rx.el.button(
                rx.icon("settings", size=20),
                class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200",
            )
        ),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                "Settings", class_name="text-lg font-semibold"
            ),
            rx.radix.primitives.dialog.description(
                "Manage your browser preferences.",
                class_name="text-sm text-gray-500 mb-4",
            ),
            rx.el.div(
                rx.el.label("Homepage URL", class_name="text-sm font-medium"),
                rx.el.input(
                    default_value=BrowserState.homepage,
                    on_change=BrowserState.set_homepage.debounce(500),
                    placeholder="https://example.com",
                    class_name="w-full mt-1 h-10 px-3 bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label("Search Engine", class_name="text-sm font-medium"),
                rx.el.select(
                    rx.foreach(
                        BrowserState.search_engines,
                        lambda se: rx.el.option(se, value=se),
                    ),
                    value=BrowserState.search_engine,
                    on_change=BrowserState.set_search_engine,
                    class_name="w-full mt-1 h-10 px-3 bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        "Close",
                        class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200",
                    )
                ),
                class_name="flex justify-end",
            ),
            class_name="bg-white p-6 rounded-lg shadow-lg",
            style={"maxWidth": "500px"},
        ),
        open=BrowserState.show_settings,
        on_open_change=BrowserState.set_show_settings,
    )


def downloads_popover() -> rx.Component:
    return rx.popover.root(
        rx.popover.trigger(
            rx.el.button(
                rx.icon("download", size=20),
                class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200",
            )
        ),
        rx.popover.content(
            rx.el.div(
                rx.el.div(
                    rx.el.h3("Downloads", class_name="font-semibold text-gray-800"),
                    rx.el.button(
                        "Start Dummy Download",
                        on_click=DownloadState.start_dummy_download,
                        class_name="text-xs text-blue-500 hover:underline",
                    ),
                    class_name="flex justify-between items-center p-4 border-b",
                ),
                rx.cond(
                    DownloadState.downloads.length() == 0,
                    rx.el.div(
                        "No downloads yet.", class_name="p-4 text-center text-gray-500"
                    ),
                    rx.el.ul(
                        rx.foreach(DownloadState.downloads, download_item),
                        class_name="divide-y divide-gray-200 max-h-96 overflow-y-auto",
                    ),
                ),
            ),
            class_name="w-96 bg-white rounded-lg shadow-lg border border-gray-200",
            side="bottom",
            align="end",
        ),
    )


def download_item(item: dict) -> rx.Component:
    return rx.el.li(
        rx.el.div(
            rx.icon("file", class_name="w-5 h-5 text-gray-500"),
            rx.el.div(
                rx.el.p(item["name"], class_name="text-sm font-medium truncate"),
                rx.cond(
                    item["status"] == "In Progress",
                    rx.el.div(
                        rx.el.div(
                            class_name="bg-blue-500 h-1.5 rounded-full transition-all",
                            style={"width": item["progress"].to_string() + "%"},
                        ),
                        class_name="w-full bg-gray-200 rounded-full h-1.5 mt-1",
                    ),
                    rx.el.p(
                        item["status"],
                        class_name=rx.cond(
                            item["status"] == "Completed",
                            "text-xs text-green-600",
                            rx.cond(
                                item["status"] == "Paused",
                                "text-xs text-yellow-600",
                                "text-xs text-gray-500",
                            ),
                        ),
                    ),
                ),
                class_name="flex-1 overflow-hidden mr-2",
            ),
            class_name="flex-1 flex items-center gap-3 overflow-hidden",
        ),
        rx.el.div(
            rx.cond(
                item["status"] == "Paused",
                rx.el.button(
                    rx.icon("play", size=14),
                    on_click=lambda: DownloadState.resume_download(item["id"]),
                    class_name="p-1 text-gray-500 hover:bg-gray-100 rounded-md transition-colors",
                ),
                rx.el.button(
                    rx.icon("pause", size=14),
                    on_click=lambda: DownloadState.pause_download(item["id"]),
                    class_name="p-1 text-gray-500 hover:bg-gray-100 rounded-md transition-colors",
                    disabled=item["status"] != "In Progress",
                ),
            ),
            rx.el.button(
                rx.icon("trash-2", size=14),
                on_click=lambda: DownloadState.cancel_download(item["id"]),
                class_name="p-1 text-red-500 hover:bg-red-50 rounded-md transition-colors",
            ),
            class_name="flex items-center gap-1",
        ),
        class_name="flex items-center justify-between p-3 hover:bg-gray-50 transition-colors",
    )


def bookmark_manager_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(
            rx.el.button(
                rx.icon("bookmark", size=20),
                class_name="p-2 rounded-md text-gray-500 hover:bg-gray-200 transition-colors",
            )
        ),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                "Bookmark Manager", class_name="text-lg font-semibold"
            ),
            rx.el.div(
                rx.foreach(
                    BrowserState.bookmarks,
                    lambda bm: rx.el.div(
                        rx.icon(bm["icon"], class_name="mr-2"),
                        rx.el.input(
                            default_value=bm["title"],
                            on_blur=lambda val: BrowserState.edit_bookmark(
                                bm["url"], val, bm["url"]
                            ),
                            class_name="flex-grow bg-transparent",
                        ),
                        rx.el.input(
                            default_value=bm["url"],
                            on_blur=lambda val: BrowserState.edit_bookmark(
                                bm["url"], bm["title"], val
                            ),
                            class_name="flex-grow bg-transparent text-sm text-gray-500",
                        ),
                        rx.el.button(
                            rx.icon("trash-2", size=14),
                            on_click=lambda: BrowserState.remove_bookmark(bm["url"]),
                        ),
                        class_name="flex items-center p-2 hover:bg-gray-100 rounded-md",
                    ),
                ),
                class_name="my-4 max-h-96 overflow-y-auto",
            ),
            rx.radix.primitives.dialog.close(rx.el.button("Done")),
            class_name="bg-white p-6 rounded-lg shadow-lg",
            style={"maxWidth": "600px"},
        ),
    )


def dev_tools_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p("Developer Tools", class_name="font-semibold"),
            class_name="p-2 border-b",
        ),
        rx.el.div(
            rx.el.p(
                "> console.log('Hello from Taviad Surf!')",
                class_name="font-mono text-sm",
            ),
            class_name="p-4 h-full overflow-y-auto",
        ),
        class_name="h-full bg-gray-800 text-white border-t-2 border-gray-600",
    )


def statistics_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p("Browser Statistics", class_name="font-semibold"),
            class_name="p-2 border-b",
        ),
        rx.el.div(
            rx.el.h3("History", class_name="font-semibold mb-2"),
            rx.el.ul(
                rx.foreach(
                    BrowserState.tabs.reverse(),
                    lambda tab: rx.foreach(
                        tab["history"].reverse(),
                        lambda h: rx.el.li(h, class_name="truncate text-sm"),
                    ),
                ),
                class_name="list-disc list-inside text-gray-600",
            ),
            class_name="p-4",
        ),
        class_name="h-full bg-white border-t-2 border-gray-200",
    )


def index() -> rx.Component:
    return rx.el.div(
        browser_header(),
        bookmark_bar(),
        browser_content(),
        rx.window_event_listener(on_key_down=BrowserState.handle_key_down),
        class_name="flex flex-col h-screen w-screen bg-gray-50 font-['Open_Sans']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, title="Taviad Surf")