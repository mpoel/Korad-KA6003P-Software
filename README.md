Korad-KA6003P-Software Tool - CLI Only 
======================================

Based on the [Korad-KA6003P-Software](https://github.com/Tamagotono/Korad-KA6003P-Software), this is a fork that aims to
make this Korad-KA6003P power supply manageable via a simple CLI tool. The primary features are:
- Set target voltage and max current
- Provides measured value for voltage and current to stdout (simply redirect for logging purposes)
- OCP/OVP/Output can be set via flags
- Serial device can be configured via CLI flag
- Polling interval is configurable as well, note that ca. 50ms is the lower limit
