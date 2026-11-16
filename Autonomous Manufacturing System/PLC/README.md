# PLC source

The native OpenPLC Editor V4 project is `OpenPLCProjects/` (project name: `Industrial_Automation`). It uses a cyclic 20 ms task running `main`.

- `project.json`: project configuration
- `devices/`: runtime selection, pin mapping and Modbus server configuration
- `pous/function-blocks/PRODUCT_SIMULATOR.st`: virtual product simulator
- `pous/programs/main.ld`: native 28-rung Ladder Logic program
- [PLCopen XML export](PLCopen_Export/plc.xml): interchange representation

Generated compiler files and binaries are excluded. Rebuild using OpenPLC Editor V4. A clean checkout has not yet been independently reopened and built.
