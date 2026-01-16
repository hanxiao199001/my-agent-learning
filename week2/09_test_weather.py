"""
测试 OpenWeatherMap API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY")

print(f"API Key: {api_key}")
print("\n测试 API 调用...")

# 测试调用
city = "Beijing"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=zh_cn"

print(f"\nURL: {url}")

response = requests.get(url)

print(f"\n状态码: {response.status_code}")
print(f"响应内容: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    print("\n✅ 成功!")
    print(f"城市: {data['name']}")
    print(f"温度: {data['main']['temp']}°C")
    print(f"天气: {data['weather'][0]['description']}")
elif response.status_code == 401:
    print("\n❌ API Key 无效或未激活")
    print("请检查:")
    print("1. API Key 是否正确")
    print("2. API Key 是否已激活(可能需要等待几分钟)")
    print("3. 访问 https://home.openweathermap.org/api_keys 检查状态")
elif response.status_code == 404:
    print("\n❌ 城市未找到")
else:
    print(f"\n❌ 错误: {response.status_code}")