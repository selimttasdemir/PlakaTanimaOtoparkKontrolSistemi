import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
import cv2
import easyocr
import numpy as np
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
                            QHBoxLayout, QFrame, QHeaderView, QComboBox, QPushButton,
                            QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
from datetime import datetime

class PlakaArayuz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Otopark Plaka Okuma Sistemi")
        self.setGeometry(200, 200, 1200, 800)
        
        # Ana pencere stilini ayarla
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QLabel {
                color: #1a237e;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1a237e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QMessageBox {
                background-color: white;
            }
            QComboBox, QLineEdit, QPushButton {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                min-width: 200px;
            }
            QPushButton {
                background-color: #1a237e;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #283593;
            }
        """)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Başlık etiketi
        self.title_label = QLabel("Otopark Plaka Okuma Sistemi")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #1a237e;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        """)
        self.main_layout.addWidget(self.title_label)

        # Kamera ayarları için form
        self.camera_settings_frame = QFrame()
        self.camera_settings_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.camera_settings_layout = QFormLayout(self.camera_settings_frame)

        # Kamera seçimi
        self.camera_type_combo = QComboBox()
        self.camera_type_combo.addItems(["Yerel Kamera", "DroidCam"])
        self.camera_settings_layout.addRow("Kamera Tipi:", self.camera_type_combo)

        # DroidCam IP adresi
        self.droidcam_ip = QLineEdit()
        self.droidcam_ip.setPlaceholderText("Örn: 192.168.1.100")
        self.droidcam_ip.setText("192.168.1.100")
        self.camera_settings_layout.addRow("DroidCam IP:", self.droidcam_ip)

        # DroidCam Port
        self.droidcam_port = QLineEdit()
        self.droidcam_port.setPlaceholderText("Örn: 4747")
        self.droidcam_port.setText("4747")
        self.camera_settings_layout.addRow("DroidCam Port:", self.droidcam_port)

        # Bağlan butonu
        self.connect_button = QPushButton("Kameraya Bağlan")
        self.connect_button.clicked.connect(self.connect_camera)
        self.camera_settings_layout.addRow("", self.connect_button)

        self.main_layout.addWidget(self.camera_settings_frame)

        # Kamera görüntüsü için çerçeve
        self.camera_frame = QFrame()
        self.camera_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.camera_layout = QVBoxLayout(self.camera_frame)
        
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumHeight(400)
        self.camera_label.setStyleSheet("""
            QLabel {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        self.camera_layout.addWidget(self.camera_label)
        self.main_layout.addWidget(self.camera_frame)

        # Tablo widget'ı
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Plaka", "Giriş Tarihi", "Giriş Saati", "Çıkış Saati"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1a237e;
            }
        """)
        self.main_layout.addWidget(self.table)

        self.reader = easyocr.Reader(['tr'], gpu=False)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.cap = None
        self.plaka_kayitlari = {}
        self.ocr_counter = 0
        self.ocr_interval = 5
        self.plaka_pattern = re.compile(r'^[0-9]{2}[A-Z]{1,3}[0-9]{2,4}$')

    def connect_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.timer.stop()

        camera_type = self.camera_type_combo.currentText()
        if camera_type == "Yerel Kamera":
            self.cap = cv2.VideoCapture(0)
        else:  # DroidCam
            ip = self.droidcam_ip.text()
            port = self.droidcam_port.text()
            
            # Önce USB bağlantısını dene
            usb_url = f"http://localhost:{port}/video"
            self.cap = cv2.VideoCapture(usb_url)
            
            if not self.cap.isOpened():
                # USB bağlantısı başarısız olursa WiFi bağlantısını dene
                urls = [
                    f"http://{ip}:{port}",f"http://192.168.1.11:4747"
                ]
                
                connected = False
                for url in urls:
                    try:
                        self.cap = cv2.VideoCapture(url)
                        if self.cap.isOpened():
                            # Test frame'i oku
                            ret, frame = self.cap.read()
                            if ret and frame is not None:
                                connected = True
                                print(f"Başarılı bağlantı URL'si: {url}")
                                break
                    except Exception as e:
                        print(f"URL deneme hatası ({url}): {e}")
                    finally:
                        if not connected:
                            self.cap.release()

                if not connected:
                    QMessageBox.warning(self, "Hata", 
                        "Kamera bağlantısı başarısız!\n\n"
                        "Lütfen şunları kontrol edin:\n"
                        "1. DroidCam uygulamasını yeniden başlatın\n"
                        "2. USB bağlantısı için:\n"
                        "   - USB hata ayıklama modunu açın\n"
                        "   - USB kablosunu çıkarıp takın\n"
                        "3. WiFi bağlantısı için:\n"
                        "   - Telefonunuz ve bilgisayarınız aynı ağda mı?\n"
                        "   - IP adresi ve port doğru mu?\n"
                        "4. DroidCam uygulamasında:\n"
                        "   - 'Start' butonuna basın\n"
                        "   - Bağlantı modunu değiştirin (USB/WiFi)\n"
                        "5. Güvenlik duvarı ayarlarını kontrol edin")
                    return

        if self.cap.isOpened():
            try:
                # Kamera ayarlarını optimize et
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer boyutunu küçült
                
                # Test frame'i oku
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.timer.start(100)
                    QMessageBox.information(self, "Başarılı", "Kamera bağlantısı başarılı!")
                else:
                    raise Exception("Test frame okunamadı")
            except Exception as e:
                self.cap.release()
                QMessageBox.warning(self, "Hata", f"Kamera ayarları yapılandırılamadı: {str(e)}")
        else:
            QMessageBox.warning(self, "Hata", "Kamera bağlantısı başarısız!")

    def preprocess_image(self, frame):
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blur, 50, 150)
        kernel = np.ones((3,3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        return frame, dilated

    def plaka_format_kontrol(self, text):
        text = re.sub(r'[^A-Z0-9]', '', text.upper())
        if len(text) < 5 or len(text) > 8: return False
        if not text[:2].isdigit(): return False
        if not text[-2:].isdigit(): return False
        if not all(c.isalpha() for c in text[2:-2]): return False
        return bool(self.plaka_pattern.match(text))

    def update_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return

        try:
            ret, frame = self.cap.read()
            if ret:
                display_frame, processed_frame = self.preprocess_image(frame)
                self.ocr_counter += 1
                if self.ocr_counter >= self.ocr_interval:
                    self.ocr_counter = 0
                    try:
                        results = self.reader.readtext(processed_frame)
                        for (bbox, text, prob) in results:
                            if prob > 0.3 and self.plaka_format_kontrol(text):
                                text = re.sub(r'[^A-Z0-9]', '', text.upper())
                                pts = np.array(bbox, np.int32).reshape((-1, 1, 2))
                                cv2.polylines(display_frame, [pts], True, (0, 255, 0), 2)
                                self.plaka_kontrol(text)
                    except Exception as e:
                        print(f"OCR hatası: {e}")

                rgb_image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.camera_label.setPixmap(QPixmap.fromImage(qt_image))
            else:
                print("Kamera görüntüsü alınamadı")
                self.cap.release()
                self.timer.stop()
                QMessageBox.warning(self, "Hata", "Kamera bağlantısı koptu!")
        except Exception as e:
            print(f"Frame güncelleme hatası: {e}")
            self.cap.release()
            self.timer.stop()
            QMessageBox.warning(self, "Hata", f"Kamera hatası: {str(e)}")

    def plaka_kontrol(self, plaka):
        simdi = datetime.now()
        tarih = simdi.strftime("%d/%m/%Y")
        saat = simdi.strftime("%H:%M:%S")
        if plaka not in self.plaka_kayitlari:
            self.plaka_kayitlari[plaka] = {
                "giris_tarih": tarih,
                "giris_saat": saat,
                "cikis_saat": None
            }
            self.tabloya_ekle(plaka, tarih, saat, None)
            QMessageBox.information(self, "Araç Girişi", f"Plaka: {plaka}\nGiriş: {saat}")
        else:
            if self.plaka_kayitlari[plaka]["cikis_saat"] is None:
                self.plaka_kayitlari[plaka]["cikis_saat"] = saat
                self.tablo_guncelle(plaka, saat)
                QMessageBox.information(self, "Araç Çıkışı", f"Plaka: {plaka}\nÇıkış: {saat}")

    def tabloya_ekle(self, plaka, tarih, giris_saat, cikis_saat):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(plaka))
        self.table.setItem(row, 1, QTableWidgetItem(tarih))
        self.table.setItem(row, 2, QTableWidgetItem(giris_saat))
        self.table.setItem(row, 3, QTableWidgetItem(cikis_saat if cikis_saat else "-"))

    def tablo_guncelle(self, plaka, cikis_saat):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == plaka:
                self.table.setItem(row, 3, QTableWidgetItem(cikis_saat))
                break

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlakaArayuz()
    window.show()
    sys.exit(app.exec_())
