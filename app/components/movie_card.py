import reflex as rx


def movie_card(movie: dict[str, str]) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.image(
                    src=movie["image"],
                    alt=movie["title"],
                    class_name="w-full h-full object-cover",
                    loading="lazy",
                ),
                class_name="aspect-[2/3] overflow-hidden relative bg-black",
            ),
            rx.el.div(
                rx.el.h3(
                    movie["title"],
                    class_name="text-xs md:text-sm font-bold text-white line-clamp-2 leading-tight font-['JetBrains_Mono']",
                ),
                class_name="p-2 flex-grow flex flex-col bg-black relative z-10 border-t border-white/10",
            ),
            class_name="flex flex-col bg-black h-full border border-white/10",
        ),
        href="/details?url=" + movie["link"],
        class_name="block h-full",
    )