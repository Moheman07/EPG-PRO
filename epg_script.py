import io
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# تجاهل تحذيرات الشهادات
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# تحميل ملف XML من المصدر
url = 'https://www.open-epg.com/generate/xtckHrCmAy.xml'
response = requests.get(url, verify=False)

if response.status_code != 200:
    raise Exception(f"Download failed: {response.status_code}")

# تحليل XML
root = ET.fromstring(response.content.decode('utf-8'))

# نعيد التاريخ بصيغة UTC القياسية: 2025-05-02T17:30:00Z
def parse_time_utc(t_str):
    t_utc = datetime.strptime(t_str[:14], '%Y%m%d%H%M%S')
    return t_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

epg_data = []

for programme in root.findall('programme'):
    epg_data.append({
        'channel': programme.attrib.get('channel'),
        'start': parse_time_utc(programme.attrib['start']),
        'stop': parse_time_utc(programme.attrib['stop']),
        'title': programme.findtext('title', default='').strip(),
        'description': programme.findtext('desc', default='').strip()
    })

# حفظ كـ JSON
with io.open('epg-pro.json', 'w', encoding='utf-8') as f:
    json.dump(epg_data, f, ensure_ascii=False, indent=2)
