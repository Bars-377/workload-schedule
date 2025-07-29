# Инструкция

## Запуск

1. Создать виртуальное окружение:
         python -m venv venv

2. Запустить виртуальное окружение:

         .\venv\Scripts\activate

3. Запустить приложение:

   python app.py

## Дополнительно:

Создаёт requirements.txt:

      python -m pip freeze > requirements.txt

Установить requirements.txt:

      python -m pip install -r requirements.txt

PowerShell:

      python -m pip freeze | ForEach-Object { python -m pip uninstall -y $_ }