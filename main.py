import pdfplumber
import re
import os
import pandas as pd

# Türkiye'de en yaygın kullanılan bankalar
bankalar = [
    "T. Garanti Bankası A.Ş.", "Enpara Şubesi", "T.C. ZİRAAT BANKASI A.Ş.", "Papara Elektronik Para A.Ş.", "Garanti BBVA", "Akbank T.A.Ş.", "Denizbank A.Ş.",
    "Türkiye İş Bankası A.Ş.", "VakıfBank", "Halkbank", "Ziraat Bankası",
    "Yapı ve Kredi Bankası A.Ş.", "QNB Finansbank", "ING Bank A.Ş.", 
    "TEB (Türk Ekonomi Bankası)", "Şekerbank T.A.Ş.", "Alternatif Bank A.Ş.",
    "Fibabanka A.Ş.", "Kuveyt Türk Katılım Bankası A.Ş.", 
    "Albaraka Türk Katılım Bankası A.Ş.", "Türkiye Finans Katılım Bankası A.Ş."
]

def clean_text(text):
    # Gereksiz kelimeleri temizleme
    remove_keywords = ["Tutar", "Adı Soyadı", "TCKN", "ALACAKLI IBAN", "Ünvan", "ADRES", "İşlem", "AÇIKLAMA", "ALACAKLI","KOMİSYON HESAP NUMARASI", "GÖNDERİCİ", "TUTAR BİLGİLERİ", "GÖNDERİCİ BİLGİLERİ", "ALICI BİLGİLERİ", "İŞLEM BİLGİLERİ"]
    for word in remove_keywords:
        text = re.sub(rf"\b{word}\b", "", text, flags=re.IGNORECASE)
    
    # Metni temizle ve büyük harfe çevir
    cleaned_text = text.strip().upper()
    
    return cleaned_text

def tespit_banka_iban(iban):
    # Türkiye'deki banka kodları
    banka_kodlari = {
        '00010': 'Ziraat Bankası',
        '00012': 'Halk Bankası',
        '00015': 'VakıfBank',
        '00032': 'TEB',
        '00046': 'Akbank',
        '00059': 'Şekerbank',
        '00062': 'Garanti BBVA',
        '00064': 'Türkiye İş Bankası',
        '00092': 'Citibank',
        '00099': 'ING Bank',
        '00103': 'Fibabanka',
        '00111': 'QNB Finansbank',
        '00123': 'HSBC',
        '00124': 'Alternatif Bank',
        '00125': 'Burgan Bank',
        '00134': 'Denizbank',
        '00135': 'Anadolu Bank',
        '00146': 'OdeaBank',
        '00167': 'Yapı Kredi',
        '00203': 'Albaraka Türk',
        '00205': 'Kuveyt Türk',
        '00206': 'Türkiye Finans'
    }

    # IBAN formatını kontrol et
    if len(iban) != 26 or not iban.startswith('TR'):
        return 'Geçersiz IBAN'

    # Banka kodunu al
    banka_kodu = iban[4:9]

    # Banka kodunu sözlükte ara
    banka_adi = banka_kodlari.get(banka_kodu, 'Bilinmeyen Banka')

    return banka_adi

def extract_info_from_receipt(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Değişkenleri başta tanımla
    alici_iban = "IBAN bulunamadı"
    alici_adi = "Alıcı adı bulunamadı"
    alici_banka = "Alıcı banka bulunamadı"
    tutar = "Tutar bulunamadı"
    tarih = "Tarih bulunamadı"

    # Banka adını bulmadan önce IBAN'ı kontrol et
    banka_adi = "Banka adı bulunamadı"
    
    # Önce sadece IBAN: formatını ara
    iban_match = re.search(r"IBAN\s*:\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})", text, re.IGNORECASE)
    if iban_match:
        temp_iban = clean_text(iban_match.group(1).replace(" ", ""))
        tespit_edilen_banka = tespit_banka_iban(temp_iban)
        # Eğer İş Bankası ise kabul et
        if tespit_edilen_banka == "Türkiye İş Bankası":
            banka_adi = "Türkiye İş Bankası"
    
    # Eğer banka adı hala bulunamadıysa veya İş Bankası değilse, banka listesinden kontrol et
    if banka_adi == "Banka adı bulunamadı":
        for banka in bankalar:
            # Metinde bankayı ara
            matches = re.finditer(banka, text)
            for match in matches:
                # Eşleşmenin öncesinde "Alıcı" veya "ALICI" veya "banka" kelimesi var mı kontrol et
                start_pos = max(0, match.start() - 30)  # 30 karakter öncesine bak
                preceding_text = text[start_pos:match.start()]
                if not any(keyword in preceding_text.upper() for keyword in ["ALICI", "BANKA", "ALACAKLI"]):
                    banka_adi = banka
                    break
            if banka_adi != "Banka adı bulunamadı":
                break

    # İşlem tarihi
    tarih_match = re.search(r"(\d{2}/\d{2}/\d{4}|\d{2}\.\d{2}\.\d{4})", text)
    tarih = tarih_match.group(1) if tarih_match else "Tarih bulunamadı"

    # İşlem tutarı (TL ile biten ilk para miktarı)
    tutar_match = re.search(r"([\d,.]+)\s*TL", text)
    tutar = tutar_match.group(1) + " TL" if tutar_match else "Tutar bulunamadı"

    if banka_adi == "T. Garanti Bankası A.Ş.":
        # IBAN bilgisi - önce ALACAKLI IBAN'ı ara
        iban_match = re.search(r"ALACAKLI IBAN\s*:\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})", text, re.IGNORECASE)
        if not iban_match:
            # Bulunamazsa IBAN'ı dene
            iban_match = re.search(r"IBAN\s*:\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})", text, re.IGNORECASE)
        if iban_match:
            alici_iban = clean_text(iban_match.group(1).replace(" ", ""))

        # Alıcı adı
        alici_adi_match = re.search(r"ALACAKLI HESAP\s*:\s*(?:\d+\s*/\s*\d+\s*)?([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", text)
        if alici_adi_match and alici_adi_match.group(1).strip():
            alici_adi = clean_text(alici_adi_match.group(1).strip())
        else:
            alici_adi_alt = re.search(r"ALACAKLI\s*:\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", text)
            if alici_adi_alt:
                alici_adi = clean_text(alici_adi_alt.group(1).strip())

        # İşlem tutarı
        tutar_match = re.search(r"TUTAR\s*:\s*-\s*(\d{1,3}(?:\.\d{3})*,\d{2})\s*TL", text, re.IGNORECASE)
        if tutar_match:
            tutar = tutar_match.group(1) + " TL"

    elif banka_adi == "Denizbank A.Ş.":
        iban_match = re.search(r"Alıcı IBAN\s*[:\-]?\s*(TR\d{2}[\d\s]+)", text, re.IGNORECASE)
        if iban_match:
            alici_iban = clean_text(iban_match.group(1).replace(" ", ""))

        alici_adi_match = re.search(r"Alıcı Adı Soyadı\s*[:\-]?\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", text, re.IGNORECASE)
        if alici_adi_match:
            alici_adi = clean_text(alici_adi_match.group(1).strip())
    
    elif banka_adi == "Akbank T.A.Ş.":
        # Önce ALICI BİLGİLERİ bölümünü bul
        alici_bilgileri_section = re.search(r"ALICI BİLGİLERİ(.*?)(?:GÖNDERİCİ BİLGİLERİ|TUTAR BİLGİLERİ)", text, re.IGNORECASE | re.DOTALL)
        if alici_bilgileri_section:
            alici_bilgileri_text = alici_bilgileri_section.group(1)
            
            # İkinci Adı Soyadı/Unvan eşleşmesini bul
            alici_adi_match = re.search(
                r"Adı Soyadı/Unvan\s*:\s*[A-Za-zÇĞİÖŞÜçğıöşü\s]+\s*Adı Soyadı/Unvan\s*:\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", 
                alici_bilgileri_text, 
                re.IGNORECASE
            )
            if alici_adi_match:
                alici_adi = clean_text(alici_adi_match.group(1))
            
            # Debug için yazdır

        # Alıcı IBAN
        iban_match = re.search(r"Alacaklı Hesap No\s*[:\-]?\s*(TR\d{2}[\d\s]+)", text, re.IGNORECASE)
        if iban_match:
            alici_iban = clean_text(iban_match.group(1).replace(" ", ""))

    elif banka_adi == "Papara Elektronik Para A.Ş.":
        # Papara için Alıcı Bilgileri bölümünden Ad Soyad/Unvan ve IBAN alınır
        alici_bilgileri_section = re.search(r"Alıcı Bilgileri(.*?)İşlem Bilgileri", text, re.IGNORECASE | re.DOTALL)
        if alici_bilgileri_section:
            alici_bilgileri_text = alici_bilgileri_section.group(1)

            # Alıcı Adı - Önce Ad Soyad / Ünvan'ı dene
            alici_adi_match = re.search(r"Ad Soyad / Ünvan\s*[:\-]?\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+?)(?:\n|$)", 
                                      alici_bilgileri_text, 
                                      re.IGNORECASE)
            if alici_adi_match:
                alici_adi = clean_text(alici_adi_match.group(1).strip())
            else:
                # Ad Soyad bulunamazsa Alıcı değerini kontrol et
                alici_match = re.search(r"Alıcı\s*[:\-]?\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+?)(?:\n|$)", 
                                      text, 
                                      re.IGNORECASE)
                if alici_match:
                    alici_adi = clean_text(alici_match.group(1).strip())

            # Önce IBAN'ı kontrol et
            iban_match = re.search(r"IBAN\s*[:\-]?\s*(TR\d{2}[\d\s]+)", alici_bilgileri_text, re.IGNORECASE)
            if iban_match:
                alici_iban = clean_text(iban_match.group(1).replace(" ", ""))
            else:
                # IBAN bulunamazsa Açıklama bölümünde ara
                aciklama_iban = re.search(r"(?:IBAN|Hesap No)\s*[:\-]?\s*(TR\d{2}[\d\s]+)", text, re.IGNORECASE)
                if aciklama_iban:
                    alici_iban = clean_text(aciklama_iban.group(1).replace(" ", ""))
                else:
                    # IBAN yoksa Papara No'yu kontrol et
                    papara_matches = list(re.finditer(r"Papara No\s*[:\-]?\s*(\d+)", alici_bilgileri_text, re.IGNORECASE))
                    if len(papara_matches) > 1:  # Birden fazla eşleşme varsa
                        alici_iban = papara_matches[1].group(1)  # İkinci eşleşmeyi al
                    elif papara_matches:  # Tek eşleşme varsa
                        alici_iban = papara_matches[0].group(1)  # İlk eşleşmeyi al

    elif banka_adi == "T.C. ZİRAAT BANKASI A.Ş.":
        # Ziraat Bankası için IBAN bilgisi - önce Alıcı hesap, sonra alacaklı IBAN'ı dene
        iban_patterns = [
            r"Alıcı hesap\s*[:\-]?\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})",
            r"Alacaklı IBAN\s*[:\-]?\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})",
            r"Alıcı IBAN\s*[:\-]?\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})"
        ]
        
        for pattern in iban_patterns:
            iban_match = re.search(pattern, text, re.IGNORECASE)
            if iban_match:
                alici_iban = clean_text(iban_match.group(1).replace(" ", ""))
                alici_banka = tespit_banka_iban(alici_iban)
                break

        # Alıcı banka bulunamadıysa alacaklı IBAN'dan tespit et
        if alici_banka == "Alıcı banka bulunamadı":
            alacakli_iban_match = re.search(r"Alacaklı IBAN\s*[:\-]?\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})", text, re.IGNORECASE)
            if alacakli_iban_match:
                alacakli_iban = clean_text(alacakli_iban_match.group(1).replace(" ", ""))
                alici_banka = tespit_banka_iban(alacakli_iban)
                if alici_iban == "IBAN bulunamadı":
                    alici_iban = alacakli_iban  # Eğer alıcı IBAN bulunamadıysa alacaklı IBAN'ı kullan

        # Ziraat Bankası için alıcı adı - önce Alıcı, sonra Alacaklı Adı Soyadı'nı dene
        alici_adi_match = re.search(r"Alıcı\s*:\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+?)(?=\s*(?:IBAN|Hesap|Tutar|$))", 
                                  text, 
                                  re.IGNORECASE)
        if not alici_adi_match:
            alici_adi_match = re.search(r"Alacaklı Adı Soyadı\s*:\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", 
                                      text, 
                                      re.IGNORECASE)
        if alici_adi_match:
            alici_adi = clean_text(alici_adi_match.group(1).strip())

        # İşlem tutarı - önce İşlem Tutarı, bulamazsa Havale Tutarı'nı kontrol et
        tutar_match = re.search(r"İşlem Tutarı\s*:\s*([\d,.]+)\s*(?:TL|TRY)", text, re.IGNORECASE)
        if not tutar_match:
            tutar_match = re.search(r"Havale Tutarı\s*:\s*([\d,.]+)\s*(?:TL|TRY)", text, re.IGNORECASE)
        if tutar_match:
            tutar = tutar_match.group(1) + " TL"

    elif banka_adi == "Türkiye İş Bankası":
        # IBAN bilgisi - Alıcı IBAN kısmından
        iban_match = re.search(r"Alıcı IBAN\s*:\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})", text, re.IGNORECASE)
        if iban_match:
            alici_iban = clean_text(iban_match.group(1).replace(" ", ""))

        # Alıcı adı - Alıcı Isim\Unvan kısmından
        alici_adi_match = re.search(r"Alıcı Isim\\Unvan\s*:\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", text, re.IGNORECASE)
        if alici_adi_match:
            alici_adi = clean_text(alici_adi_match.group(1).strip())

        # İşlem tutarı - sadece İşlem Tutarı kısmını al
        tutar_match = re.search(r"İşlem Tutarı\s*:\s*([\d,.]+)\s*TRY", text, re.IGNORECASE)
        if tutar_match:
            tutar = tutar_match.group(1) + " TL"

    elif banka_adi == "Enpara Şubesi":
        # Enpara için alıcı adı tespiti
        alici_adi_match = re.search(r"HAVALEYİ ALAN MUSTERİ UNVANI\s*:\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", text, re.IGNORECASE)
        if alici_adi_match:
            alici_adi = clean_text(alici_adi_match.group(1).strip())

        # IBAN bilgisi
        iban_match = re.search(r"IBAN\s*:\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})", text, re.IGNORECASE)
        if iban_match:
            alici_iban = clean_text(iban_match.group(1).replace(" ", ""))

        # İşlem tutarı - TL önce gelen format için
        tutar_match = re.search(r"TL\s*([\d,\.]+)", text, re.IGNORECASE)
        if tutar_match:
            tutar = tutar_match.group(1) + " TL"
        else:
            # Alternatif format için kontrol
            tutar_match = re.search(r"İŞLEM TUTARI\s*:\s*([\d,.]+)\s*TL", text, re.IGNORECASE)
            if tutar_match:
                tutar = tutar_match.group(1) + " TL"

        # İşlem tarihi
        tarih_match = re.search(r"İŞLEM TARİHİ\s*:\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
        if tarih_match:
            tarih = tarih_match.group(1)

    elif banka_adi == "Yapı ve Kredi Bankası A.Ş.":
        # Alıcı adı - tüm olası formatları dene
        alici_adi_patterns = [
            # Format 1: ALICI ADI (normal format)
            r"ALICI ADI\s*[:\-]?\s*([A-Za-zÇĞİÖŞÜçğıöşü\s\.]+?)(?=\s*(?:ALICI|TUTAR|$))",
            
            # Format 2: ALICI ADI (şirket/kurum formatı)
            r"ALICI ADI\s*[:\-]?\s*([A-Za-zÇĞİÖŞÜçğıöşü\s\.,&]+?(?:A\.Ş\.|LTD\.ŞTİ\.|TİC\.SAN\.|[A-Z]+\.)+[A-Za-zÇĞİÖŞÜçğıöşü\s\.,&]*)",
            
            # Format 3: ALACAKLI ADI (sansürlü format)
            r"ALACAKLI ADI\s*[:\-]?\s*([A-Za-zÇĞİÖŞÜçğıöşü\s\*]+)"
        ]
        
        for pattern in alici_adi_patterns:
            alici_adi_match = re.search(pattern, text, re.IGNORECASE)
            if alici_adi_match and alici_adi_match.group(1).strip():
                alici_adi = clean_text(alici_adi_match.group(1).strip())
                break

        # IBAN bilgisi - sadece spesifik formatları kullan
        iban_patterns = [
            r"ALICI HESAP\s*[:\-]?\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})",  # ALICI HESAP formatı
            r"ALACAKLI HESAP\s*[:\-]?\s*\d+/IBAN\s*[:\-]?\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})",  # ALACAKLI HESAP/IBAN formatı
            r"ALACAKLI HESAP NO\s*[:\-]?\s*(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})"  # ALACAKLI HESAP NO formatı
        ]
        
        for pattern in iban_patterns:
            iban_match = re.search(pattern, text, re.IGNORECASE)
            if iban_match:
                alici_iban = clean_text(iban_match.group(1).replace(" ", ""))
                alici_banka = tespit_banka_iban(alici_iban)
                break

        # İşlem tutarı - önce GİDEN FAST TUTARI, bulamazsa ISLEM TUTARI kısmından
        tutar_match = re.search(r"GİDEN FAST TUTARI\s*[:\-]?\s*-?\s*([\d,.]+)", text, re.IGNORECASE)
        if not tutar_match:
            tutar_match = re.search(r"ISLEM TUTARI\s*[:\-]?\s*-?\s*([\d,.]+)", text, re.IGNORECASE)
        if tutar_match:
            tutar = tutar_match.group(1) + " TL"

    else:
        iban_patterns = [
            r"(?:ALACAKLI IBAN|ALACAKLI HESAP|HESAP NO|IBAN|Hesap)\s*[:\-]?\s*(TR\d{2}[\d\s]+)",
            r"(TR\d{2}(?:\s*\d{4}){5}\s*\d{2})"
        ]
        for pattern in iban_patterns:
            iban_match = re.search(pattern, text, re.IGNORECASE)
            if iban_match:
                alici_iban = clean_text(iban_match.group(1).replace(" ", ""))
                break

        alici_adi_patterns = [
            r"(?:ALICI ADI SOYADI|ADI SOYADI|Adı Soyadı|Ad Soyad)\s*[:\-]?\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)",
            r"(?:ALICISI|HESAP SAHİBİ)[:\s]+([A-Za-zÇĞİÖŞÜçğıöşü\s]+)"
        ]
        for pattern in alici_adi_patterns:
            alici_adi_match = re.search(pattern, text, re.IGNORECASE)
            if alici_adi_match:
                alici_adi = clean_text(alici_adi_match.group(1).strip())
                break

    # Alıcı bankayı tespit et
    alici_banka = "Alıcı banka bulunamadı"
    if banka_adi == "Papara Elektronik Para A.Ş.":
        # Önce IBAN'dan banka tespiti yap
        if alici_iban != "IBAN bulunamadı" and alici_iban.startswith('TR'):
            alici_banka = tespit_banka_iban(alici_iban)
            
        # Eğer banka bulunamadıysa veya Papara No kullanılmışsa kurum değerini kullan
        if alici_banka == "Alıcı banka bulunamadı" or alici_banka == "Bilinmeyen Banka":
            kurum_patterns = [
                r"Kurum\s*[:\-]?\s*([^:\n]+?)(?:\s*(?:Şube|Hesap|$))",
                r"Kurum\s*[:\-]?\s*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)",
                r"(?:Kurum|KURUM)\s*:?\s*([^\n:]+)",
                r"Alıcı Bilgileri.*?Kurum\s*:?\s*([^:\n]+?)(?:\s*(?:Şube|Hesap|$))",
                r"(?:Kurum|KURUM)\s*Adı\s*:?\s*([^\n:]+)"
            ]
            
            for pattern in kurum_patterns:
                kurum_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if kurum_match:
                    alici_banka = clean_text(kurum_match.group(1).strip())
                    alici_banka = re.sub(r'[.,;:]$', '', alici_banka)
                    break
    elif alici_iban != "IBAN bulunamadı":
        alici_banka = tespit_banka_iban(alici_iban)

    return {
        "Banka": banka_adi,
        "İşlem Tarihi": tarih,
        "Alıcı Adı": alici_adi,
        "Alıcı IBAN": alici_iban,
        "Alıcı Banka": alici_banka,
        "İşlem Tutarı": tutar
    }

# Otomatik işleme kısmını kaldır
# PDF klasöründeki tüm dosyaları listele
pdf_folder = "pdf"

# Klasör yoksa oluştur
if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)

# Aşağıdaki kısımları kaldır
# pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
# tum_bilgiler = []
# with open("dekont_bilgileri.txt", "w", encoding="utf-8") as f:
#     for pdf_file in pdf_files:
#         ...
# df = pd.DataFrame(tum_bilgiler)
# excel_path = "dekont_bilgileri.xlsx"
# df.to_excel(excel_path, index=False, engine='openpyxl')
# print("Dekont bilgileri 'dekont_bilgileri.txt' ve 'dekont_bilgileri.xlsx' dosyalarına kaydedildi.")
