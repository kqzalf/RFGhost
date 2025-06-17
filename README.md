# RFGhost

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Pylint Score](https://img.shields.io/badge/pylint-9.96%2F10-brightgreen.svg)](https://github.com/yourusername/RFGhost)

RFGhost is a Python application designed to monitor and detect anomalies in RF signals. It uses statistical methods to analyze signal patterns and alerts users when unusual activity is detected. The application supports both HackRF hardware and simulated signals, with MQTT and Serial outputs for integration with Home Assistant and other systems.

## Features

- **RF Signal Monitoring**: 
  - Support for HackRF One SDR
  - Simulated signal mode for testing
  - Configurable sample rates and frequencies
  - Real-time signal processing

- **Anomaly Detection**: 
  - Statistical analysis for pattern detection
  - Configurable detection thresholds
  - Real-time anomaly scoring
  - Historical data analysis

- **Multiple Outputs**: 
  - MQTT integration for Home Assistant
  - Serial output for custom devices
  - JSON-formatted data
  - Configurable output rates

- **Home Assistant Integration**: 
  - Native MQTT sensor support
  - Real-time signal strength monitoring
  - Anomaly detection alerts
  - Historical data visualization

- **Configurable**: 
  - YAML-based configuration
  - Runtime parameter adjustment
  - Multiple frequency support
  - Customizable thresholds

- **Alert System**: 
  - Email notifications
  - Webhook alerts
  - MQTT status updates
  - Configurable alert thresholds

## Prerequisites

- Python 3.10 or higher
- Required Python packages (see `requirements.txt` and `requirements-dev.txt`)
- For HackRF support:
  - HackRF One SDR
  - USB 2.0 or higher port
  - libusb drivers installed

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RFGhost.git
   cd RFGhost
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development dependencies
   ```

4. Configure the application:
   - Copy `config.yaml.example` to `config.yaml`
   - Update the configuration settings as needed

## Usage

1. Start the application:
   ```bash
   python -m rfghost.main
   ```

2. For debug mode:
   ```bash
   python -m rfghost.main --debug
   ```

3. Use a custom configuration file:
   ```bash
   python -m rfghost.main -c custom_config.yaml
   ```

## HackRF Configuration

1. Basic HackRF setup in `config.yaml`:
   ```yaml
   rf_interface:
     type: "hackrf"
     sample_rate: 2000000  # 2MHz
     frequency: 433920000  # 433.92MHz in Hz
     gain: 20  # dB
     lna_gain: 40  # dB (0-40)
     vga_gain: 40  # dB (0-62)
     buffer_size: 16384  # Samples per read
     usb_timeout: 1000  # ms
   ```

2. Advanced HackRF settings:
   ```yaml
   rf_interface:
     type: "hackrf"
     # Frequency scanning
     frequencies: [315000000, 433920000, 868350000]  # Multiple frequencies
     scan_interval: 1.0  # Seconds per frequency
     
     # Gain settings
     gain: 20  # RF gain
     lna_gain: 40  # Low Noise Amplifier gain
     vga_gain: 40  # Variable Gain Amplifier
     
     # Performance
     sample_rate: 2000000  # 2MHz
     buffer_size: 16384
     usb_timeout: 1000
   ```

## Home Assistant Integration

1. Configure MQTT in your `config.yaml`:
   ```yaml
   mqtt:
     enabled: true
     host: your_home_assistant_ip
     port: 1883
     username: your_mqtt_username
     password: your_mqtt_password
     topic: rfghost/data
     retain: true
     qos: 1
   ```

2. Add these sensors to your Home Assistant `configuration.yaml`:
   ```yaml
   sensor:
     - platform: mqtt
       name: "RF Signal Strength"
       state_topic: "rfghost/data"
       value_template: "{{ value_json.statistics.mean }}"
       unit_of_measurement: "dBm"
       
     - platform: mqtt
       name: "RF Anomaly Detected"
       state_topic: "rfghost/data"
       value_template: "{{ value_json.anomalies }}"
       
     - platform: mqtt
       name: "RF Signal Min"
       state_topic: "rfghost/data"
       value_template: "{{ value_json.statistics.min }}"
       unit_of_measurement: "dBm"
       
     - platform: mqtt
       name: "RF Signal Max"
       state_topic: "rfghost/data"
       value_template: "{{ value_json.statistics.max }}"
       unit_of_measurement: "dBm"
   ```

## Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Run linting:
   ```bash
   pylint src/
   ```

4. Format code:
   ```bash
   black src/
   ```

## Troubleshooting

### HackRF Issues

1. Device not found:
   - Ensure HackRF is properly connected
   - Check USB drivers are installed
   - Try different USB ports
   - Verify device permissions

2. Poor signal quality:
   - Adjust LNA and VGA gain settings
   - Check antenna connection
   - Verify frequency settings
   - Monitor for USB bandwidth issues

3. High CPU usage:
   - Reduce sample rate
   - Increase buffer size
   - Adjust processing interval
   - Monitor system resources

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the open-source community for their contributions and support.
- Special thanks to the HackRF project for their excellent SDR hardware.
