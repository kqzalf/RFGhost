# Simulated RF interface for testing. Replace with real CC1101 SPI calls.
import random, time
import spidev
import logging
from typing import Dict, Optional, Tuple, List
import math
from dataclasses import dataclass
from enum import Enum
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class ModulationType(Enum):
    FSK = 0x02
    GFSK = 0x03
    MSK = 0x07
    OOK = 0x08

@dataclass
class SignalMetrics:
    rssi: int
    lqi: int
    crc_ok: bool
    timestamp: float
    frequency: float
    duration: float
    entropy: float
    pattern_match: float
    signal_quality: float

# CC1101 Register Addresses
CC1101_VERSION = 0x31
CC1101_FREQ2 = 0x0D
CC1101_FREQ1 = 0x0E
CC1101_FREQ0 = 0x0F
CC1101_MDMCFG4 = 0x10
CC1101_MDMCFG3 = 0x11
CC1101_MDMCFG2 = 0x12
CC1101_MDMCFG1 = 0x13
CC1101_MDMCFG0 = 0x14
CC1101_DEVIATN = 0x15
CC1101_MCSM2 = 0x17
CC1101_MCSM1 = 0x18
CC1101_MCSM0 = 0x19
CC1101_FOCCFG = 0x1A
CC1101_BSCFG = 0x1B
CC1101_AGCCTRL2 = 0x1C
CC1101_AGCCTRL1 = 0x1D
CC1101_AGCCTRL0 = 0x1E
CC1101_WOREVT1 = 0x1F
CC1101_WOREVT0 = 0x20
CC1101_WORCTRL = 0x21
CC1101_FREND1 = 0x22
CC1101_FREND0 = 0x23
CC1101_FSCAL3 = 0x24
CC1101_FSCAL2 = 0x25
CC1101_FSCAL1 = 0x26
CC1101_FSCAL0 = 0x27
CC1101_RCCTRL1 = 0x28
CC1101_RCCTRL0 = 0x29
CC1101_FSTEST = 0x2A
CC1101_PTEST = 0x2B
CC1101_AGCTEST = 0x2C
CC1101_TEST2 = 0x2D
CC1101_TEST1 = 0x2E
CC1101_TEST0 = 0x2F
CC1101_RSSI = 0x34
CC1101_LQI = 0x35
CC1101_MARCSTATE = 0x36

# CC1101 Commands
CC1101_SRES = 0x30  # Reset chip
CC1101_SFSTXON = 0x31  # Enable and calibrate frequency synthesizer
CC1101_SXOFF = 0x32  # Turn off crystal oscillator
CC1101_SCAL = 0x33  # Calibrate frequency synthesizer and turn it off
CC1101_SRX = 0x34  # Enable RX
CC1101_STX = 0x35  # Enable TX
CC1101_SIDLE = 0x36  # Exit RX / TX, turn off frequency synthesizer
CC1101_SWOR = 0x38  # Start automatic RX polling sequence
CC1101_SPWD = 0x39  # Enter power down mode when CSn goes high
CC1101_SFRX = 0x3A  # Flush the RX FIFO buffer
CC1101_SFTX = 0x3B  # Flush the TX FIFO buffer
CC1101_SWORRST = 0x3C  # Reset real time clock
CC1101_SNOP = 0x3D  # No operation

class CC1101Interface:
    def __init__(self, bus: int = 0, device: int = 0, speed_hz: int = 1000000, config: Dict = None):
        """Initialize CC1101 interface with SPI communication."""
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = speed_hz
        self.spi.mode = 0
        
        # Initialize logging
        self.logger = logging.getLogger('RFGhost')
        
        # Store configuration
        self.config = config or {}
        
        # Initialize state variables
        self._last_calibration = 0
        self._calibration_interval = 300  # 5 minutes
        self._temperature = 25  # Default temperature
        self._signal_patterns = {}  # Store known signal patterns
        self._power_mode = 'active'
        
        # Initialize CC1101
        self._initialize_chip()
        
    def _initialize_chip(self) -> bool:
        """Initialize the CC1101 chip with proper sequence."""
        try:
            # Reset chip
            self._reset()
            time.sleep(0.1)
            
            # Verify chip
            if not self._verify_chip():
                return False
                
            # Configure chip
            self._configure_chip()
            
            # Perform initial calibration
            self._calibrate_frequency()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize CC1101: {e}")
            return False
            
    def _calibrate_frequency(self) -> None:
        """Calibrate frequency synthesizer."""
        try:
            # Enter calibration mode
            self.spi.xfer([CC1101_SCAL])
            time.sleep(0.1)
            
            # Wait for calibration to complete
            while self._read_register(CC1101_MARCSTATE) != 0x01:
                time.sleep(0.01)
                
            self._last_calibration = time.time()
            self.logger.info("Frequency calibration completed")
        except Exception as e:
            self.logger.error(f"Frequency calibration failed: {e}")
            
    def _check_calibration(self) -> None:
        """Check if frequency calibration is needed."""
        if time.time() - self._last_calibration > self._calibration_interval:
            self._calibrate_frequency()
            
    def _reset(self) -> None:
        """Reset the CC1101 chip."""
        self.spi.xfer([CC1101_SRES])
        time.sleep(0.1)
        
    def _verify_chip(self) -> bool:
        """Verify CC1101 chip is present and responding."""
        version = self._read_register(CC1101_VERSION)
        if version != 0x14:  # Expected version for CC1101
            self.logger.error(f"Invalid CC1101 version: {version}")
            return False
        self.logger.info("CC1101 initialized successfully")
        return True
        
    def _configure_chip(self) -> None:
        """Configure CC1101 with settings from config."""
        settings = self.config.get('cc1101_settings', {})
        
        # Set modulation type
        modulation = settings.get('modulation', 'FSK')
        try:
            mod_type = ModulationType[modulation]
            self._write_register(CC1101_MDMCFG2, mod_type.value)
        except KeyError:
            self.logger.warning(f"Invalid modulation type: {modulation}, using FSK")
            self._write_register(CC1101_MDMCFG2, ModulationType.FSK.value)
            
        # Set data rate with error checking
        data_rate = settings.get('data_rate', 1.2)  # kbps
        if not 0.6 <= data_rate <= 500:
            self.logger.warning(f"Data rate {data_rate} kbps out of range, using 1.2 kbps")
            data_rate = 1.2
            
        drate_e = int(math.log2(data_rate * 1000 / 0.024))
        drate_m = int((data_rate * 1000 / (0.024 * (2 ** drate_e))) - 256)
        self._write_register(CC1101_MDMCFG4, (drate_e << 4) | (drate_m & 0x0F))
        self._write_register(CC1101_MDMCFG3, (drate_m >> 4) & 0xFF)
        
        # Set frequency deviation with validation
        deviation = settings.get('deviation', 45)  # kHz
        if not 1.587 <= deviation <= 380:
            self.logger.warning(f"Deviation {deviation} kHz out of range, using 45 kHz")
            deviation = 45
            
        dev_e = int(math.log2(deviation / 1.587))
        dev_m = int((deviation / (1.587 * (2 ** dev_e))) - 8)
        self._write_register(CC1101_DEVIATN, (dev_e << 4) | (dev_m & 0x07))
        
        # Configure AGC with optimized settings
        self._write_register(CC1101_AGCCTRL2, 0x03)  # Maximum gain
        self._write_register(CC1101_AGCCTRL1, 0x40)  # Medium hysteresis
        self._write_register(CC1101_AGCCTRL0, 0x91)  # Medium filter bandwidth
        
        # Configure frequency synthesizer
        self._write_register(CC1101_FREND1, 0xB6)  # Front-end RX configuration
        self._write_register(CC1101_FREND0, 0x10)  # Front-end TX configuration
        
        # Configure frequency calibration
        self._write_register(CC1101_FSCAL3, 0xE9)
        self._write_register(CC1101_FSCAL2, 0x2A)
        self._write_register(CC1101_FSCAL1, 0x00)
        self._write_register(CC1101_FSCAL0, 0x1F)
        
        # Configure power management
        self._write_register(CC1101_MCSM0, 0x18)  # Auto-calibrate when going to idle
        self._write_register(CC1101_MCSM1, 0x3F)  # Stay in RX after packet reception
        self._write_register(CC1101_MCSM2, 0x07)  # RX timeout after 64 bytes
        
    def _read_register(self, address: int) -> int:
        """Read a single register from CC1101."""
        response = self.spi.xfer([address | 0x80, 0x00])
        return response[1]
        
    def _write_register(self, address: int, value: int) -> None:
        """Write a single register to CC1101."""
        self.spi.xfer([address, value])
        
    def _calculate_freq_registers(self, freq_mhz: float) -> Tuple[int, int, int]:
        """Calculate frequency register values for given frequency in MHz."""
        freq_hz = int(freq_mhz * 1000000)
        freq_reg = int(freq_hz / (26 * 1000000) * 65536)
        freq2 = (freq_reg >> 16) & 0xFF
        freq1 = (freq_reg >> 8) & 0xFF
        freq0 = freq_reg & 0xFF
        return freq2, freq1, freq0
        
    def set_frequency(self, freq_mhz: float) -> bool:
        """Set the CC1101 to the specified frequency in MHz."""
        try:
            # Validate frequency is within CC1101's range
            if not (300 <= freq_mhz <= 348 or 387 <= freq_mhz <= 464 or 779 <= freq_mhz <= 928):
                self.logger.error(f"Frequency {freq_mhz} MHz is outside CC1101's range")
                return False
                
            freq2, freq1, freq0 = self._calculate_freq_registers(freq_mhz)
            self._write_register(CC1101_FREQ2, freq2)
            self._write_register(CC1101_FREQ1, freq1)
            self._write_register(CC1101_FREQ0, freq0)
            self.logger.info(f"Tuned to {freq_mhz} MHz")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set frequency: {e}")
            return False
            
    def get_rssi(self) -> int:
        """Read RSSI value from CC1101."""
        rssi = self._read_register(CC1101_RSSI)
        if rssi >= 128:
            return (rssi - 256) // 2 - 74
        return rssi // 2 - 74
        
    def calculate_entropy(self, samples: list) -> float:
        """Calculate Shannon entropy of signal samples."""
        if not samples:
            return 0.0
        value_counts = {}
        for sample in samples:
            value_counts[sample] = value_counts.get(sample, 0) + 1
        entropy = 0
        for count in value_counts.values():
            probability = count / len(samples)
            entropy -= probability * math.log2(probability)
        return entropy
        
    def set_power_mode(self, mode: str) -> None:
        """Set power mode of the CC1101."""
        if mode == self._power_mode:
            return
            
        if mode == 'sleep':
            self.spi.xfer([CC1101_SPWD])
        elif mode == 'idle':
            self.spi.xfer([CC1101_SIDLE])
        elif mode == 'active':
            self.spi.xfer([CC1101_SRX])
            
        self._power_mode = mode
        self.logger.info(f"Power mode set to {mode}")
        
    def calculate_signal_quality(self, rssi: int, lqi: int) -> float:
        """Calculate signal quality metric from RSSI and LQI."""
        # Normalize RSSI to 0-1 range (-120 dBm to 0 dBm)
        rssi_norm = (rssi + 120) / 120
        
        # Normalize LQI to 0-1 range (0-255)
        lqi_norm = lqi / 255
        
        # Weighted combination
        return 0.7 * rssi_norm + 0.3 * lqi_norm
        
    def detect_signal_pattern(self, samples: List[int]) -> float:
        """Detect if signal matches known patterns."""
        if not samples:
            return 0.0
            
        # Convert samples to numpy array for efficient processing
        samples_array = np.array(samples)
        
        # Calculate basic statistics
        mean = np.mean(samples_array)
        std = np.std(samples_array)
        
        # Check for periodic patterns
        if len(samples) > 10:
            autocorr = np.correlate(samples_array, samples_array, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            peaks = np.where(autocorr > 0.7 * max(autocorr))[0]
            if len(peaks) > 1:
                period = np.mean(np.diff(peaks))
                if 0.1 < period < 10:  # Reasonable period range
                    return 0.8
                    
        # Check for known patterns
        for pattern in self._signal_patterns.values():
            if len(samples) >= len(pattern):
                correlation = np.correlate(samples_array, pattern)[0]
                if correlation > 0.7:
                    return correlation
                    
        return 0.0
        
    def scan_frequency(self, freq_mhz: float) -> Optional[SignalMetrics]:
        """Scan for signals at specified frequency and return signal metrics."""
        try:
            # Check if calibration is needed
            self._check_calibration()
            
            if not self.set_frequency(freq_mhz):
                return None
                
            # Enter RX mode
            self.set_power_mode('active')
            time.sleep(0.1)  # Allow PLL to settle
            
            # Collect samples
            start_time = time.time()
            samples = []
            lqi_samples = []
            
            while time.time() - start_time < 1.0:
                rssi = self.get_rssi()
                lqi = self._read_register(CC1101_LQI)
                samples.append(rssi)
                lqi_samples.append(lqi)
                time.sleep(0.01)
                
            # Calculate metrics
            duration = time.time() - start_time
            avg_rssi = int(sum(samples) / len(samples))
            avg_lqi = int(sum(lqi_samples) / len(lqi_samples))
            entropy = self.calculate_entropy(samples)
            pattern_match = self.detect_signal_pattern(samples)
            signal_quality = self.calculate_signal_quality(avg_rssi, avg_lqi)
            
            # Return to idle mode
            self.set_power_mode('idle')
            
            return SignalMetrics(
                rssi=avg_rssi,
                lqi=avg_lqi,
                crc_ok=True,  # TODO: Implement CRC checking
                timestamp=time.time(),
                frequency=freq_mhz,
                duration=round(duration, 2),
                entropy=round(entropy, 2),
                pattern_match=round(pattern_match, 2),
                signal_quality=round(signal_quality, 2)
            )
            
        except Exception as e:
            self.logger.error(f"Error scanning frequency {freq_mhz} MHz: {e}")
            return None
            
    def close(self) -> None:
        """Close SPI connection and enter sleep mode."""
        try:
            self.set_power_mode('sleep')
            self.spi.close()
        except Exception as e:
            self.logger.error(f"Error closing interface: {e}")

# Create a singleton instance
_rf_interface = None

def get_rf_interface(config: Dict = None) -> CC1101Interface:
    """Get or create the RF interface singleton."""
    global _rf_interface
    if _rf_interface is None:
        _rf_interface = CC1101Interface(config=config)
    return _rf_interface

def scan_frequency(freq: float, config: Dict = None) -> Dict:
    """Public interface for scanning a frequency."""
    interface = get_rf_interface(config)
    result = interface.scan_frequency(freq)
    if result is None:
        # Return a default structure if scan fails
        return {
            "frequency": freq,
            "rssi": -120,
            "lqi": 0,
            "crc_ok": False,
            "duration": 0.0,
            "entropy": 0.0,
            "pattern_match": 0.0,
            "signal_quality": 0.0,
            "timestamp": time.time()
        }
    return result.__dict__
