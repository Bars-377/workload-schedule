# # Используем официальный образ Python
# FROM python:3.12-slim

# # Устанавливаем рабочую директорию в контейнере
# WORKDIR /app

# # Копируем файлы проекта в контейнер
# COPY . /app

# # Устанавливаем зависимости
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt

# # # Копируем директорию виртуального окружения в контейнер
# # COPY myenv /app/myenv

# # # Устанавливаем переменную окружения для Python, чтобы он использовал библиотеки из виртуального окружения
# # ENV VIRTUAL_ENV=/app/myenv
# # ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# # Открываем порт для приложения (если это веб-сервер)
# EXPOSE 5000

# # Команда для запуска приложения
# CMD ["python", "start.py"]

# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Убедитесь, что venv доступен
RUN python -m venv /venv

# Убедитесь, что venv доступен
ENV PATH="/venv/bin:$PATH"

# Устанавливаем зависимости
RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# # Копируем директорию виртуального окружения в контейнер
# COPY myenv /app/myenv

# # Устанавливаем переменную окружения для Python, чтобы он использовал библиотеки из виртуального окружения
# ENV VIRTUAL_ENV=/app/myenv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Открываем порт для приложения (если это веб-сервер)
EXPOSE 5757