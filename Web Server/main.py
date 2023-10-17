import ModbusVictron
import VRMapi
from http.server import HTTPServer, BaseHTTPRequestHandler
import sched, time
import threading

hostName = "192.168.178.41"
serverPort = 9999
modbus_data = [""]
api_installation_data = [""]


class MyServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        # self.send_header("Access-Control-Allow-Headers", "application/json")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(bytes(modbus_data[0], "utf-8"))


if __name__ == "__main__":

    # MODBUS CLIENT
    modbus_client = ModbusVictron.ModbusClient(port=502, host="192.168.178.110")

    # in den Registernamen ist ein Divisor eingebaut (selbst ausgedacht)
    device_list = [ModbusVictron.Device(24, "Temperatursensor",
                                        {"registers": {1: {"Temperatur": 3304, "unit": '°C', "divisor": 100}}}),
                   ModbusVictron.Device(100, "System",
                                        {"registers": {1: {"Leistung String 1": 3724, "unit": 'W', "divisor": 1},
                                                       2: {"Leistung String 2": 3725, "unit": 'W', "divisor": 1},
                                                       3: {"Energie heute": 784, "unit": 'kWh', "divisor": 10},
                                                       4: {"Energie gestern": 786, "unit": 'kWh', "divisor": 10},
                                                       5: {"Energie heute 1": 3708, "unit": 'kWh', "divisor": 10},
                                                       6: {"Energie gestern 1": 3712, "unit": 'kWh', "divisor": 10},
                                                       7: {"Energie heute 2": 3709, "unit": 'kWh', "divisor": 10},
                                                       8: {"Energie gestern 2": 3713, "unit": 'kWh', "divisor": 10},
                                                       9: {"AC Consumption L1": 817, "unit": 'W', "divisor": 1},
                                                       10: {"AC Consumption L2": 818, "unit": 'W', "divisor": 1},
                                                       11: {"AC Consumption L3": 819, "unit": 'W', "divisor": 1},
                                                       12: {"Input Power L1": 820, "unit": 'W', "divisor": 1},
                                                       13: {"Input Power L2": 821, "unit": 'W', "divisor": 1},
                                                       14: {"Input Power L3": 822, "unit": 'W', "divisor": 1}}}),
                   ModbusVictron.Device(225, "Pylontech",
                                        {"registers": {1: {"Battery Voltage": 259, "unit": 'V', "divisor": 100},
                                                       2: {"Battery Current": 261, "unit": 'A', "divisor": 10},
                                                       3: {"Battery SOC": 266, "unit": '%', "divisor": 10}}}),
                   ModbusVictron.Device(227, "VEBus",
                                        {"registers": {1: {"Input Voltage L1": 3, "unit": 'V', "divisor": 10},
                                                       2: {"Input Voltage L2": 4, "unit": 'V', "divisor": 10},
                                                       3: {"Input Voltage L3": 5, "unit": 'V', "divisor": 10},
                                                       8: {"Energy Load L1": 74, "unit": 'kWh', "divisor": 1},
                                                       9: {"Energy Load L2": 76, "unit": 'kWh', "divisor": 1}}})]

    # WEB SERVER
    webServer = HTTPServer((hostName, serverPort), MyServer)
    threading.Thread(target=webServer.serve_forever).start()
    print("Server started http://%s:%s" % (hostName, serverPort))

    # MODBUS

    server_sched = sched.scheduler(time.time, time.sleep)
    server_sched.enter(1, 1, ModbusVictron.acquire_data, (modbus_client, device_list, modbus_data,
                                                          api_installation_data,server_sched))
    threading.Thread(target=server_sched.run).start()

    # API request
    api_connection, inst_id = VRMapi.initiate_connection()
    api_token = VRMapi.get_token(api_connection, inst_id)

    api_sched = sched.scheduler(time.time, time.sleep)
    api_sched.enter(10, 2, VRMapi.get_installation_data,
                    (api_connection, api_token, "stats?", inst_id, api_installation_data, api_sched))
    api_sched.run()


    #try:
    #    webServer.serve_forever()
    #except KeyboardInterrupt:
    #    pass

    #webServer.server_close()
    print("Server stopped.")
