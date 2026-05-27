# Task Manager API

FastAPI приложение для управления задачами с WebSocket чатом.

## Установка и запуск

### Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
