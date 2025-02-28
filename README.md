# DekontMaster

DekontMaster, PDF formatındaki dekont belgelerini otomatik olarak analiz eden ve içindeki belirli bilgileri temizleyerek Excel dosyası olarak çıktı veren bir programdır. Finansal veri işleme süreçlerini hızlandırmak için tasarlanmıştır.

## Özellikler / Features
- PDF dosyalarından bilgi çıkarımı
- Otomatik veri temizleme
- Excel (XLSX) çıktısı oluşturma
- Çoklu dosya desteği
- Hızlı ve güvenilir işlem

## Kurulum / Installation
### Gereksinimler / Requirements
- Python 3.x
- Gerekli kütüphaneler:
  - `pdfplumber`
  - `pandas`
  - `openpyxl`
  - `re`
  - `os`
  - `PyQt5`
  - `sys`
  - `json`
  - `datetime`

### Kurulum Adımları / Installation Steps
1. Gerekli kütüphaneleri yükleyin:

```bash
pip install pdfplumber pandas openpyxl PyQt5
```

2. Proje dosyalarını indirin.

3. Build almak için aşağıdaki komutu çalıştırın:

```bash
pyinstaller ReceiptAnalysis.spec
```

## Kullanım / Usage
### Örnek Kullanım / Example Usage
Gerekli PDF dekontlarını **pdf** klasörüne atın. Programı açıp çalıştırarak dekontları analiz edin.

```python
from main import extract_info_from_receipt

dekont_analiz("dosya.pdf", "cikti.xlsx")
```

## Lisans / License
Bu proje MIT lisansı ile lisanslanmıştır.

---

# ReceiptMaster

ReceiptMaster is a program that automatically analyzes receipt documents in PDF format, extracts certain information, and outputs it as an Excel file. It is designed to speed up financial data processing workflows.

## Features
- Extract information from PDF files
- Automatic data cleaning
- Generate Excel (XLSX) output
- Multi-file support
- Fast and reliable processing

## Installation
### Requirements
- Python 3.x
- Required Libraries:
  - `pdfplumber`
  - `pandas`
  - `openpyxl`
  - `re`
  - `os`
  - `PyQt5`
  - `sys`
  - `json`
  - `datetime`

### Installation Steps
1. Install the required libraries:

```bash
pip install pdfplumber pandas openpyxl PyQt5
```

2. Download the project files.

3. To build the project, run the following command:

```bash
pyinstaller ReceiptAnalysis.spec
```

## Usage
### Example Usage
Place the required PDF receipts in the **pdf** folder. Open and run the program to analyze the receipts.

```python
from main import extract_info_from_receipt

dekont_analiz("file.pdf", "output.xlsx")
```

## License
This project is licensed under the MIT License.

