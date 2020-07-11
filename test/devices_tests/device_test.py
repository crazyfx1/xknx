"""Unit test for Switch objects."""
import asyncio
import unittest
from unittest.mock import Mock, patch

from xknx import XKNX
from xknx.devices import Device
from xknx.dpt import DPTArray
from xknx.telegram import GroupAddress, Telegram, TelegramType


class TestDevice(unittest.TestCase):
    """Test class for Switch object."""

    def setUp(self):
        """Set up test class."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Tear down test class."""
        self.loop.close()

    def test_process_callback(self):
        """Test process / reading telegrams from telegram queue. Test if callback was called."""
        xknx = XKNX(loop=self.loop)
        device = Device(xknx, 'TestDevice')

        after_update_callback1 = Mock()
        after_update_callback2 = Mock()

        async def async_after_update_callback1(device):
            """Async callback No. 1."""
            after_update_callback1(device)

        async def async_after_update_callback2(device):
            """Async callback No. 2."""
            after_update_callback2(device)

        device.register_device_updated_cb(async_after_update_callback1)
        device.register_device_updated_cb(async_after_update_callback2)

        # Triggering first time. Both have to be called
        self.loop.run_until_complete(asyncio.Task(device.after_update()))
        after_update_callback1.assert_called_with(device)
        after_update_callback2.assert_called_with(device)
        after_update_callback1.reset_mock()
        after_update_callback2.reset_mock()

        # Triggering 2nd time. Both have to be called
        self.loop.run_until_complete(asyncio.Task(device.after_update()))
        after_update_callback1.assert_called_with(device)
        after_update_callback2.assert_called_with(device)
        after_update_callback1.reset_mock()
        after_update_callback2.reset_mock()

        # Unregistering first callback
        device.unregister_device_updated_cb(async_after_update_callback1)
        self.loop.run_until_complete(asyncio.Task(device.after_update()))
        after_update_callback1.assert_not_called()
        after_update_callback2.assert_called_with(device)
        after_update_callback1.reset_mock()
        after_update_callback2.reset_mock()

        # Unregistering second callback
        device.unregister_device_updated_cb(async_after_update_callback2)
        self.loop.run_until_complete(asyncio.Task(device.after_update()))
        after_update_callback1.assert_not_called()
        after_update_callback2.assert_not_called()

    def test_process(self):
        """Test if telegram is handled by the correct process_* method."""
        xknx = XKNX(loop=self.loop)
        device = Device(xknx, 'TestDevice')

        with patch('xknx.devices.Device.process_group_read') as mock_group_read:
            fut = asyncio.Future()
            fut.set_result(None)
            mock_group_read.return_value = fut
            telegram = Telegram(
                GroupAddress('1/2/1'),
                payload=DPTArray((0x01, 0x02)),
                telegramtype=TelegramType.GROUP_READ)
            self.loop.run_until_complete(asyncio.Task(device.process(telegram)))
            mock_group_read.assert_called_with(telegram)

        with patch('xknx.devices.Device.process_group_write') as mock_group_write:
            fut = asyncio.Future()
            fut.set_result(None)
            mock_group_write.return_value = fut
            telegram = Telegram(
                GroupAddress('1/2/1'),
                payload=DPTArray((0x01, 0x02)),
                telegramtype=TelegramType.GROUP_WRITE)
            self.loop.run_until_complete(asyncio.Task(device.process(telegram)))
            mock_group_write.assert_called_with(telegram)

        with patch('xknx.devices.Device.process_group_response') as mock_group_response:
            fut = asyncio.Future()
            fut.set_result(None)
            mock_group_response.return_value = fut
            telegram = Telegram(
                GroupAddress('1/2/1'),
                payload=DPTArray((0x01, 0x02)),
                telegramtype=TelegramType.GROUP_RESPONSE)
            self.loop.run_until_complete(asyncio.Task(device.process(telegram)))
            mock_group_response.assert_called_with(telegram)

    def test_process_group_write(self):
        """Test if process_group_write. Nothing really to test here."""
        xknx = XKNX(loop=self.loop)
        device = Device(xknx, 'TestDevice')
        self.loop.run_until_complete(asyncio.Task(device.process_group_write(Telegram())))

    def test_process_group_response(self):
        """Test if process_group_read. Testing if mapped to group_write."""
        xknx = XKNX(loop=self.loop)
        device = Device(xknx, 'TestDevice')
        with patch('xknx.devices.Device.process_group_write') as mock_group_write:
            fut = asyncio.Future()
            fut.set_result(None)
            mock_group_write.return_value = fut
            self.loop.run_until_complete(asyncio.Task(device.process_group_response(Telegram())))
            mock_group_write.assert_called_with(Telegram())

    def test_process_group_read(self):
        """Test if process_group_read. Nothing really to test here."""
        xknx = XKNX(loop=self.loop)
        device = Device(xknx, 'TestDevice')
        self.loop.run_until_complete(asyncio.Task(device.process_group_read(Telegram())))

    def test_do(self):
        """Testing empty do."""
        xknx = XKNX(loop=self.loop)
        device = Device(xknx, 'TestDevice')
        with patch('logging.Logger.info') as mock_info:
            self.loop.run_until_complete(asyncio.Task(device.do("xx")))
            mock_info.assert_called_with("Do not implemented action '%s' for %s", 'xx', 'Device')
