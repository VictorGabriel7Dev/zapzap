"""Native unread badges follow the aggregate tray counter and its preference."""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from qt_test_case import QtTestCase
from zapzap.features.tray.sys_tray_manager import SysTrayManager


class TaskbarBadgeTests(QtTestCase):
    def setUp(self):
        self.manager = object.__new__(SysTrayManager)
        self.manager._settings = SimpleNamespace(
            notification_counter_enabled=True, tray_icon_enabled=False)
        self.manager._tray = MagicMock()
        self.manager.current_icon = object()
        self.manager.number_notifications = 0
        self.application = MagicMock()
        patches = (
            patch.object(SysTrayManager, "_instance", self.manager),
            patch("zapzap.features.tray.sys_tray_manager.QApplication.instance",
                  return_value=self.application),
            patch("zapzap.features.tray.sys_tray_manager.TrayIcon.getIcon"),
        )
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_unread_updates_and_zero_reach_native_badge_with_tray_hidden(self):
        for count in (3, 8, 0):
            SysTrayManager.set_number_notifications(count)
        self.assertEqual(self.application.setBadgeNumber.call_args_list,
                         [call(3), call(8), call(0)])
        self.assertEqual(self.manager.number_notifications, 0)
        self.assertEqual(self.manager._tray.setIcon.call_count, 3)
        self.manager._tray.show.assert_not_called()

    def test_preference_refresh_clears_and_restores_current_count(self):
        SysTrayManager.set_number_notifications(5)
        self.manager._settings.notification_counter_enabled = False
        SysTrayManager.refresh()
        self.manager._settings.notification_counter_enabled = True
        SysTrayManager.refresh()
        self.assertEqual(self.application.setBadgeNumber.call_args_list,
                         [call(5), call(0), call(5)])

    def test_disabled_counter_keeps_new_unread_count_hidden(self):
        self.manager._settings.notification_counter_enabled = False
        SysTrayManager.set_number_notifications(9)
        self.application.setBadgeNumber.assert_called_once_with(0)
        self.assertEqual(self.manager.number_notifications, 9)

    def test_older_qt_still_updates_tray_without_badge_api(self):
        with patch("zapzap.features.tray.sys_tray_manager.QApplication.instance",
                   return_value=SimpleNamespace()):
            SysTrayManager.set_number_notifications(4)
        self.manager._tray.setIcon.assert_called_once()


if __name__ == "__main__":
    unittest.main()
