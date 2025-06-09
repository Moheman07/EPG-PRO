import io
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# إعدادات التوقيت (بدون pytz)
TIMEZONE_OFFSET = timedelta(hours=3)  # توقيت الدوحة (UTC+3)

def fetch_xml(url: str) -> ET.ElementTree:
    """جلب ملف XML من المصدر"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return ET.fromstring(response.content.decode('utf-8'))
    except Exception as e:
        raise Exception(f"فشل جلب XML: {str(e)}")

def convert_epg_time(epg_time: str) -> str:
    """تحويل تنسيق الوقت من XML إلى ISO 8601 مع Timezone"""
    try:
        naive_dt = datetime.strptime(epg_time[:14], '%Y%m%d%H%M%S')
        tz_aware_dt = naive_dt + TIMEZONE_OFFSET
        return tz_aware_dt.strftime('%Y-%m-%dT%H:%M:%S+03:00')
    except ValueError as e:
        raise ValueError(f"تنسيق وقت غير صحيح: {epg_time} - {str(e)}")

def main():
    try:
        # 1. جلب البيانات
        xml_url = "https://www.open-epg.com/generate/xtckHrCmAy.xml"
        root = fetch_xml(xml_url)
        
        # 2. تحويل البيانات
        epg_programs = []
        for prog in root.findall('programme'):
            try:
                epg_programs.append({
                    'channel': prog.get('channel', '').strip(),
                    'start': convert_epg_time(prog.get('start')),
                    'stop': convert_epg_time(prog.get('stop')),
                    'title': prog.findtext('title', default='').strip(),
                    'description': prog.findtext('desc', default='').strip()
                })
            except Exception as e:
                print(f"تحذير: تخطي برنامج بسبب خطأ - {str(e)}")
                continue
        
        # 3. حفظ الملف
        with io.open('epg-pro.json', 'w', encoding='utf-8') as f:
            json.dump(epg_programs, f, ensure_ascii=False, indent=2)
        
        print(f"تم إنشاء ملف EPG بنجاح يحتوي على {len(epg_programs)} برنامج")
        return True
    except Exception as e:
        print(f"خطأ فادح: {str(e)}")
        return False

if __name__ == "__main__":
    main()
