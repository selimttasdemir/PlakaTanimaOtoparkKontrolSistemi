import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import easyocr

# OCR motorunu başlat (Türkçe ve İngilizce destekli)
reader = easyocr.Reader(['en', 'tr'])

# Kamerayı açq
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Plaka bölgesini manuel seçmek için
    cv2.putText(frame, "Secmek icin: 's' - Cikmak icin: 'q'", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.imshow("Plaka Okuma", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # 's' tuşuna basınca bölge seçme ekranı gelir
        roi = cv2.selectROI("Plaka Sec", frame, fromCenter=False, showCrosshair=True)
        if roi != (0, 0, 0, 0):  # Eğer boş seçim yapılmadıysa
            x, y, w, h = roi
            plate_img = frame[y:y+h, x:x+w]

            # OCR ile plakayı oku
            results = reader.readtext(plate_img)

            # Sonuçları ekrana yazdır
            for (bbox, text, prob) in results:
                print(f"Okunan Plaka: {text} - Güvenilirlik: {prob:.2f}")
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    elif key == ord('q'):  # 'q' tuşuna basınca çıkış yap
        break

    cv2.imshow("Plaka Okuma", frame)

cap.release()
cv2.destroyAllWindows()
