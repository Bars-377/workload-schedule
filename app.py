import matplotlib
matplotlib.use('Agg')  # Использовать backend без GUI

from flask import Flask, Response, abort
import requests
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from io import BytesIO
from collections import defaultdict

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

    fig, ax = plt.subplots(figsize=(10, 6))

    norm = BoundaryNorm(COLOR_BOUNDS, len(COLOR_PALETTE))
    color_map = matplotlib.colors.ListedColormap(COLOR_PALETTE)

    ax.imshow(values, cmap=color_map, norm=norm, aspect='auto')

    # Горизонтальная ось сверху
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    # Подписи осей
    ax.set_xticks(range(len(DAYS_ORDER)))
    ax.set_xticklabels(DAYS_ORDER, fontsize=10)
    ax.set_yticks(range(len(hour_labels)))
    ax.set_yticklabels(hour_labels, fontsize=10)

    # Добавляем сетку (границы ячеек)
    ax.set_xticks([x - 0.5 for x in range(1, len(DAYS_ORDER))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(hour_labels))], minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=1)

    # Отключаем основные линии сетки (если включены)
    ax.grid(which='major', visible=False)

    ax.set_title("Информация о предполагаемой загруженности на текущую неделю", fontsize=16)
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.tight_layout()

    img = BytesIO()
    fig.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)

    return Response(img.getvalue(), mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
