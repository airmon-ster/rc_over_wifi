from time import sleep
from inputs import get_gamepad
import math
import threading
from dataclasses import dataclass
import websockets
import websockets.sync.server


@dataclass
class Server():
    websocket: websockets.sync.server.ServerConnection = None

    def __init__(self, XboxController) -> None:
        self.XboxController = XboxController

        self.server_thread = threading.Thread(target=self.serve, args=())
        self.server_thread.daemon = True
        self.server_thread.start()

        self.server_thread.join()

    def serve(self) -> None:
        print("Starting websocket server...")
        try:
            with websockets.sync.server.serve(self.handler, "0.0.0.0", 8765) as server:
                print("Websocket server started...")
                server.serve_forever()
        except Exception as e:
            print(f"Error in serve: {repr(e)}")

    def handler(self, websocket):
        global g_websocket
        g_websocket = websocket

        try:
            print("Client connected...")
            while True:
                data = self.XboxController.read()
                websocket.send(f"{data[0]},{data[1]},{data[2]}")
                # run every 30Hz
                sleep(1 / 30)
        except websockets.ConnectionClosed:
            print("Connection closed")
            g_websocket = None
        except Exception as e:
            print(f"Error in handler: {repr(e)}")
            g_websocket = None


class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):

        self.LeftJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def read(self):  # return the buttons/triggers that you care about in this methode
        x = self.LeftJoystickX
        throttle = self.RightTrigger
        brake = self.LeftTrigger
        return [x, throttle, brake]

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1


if __name__ == '__main__':
    controller = XboxController()
    server = Server(controller)
    # while True:
    #     print(controller.read())
