# Manufacturing HMI

The original `manufacturing_hmi.py` uses CustomTkinter and PyModbus. The HMI connects to 127.0.0.1:1502, device ID 1, and reads nine holding registers and 18 coil positions. A background worker uses queues to keep network operations separate from the GUI thread. The idle polling timeout is 300 ms; GUI updates are scheduled every 100 ms. Start, stop and reset use 250 ms coil pulses.

## Operator features

- Set order quantity and batch capacity (1–1000), and defect probability (0–99%).
- Apply settings with PLC readback verification.
- Start, stop and reset production with state-based restrictions.
- Display accepted, rejected, processed, remaining and package counts, quality yield and order progress.
- Display schematic station activity, connection state and communication errors.
- Reconnect after communication failure and release pending command coils.

Closing the HMI does not stop the independent PLC runtime. The display is schematic, not a physical position sensor or safety system.

## Launch

Install Python with Tk support and the dependencies listed in `requirements.txt`, start the configured PLC runtime, then run:

```sh
python -m pip install -r requirements.txt
python manufacturing_hmi.py
```

The development machine uses Python 3.12, PyModbus 3.16.2 and CustomTkinter 6.0.0. The dependency file pins the observed package versions.
