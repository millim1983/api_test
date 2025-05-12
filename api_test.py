import requests
import urllib.parse
import xml.etree.ElementTree as ET
import json

url = 'http://apis.data.go.kr/1611000/undergroundsafetyinfo/getSubsidenceList'
params ={'serviceKey' : 'dfYc/F69J2aDe9EZCApdr8EfCaK6FlRmn7wLvqs/aOh8CBZB6DYRcIYOiV8aUe161WqfU7NZ7RRAepFsJEuCMA==', 'sagoDateFrom' : '20240101', 'sagoDateTo' : '20241231', 'numOfRows' : '10000', 'pageNo' : '1' }

response = requests.get(url, params=params, verify=False)

print("응답 코드:", response.status_code)
print("내용 미리보기:")
print(response.text[:500])  # XML 일부 미리보기

try:
    root = ET.fromstring(response.text)

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

    parsed_dict = etree_to_dict(root)

    # JSON 파일로 저장
    with open("subsidence_info_침하사고.json", "w", encoding="utf-8") as f:
        json.dump(parsed_dict, f, indent=2, ensure_ascii=False)

    print("✅ subsidence_info.json 파일로 저장 완료")

except ET.ParseError:
    print("❌ XML 파싱에 실패했습니다.")