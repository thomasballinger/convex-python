from convex import Convex
import pprint

url = "wss://murky-swan-635.convex.cloud/api/0.1.10/sync"


c = Convex(url)

from rich.markdown import Markdown

from textual import events
from textual.app import App
from textual.widgets import Header, Footer, Placeholder, ScrollView


from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer, Placeholder
from rich.panel import Panel
from textual.widget import Widget

class OpinionsWidget(Widget):

    mouse_over = Reactive(False)

    opinions = Reactive([])

    def watch_opinions(self, value: list) -> None:
        self.refresh()

    def render(self) -> Panel:
        opinions = [(d['agree'], d['opinion']) for d in self.opinions]
        return Panel(pprint.pformat(opinions), style=("on red" if self.mouse_over else ""))

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
    
    def on_convex_update(self, value):
        self.opinions = value


class SmoothApp(App):
    """Demonstrates smooth animation. Press 'b' to see it in action."""

    async def on_load(self) -> None:
        """Bind keys here."""
        await self.bind("b", "toggle_sidebar", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")  

    show_bar = Reactive(False)

    def watch_show_bar(self, show_bar: bool) -> None:
        """Called when show_bar changes."""
        self.bar.animate("layout_offset_x", 0 if show_bar else -40)

    def action_toggle_sidebar(self) -> None:
        """Called when user hits 'b' key."""
        self.show_bar = not self.show_bar

    async def on_mount(self) -> None:
        """Build layout here."""
        footer = Footer()
        self.bar = Placeholder(name="left")

        await self.view.dock(footer, edge="bottom")
        ow = OpinionsWidget()
        c.on_query("listOpinions.js:default", [], ow.on_convex_update)

        await self.view.dock(ow, Placeholder(), edge="top")
        await self.view.dock(self.bar, edge="left", size=40, z=1)

        self.bar.layout_offset_x = -40

        # self.set_timer(10, lambda: self.action("quit"))


SmoothApp.run(log="textual.log", log_verbosity=2)