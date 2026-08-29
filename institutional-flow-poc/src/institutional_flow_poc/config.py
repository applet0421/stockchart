from pathlib import Path

SOURCE_URLS = {
    "companies": "https://openapi.twse.com.tw/v1/opendata/t187ap03_L",
    "market": "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX",
    "t86": "https://www.twse.com.tw/rwd/zh/fund/T86",
}

INDUSTRIES = {
    "01": "水泥工業", "02": "食品工業", "03": "塑膠工業", "04": "紡織纖維",
    "05": "電機機械", "06": "電器電纜", "08": "玻璃陶瓷", "09": "造紙工業",
    "10": "鋼鐵工業", "11": "橡膠工業", "12": "汽車工業", "14": "建材營造",
    "15": "航運業", "16": "觀光餐旅", "17": "金融保險", "18": "貿易百貨",
    "19": "綜合", "20": "其他", "21": "化學工業", "22": "生技醫療業",
    "23": "油電燃氣業", "24": "半導體業", "25": "電腦及週邊設備業", "26": "光電業",
    "27": "通信網路業", "28": "電子零組件業", "29": "電子通路業", "30": "資訊服務業",
    "31": "其他電子業", "32": "文化創意業", "33": "農業科技業", "34": "電子商務業",
    "35": "綠能環保", "36": "數位雲端", "37": "運動休閒", "38": "居家生活",
}

# 32-34 are legacy/TPEx categories and are not present in the current TWSE 33-category
# list. Keep only official TWSE-listed categories.
for _code in ("32", "33", "34"):
    INDUSTRIES.pop(_code)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
RAW_ROOT = DATA_ROOT / "raw"
PROCESSED_ROOT = DATA_ROOT / "processed"
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
