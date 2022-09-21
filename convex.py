import threading
from typing import Callable, List, Tuple, Any, Dict
from uuid import uuid4
import websocket
import _thread
import time
import rel
import json
import difflib
import threading


import websocket
import _thread
import time
import rel

url = "wss://murky-swan-635.convex.cloud/api/0.1.10/sync"

class Convex:
    """
    >>> c = Convex(url)
    >>> c.on_query("listOpinions.js:default", [], cb)
    >>> c.on_query("listOpinions", [], cb2)
    >>> c.mutate("upvote", [13])
    >>> 
    """

    def __init__(self, url):
        self.ws = websocket.WebSocketApp(url,
                              on_open=self._on_open,
                              on_message=self._on_message,
                              on_error=self._on_error,
                              on_close=self._on_close)
        self.queries: Dict[int, Callable[[Any], None]] = {}
        self._next_query_id = 1
        self.opened = False
        threading.Thread(target=self.ws.run_forever).start()
        while not self.opened:
            time.sleep(.05)

    def _on_message(self, ws, message):
        msg = json.loads(message)
        if msg['type'] == 'Transition':
            for mod in msg['modifications']:
                if mod['type'] == 'QueryUpdated':
                    self.queries[mod['queryId']](mod['value'])

    def _on_error(self, ws, error: Exception):
        raise error

    def _on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def _on_open(self, ws):
        print("Opened connection")
        self._send_message(connect())
        self.opened = True

    def _send_message(self, message):
        print('sending:', message)
        self.ws.send(json.dumps(message))

    def on_query(self, udf_path, args, cb):
        self.queries[self._next_query_id] = cb
        self._send_message(modify_query_set([(udf_path, args, self._next_query_id)]))
        self._next_query_id += 1

    def wait(self):
        self.ws.run_forever(dispatcher=rel)


import pprint
def main():
    c = Convex(url)
    c.on_query("listOpinions.js:default", [], lambda v: pprint.pprint(v))
    import time; time.sleep(10)
    


def connect():
    return {
        "type": "Connect",
        "sessionId": str(uuid4()),
        "connectionCount": 0,
    }

def modify_query_set(queries: List[Tuple[str, List[Any], int]]):
    return {
        "type": "ModifyQuerySet",
        "baseVersion": 0,
        "newVersion": 1,
        "modifications": [
            {
                "type": "Add",
                "queryId": i,
                "udfPath": udf_path,
                "args": args,
            }
            for (udf_path, args, i) in queries
        ],
    }


#websocket.enableTrace(True)
if __name__ == '__main__':
    main()
