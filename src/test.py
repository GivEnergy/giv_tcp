from datetime import time
from givenergy_modbus.client import GivEnergyClient

client = GivEnergyClient(host="192.168.2.146")
client.refresh()
client.set_winter_mode(True)
# set a charging slot from 00:30 to 04:30
client.set_charge_slot_1(time(hour=0, minute=30), time(hour=4, minute=30))

# Data is returned as an instance of `model.Inverter` which
# allows indexing and direct attribute access
client.refresh()
assert client.inverter.serial_number == 'SA1234G567'
assert client.inverter['model'] == 'Hybrid'
assert client.inverter.v_pv1 == 1.4000000000000001
assert client.inverter.v_battery_cell01 == 3.117
assert client.inverter.e_grid_out_total == 0.6000000000000001
assert client.inverter.winter_mode