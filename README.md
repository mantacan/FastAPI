# Инструкция по использованию API

1. **Запуск**
   ```bash
   uvicorn todo_app.main:app --reload
   ```
   Swagger будет доступен по адресу:  
   http://127.0.0.1:8000/docs

---

2. **Регистрация**
   - Нажать **POST /register/**
   - Ввести `username` и `password`
   - Нажать **Execute**

---

3. **Получение токена**
   - Нажать **POST /token/**
   - Ввести `username` и `password`
   - Нажать **Execute**
   - Скопировать `access_token` из ответа

---

4. **Аутентификация**
   - Нажать **Authorize ( Зеленая кнопка )** 
   - Вставить в поле: `access_token`
   - Нажать **Authorize**, затем **Close**

---
5. **Работать с ручками ;}**
