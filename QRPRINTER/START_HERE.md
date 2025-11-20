# QR Printer System - התחלה מהירה

## 🚀 הפעלה מהירה

### שיטה 1: הפעלה ישירה (מומלץ)
```bash
python qr_printer_system.py
```

או פשוט:
```bash
start.bat
```

זה מפעיל את כל המערכת:
- ✅ שרת הדפסה (פורט 5000)
- ✅ שרת תצוגה (פורט 8080) 
- ✅ מעקב קבצים (File Watcher)

### שיטה 2: הפעלה נפרדת (אם צריך)
אם אתה רוצה להריץ כל שירות בנפרד:
- `python printer_service.py` - שרת הדפסה בלבד
- `python display_server.py` - שרת תצוגה בלבד
- `python print_file_watcher.py` - מעקב קבצים בלבד

## 📋 איך זה עובד

1. **הפעל את המערכת:**
   ```bash
   python qr_printer_system.py
   ```

2. **פתח דפדפן:**
   - לך ל: `http://localhost:8080`
   - תראה את מסך התצוגה

3. **הדפס משהו:**
   - הדפס מהמחשב ל-"QR Printer"
   - או שלח בקשה HTTP ל-`http://localhost:5000/print`

4. **התוצאה:**
   - נוצר QR code פחות צפוף
   - התוכן מוצג על המסך למשך 10 שניות
   - ה-QR מוצג מתחת לתוכן

## 🔧 הגדרת מדפסת Windows

אם אתה רוצה להדפיס מהמחשב:

1. פתח הגדרות Windows → מדפסות
2. הוסף מדפסת → "המדפסת שלי לא מופיעה"
3. בחר "הוסף מדפסת מקומית"
4. פורט: **FILE: (Print to File)**
5. דרייבר: **Generic / Text Only**
6. שם: **QR Printer**
7. כשמדפיסים, שמור ל: `print_input\print.txt`

## 📝 דוגמאות שימוש

### שליחת הדפסה דרך HTTP:
```python
import requests
requests.post('http://localhost:5000/print', 
              json={'content': 'Hello World!'})
```

### או עם PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:5000/print -Method Post -ContentType "application/json" -Body '{"content":"Hello World"}'
```

## 📁 מבנה קבצים

```
QRPRINTER/
├── qr_printer_system.py    ← קובץ ראשי אחד (הכל כאן!)
├── start.bat               ← הפעלה מהירה
├── qr_codes/               ← קבצי QR שנוצרו
├── print_content/          ← תוכן ההדפסות
├── print_input/            ← קבצי הדפסה מ-Windows
└── print_archive/          ← קבצים מעובדים
```

## ✨ תכונות

- ✅ QR codes פחות צפופים וקריאים יותר
- ✅ תצוגת תוכן ההדפסה על המסך
- ✅ תמיכה בעברית ואנגלית
- ✅ הכל בקובץ אחד - קל להפעלה
- ✅ מוצג למשך 10 שניות ואז נעלם

## 🛑 עצירה

לחץ `Ctrl+C` כדי לעצור את כל השירותים.

