from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class MyDashboard(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("📊 My Command-Line Dashboard")
        yield Footer()

if __name__ == "__main__":
    MyDashboard().run()
    v = 1