# Modbus TCP address map

Source: native `main.ld` located variable declarations and `HMI_Server.json`. The server listens on port 1502 and allocates 24 output coil bits and 16 holding registers. There are 22 located variables. Coil offsets are calculated as byte × 8 + bit; register offsets are zero-based. Actual HMI calls remain to be verified from Python source.

## Coils

| Variable | IEC location | Offset |
|---|---|---:|
| START | %QX0.0 | 0 |
| STOP | %QX0.1 | 1 |
| RESET_COUNTS | %QX0.2 | 2 |
| SYSTEM_RUN | %QX1.0 | 8 |
| WARNING_LIGHT | %QX1.1 | 9 |
| MOTOR | %QX1.2 | 10 |
| PROCESSOR | %QX1.3 | 11 |
| INSPECTION_ACTIVE | %QX1.4 | 12 |
| REJECT_ACTIVE | %QX1.5 | 13 |
| PACKAGING_ACTIVE | %QX1.6 | 14 |
| ORDER_COMPLETE | %QX1.7 | 15 |
| PRODUCT_SENSOR | %QX2.0 | 16 |
| QUALITY_FAIL | %QX2.1 | 17 |

## Holding registers

| Variable | IEC location | Offset |
|---|---|---:|
| ORDER_QUANTITY | %QW0 | 0 |
| BATCH_CAPACITY | %QW1 | 1 |
| DEFECT_PERCENT | %QW2 | 2 |
| ACCEPT_COUNT | %QW3 | 3 |
| REJECT_COUNT | %QW4 | 4 |
| TOTAL_PROCESSED | %QW5 | 5 |
| ORDER_REMAINING | %QW6 | 6 |
| BATCH_COUNT | %QW7 | 7 |
| PACKAGE_COUNT | %QW8 | 8 |
