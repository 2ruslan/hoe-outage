import json
import time
from datetime import datetime, timezone
import requests
from io import BytesIO
from PIL import Image

# =============================
# 🔧 НАЛАШТУВАННЯ
# =============================

IMAGE_URL = "https://hoe.com.ua/Content/Uploads/2025/11/file20251112193957906.png"
REGION_ID = "hoe"

# Вихідні файли
OUTPUT_JSON = "data/hoe.json"
OUTPUT_IMG = "data/hoe-source.png"

# Координати сітки (в пікселях)
GRID_X = 100      # зсув зліва (початок таблиці)
GRID_Y = 200      # зсув зверху
CELL_W = 70       # ширина однієї клітинки
CELL_H = 60       # висота однієї клітинки
COLS = 24         # кількість годин
ROWS = 6          # кількість черг

# Кольори: RGB-умови для розпізнавання
COLOR_MAP = {
    "white": "yes",    # світло є
    "gray": "maybe",   # можливо відключення
    "blue": "no"       # світла немає
}

# =============================
# 🧠 ЛОГІКА РОЗПІЗНАВАННЯ
# =============================

def detect_color(pixel):
    """Визначає колір клітинки (спрощено по RGB)."""
    r, g, b = pixel
    if b > 150 and r < 100 and g < 150:
        return "blue"
    avg = (r + g + b) / 3
    if avg > 220:
        return "white"
    elif avg < 150:
        return "gray"
    return "white"

def main():
    # Завантажити зображення
    response = requests.get(IMAGE_URL)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img.save(OUTPUT_IMG)

    width, height = img.size
    print(f"✅ Image loaded: {width}x{height}px")

    data = {}
    for row in range(ROWS):
        queue_name = f"queue{row + 1}"
        data[queue_name] = {}
        for col in range(COLS):
            # Центр клітинки
            x = GRID_X + col * CELL_W + CELL_W // 2
            y = GRID_Y + row * CELL_H + CELL_H // 2

            if x >= width or y >= height:
                continue  # на випадок, якщо виходить за межі

            color_name = detect_color(img.getpixel((x, y)))
            data[queue_name][str(col + 1)] = COLOR_MAP[color_name]

    # Unix timestamp початку доби
    today_ts = int(time.time() // 86400 * 86400)

    result = {
        "regionId": REGION_ID,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "fact": {
            "data": {
                str(today_ts): data
            }
        }
    }

    # Записати результат
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved JSON to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
