from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QTableWidget, 
                           QTableWidgetItem, QHeaderView, QProgressDialog, QLineEdit, QDialog, QCheckBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPalette, QColor, QFontDatabase, QFont
import sys
from main import extract_info_from_receipt
import os
import pandas as pd
import json
from datetime import datetime

# Dark theme style sheet
STYLE_SHEET = """
* {
    font-family: 'Roboto';
}

QMainWindow, QDialog {
    background-color: #1b1e23;
    color: #ffffff;
}

QWidget#leftMenu {
    background-color: #15171c;
    border-radius: 10px;
    margin: 10px;
    padding: 20px;
}

QWidget#mainContent {
    background-color: #1b1e23;
    margin: 10px;
    padding: 20px;
}

QWidget#statsCard {
    background-color: #22252d;
    border-radius: 15px;
    padding: 25px;
    margin: 10px;
}

QLabel {
    font-family: 'Roboto';
    font-weight: 500;
    letter-spacing: 0.3px;
}

QLabel#titleLabel {
    color: white;
    font-size: 14px;
    font-weight: 600;  /* Semi-bold */
    letter-spacing: 0.5px;
}

QLabel#cardTitle {
    color: #6c7293;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.3px;
    padding: 5px 0;
}

QLabel#cardValue {
    color: white;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 10px 0;
}

QLabel#cardSubtext {
    color: #34c698;
    font-size: 11px;
    font-family: 'Roboto';
    padding: 5px 0;
}

QPushButton {
    background-color: #2d5eff;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-family: 'Roboto';
}

QPushButton:hover {
    background-color: #4171ff;
}

QPushButton:pressed {
    background-color: #1d3eb3;
}

QPushButton:disabled {
    background-color: #3d4250;
    color: #6c7293;
}

QLineEdit {
    background-color: #22252d;
    color: white;
    border: 2px solid #2d3035;
    border-radius: 8px;
    padding: 12px 15px;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.3px;
    font-family: 'Roboto';
}

QLineEdit:focus {
    border: 2px solid #2d5eff;
    background-color: #2a2d36;  /* Odaklandığında hafif renk değişimi */
}

QTableWidget {
    background-color: #22252d;
    color: white;
    border: none;
    border-radius: 15px;
    gridline-color: #2d3035;
    padding: 20px;
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 0.2px;
    font-family: 'Roboto';
}

QTableWidget::item {
    padding: 15px;
    border-bottom: 1px solid #2d3035;
}

QHeaderView::section {
    background-color: #22252d;
    color: #6c7293;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    border: none;
    padding: 15px;
    font-family: 'Roboto';
}

QHeaderView::section:first {
    border-top-left-radius: 15px;
}

QHeaderView::section:last {
    border-top-right-radius: 15px;
}

QHeaderView {
    background-color: transparent;
}

QTextEdit#logArea {
    background-color: #22252d;
    color: #6c7293;
    border: none;
    border-radius: 8px;
    padding: 15px;
    font-family: 'Consolas';
    margin: 10px 0;
}

/* Dikey Scrollbar */
QScrollBar:vertical {
    border: none;
    background: #1b1e23;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2d5eff;
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4171ff;
}

QScrollBar::handle:vertical:pressed {
    background: #1d3eb3;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

/* Yatay Scrollbar */
QScrollBar:horizontal {
    border: none;
    background: #1b1e23;
    height: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #2d5eff;
    min-width: 30px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #4171ff;
}

QScrollBar::handle:horizontal:pressed {
    background: #1d3eb3;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
    width: 0px;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}

QTableCornerButton::section {
    background-color: #22252d;
    border: none;
}

QTableWidget QTableCornerButton::section {
    background-color: #22252d;
    border: none;
}

/* Başlık çubuğu butonları için özel stiller */
QPushButton#minimizeBtn, 
QPushButton#maximizeBtn, 
QPushButton#closeBtn {
    background: transparent;
    border: none;
    color: #6c7293;
    font-size: 16px;
    font-weight: bold;
    padding: 5px 12px;
    text-transform: none;  /* Büyük harf yapma */
}

QPushButton#minimizeBtn:hover, 
QPushButton#maximizeBtn:hover {
    background-color: rgba(45, 94, 255, 0.2);  /* Yarı saydam mavi */
    color: white;
}

QPushButton#closeBtn:hover {
    background-color: rgba(220, 53, 69, 0.2);  /* Yarı saydam kırmızı */
    color: #dc3545;
}
"""

class WorkerThread(QThread):
    progress = pyqtSignal(str)  # İlerleme sinyali
    finished = pyqtSignal(list)  # Bitti sinyali
    error = pyqtSignal(str)  # Hata sinyali

    def __init__(self):
        super().__init__()
        self.search_text = ""  # Arama metni için değişken

    def run(self):
        try:
            pdf_folder = "pdf"
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
                self.progress.emit("PDF klasörü oluşturuldu.")
                return

            pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
            if not pdf_files:
                self.progress.emit("PDF klasöründe dosya bulunamadı!")
                return

            tum_bilgiler = []
            cikarilanlar = []  # Çıkarılan dekontları tutacak liste
            
            # Arama metnini virgülle ayır ve normalize et
            arama_isimleri = [self._normalize_text(isim.strip()) 
                            for isim in self.search_text.split(',') 
                            if isim.strip()]
            
            # TXT dosyasını aç
            with open("dekont_bilgileri.txt", "w", encoding="utf-8") as f:
                f.write("İŞLENEN DEKONTLAR:\n")
                f.write("=" * 50 + "\n\n")
                
                for pdf_file in pdf_files:
                    try:
                        self.progress.emit(f"{pdf_file} işleniyor...")
                        file_path = os.path.join(pdf_folder, pdf_file)
                        bilgiler = extract_info_from_receipt(file_path)
                        
                        # Alıcı adını normalize et
                        alici_adi = self._normalize_text(bilgiler["Alıcı Adı"])
                        
                        # Herhangi bir isimle eşleşme var mı kontrol et
                        eslesme_var = any(isim in alici_adi for isim in arama_isimleri if isim)
                        
                        # Eşleşme yoksa ekle
                        if not eslesme_var:
                            tum_bilgiler.append(bilgiler)
                            
                            # TXT dosyasına yaz
                            f.write(f"{pdf_file} için çıkarılan bilgiler:\n")
                            for key, value in bilgiler.items():
                                f.write(f"{key}: {value}\n")
                            f.write("-" * 50 + "\n")
                        else:
                            cikarilanlar.append({
                                'dosya': pdf_file,
                                'alici': bilgiler["Alıcı Adı"],
                                'tutar': bilgiler["İşlem Tutarı"]
                            })
                            self.progress.emit(f"❌ {pdf_file} eşleşme nedeniyle çıkarıldı")
                        
                    except Exception as e:
                        self.error.emit(f"{pdf_file} işlenirken hata: {str(e)}")

                # Çıkarılan dekontları TXT dosyasına ekle
                if cikarilanlar:
                    f.write("\nÇIKARILAN DEKONTLAR:\n")
                    f.write("=" * 50 + "\n")
                    for cikarilan in cikarilanlar:
                        f.write(f"Dosya: {cikarilan['dosya']}\n")
                        f.write(f"Alıcı: {cikarilan['alici']}\n")
                        f.write(f"Tutar: {cikarilan['tutar']}\n")
                        f.write("-" * 30 + "\n")

            if tum_bilgiler:
                # Excel'e kaydet
                df = pd.DataFrame(tum_bilgiler)
                excel_path = "dekont_bilgileri.xlsx"
                df.to_excel(excel_path, index=False, engine='openpyxl')
                
                self.progress.emit(f"İşlem tamamlandı! {len(tum_bilgiler)} dekont işlendi, {len(cikarilanlar)} dekont çıkarıldı.")
                self.finished.emit(tum_bilgiler)
            else:
                self.progress.emit(f"Tüm dekontlar ({len(cikarilanlar)} adet) eşleşme nedeniyle çıkarıldı!")
                self.finished.emit([])

        except Exception as e:
            self.error.emit(f"Genel hata: {str(e)}")

    def _normalize_text(self, text):
        """Metni normalize eder ve büyük harfe çevirir"""
        # Türkçe karakterleri normalize et
        replacements = {
            'İ': 'I', 'I': 'I', 'ı': 'I',
            'Ğ': 'G', 'ğ': 'G',
            'Ü': 'U', 'ü': 'U',
            'Ş': 'S', 'ş': 'S',
            'Ö': 'O', 'ö': 'O',
            'Ç': 'C', 'ç': 'C',
        }
        normalized = text.strip().upper()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return normalized

class YeniliklerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STYLE_SHEET)  # Aynı stili dialog'a da uygula
        self.setWindowTitle("Yeni Özellikler")
        self.setGeometry(200, 200, 600, 400)
        self.setWindowModality(Qt.ApplicationModal)  # Ana pencere üzerinde göster
        
        layout = QVBoxLayout()
        
        # Yenilikler metni
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
        <h2>Son Eklenen Özellikler</h2>
        <hr>
        <h3>1. ÇOKLU İSİM FİLTRELEME</h3>
        <ul>
            <li>Virgülle ayrılmış birden fazla isim girişi</li>
            <li>Her bir isim için ayrı kontrol</li>
            <li>Normalize edilmiş isim karşılaştırması</li>
        </ul>
        
        <h3>2. BANKA ÖZEL İYİLEŞTİRMELERİ</h3>
        <h4>YAPI KREDİ:</h4>
        <ul>
            <li>Şirket ve kurum isimleri desteği</li>
            <li>Sansürlü isim desteği (SA***** ŞA*****)</li>
            <li>ALACAKLI HESAP/IBAN formatı</li>
            <li>GİDEN FAST TUTARI ve ISLEM TUTARI desteği</li>
        </ul>
        
        <h4>ZİRAAT BANKASI:</h4>
        <ul>
            <li>İşlem tutarı ve Havale tutarı kontrolü</li>
            <li>Alıcı hesap ve Alacaklı IBAN kontrolü</li>
        </ul>
        
        <h4>GARANTİ BANKASI:</h4>
        <ul>
            <li>ALACAKLI IBAN formatı desteği</li>
            <li>Tutar formatı iyileştirmesi</li>
        </ul>
        
        <h3>3. PROGRAM İKONU</h3>
        <ul>
            <li>Özel program ikonu eklendi</li>
        </ul>
        """)
        layout.addWidget(text)
        
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class DekontAnaliz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # Varsayılan başlık çubuğunu kaldır
        
        # Ekran boyutunu al ve pencere boyutunu ayarla
        screen = QApplication.primaryScreen().size()
        self.setGeometry(
            (screen.width() - 1400) // 2,  # Ekranın ortasında
            (screen.height() - 900) // 2,  # Ekranın ortasında
            1400,  # Genişlik
            900   # Yükseklik
        )

        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Özel başlık çubuğu
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(35)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # Program ikonu ve başlığı
        title_label = QLabel("Dekont Analiz")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        
        # Boşluk
        title_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Kontrol butonları
        minimize_btn = QPushButton("—")
        minimize_btn.setObjectName("minimizeBtn")
        minimize_btn.clicked.connect(self.showMinimized)
        
        maximize_btn = QPushButton("□")
        maximize_btn.setObjectName("maximizeBtn")
        maximize_btn.clicked.connect(self.toggle_maximize)
        
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(minimize_btn)
        title_layout.addWidget(maximize_btn)
        title_layout.addWidget(close_btn)
        
        main_layout.addWidget(title_bar)
        
        # İçerik alanı
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Üst kısım - Arama ve istatistikler
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        
        # Arama alanı
        search_layout = QVBoxLayout()  # Dikey layout'a çevirdik
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Listeden çıkarmak istediğiniz alıcı adlarını virgülle ayırarak girin...")
        search_layout.addWidget(self.search_input)
        
        # İşlem butonu buraya taşındı
        self.process_button = QPushButton("Dekontları İşle")
        self.process_button.clicked.connect(self.process_all_files)
        search_layout.addWidget(self.process_button)
        
        top_layout.addLayout(search_layout)
        
        # İstatistik kartları
        stats_layout = QHBoxLayout()
        
        # İstatistik kartlarını oluştur
        self.total_card = self.create_stat_card(stats_layout, "Toplam Dekont", "0")
        self.processed_card = self.create_stat_card(stats_layout, "İşlenen Dekont", "0")
        self.removed_card = self.create_stat_card(stats_layout, "Çıkarılan Dekont", "0")

        top_layout.addLayout(stats_layout)
        content_layout.addWidget(top_section)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Banka", "İşlem Tarihi", "Alıcı Adı", 
            "Alıcı IBAN", "Alıcı Banka", "İşlem Tutarı"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        content_layout.addWidget(self.table)
        
        # Log alanı
        self.log_area = QTextEdit()
        self.log_area.setObjectName("logArea")
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(100)
        content_layout.addWidget(self.log_area)
        
        main_layout.addWidget(content_widget)
        
        # Stil eklemeleri
        self.setStyleSheet(STYLE_SHEET + """
            /* Başlık çubuğu stilleri */
            QWidget#titleBar {
                background-color: #15171c;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            
            QLabel#titleLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
            
            QPushButton#minimizeBtn, 
            QPushButton#maximizeBtn, 
            QPushButton#closeBtn {
                background: transparent;
                border: none;
                color: #6c7293;
                font-size: 16px;
                padding: 5px 8px;
            }
            
            QPushButton#minimizeBtn:hover, 
            QPushButton#maximizeBtn:hover {
                background-color: #2d5eff;
                color: white;
                border-radius: 4px;
            }
            
            QPushButton#closeBtn:hover {
                background-color: #dc3545;
                color: white;
                border-radius: 4px;
            }
        """)
        
        # Pencere taşıma için değişkenler
        self.dragging = False
        self.drag_position = None
        
        # Pencereyi göster
        self.show()
        # Yenilikleri göster
        self.show_whats_new()

    def mouseDoubleClickEvent(self, event):
        # Başlık çubuğuna çift tıklama kontrolü
        if event.pos().y() <= 35:  # Başlık çubuğu yüksekliği
            self.toggle_maximize()
            event.accept()

    def mousePressEvent(self, event):
        # Sadece başlık çubuğundan sürüklemeye izin ver
        if event.button() == Qt.LeftButton and event.pos().y() <= 35:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and not self.isMaximized():  # Maksimize durumda sürüklemeyi engelle
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            # Normal boyuta döndüğünde kenarlıkları yuvarlak yap
            self.setStyleSheet(self.styleSheet().replace("border-radius: 0px;", "border-radius: 10px;"))
        else:
            self.showMaximized()
            # Tam ekranda kenarlıkları düz yap
            self.setStyleSheet(self.styleSheet().replace("border-radius: 10px;", "border-radius: 0px;"))

    def create_stat_card(self, parent_layout, title, value):
        card = QWidget()
        card.setObjectName("statsCard")
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        
        value_label = QLabel(value)
        value_label.setObjectName("cardValue")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        parent_layout.addWidget(card)
        return value_label

    def show_whats_new(self):
        # Ayarlar dosyasını kontrol et
        settings_file = "program_settings.json"
        show_dialog = True
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                if settings.get('whats_new_shown', False):
                    show_dialog = False
        
        if show_dialog:
            dialog = YeniliklerDialog(self)
            dialog.exec_()
            
            # Ayarları kaydet
            settings = {'whats_new_shown': True}
            with open(settings_file, 'w') as f:
                json.dump(settings, f)

    def process_all_files(self):
        self.process_button.setEnabled(False)
        self.table.setRowCount(0)
        self.log_area.clear()
        
        # Arama metnini al
        search_text = self.search_input.text().strip().upper()
        
        # İlerleme penceresini oluştur
        self.progress_dialog = QProgressDialog("Dekontlar işleniyor...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("İşlem Durumu")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.show()

        # Worker thread'i başlat
        self.worker = WorkerThread()
        self.worker.search_text = search_text  # Arama metnini worker'a aktar
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.handle_error)
        self.worker.finished.connect(self.process_complete)
        self.worker.start()

    def update_progress(self, message):
        self.log_area.append(message)
        self.progress_dialog.setLabelText(message)

    def handle_error(self, error_message):
        self.log_area.append(f"❌ {error_message}")

    def process_complete(self, results):
        self.progress_dialog.close()
        self.process_button.setEnabled(True)
        
        # PDF klasöründeki toplam dekont sayısı
        pdf_files = [f for f in os.listdir("pdf") if f.lower().endswith('.pdf')]
        total_count = len(pdf_files)
        processed_count = len(results)
        removed_count = total_count - processed_count
        
        # İstatistik kartlarını güncelle
        self.total_card.setText(str(total_count))
        self.processed_card.setText(str(processed_count))
        self.removed_card.setText(str(removed_count))
        
        # Tabloyu doldur
        self.table.setRowCount(0)
        for bilgiler in results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(bilgiler["Banka"]))
            self.table.setItem(row, 1, QTableWidgetItem(bilgiler["İşlem Tarihi"]))
            self.table.setItem(row, 2, QTableWidgetItem(bilgiler["Alıcı Adı"]))
            self.table.setItem(row, 3, QTableWidgetItem(bilgiler["Alıcı IBAN"]))
            self.table.setItem(row, 4, QTableWidgetItem(bilgiler["Alıcı Banka"]))
            self.table.setItem(row, 5, QTableWidgetItem(bilgiler["İşlem Tutarı"]))
        
        self.log_area.append("✅ İşlem tamamlandı!")

def setup_fonts():
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    
    # Sadece mevcut Roboto-Regular fontunu yükle
    font_path = os.path.join(fonts_dir, 'Roboto-Regular.ttf')
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id < 0:
            print("Hata: Font yüklenemedi!")
        else:
            print("Font başarıyla yüklendi!")

def main():
    # QApplication oluşturmadan önce High DPI ayarlarını yap
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    
    # Font kurulumunu yap
    setup_fonts()
    
    # Font render ayarları
    font = app.font()
    font.setHintingPreference(QFont.PreferFullHinting)
    font.setStyleStrategy(QFont.PreferAntialias | QFont.PreferQuality)
    app.setFont(font)

    # Ekran DPI'ına göre font boyutunu ayarla
    screen = app.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    font_size_multiplier = dpi / 96.0  # 96 DPI standart değer
    
    # Karanlık tema için palette ayarları
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(43, 43, 43))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(59, 59, 59))
    dark_palette.setColor(QPalette.AlternateBase, QColor(43, 43, 43))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(43, 43, 43))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(13, 110, 253))
    dark_palette.setColor(QPalette.Highlight, QColor(13, 110, 253))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    
    app.setPalette(dark_palette)
    
    window = DekontAnaliz()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 