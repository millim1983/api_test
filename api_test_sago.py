import requests
import xml.etree.ElementTree as ET
import json
import math
import urllib.parse

# API 기본 설정
url = 'http://apis.data.go.kr/1611000/undergroundsafetyinfo/getSubsidenceList'
service_key = 'dfYc/F69J2aDe9EZCApdr8EfCaK6FlRmn7wLvqs/aOh8CBZB6DYRcIYOiV8aUe161WqfU7NZ7RRAepFsJEuCMA=='
base_params = {
    'serviceKey': service_key,
    'sagoDateFrom': '20240101',
    'sagoDateTo': '20241231',
    'numOfRows': '100',  # 한 페이지 100건
    'pageNo': '1'
}

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = {}
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                if k in dd:
                    if not isinstance(dd[k], list):
                        dd[k] = [dd[k]]
                    dd[k].append(v)
                else:
                    dd[k] = v
        d = {t.tag: dd}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text and t.text.strip():
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

# 1. 첫 페이지 요청 → totalCount 확인
response = requests.get(url, params=base_params, verify=False)
root = ET.fromstring(response.text)
parsed = etree_to_dict(root)

try:
    total_count = int(parsed['resonse']['body']['totalCount'])
    print(f"📦 총 데이터 건수: {total_count}")
except Exception as e:
    print("❌ totalCount 추출 오류:", e)
    total_count = 0

# 2. 전체 페이지 수 계산
items_all = []
if total_count > 0:
    total_pages = math.ceil(total_count / int(base_params['numOfRows']))
    print(f"📄 총 페이지 수: {total_pages}")

    # 3. 각 페이지 반복 수집
    for page in range(1, total_pages + 1):
        print(f"🔄 {page}/{total_pages} 페이지 처리 중...")
        base_params['pageNo'] = str(page)
        resp = requests.get(url, params=base_params, verify=False)
        root = ET.fromstring(resp.text)
        parsed = etree_to_dict(root)

        try:
            items = parsed['resonse']['body']['items']['item']
            if isinstance(items, list):
                items_all.extend(items)
            else:
                items_all.append(items)
        except:
            print(f"⚠️ {page}페이지에서 item 없음")


# 4. JSON 파일로 저장
output = {
    'totalCount': total_count,
    'items': items_all
}
with open("subsidence_info_침하사고_all.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ subsidence_info_침하사고_all.json 파일 저장 완료")