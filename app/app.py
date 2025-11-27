import reflex as rx
from app.states.search_state import SearchState
from app.states.details_state import DetailsState, DownloadGroup, DownloadLink
from app.states.auth_state import AuthState
from app.components.movie_card import movie_card


def navbar() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.icon("clapperboard", class_name="text-white w-6 h-6 mr-3"),
                    rx.el.h1(
                        "Adfree-MLWBD",
                        class_name="text-xl font-bold text-white tracking-tight",
                    ),
                    class_name="flex items-center",
                ),
                href="/",
                class_name="opacity-100",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="w-4 h-4 text-white"),
                on_click=AuthState.logout,
                class_name="p-2 border border-white/10 hover:bg-white hover:text-black transition-colors ml-auto rounded-sm",
            ),
            class_name="container mx-auto px-4 h-16 flex items-center",
        ),
        class_name="bg-black border-b border-white/10 sticky top-0 z-50",
    )


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.p(
                "Made with ai by Siam", class_name="text-xs font-medium text-white"
            ),
            class_name="container mx-auto px-4 py-8 flex justify-center items-center",
        ),
        class_name="bg-black border-t border-white/10 mt-auto",
    )


def login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("clapperboard", class_name="w-12 h-12 text-white mx-auto mb-6"),
                rx.el.h1(
                    "Welcome Back",
                    class_name="text-3xl font-bold text-white text-center mb-2",
                ),
                rx.el.p(
                    "Enter password to access the archives",
                    class_name="text-white text-center mb-8 text-sm",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.input(
                            placeholder="Enter Password",
                            type=rx.cond(AuthState.show_password, "text", "password"),
                            on_change=AuthState.set_password_input,
                            class_name="w-full bg-black border border-white/20 rounded-sm px-3 py-2 text-white placeholder:text-gray-500 focus:outline-none focus:border-white",
                            default_value=AuthState.password_input,
                        ),
                        rx.el.button(
                            rx.cond(
                                AuthState.show_password,
                                rx.icon("eye-off", class_name="w-4 h-4"),
                                rx.icon("eye", class_name="w-4 h-4"),
                            ),
                            on_click=AuthState.toggle_password_visibility,
                            class_name="absolute right-3 top-1/2 -translate-y-1/2 text-white",
                        ),
                        class_name="relative mb-4",
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.p(
                            AuthState.error_message,
                            class_name="text-white underline decoration-1 text-xs mb-4 text-center font-medium",
                        ),
                        rx.fragment(),
                    ),
                    rx.el.button(
                        "Access Library",
                        on_click=AuthState.login,
                        class_name="w-full bg-white text-black border border-white font-bold py-2 rounded-sm hover:bg-gray-200 transition-colors",
                    ),
                    class_name="w-full",
                ),
                class_name="bg-black p-6 border border-white/10 max-w-md w-full mx-4",
            ),
            class_name="container mx-auto min-h-screen flex items-center justify-center",
        ),
        class_name="min-h-screen bg-black font-['JetBrains_Mono']",
    )


def search_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.h2(
                "Find Your Movies",
                class_name="text-4xl md:text-6xl font-bold text-white mb-8 text-center tracking-tight",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-1/2 -translate-y-1/2 text-white w-4 h-4",
                    ),
                    rx.el.input(
                        placeholder="Search by movie name / link",
                        on_change=SearchState.set_search_query,
                        on_key_down=SearchState.handle_key_down,
                        class_name="w-full pl-10 pr-3 py-3 border border-white/20 outline-none bg-black focus:border-white text-base font-['JetBrains_Mono'] placeholder:text-gray-500 rounded-sm text-white",
                        default_value=SearchState.search_query,
                    ),
                    class_name="relative flex-grow",
                ),
                rx.el.button(
                    rx.cond(
                        SearchState.is_loading,
                        rx.spinner(color="black", size="2"),
                        rx.icon("arrow-right", class_name="w-5 h-5"),
                    ),
                    on_click=SearchState.search_movie_event,
                    disabled=SearchState.is_loading,
                    class_name="bg-white text-black border border-white px-6 py-3 font-bold rounded-sm disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center min-w-[60px] hover:bg-gray-200 transition-colors",
                ),
                class_name="flex flex-col sm:flex-row gap-2 max-w-3xl mx-auto",
            ),
            class_name="container mx-auto px-4 py-20 md:py-32",
        ),
        class_name="relative",
    )


def latest_movies_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.h2(
                "Latest Movies",
                class_name="text-xl font-bold text-white mb-8 flex items-center gap-3",
            ),
            rx.cond(
                SearchState.is_initial_loading,
                rx.el.div(
                    rx.spinner(color="white", size="3"),
                    rx.el.p(
                        "Loading library...",
                        class_name="mt-4 text-white font-medium text-sm",
                    ),
                    class_name="flex flex-col items-center justify-center py-20",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.foreach(SearchState.latest_movies, movie_card),
                        class_name="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6 md:gap-8",
                    ),
                    rx.cond(
                        SearchState.has_more_movies,
                        rx.el.div(
                            rx.el.button(
                                rx.cond(
                                    SearchState.is_loading_more,
                                    rx.spinner(color="white", size="2"),
                                    "Load More Movies",
                                ),
                                on_click=SearchState.load_more_movies,
                                disabled=SearchState.is_loading_more,
                                class_name="bg-black text-white border border-white/20 px-6 py-3 rounded-sm font-bold text-sm disabled:opacity-50 disabled:cursor-not-allowed mt-12 flex items-center justify-center gap-3 min-w-[160px] mx-auto hover:bg-white hover:text-black transition-colors",
                            ),
                            class_name="flex justify-center pb-12",
                        ),
                        rx.el.p(
                            "End of list",
                            class_name="text-white text-center mt-12 font-medium text-sm pb-12",
                        ),
                    ),
                ),
            ),
            class_name="container mx-auto px-4",
        )
    )


def results_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.cond(
                SearchState.is_loading,
                rx.el.div(
                    rx.spinner(color="white", size="3"),
                    rx.el.p(
                        "Searching archives...",
                        class_name="mt-4 text-white font-medium text-sm",
                    ),
                    class_name="flex flex-col items-center justify-center py-20",
                ),
                rx.cond(
                    SearchState.search_results.length() > 0,
                    rx.el.div(
                        rx.el.h2(
                            "Search Results",
                            class_name="text-xl font-bold text-white mb-8 flex items-center gap-3",
                        ),
                        rx.el.div(
                            rx.foreach(SearchState.search_results, movie_card),
                            class_name="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6 md:gap-8",
                        ),
                        class_name="mb-12",
                    ),
                    rx.el.div(
                        rx.cond(
                            SearchState.has_searched,
                            rx.el.div(
                                rx.icon("film", class_name="w-16 h-16 text-white mb-6"),
                                rx.el.p(
                                    "No movies found.",
                                    class_name="text-white text-lg mb-12",
                                ),
                                class_name="flex flex-col items-center justify-center py-12 text-center",
                            ),
                            rx.fragment(),
                        ),
                        latest_movies_section(),
                    ),
                ),
            ),
            class_name="container mx-auto px-4",
        )
    )


def index() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(search_section(), results_section(), class_name="flex-grow"),
        footer(),
        class_name="min-h-screen bg-black font-['JetBrains_Mono'] text-white flex flex-col",
    )


def link_item(link: DownloadLink) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                link["info"],
                class_name="px-2 py-1 bg-black text-white text-[10px] uppercase tracking-wider font-bold mr-3 min-w-[60px] text-center rounded-sm border border-white/20",
            ),
            rx.el.span(
                link["label"], class_name="font-bold text-sm text-white truncate"
            ),
            class_name="flex items-center flex-grow min-w-0 mr-4",
        ),
        rx.el.div(
            rx.cond(
                (DetailsState.selected_link_url == link["url"])
                & (DetailsState.direct_link != ""),
                rx.el.a(
                    rx.el.button(
                        rx.icon("download", class_name="w-3 h-3 mr-2"),
                        "Download",
                        class_name="px-3 py-1.5 bg-white text-black text-xs font-bold flex items-center uppercase tracking-wide rounded-sm border border-white hover:bg-gray-200 transition-colors",
                    ),
                    href=DetailsState.direct_link,
                    target="_blank",
                    rel="noreferrer noopener",
                    class_name="mr-0",
                ),
                rx.fragment(),
            ),
            rx.el.button(
                rx.cond(
                    (DetailsState.selected_link_url == link["url"])
                    & DetailsState.is_generating_direct,
                    rx.spinner(size="1", color="white"),
                    rx.el.span("Get Link"),
                ),
                on_click=DetailsState.get_direct_link(link["url"]),
                disabled=DetailsState.is_generating_direct,
                class_name="px-3 py-1.5 border border-white/20 hover:bg-white hover:text-black text-white text-xs font-bold disabled:opacity-50 uppercase tracking-wide rounded-sm bg-black transition-colors",
            ),
            class_name="flex items-center shrink-0 ml-auto",
        ),
        class_name="flex items-center justify-between p-3 border-b border-white/10 last:border-0 hover:bg-white/5 transition-colors",
    )


def links_card(group: DownloadGroup) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                group["title"],
                class_name="font-bold text-xs uppercase tracking-widest text-white",
            ),
            class_name="p-3 border-b border-white/10 bg-black",
        ),
        rx.el.div(rx.foreach(group["links"], link_item), class_name="flex flex-col"),
        class_name="bg-black border border-white/10 overflow-hidden mb-4 rounded-sm",
    )


def generated_link_section() -> rx.Component:
    return rx.cond(
        DetailsState.direct_link != "",
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Ready for Download",
                    class_name="text-white font-bold mb-4 text-sm uppercase tracking-wide",
                ),
                rx.el.div(
                    rx.el.input(
                        read_only=True,
                        class_name="flex-grow bg-black border border-white/20 text-white text-sm p-3 outline-none font-bold font-mono rounded-l-sm border-r-0",
                        default_value=DetailsState.direct_link,
                        key=DetailsState.direct_link,
                    ),
                    rx.el.button(
                        rx.icon("copy", class_name="w-4 h-4"),
                        "Copy",
                        on_click=DetailsState.copy_to_clipboard,
                        class_name="px-5 py-3 bg-white text-black text-sm font-bold flex items-center gap-2 rounded-r-sm border border-white hover:bg-gray-200 transition-colors",
                    ),
                    class_name="flex items-center",
                ),
                class_name="bg-black border border-white/10 p-4 mb-8 rounded-sm",
            )
        ),
    )


def details() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.a(
                        rx.icon("arrow-left", class_name="w-4 h-4 mr-2"),
                        "Back to Search",
                        href="/",
                        class_name="text-white flex items-center font-bold text-sm",
                    ),
                    class_name="mb-8",
                ),
                rx.el.h1(
                    "Movie Details",
                    class_name="text-3xl md:text-5xl font-bold text-white mb-10 tracking-tight",
                ),
                generated_link_section(),
                rx.cond(
                    DetailsState.is_fetching_links,
                    rx.el.div(
                        rx.spinner(color="white", size="3"),
                        rx.el.p(
                            "Extracting links...",
                            class_name="mt-4 text-white font-medium text-sm",
                        ),
                        class_name="flex flex-col items-center justify-center py-12",
                    ),
                    rx.el.div(
                        rx.foreach(DetailsState.download_groups, links_card),
                        class_name="flex flex-col gap-6",
                    ),
                ),
                class_name="container mx-auto px-4 py-8 max-w-4xl",
            ),
            class_name="flex-grow font-['JetBrains_Mono']",
        ),
        footer(),
        class_name="min-h-screen bg-black font-['JetBrains_Mono'] flex flex-col",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.meta(
            name="description",
            content="Adfree-MLWBD: Clean, fast, and minimal movie search.",
        ),
        rx.el.title("Adfree-MLWBD | Minimal Movie Scraper"),
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/", on_load=[AuthState.on_load, SearchState.on_load])
app.add_page(
    details, route="/details", on_load=[AuthState.on_load, DetailsState.on_load]
)
app.add_page(login_page, route="/login", on_load=AuthState.on_load)