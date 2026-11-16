# PLC source

The native OpenPLC Editor V4 project is `OpenPLCProjects/` (project name: `Industrial_Automation`). It uses a cyclic 20 ms task running `main`.

- `project.json`: project configuration
- `devices/`: runtime selection, pin mapping and Modbus server configuration
- `pous/function-blocks/PRODUCT_SIMULATOR.st`: simulated product arrival, quality and clearance
- `pous/programs/main.ld`: native 28-rung Ladder Logic program (upload pending)

The project cannot yet be reopened from the repository until `main.ld` is uploaded. Generated compiler files, simulator dependencies and binary artifacts are intentionally excluded; rebuild using OpenPLC Editor V4.
