# RFGhost API Documentation

## Core Components

### RFInterface

The `RFInterface` class handles RF signal acquisition and processing.

```python
from rfghost.core.rf_interface import RFInterface

# Initialize with configuration
interface = RFInterface(config)

# Start scanning
interface.start_scanning()

# Get latest data
data = interface.get_latest_data(max_samples=100)

# Get signal statistics
stats = interface.get_signal_statistics()

# Stop scanning
interface.stop_scanning()
```

### AnomalyEngine

The `AnomalyEngine` class handles anomaly detection in RF signals.

```python
from rfghost.core.anomaly_engine import AnomalyEngine

# Initialize with threshold
engine = AnomalyEngine(threshold=2.0)

# Detect anomalies
anomalies, scores = engine.detect_anomalies(signals)
```

### OutputInterface

The `OutputInterface` class handles data output through MQTT and Serial.

```python
from rfghost.outputs.output_interface import OutputInterface

# Initialize with configuration
output = OutputInterface(config)

# Publish data
output.publish_data(data)

# Close connections
output.close()
```

## Configuration

The application is configured through a YAML file. Here's an example configuration:

```yaml
# RF Interface Configuration
rf_interface:
  sample_rate: 1000  # Samples per second
  frequency: 433.92  # MHz
  gain: 20  # dB

# Anomaly Detection Configuration
anomaly_threshold: 2.0

# Output Configuration
mqtt:
  enabled: true
  host: localhost
  port: 1883
  topic: rfghost/data

serial:
  enabled: false
  port: COM1
  baudrate: 9600
```

## Data Format

The application outputs data in the following JSON format:

```json
{
    "timestamp": 1234567890.123,
    "signals": [-50.0, -51.2, -49.8],
    "statistics": {
        "mean": -50.33,
        "std": 0.7,
        "min": -51.2,
        "max": -49.8
    },
    "anomalies": false,
    "anomaly_scores": [0.1, 0.2, 0.1]
}
```

## Error Handling

The application uses Python's built-in exception handling. Common exceptions include:

- `IOError`: When there are issues with hardware communication
- `ValueError`: When invalid parameters are provided
- `RuntimeError`: When there are issues with the application state

## Logging

The application uses a custom logger that outputs to both console and file:

```python
from rfghost.utils.logger import logger

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
``` 