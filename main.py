import sys
import os
import winreg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QSystemTrayIcon, QMenu, QFrame, QSizeGrip,
                             QPushButton, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt, QPoint, QSettings, QSize
from PyQt6.QtGui import QIcon, QAction, QFont, QGuiApplication
import vlc

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Cámara")
        self.settings = QSettings("TapoViewer", "WindowSettings")
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.ip_input = QLineEdit(self.settings.value("rtsp_ip", "192.168.1.xxx"))
        self.user_input = QLineEdit(self.settings.value("rtsp_user", "admin"))
        self.pwd_input = QLineEdit(self.settings.value("rtsp_pwd", ""))
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        
        self.path2k_input = QLineEdit(self.settings.value("stream_1_path", "/stream1"))
        self.path360_input = QLineEdit(self.settings.value("stream_2_path", "/stream2"))
        
        form_layout.addRow("IP / Hostname:", self.ip_input)
        form_layout.addRow("Usuario RTSP:", self.user_input)
        form_layout.addRow("Contraseña RTSP:", self.pwd_input)
        form_layout.addRow("Ruta Alta Calidad (2K):", self.path2k_input)
        form_layout.addRow("Ruta Baja Calidad (360p):", self.path360_input)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def save_settings(self):
        self.settings.setValue("rtsp_ip", self.ip_input.text().strip())
        self.settings.setValue("rtsp_user", self.user_input.text().strip())
        self.settings.setValue("rtsp_pwd", self.pwd_input.text().strip())
        self.settings.setValue("stream_1_path", self.path2k_input.text().strip())
        self.settings.setValue("stream_2_path", self.path360_input.text().strip())
        self.accept()

class TapoViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.settings = QSettings("TapoViewer", "WindowSettings")
        self.is_2k_mode = False
        self.is_always_on_top = self.settings.value("always_on_top", True, type=bool)
        self.old_pos = None

        self.setWindowTitle("Tapo Viewer")
        self.update_window_flags()

        saved_geometry = self.settings.value("geometry")
        if saved_geometry:
            self.restoreGeometry(saved_geometry)
        else:
            self.resize(640, 360)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.video_frame = QFrame(self.central_widget)
        self.video_frame.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.video_frame)

        self.pin_btn = QPushButton("📌", self.central_widget)
        self.pin_btn.setFixedSize(30, 30)
        self.pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_btn.clicked.connect(self.toggle_always_on_top)
        self.update_pin_style()

        self.size_grip = QSizeGrip(self.central_widget)
        self.size_grip.setStyleSheet("background-color: rgba(255, 255, 255, 50); width: 15px; height: 15px;")
        self.size_grip.setFixedSize(15, 15)

        self.init_vlc()

        self.tray_icon = QSystemTrayIcon(self)
        
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "icon.png")
        else:
            icon_path = "icon.png"
            
        self.tray_icon.setIcon(QIcon(icon_path))
        
        tray_menu = QMenu()
        
        self.show_hide_action = QAction("Ocultar", self)
        self.show_hide_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(self.show_hide_action)

        self.always_on_top_action = QAction("Fijar por encima", self, checkable=True)
        self.always_on_top_action.setChecked(self.is_always_on_top)
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top_action)
        tray_menu.addAction(self.always_on_top_action)
        
        self.startup_action = QAction("Iniciar con Windows", self, checkable=True)
        self.startup_action.setChecked(self.check_startup())
        self.startup_action.triggered.connect(self.toggle_startup)
        tray_menu.addAction(self.startup_action)
        
        config_action = QAction("Configuración", self)
        config_action.triggered.connect(self.open_config)
        tray_menu.addAction(config_action)
        
        quit_action = QAction("Cerrar", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.play_stream(self.get_stream_url(False))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None and not self.is_2k_mode:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_2k_mode()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - self.size_grip.width(), self.height() - self.size_grip.height())
        if hasattr(self, 'pin_btn'):
            self.pin_btn.move(self.width() - self.pin_btn.width() - 5, 5)

    def update_window_flags(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.is_always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        if hasattr(self, 'central_widget'):
            self.show()

    def update_pin_style(self):
        if self.is_always_on_top:
            self.pin_btn.setStyleSheet("background-color: rgba(255, 0, 0, 150); color: white; border-radius: 15px; font-size: 16px;")
        else:
            self.pin_btn.setStyleSheet("background-color: rgba(255, 255, 255, 100); color: black; border-radius: 15px; font-size: 16px;")

    def toggle_always_on_top(self):
        self.is_always_on_top = not self.is_always_on_top
        self.settings.setValue("always_on_top", self.is_always_on_top)
        self.always_on_top_action.setChecked(self.is_always_on_top)
        self.update_pin_style()
        self.update_window_flags()

    def toggle_always_on_top_action(self, checked):
        self.is_always_on_top = checked
        self.settings.setValue("always_on_top", self.is_always_on_top)
        self.update_pin_style()
        self.update_window_flags()

    def init_vlc(self):
        user = self.settings.value("rtsp_user", "admin")
        pwd = self.settings.value("rtsp_pwd", "")
        
        if hasattr(self, 'player') and self.player is not None:
            self.player.stop()
            self.player.release()
            self.vlc_instance.release()

        self.vlc_instance = vlc.Instance(
            "--avcodec-hw=any",
            "--drop-late-frames",
            f"--rtsp-user={user}",
            f"--rtsp-pwd={pwd}"
        )
        self.player = self.vlc_instance.media_player_new()
        self.player.set_hwnd(int(self.video_frame.winId()))
        self.player.video_set_mouse_input(False)
        self.player.video_set_key_input(False)
        
    def get_stream_url(self, is_2k):
        ip = self.settings.value("rtsp_ip", "192.168.1.xxx")
        if is_2k:
            path = self.settings.value("stream_1_path", "/stream1")
        else:
            path = self.settings.value("stream_2_path", "/stream2")
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path
        return f"rtsp://{ip}:554{path}"

    def play_stream(self, url):
        media = self.vlc_instance.media_new(url)
        self.player.set_media(media)
        self.player.play()
        self.player.audio_set_mute(True)

    def open_config(self):
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Restart stream with new settings
            self.init_vlc()
            url = self.get_stream_url(self.is_2k_mode)
            self.play_stream(url)

    def toggle_2k_mode(self):
        if not self.is_2k_mode:
            self.is_2k_mode = True
            self.size_grip.hide()
            self.pin_btn.hide()
            self.play_stream(self.get_stream_url(True))
            self.showFullScreen()
        else:
            self.is_2k_mode = False
            self.size_grip.show()
            self.pin_btn.show()
            self.play_stream(self.get_stream_url(False))
            self.showNormal()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
            self.show_hide_action.setText("Mostrar")
        else:
            self.show()
            self.show_hide_action.setText("Ocultar")

    def check_startup(self):
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ) as registry_key:
                value, _ = winreg.QueryValueEx(registry_key, "TapoViewer")
                return True
        except FileNotFoundError:
            return False

    def toggle_startup(self, state):
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        exe_path = os.path.abspath(sys.argv[0])
        if exe_path.endswith('.py'):
            command = f'"{sys.executable}" "{exe_path}"'
        else:
            command = f'"{exe_path}"'
            
        try:
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_WRITE) as registry_key:
                if state:
                    winreg.SetValueEx(registry_key, "TapoViewer", 0, winreg.REG_SZ, command)
                else:
                    winreg.DeleteValue(registry_key, "TapoViewer")
        except Exception as e:
            print(f"Error toggling startup: {e}")

    def closeEvent(self, event):
        if not self.is_2k_mode:
            self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def quit_app(self):
        self.player.stop()
        self.close()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    viewer = TapoViewer()
    viewer.show()
    sys.exit(app.exec())
