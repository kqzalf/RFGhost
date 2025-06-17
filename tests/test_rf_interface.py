"""Tests for the RF interface module."""
import pytest
from rfghost.core.rf_interface import RFInterface


@pytest.fixture
def rf_config():
    """Create a test configuration."""
    return {
        'sample_rate': 1000,
        'frequency': 433.92,
        'gain': 20
    }


def test_rf_interface_initialization(rf_config):
    """Test RF interface initialization."""
    interface = RFInterface(rf_config)
    assert interface._sample_rate == 1000
    assert interface._frequency == 433.92
    assert interface._gain == 20


def test_rf_interface_scanning(rf_config):
    """Test RF interface scanning functionality."""
    interface = RFInterface(rf_config)
    interface.start_scanning()
    assert interface._running is True
    interface.stop_scanning()
    assert interface._running is False


def test_rf_interface_data_acquisition(rf_config):
    """Test RF interface data acquisition."""
    interface = RFInterface(rf_config)
    data = interface.get_latest_data(max_samples=10)
    assert isinstance(data, list)
    assert len(data) <= 10 