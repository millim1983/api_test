import requests

url = 'http://apis.data.go.kr/1611000/undergroundsafetyinfo/getImpatEvalutionList'
params ={'serviceKey' : 'dfYc/F69J2aDe9EZCApdr8EfCaK6FlRmn7wLvqs/aOh8CBZB6DYRcIYOiV8aUe161WqfU7NZ7RRAepFsJEuCMA==', 'sysRegDateFrom' : '20191017', 'sysRegDateTo' : '20191117', 'numOfRows' : '10', 'pageNo' : '1' }

response = requests.get(url, params=params)
print(response.content)