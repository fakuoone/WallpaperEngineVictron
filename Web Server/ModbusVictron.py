from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import json
import re


class Device:
    def __init__(self, unit_id, name, registers):
        self.unit_id = unit_id
        self.name = name
        self.registers = registers
        self.data = {}


def acquire_data(client, dev_list, data_out, api_data_in, scheduler):
    scheduler.enter(1, 1, acquire_data, (client, dev_list, data_out, api_data_in, scheduler))

    return_dict = {}
    divisor = 1

    for device in dev_list:
        temp_dict = {}
        client.unit_id = device.unit_id

        for register in device.registers["registers"].items():

            reg_name, reg_addr = list(register[1].items())[0]
            divisor = register[1]["divisor"]
            unit = register[1]["unit"]
            modbus_coil = (client.read_holding_registers(reg_addr))[0]
            modbus_coil = utils.get_2comp(modbus_coil, 16)
            if unit not in ['%', '°C', 'W']:
                device.data[reg_name] = {"value": '{:.2f}'.format(modbus_coil / divisor), "unit": unit}
            else:
                device.data[reg_name] = {"value": modbus_coil / divisor, "unit": unit}
            #print(reg_name, device.data[reg_name])

        if device.name == "VEBus":
            # Einfügen des Tagesverbrauches aus API
            if api_data_in != [""]:
                device.data["Verbrauch heute"] = {"value": '{:.2f}'.format(round(float(api_data_in[0]["total_consumption"][0][1]), 2)),
                                                  "unit": "kWh"}
                try:
                    grid_history_from = float(api_data_in[0]['grid_history_from'][0][1])
                except TypeError:
                    grid_history_from = 0
                try:
                    grid_history_to = float(api_data_in[0]['grid_history_to'][0][1])
                except TypeError:
                    grid_history_to = 0

                device.data["Netzbezug heute"] = {"value": '{:.2f}'.format((grid_history_from - grid_history_to)), "unit": "kWh"}

        if device.name == "Pylontech":
            device.data["Battery Power"] = {"value": round(float(device.data["Battery Voltage"]["value"]) * float(device.data["Battery Current"]["value"])), "unit": "W"}

        if device.name == "System":
            device.data["Total Consumption"] = {"value": 0, "unit": "W"}
            for key in device.data.keys():
                if "Consumption L" in key:
                    device.data["Total Consumption"]["value"] += float(device.data[key]['value'])
            '{:.2f}'.format(device.data["Total Consumption"]["value"])

            device.data["Input Power"] = {"value": round(float(device.data['Input Power L1']["value"]) +
                                                         float(device.data['Input Power L2']["value"]) +
                                                         float(device.data['Input Power L3']["value"])), "unit": "W"}

        temp_dict["Device Name"] = device.name
        temp_dict["Data"] = device.data

        return_dict[device.unit_id] = temp_dict

    data_out[0] = json.dumps(return_dict)
    api_data_in = [""]

