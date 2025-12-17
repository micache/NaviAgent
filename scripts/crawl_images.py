# %%
# !pip install -U ddgs pillow requests

# %%
from ddgs import DDGS
import requests
from PIL import Image
from io import BytesIO
import os
import time

# ----------- danh sách địa danh -----------

locations = [
"Hoi An, Vietnam", "Nha Trang, Vietnam", "Sapa, Vietnam", "Seoul, South Korea",
"Kyoto, Japan", "Shanghai, China", "Phu Quoc, Vietnam", "Ho Chi Minh City, Vietnam",
"Hangzhou, China", "Da Nang, Vietnam", "Guilin, China", "Da Lat, Vietnam",
"Busan, South Korea", "Taipei, Taiwan", "Shenzhen, China", "Nara, Japan",
"Macau, China", "Hue, Vietnam", "Xian, China", "Osaka, Japan", "Suzhou, China",
"Jeju City, South Korea", "Ha Long, Vietnam", "Hong Kong, China", "Tainan, Taiwan",
"Hanoi, Vietnam", "Chengdu, China", "Taichung, Taiwan", "Guangzhou, China",
"Tokyo, Japan", "Kaohsiung, Taiwan", "Beijing, China", "Incheon, South Korea",
"Hualien, Taiwan", "Xi'an, China", "Fukuoka, Japan", "Nagasaki, Japan", "Taiwan",
"Kobe, Japan", "Daegu, South Korea", "Zhuhai, China", "Makau, China",
"Sapporo, Japan", "Gwangju, South Korea", "Huizhou, China", "Fuji, Japan",
"Sanya, China", "Xiamen, China", "Kumamoto, Japan", "Kunming, China",
"Dalat, Vietnam", "Huashan, China", "Yokohama, Japan",
"Buddhist temple in Gwangju, South Korea", "Lijiang, China", "Huế, Vietnam",
"Chiang Mai, Thailand", "Souzhou, China", "Suwon, South Korea",
"Hội An, Vietnam", "Daejeon, South Korea", "Su Zhou, China",
"Nagasaki, Japan", "Wuxi, China", "Jiangsu, China", "Nagoya, Japan",
"Japanese Garden, Japan", "Bangkok, Thailand", "Chenjiang, China",
"Huangshan, China", "Naoshima, Japan", "Guangxi, China"
]

# ----------- tạo folder output -----------

save_dir = "C:\\Users\\duong\\Downloads\\destinations"
os.makedirs(save_dir, exist_ok=True)

# ----------- search và download -----------

with DDGS() as ddgs:
    for loc in locations:
        print(f"\n🔍 Searching image for: {loc}")

        try:
            results = ddgs.images(query=loc, max_results=1)
        except Exception as e:
            print("⚠ Error:", e)
            continue

        if not results:
            print("❌ No image found")
            continue

        img_url = results[0].get("image") or results[0].get("thumbnail")
        print("➡ URL:", img_url)

        if not img_url:
            print("❌ No valid image URL")
            continue

        try:
            img_bytes = requests.get(img_url, timeout=15).content
            img = Image.open(BytesIO(img_bytes)).convert("RGB")

            filename = loc.replace(",", "").replace(" ", "_") + ".jpg"
            path = f"{save_dir}/{filename}"
            img.save(path)

            print(f"✅ Saved: {path}")

        except Exception as e:
            print("⚠ Download failed:", e)

        time.sleep(0.8)   # tránh hồ sơ rate-limit


# %%



