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

        if device.name == "VEBus":
            # Einfügen des Tagesverbrauches aus API

            try:
                device.data["Verbrauch heute"] = {"value": round(float(api_data_in[0]), 2), "unit": "kWh"}
            except ValueError:
                pass

        if device.name == "Pylontech":
            device.data["Battery Power"] = {"value": round(float(device.data["Battery Voltage"]["value"]) * float(device.data["Battery Current"]["value"])), "unit": "W"}

        if device.name == "System":
            device.data["Total Consumption"] = {"value": 0, "unit": "W"}
            for key in device.data.keys():
                if "Consumption L" in key:
                    device.data["Total Consumption"]["value"] += float(device.data[key]['value'])
            '{:.2f}'.format(device.data["Total Consumption"]["value"])

        temp_dict["Device Name"] = device.name
        temp_dict["Data"] = device.data

        return_dict[device.unit_id] = temp_dict

    data_out[0] = json.dumps(return_dict)
    print(api_data_in)
    api_data_in = [""]

