import io
import time
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# تجاهل تحذيرات الشهادات
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# إعداد التوقيت المحلي
is_dst = time.localtime().tm_isdst > 0
utc_offset = - (time.altzone if is_dst else time.timezone)
offset = timedelta(seconds=utc_offset)
time_zone_str = time.strftime('%z')

# تحميل ملف XML من المصدر
url = 'https://www.open-epg.com/generate/xtckHrCmAy.xml'
response = requests.get(url, verify=False)

if response.status_code != 200:
    raise Exception(f"Download failed: {response.status_code}")

# تحليل XML
root = ET.fromstring(response.content.decode('utf-8'))

def parse_and_adjust_time(t_str):
    t_utc = datetime.strptime(t_str[:14], '%Y%m%d%H%M%S')
    t_local = t_utc + offset
    return t_local.strftime('%Y-%m-%dT%H:%M:%S') + time_zone_str

epg_data = []

for programme in root.findall('programme'):
    epg_data.append({
        'channel': programme.attrib.get('channel'),
        'start': parse_and_adjust_time(programme.attrib['start']),
        'stop': parse_and_adjust_time(programme.attrib['stop']),
        'title': programme.findtext('title', default='').strip(),
        'description': programme.findtext('desc', default='').strip()
    })

# حفظ كـ JSON
with io.open('epg-pro.json', 'w', encoding='utf-8') as f:
    json.dump(epg_data, f, ensure_ascii=False, indent=2)
