"""Test class to test the TemperatureSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.temperature_sensor import TemperatureSensor
from src.abbfreeathome.device import Device


def get_temperature_sensor(mock_api, mock_device):
    """Get the TemperatureSensor class to be tested against."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 38, "value": "0"},
        "odp0001": {"pairingID": 1024, "value": "15.50"},
        "odp0002": {"pairingID": 4, "value": "0"},
    }
    parameters = {"par002d": "4", "par0047": "7", "par0048": "7"}

    return TemperatureSensor(
        device=mock_device,
        channel_id="ch0002",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def temperature_sensor(mock_api, mock_device):
    """Set up the instance for testing the TemperatureSensor channel."""
    mock_device.device_serial = "7EB1000021C5"

    mock_device.api = mock_api
    return get_temperature_sensor(mock_api, mock_device)


@pytest.fixture
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.mark.asyncio
async def test_initial_state(temperature_sensor):
    """Test the intial state of the sensor."""
    assert temperature_sensor.state == 15.50
    assert temperature_sensor.alarm is False


@pytest.mark.asyncio
async def test_refresh_state(temperature_sensor):
    """Test refreshing the state of the sensor."""
    temperature_sensor.device.api.get_datapoint.return_value = ["1"]
    await temperature_sensor.refresh_state()
    assert temperature_sensor.state == 1.0
    assert temperature_sensor.alarm is True
    temperature_sensor.device.api.get_datapoint.assert_called_with(
        device_serial="7EB1000021C5",
        channel_id="ch0002",
        datapoint="odp0000",
    )


def test_refresh_state_from_datapoint(temperature_sensor):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    temperature_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1024, "value": "20.1"},
    )
    assert temperature_sensor.state == 20.1

    # Check output that affects the state.
    temperature_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 38, "value": "1"},
    )
    assert temperature_sensor.alarm is True

    # Check output that does NOT affect the state.
    temperature_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 4, "value": "1"},
    )
    assert temperature_sensor.state == 20.1
