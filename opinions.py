from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, Static, DataTable
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.message import Message

from convex import Convex
from typing_extensions import TypedDict

OpinionDict = TypedDict('OpinionDict', {
    '_creationTime': float,
    '_id': dict,
    'agree': int,
    'allVotes': int,
    'disagree': int,
    'opinion': str,
})

url = "wss://murky-swan-635.convex.cloud/api/0.1.10/sync"

class Content(Widget):
    body = reactive('opinion goes here')

    def render(self):
        return self.body

class OpinionWidget(Static):
    def __init__(self, od: OpinionDict):
        self.opinion_id = str(od['_id'])
        super().__init__();
        self.initial_data = od;

    data: reactive[OpinionDict] = reactive(None, layout=True)

    def on_mount(self):
        self.data = self.initial_data

    def watch_data(self, prev: str, cur: str):
        if not cur: return
        opinion = self.query_one(Content).body = cur['opinion']
        self.query_one("#agree").label = f"agree ({int(cur['agree'])})"
        self.query_one("#disagree").label = f"disagree ({int(cur['disagree'])})"

    def compose(self):
        yield Horizontal(
            Button("agree", id="agree"),
            Button("disagree", id="disagree"),
            Content()
        )

class DataUpdate(Message):
    def __init__(self, data):
        super().__init__(self);
        self.data = data
    def __repr__(self):
        return 'DataUpdate(data)'

class Vote(Message):
    def __init__(self, opinion, agree=True):
        self.opinion = opinion
        self.agree = agree

class OpinionsApp(App):
    """A Textual app to manage stopwatches."""
    CSS_PATH = "style.css"

    def __init__(self):
        super().__init__()
        self.c = Convex(url)

    def on_mount(self):
        self.c.on_query("listOpinions.js:default", [], self.on_convex_update)

    # called from another thread
    def on_convex_update(self, data):
        self.post_message_no_wait(DataUpdate(data))

    def on_data_update(self, message: DataUpdate):
        self.update_data(message.data)

    def update_data(self, opinion_dicts):
        opinions_by_id = {str(od['_id']): od for od in opinion_dicts}

        opinion_widgets = list(self.query(OpinionWidget).results())
        # remove opinions no longer present
        for widget in opinion_widgets:
            if widget.opinion_id not in opinions_by_id:
                widget.remove()

        # add new opinions
        opinion_widgets = list(self.query(OpinionWidget).results())
        existing = {w.opinion_id for w in opinion_widgets}
        for od in opinion_dicts:
            if str(od['_id']) not in existing:
                vertical = self.query_one(Vertical)
                vertical.mount(OpinionWidget(od))

        # update all widgets
        opinion_widgets = list(self.query(OpinionWidget).results())
        for widget in opinion_widgets:
            widget.data = opinions_by_id[widget.opinion_id]

        # TODO update order of opinions
        # maybe remove all and recreate each time?

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def on_button_pressed(self, event: Button.Pressed):
        opinion = event.sender.parent.parent.data['opinion']
        agree = event.sender.id == 'agree'
        method = 'agreeWithOpinion' if agree else 'disagreeWithOpinion'
        self.c.mutate(method, [opinion])

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Vertical()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = OpinionsApp()
    app.run()
