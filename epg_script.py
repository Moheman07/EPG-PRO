import io
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz

# إعدادات التوقيت
TIMEZONE = pytz.timezone('Asia/Qatar')  # توقيت الدوحة (UTC+3)

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
        tz_aware_dt = TIMEZONE.localize(naive_dt)
        return tz_aware_dt.isoformat()
    except ValueError as e:
        raise ValueError(f"تنسيق وقت غير صحيح: {epg_time} - {str(e)}")

def filter_future_programs(programs: list, days_ahead: int = 3) -> list:
    """تصفية البرامج المستقبلية فقط"""
    now = datetime.now(TIMEZONE)
    cutoff = now + timedelta(days=days_ahead)
    return [
        p for p in programs 
        if datetime.fromisoformat(p['start']).astimezone(TIMEZONE) <= cutoff
    ]

def main():
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
    
    # 3. تصفية البرامج المستقبلية (3 أيام القادمة)
    filtered_programs = filter_future_programs(epg_programs)
    
    # 4. حفظ الملف
    with io.open('epg-pro.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_programs, f, ensure_ascii=False, indent=2)
    
    print(f"تم إنشاء ملف EPG بنجاح يحتوي على {len(filtered_programs)} برنامج")

if __name__ == "__main__":
    main()
