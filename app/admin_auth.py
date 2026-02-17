# Назначение файла:
# Логика аутентификации администратора и работы с сессиями.

# Импортируем системные инструменты.
import os
import secrets

# Импортируем типы FastAPI.
from fastapi import Request, HTTPException, status

# Настройки учётных данных администратора.
ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'bodryakov')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'bod')

# Ключ для CSRF-токенов.
CSRF_SECRET = os.getenv('CSRF_SECRET', 'change_me_csrf_secret')

# Проверяем логин/пароль.
def verify_credentials(login: str, password: str) -> bool:
    # Сравниваем введённые данные с настройками.
    return login == ADMIN_LOGIN and password == ADMIN_PASSWORD

# Устанавливаем флаг авторизации в сессии.
def set_admin_session(request: Request) -> None:
    # Помечаем сессию как авторизованную.
    request.session['is_admin'] = True

# Очищаем сессию администратора.
def clear_admin_session(request: Request) -> None:
    # Удаляем данные админа из сессии.
    request.session.pop('is_admin', None)

# Проверяем, что пользователь является администратором.
def require_admin(request: Request) -> None:
    # Если нет флага авторизации — запрещаем доступ.
    if not request.session.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

# Генерируем CSRF-токен и сохраняем в сессию.
def ensure_csrf_token(request: Request) -> str:
    # Получаем токен из сессии или создаём новый.
    token = request.session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        request.session['csrf_token'] = token
    return token

# Проверяем CSRF-токен для опасных запросов.
def verify_csrf_token(request: Request, token: str) -> None:
    # Считываем токен из сессии.
    session_token = request.session.get('csrf_token')
    # Сравниваем безопасно.
    if not session_token or not secrets.compare_digest(session_token, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='CSRF token invalid')
