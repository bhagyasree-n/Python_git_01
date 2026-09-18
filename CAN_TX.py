import sys
import os

# So "Tosun" package is importable — point this at the folder that CONTAINS Tosun/
sys.path.insert(0, r"B:\\Workspaces\\PYTHON\\CAN\\Tosun-Pyflash\\Tosun-Pyflash\\GenX-Flashing")   # adjust to your actual layout

from Tosun.libtosun import libtosunBus
import can

# ---- Configure and open the bus ----
configs = [
    {
        "FChannel": 0,
        "rate_baudrate": 500,      # kbps (arbitration phase)
        "data_baudrate": 2000,     # kbps (CAN FD data phase, ignored if is_fd=False)
        "enable_120hm": True,      # 120ohm termination
        "is_fd": False,            # classic CAN, not CAN FD
    }
]

bus = libtosunBus(channel=0, bitrate=500000, configs=configs)

# ---- Send a classic CAN message ----
msg = can.Message(
    arbitration_id=0x7E0,
    data=[20, 32, 3, 4, 5, 6, 7, 8],
    is_extended_id=False,
)
bus.send(msg)
print("Sent:", msg)

# ---- Optional: receive ----
# rx = bus.recv(timeout=1.0)
# if rx is not None:
#     print("Received:", rx)

bus.shutdown()