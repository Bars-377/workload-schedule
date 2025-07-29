import matplotlib
matplotlib.use('Agg')  # Использовать backend без GUI

from flask import Flask, Response, abort
import requests
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import BoundaryNorm
from collections import defaultdict
import numpy as np

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

    # Создание матрицы значений: {hour -> {day -> value}}
    data_matrix = defaultdict(dict)
    hours_set = set()

    for entry in load_history:
        hour = entry['hour']
        day = DAY_MAP.get(entry['day'])
        value = entry['value']
        if day is not None:
            data_matrix[hour][day] = value
            hours_set.add(hour)

    # Упорядочим часы
    sorted_hours = sorted(hours_set)
    hour_labels = [f"{h}:00-{h+1}:00" for h in sorted_hours]

    # Формирование двумерного массива значений
    values = []
    for hour in sorted_hours:
        row = [data_matrix[hour].get(day, 0) for day in DAYS_ORDER]
        values.append(row)

    values_array = np.array(values)

    # Построение графика
    norm = BoundaryNorm(boundaries=COLOR_BOUNDS, ncolors=len(COLOR_PALETTE))
    sns.set_theme()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        values_array,
        cmap=COLOR_PALETTE,
        norm=norm,
        annot=True,
        cbar_kws={'label': 'Количество заявителей'},
        xticklabels=DAYS_ORDER,
        yticklabels=hour_labels,
        ax=ax
    )
    ax.set_title("Информация о предполагаемой загруженности на текущую неделю", fontsize=18)
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
