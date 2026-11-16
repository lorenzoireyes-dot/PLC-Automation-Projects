FUNCTION_BLOCK PRODUCT_SIMULATOR
  VAR
    ARRIVAL_TIMER : TON;
    RANDOM_SEED : DINT := 12345;
    RANDOM_VALUE : DINT := 0;
    SIM_STATE : INT := 0;
    CLEAR_TIMER : TON;
  END_VAR
  VAR_INPUT
    READY : BOOL;
    CONVEYOR : BOOL;
    ACCEPTED : BOOL;
    REJECTED : BOOL;
    REJECTING : BOOL;
    PACKAGING : BOOL;
    TARGET_REACHED : BOOL;
    DEFECT_RATE : INT;
  END_VAR
  VAR_OUTPUT
    SENSOR_OUT : BOOL;
    QUALITY_OUT : BOOL;
  END_VAR

(* Virtual product arrival timer *)
ARRIVAL_TIMER(
    IN := READY AND CONVEYOR
          AND NOT TARGET_REACHED
          AND (SIM_STATE = 0),
    PT := T#2s
);

(* Product clearance delay *)
CLEAR_TIMER(
    IN := SIM_STATE = 30,
    PT := T#1s
);

IF NOT READY THEN

    SENSOR_OUT := FALSE;
    QUALITY_OUT := FALSE;
    SIM_STATE := 0;

ELSE

    CASE SIM_STATE OF

        0:
            (* Wait for next product *)
            IF ARRIVAL_TIMER.Q THEN
                SIM_STATE := 10;
            END_IF;

        10:
            (* Generate pseudorandom quality *)
            RANDOM_SEED :=
                (RANDOM_SEED * 25173 + 13849)
                MOD 65536;

            RANDOM_VALUE :=
                (RANDOM_SEED * 100) / 65536;

            QUALITY_OUT :=
                RANDOM_VALUE <
                INT_TO_DINT(DEFECT_RATE);

            SENSOR_OUT := TRUE;
            SIM_STATE := 20;

        20:
            (* Wait until product is finished *)
            IF ACCEPTED AND NOT PACKAGING THEN

                SIM_STATE := 30;

            ELSIF REJECTED AND NOT REJECTING THEN

                SIM_STATE := 30;

            END_IF;

        30:
            (* Clear simulated product *)
            SENSOR_OUT := FALSE;

            IF CLEAR_TIMER.Q THEN
                QUALITY_OUT := FALSE;
                SIM_STATE := 0;
            END_IF;

    ELSE
        SENSOR_OUT := FALSE;
        QUALITY_OUT := FALSE;
        SIM_STATE := 0;

    END_CASE;

END_IF;

END_FUNCTION_BLOCK