import json
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm


# ✔️ 설정
API_URL = "http://apis.data.go.kr/1611000/undergroundsafetyinfo/getSubsidenceInfo"
SERVICE_KEY = "dfYc/F69J2aDe9EZCApdr8EfCaK6FlRmn7wLvqs/aOh8CBZB6DYRcIYOiV8aUe161WqfU7NZ7RRAepFsJEuCMA=="

# ✔️ JSON 원본 로드
with open("subsidence_info_침하사고_all.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

# ✔️ 사고번호 리스트 추출
sago_no_list = [item["sagoNo"] for item in json_data["items"]]

# ✔️ XML to dict 변환 함수
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

# ✔️ 사고 상세 정보 수집
details = []

for sago_no in tqdm(sago_no_list, desc="📡 사고번호 상세 조회 중"):
    params = {
        "serviceKey": SERVICE_KEY,
        "sagoNo": sago_no
    }

    try:
        response = requests.get(API_URL, params=params, timeout=5)
        root = ET.fromstring(response.content)
        parsed = etree_to_dict(root)

        item = parsed.get("response", parsed.get("resonse", {})).get("body", {}).get("items", {}).get("item")
        if item:
            details.append(item)

    except Exception as e:
        print(f"❌ 에러 발생: sagoNo={sago_no} → {e}")

# ✔️ 결과 JSON 저장
with open("subsidence_detail_all.json", "w", encoding="utf-8") as f:
    json.dump(details, f, indent=2, ensure_ascii=False)

# ✔️ 엑셀로도 저장 (원하는 경우)
df = pd.DataFrame(details)

# 3️⃣ 위도/경도 → 문자열로 강제 형변환 (지수 표기 방지)
df["sagoLat"] = df["sagoLat"].astype(str)
df["sagoLon"] = df["sagoLon"].astype(str)

# 4️⃣ JSON 저장 (값 그대로 유지)
with open("subsidence_detail_clean.json", "w", encoding="utf-8") as f:
    #json.dump(df, f, indent=2, ensure_ascii=False)
    json.dump(df.to_dict(orient="records"), f, indent=2, ensure_ascii=False)  # ✅ 정상


# 5️⃣ CSV 저장 (Excel에서 열어도 지수 표기 방지)
df.to_csv("subsidence_detail_clean.csv", index=False, encoding="utf-8-sig")

# 6️⃣ (선택) 엑셀 저장: 숫자형 → 문자열 처리한 상태로 저장

df.to_excel("subsidence_detail_clean.xlsx", index=False, engine="openpyxl")

print("✅ 사고 상세정보 수집 및 저장 완료 (JSON + Excel)")
