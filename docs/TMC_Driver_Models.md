# TMC Driver Model Definitions

This document explains how to use the `driver_model` configuration option for TMC stepper drivers.

## Overview

Many stepper motor drivers use non-standard sense resistor values, which can lead to incorrect current settings if not properly configured. Incorrect current settings may result in poor motor performance or even hardware damage.

Kalico addresses this by allowing you to specify predefined driver models with reviewed sense resistor and maximum current values, eliminating the need to manually look up and configure these values.

## Configuration

You can configure your TMC drivers in two ways:

1. **Recommended**: Use `driver_model` to select a predefined configuration
   ```
   [tmc2209 stepper_x]
   driver_model: REFERENCE_2209
   ```

2. **Alternative**: Manually specify the sense resistor value
   ```
   [tmc2209 stepper_x]
   sense_resistor: 0.11
   ```

> [!IMPORTANT]
> Either `driver_model` or `sense_resistor` **must** be specified. Kalico will raise an error if neither option is provided, as this could lead to incorrect current settings and potential hardware damage.

If both `driver_model` and `sense_resistor` are specified, Kalico will use the provided `sense_resistor` value and issue a warning.

> [!NOTE]
> Some drivers with variable sense resistors (like FYSETC EXT2160) are intentionally omitted from the table. For these drivers, you must manually set the sense_resistor value.

## Available Driver Models

| Driver Type                             | Config Name             | Sense Resistor | Max Current |
|-----------------------------------------|-------------------------|----------------|-------------|
| BTT Kraken S1-4                         | KRAKEN_2160_8A          | 0.022          | 8           |
| BTT Kraken S5-8                         | KRAKEN_2160_3A          | 0.075          | 3           |
| LDO Leviathan HV0,HV1                   | REFERENCE_5160          | 0.075          | 3           |
| LDO Leviathan S0-4                      | REFERENCE_2209          | 0.11           | 2           |
| BTT TMC2208                             | REFERENCE_2209          | 0.11           | 2           |
| BTT TMC2209                             | REFERENCE_2209          | 0.11           | 2           |
| BTT TMC2240                             | BTT_2240                | 0.11           | 2           |
| BTT TMC5160T Pro                        | REFERENCE_5160          | 0.075          | 3           |
| BTT EZ2130                              | REFERENCE_2209          | 0.11           | 2           |
| BTT EZ2208                              | REFERENCE_2209          | 0.11           | 2           |
| BTT EZ2209                              | REFERENCE_2209          | 0.11           | 2           |
| BTT EZ2225                              | REFERENCE_2209          | 0.11           | 2           |
| BTT EZ2226                              | REFERENCE_2209          | 0.11           | 2           |
| BTT EZ5160 Pro                          | BTT_EZ_5160_PRO         | 0.075          | 2.5         |
| BTT EZ5160 RGB                          | BTT_EZ_5160_RGB         | 0.05           | 4.7         |
| BTT EZ6609                              | REFERENCE_2209          | 0.11           | 2           |
| BTT TMC5160T Plus                       | BTT_EXT_5160            | 0.022          | 10.6        |
| COREVUS TMC2209                         | COREVUS_2209            | 0.1            | 3           |
| COREVUS TMC2160 OLD                     | COREVUS_2160_OLD        | 0.03           | 3           |
| COREVUS TMC2160 5A                      | COREVUS_2160_5A         | 0.03           | 5           |
| COREVUS TMC2160                         | COREVUS_2160            | 0.05           | 3           |
| Watterott SilentStepStick TMC2100       | REFERENCE_WOTT          | 0.11           | 1.2         |
| Watterott SilentStepStick TMC2130       | REFERENCE_WOTT          | 0.11           | 1.2         |
| Watterott SilentStepStick TMC2208       | REFERENCE_WOTT          | 0.11           | 1.2         |
| Watterott SilentStepStick TMC2209       | WOTT_2209               | 0.11           | 1.7         |
| Watterott SilentStepStick TMC5160       | REFERENCE_5160          | 0.075          | 3           |
| Watterott SilentStepStick TMC5160HV     | REFERENCE_5160          | 0.075          | 3           |
| FYSETC TMC2100                          | REFERENCE_WOTT          | 0.11           | 1.2         |
| FYSETC TMC2130                          | REFERENCE_WOTT          | 0.11           | 1.2         |
| FYSETC TMC2208                          | REFERENCE_WOTT          | 0.11           | 1.2         |
| FYSETC TMC2209                          | WOTT_2209               | 0.11           | 1.7         |
| FYSETC TMC2225                          | FYSETC_2225             | 0.11           | 1.4         |
| FYSETC TMC2226                          | REFERENCE_2209          | 0.11           | 2           |
| FYSETC HV5160                           | REFERENCE_5160          | 0.075          | 3           |
| FYSETC QHV5160                          | REFERENCE_5160          | 0.075          | 3           |
| FYSETC Silent5161                       | FYSETC_5161             | 0.06           | 3.5         |
| MKS 2130                                | REFERENCE_2209          | 0.11           | 2           |
| MKS 2208                                | REFERENCE_2209          | 0.11           | 2           |
| MKS 2209                                | REFERENCE_2209          | 0.11           | 2           |
| MKS 2225                                | REFERENCE_2209          | 0.11           | 2           |
| MKS 2226                                | MKS_2226                | 0.17           | 2.5         |
| MKS 2240                                | REFERENCE_2209          | 0.11           | 2           |
| Mellow Fly 2209                         | REFERENCE_2209          | 0.11           | 2           |
| Mellow Fly 5160                         | MELLOW_FLY_5160         | 0.11           | 3           |
| Mellow Fly HV-TMC5160 Pro               | MELLOW_FLY_HV_5160_Pro  | 0.033          | 6           |
