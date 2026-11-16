# Autonomous PLC Manufacturing and Customer Order Fulfillment System

## Overview

An integrated virtual manufacturing system that processes customer orders, simulates product inspection, rejects defective units, packages accepted products into full or partial batches, and automatically stops when the requested accepted quantity is reached.

## Architecture

Python CustomTkinter HMI communicates via Modbus TCP with OpenPLC Runtime V4 running in Docker. The PLC executes 28 Ladder Logic rungs and a custom Structured Text PRODUCT_SIMULATOR state machine.

## Control sequence

1. Enter the customer order and start production.
2. Simulate product manufacturing and inspection.
3. Accept conforming products and reject defective products.
4. Package accepted products in full batches or a final partial batch.
5. Stop automatically once the accepted order quantity is fulfilled.

## Implementation

- IEC 61131-3 Ladder Logic and Structured Text
- TON, TP, CTU, ADD, SUB, GE, SET and RESET instructions
- Pseudorandom defect simulation
- Modbus TCP communication with a Python HMI
- Dockerized OpenPLC Runtime V4

## Repository layout

- [PLC](PLC/README.md): PLC project source and control logic.
- [HMI](HMI/README.md): Python operator interface.
- [Runtime](Runtime/README.md): Runtime configuration and deployment.
- [Documentation](Documentation/README.md): Architecture, address mapping and testing documentation.
- [Media](Media/README.md): Screenshots and demonstration media.

## Testing status

Integrated virtual production and HMI communication were reported working during development. Physical PLC hardware was not used. Source publication, exact dependency versions, reproducible setup validation and demonstration recording are pending.
