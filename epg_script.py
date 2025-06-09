import io
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# إعداد التوقيت المحلي (UTC+3 ثابت)
utc_offset = 10800  # 3 ساعات بالثواني (UTC+3)
offset = timedelta(seconds=utc_offset)

# تحميل ملف XML من المصدر
url = 'https://www.open-epg.com/generate/xtckHrCmAy.xml'
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Failed to fetch XML: {e}")
    raise

# تحليل XML
try:
    root = ET.fromstring(response.content.decode('utf-8'))
except ET.ParseError as e:
    print(f"Failed to parse XML: {e}")
    raise

# تعديل صيغة الوقت لتتضمن +03:00
def parse_and_adjust_time(t_str):
    try:
        t_utc = datetime.strptime(t_str[:14], '%Y%m%d%H%M%S')
        t_local = t_utc + offset
        return t_local.strftime('%Y-%m-%dT%H:%M:%S+03:00')
    except ValueError as e:
        print(f"Error parsing time {t_str}: {e}")
        return None

epg_data = []
today = datetime.utcnow().date()

for programme in root.findall('programme'):
    start_time = parse_and_adjust_time(programme.attrib['start'])
    stop_time = parse_and_adjust_time(programme.attrib['stop'])
    
    if start_time and stop_time:
        start_date = datetime.strptime(start_time[:10], '%Y-%m-%d').date()
        stop_date = datetime.strptime(stop_time[:10], '%Y-%m-%d').date()
        # تضمين البرامج التي تنتهي في اليوم الحالي أو المستقبل
        if stop_date >= today:
            epg_data.append({
                'channel': programme.attrib.get('channel', ''),
                'start': start_time,
                'stop': stop_time,
                'title': programme.findtext('title', default='').strip(),
                'description': programme.findtext('desc', default='').strip()
            })
        else:
            print(f"Skipping outdated program: {programme.findtext('title', '')} (Start: {start_time}, Stop: {stop_time})")

# التحقق من وجود بيانات
if not epg_data:
    print("No valid programs found for today")
    raise ValueError("No valid EPG data generated")

# حفظ كـ JSON
with io.open('epg-pro.json', 'w', encoding='utf-8') as f:
    json.dump(epg_data, f, ensure_ascii=False, indent=2)

print(f"EPG JSON generated successfully with {len(epg_data)} programs")
