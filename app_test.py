from flask import Flask, Response, abort
import requests
from io import BytesIO
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

DAY_MAP = {
    1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб', 7: 'Вс'
}
DAYS_ORDER = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

API_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/114.0.0.0 Safari/537.36'),
    'Accept': 'application/json'
}

COLOR_BOUNDS = [0, 1, 40, 51, 100]
COLOR_PALETTE = ["#FFFFFF", "#FFE9D3", "#E8B7A2", "#CA4532"]

def value_to_color(value):
    for i in range(len(COLOR_BOUNDS)-1):
        if COLOR_BOUNDS[i] <= value < COLOR_BOUNDS[i+1]:
            return COLOR_PALETTE[i]
    return COLOR_PALETTE[-1]

@app.route("/")
def index():
    return (
        "<h2>Пример: <a href='/oktyabrskiy'>/oktyabrskiy</a> — график загруженности филиала</h2>"
    )

@app.route("/<slug>")
def load_graph(slug: str):
    api_url = f"https://md.tomsk.ru/api/v1/data/filials/{slug}?extra_bi=true"

    try:
        response = requests.get(api_url, headers=API_HEADERS, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        abort(502, description=f"Ошибка при запросе к API: {e}")

    try:
        load_history = response.json()["data"]["load_history"]
    except (KeyError, ValueError):
        abort(500, description="Невозможно извлечь данные о загруженности")

    if not load_history:
        abort(404, description="Данные загруженности отсутствуют")

    data_matrix = defaultdict(dict)
    hours_set = set()

    for entry in load_history:
        hour = entry['hour']
        day = DAY_MAP.get(entry['day'])
        value = entry['value']
        if day is not None:
            data_matrix[hour][day] = value
            hours_set.add(hour)

    sorted_hours = sorted(hours_set)
    hour_labels = [f"{h}:00-{h+1}:00" for h in sorted_hours]

    values = []
    for hour in sorted_hours:
        row = [data_matrix[hour].get(day, 0) for day in DAYS_ORDER]
        values.append(row)

    cell_width = 80
    cell_height = 30
    left_margin = 100
    top_margin = 50
    right_margin = 20
    bottom_margin = 20

    width = left_margin + cell_width * len(DAYS_ORDER) + right_margin
    height = top_margin + cell_height * len(sorted_hours) + bottom_margin

    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
        font_bold = font

    # Заголовок
    title_text = "Информация о предполагаемой загруженности на текущую неделю"
    bbox = draw.textbbox((0, 0), title_text, font=font_bold)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((width - w) / 2, 10), title_text, fill='black', font=font_bold)

    # Заголовки дней сверху
    for i, day in enumerate(DAYS_ORDER):
        x = left_margin + i * cell_width + cell_width / 2
        y = top_margin - 25
        bbox = draw.textbbox((0, 0), day, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((x - w / 2, y), day, fill='black', font=font)

    # Часы слева
    for i, hour_label in enumerate(hour_labels):
        x = 10
        y = top_margin + i * cell_height + cell_height / 2
        bbox = draw.textbbox((0, 0), hour_label, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((x, y - h / 2), hour_label, fill='black', font=font)

    # Ячейки с цветом
    for row_i, row in enumerate(values):
        for col_i, val in enumerate(row):
            x0 = left_margin + col_i * cell_width
            y0 = top_margin + row_i * cell_height
            x1 = x0 + cell_width
            y1 = y0 + cell_height
            fill_color = value_to_color(val)
            draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline='gray')

    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)

    return Response(output.getvalue(), mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)
