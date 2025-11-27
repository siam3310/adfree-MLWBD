import reflex as rx
from app.password_config import PASSWORD


class AuthState(rx.State):
    auth_token: str = rx.LocalStorage("", name="auth_token")
    password_input: str = ""
    show_password: bool = False
    error_message: str = ""
    is_hydrated: bool = False

    @rx.event
    def set_password_input(self, value: str):
        self.password_input = value
        self.error_message = ""

    @rx.event
    def toggle_password_visibility(self):
        self.show_password = not self.show_password

    @rx.event
    def login(self):
        if self.password_input == PASSWORD:
            self.auth_token = self.password_input
            self.error_message = ""
            return rx.redirect("/")
        else:
            self.error_message = "Incorrect password entered."

    @rx.event
    def logout(self):
        self.auth_token = ""
        return rx.redirect("/login")

    @rx.event
    def check_auth(self):
        if not self.is_hydrated:
            return
        current_path = self.router.page.path
        if current_path == "/login":
            if self.auth_token == PASSWORD:
                return rx.redirect("/")
            return
        if self.auth_token != PASSWORD:
            return rx.redirect("/login")

    @rx.event
    def on_load(self):
        self.is_hydrated = True
        return AuthState.check_auth