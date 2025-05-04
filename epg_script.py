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
response = requests.get(url)

if response.status_code != 200:
    raise Exception(f"Download failed: {response.status_code}")

# تحليل XML
try:
    root = ET.fromstring(response.content.decode('utf-8'))
except ET.ParseError as e:
    raise Exception(f"Failed to parse XML: {e}")

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

for programme in root.findall('programme'):
    start_time = parse_and_adjust_time(programme.attrib['start'])
    stop_time = parse_and_adjust_time(programme.attrib['stop'])
    
    if start_time and stop_time:
        epg_data.append({
            'channel': programme.attrib.get('channel', ''),
            'start': start_time,
            'stop': stop_time,
            'title': programme.findtext('title', default='').strip(),
            'description': programme.findtext('desc', default='').strip()
        })

# حفظ كـ JSON
with io.open('epg-pro.json', 'w', encoding='utf-8') as f:
    json.dump(epg_data, f, ensure_ascii=False, indent=2)

print("EPG JSON generated successfully")
