# RFGhost - RF Anomaly Detection System

RFGhost is a sophisticated RF signal monitoring and anomaly detection system designed to identify potential security threats and unusual patterns in radio frequency signals. It uses advanced signal processing and machine learning techniques to detect various types of anomalies, including ghost echoes, void pulses, static bursts, and frequency shifts.

## Features

- **Real-time RF Signal Monitoring**: Continuously monitors specified frequencies for unusual activity
- **Advanced Anomaly Detection**:
  - Ghost Echo Detection: Identifies strong, high-entropy signals
  - Void Pulse Detection: Detects weak but high-entropy signals
  - Static Burst Detection: Identifies sudden bursts of static noise
  - Frequency Shift Detection: Monitors for unexpected frequency changes
  - Pattern Recognition: Detects known signal patterns
- **Comprehensive Logging**: JSONL-based logging with automatic rotation and compression
- **Alert System**: Integration with Slack for real-time notifications
- **Configurable Thresholds**: Adjustable detection parameters
- **Thread-Safe Operations**: Built-in thread safety for concurrent operations

## Requirements

- Python 3.8 or higher
- CC1101 RF Transceiver
- SPI interface
- Linux-based system (for SPI support)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RFGhost.git
   cd RFGhost
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the system:
   - Copy `config.yaml.example` to `config.yaml`
   - Edit `config.yaml` with your settings

## Configuration

The system is configured through a YAML file. Here's an example configuration:

```yaml
# Frequencies to monitor (in MHz)
frequencies:
  - 433.92
  - 868.35
  - 915.0

# Detection thresholds
rssi_threshold_high: -50  # dBm
rssi_threshold_low: -90   # dBm
entropy_threshold: 0.8    # 80%
duration_threshold: 2.0   # seconds
pattern_threshold: 0.7    # 70% similarity

# Scan settings
scan_interval: 1.0  # seconds

# Logging settings
log_dir: "logs"
max_file_size_mb: 10
max_files: 5
compress_old: true

# Alert settings
slack_webhook: "https://hooks.slack.com/services/your/webhook/url"
```

## Usage

1. Start the system:
   ```bash
   python main.py
   ```

2. For debug mode:
   ```bash
   python main.py --debug
   ```

3. Use a custom config file:
   ```bash
   python main.py -c custom_config.yaml
   ```

## Anomaly Types

1. **Ghost Echo**
   - Strong, high-entropy signals
   - Potential intentional transmissions
   - High confidence when RSSI > -50 dBm

2. **Void Pulse**
   - Weak but high-entropy signals
   - Potential hidden transmissions
   - High confidence when RSSI < -90 dBm

3. **Static Burst**
   - Sudden bursts of static noise
   - Potential interference or jamming
   - Detected by rapid RSSI changes

4. **Frequency Shift**
   - Unexpected frequency changes
   - Potential frequency hopping
   - Detected by frequency changes > 100 kHz

5. **Pattern**
   - Known signal patterns
   - Potential protocol identification
   - Pattern matching confidence > 70%

## Logging

The system maintains detailed logs in JSONL format:
- Automatic log rotation
- Compression of old logs
- Thread-safe logging operations
- Configurable log size and retention

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- CC1101 library contributors
- Python community
- Open source RF analysis tools

## Support

For support, please:
1. Check the [documentation](docs/)
2. Open an issue
3. Contact the maintainers

## Roadmap

- [ ] Machine learning-based anomaly detection
- [ ] Web interface for monitoring
- [ ] Additional protocol support
- [ ] Mobile app integration
- [ ] Cloud synchronization
