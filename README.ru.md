# textseek

[English](README.md) | **Русский**

Python-библиотека без зависимостей для поиска и извлечения структурированных данных —
кодов подтверждения, ссылок и произвольных совпадений регулярных выражений — из простого текста.

`textseek` не привязан ни к какому источнику: текст может поступать из электронной почты, SMS, HTML,
ответа API, логов, OCR или любого другого места. Получение текста — ваша задача; извлечение
структурированных значений из него — задача `textseek`.

## Установка

```bash
pip install textseek
```

Требуется Python 3.12+. Без зависимостей во время выполнения.

## Быстрый старт

```python
from textseek import TextSeek, Extract

text = "Your verification code is 123456"

seek = TextSeek(text)
result = seek.extract_one(Extract.code(length=6, digits=True))

print(result.value)  # 123456
```

### Извлечение ссылки и просмотр её частей

```python
link = TextSeek(text).extract_one(
    Extract.link(domain="example.com")
)
print(link.domain)              # example.com
print(link.path)                # /auth/magic
print(link.query_params["token"][0])
```

### Поиск по примеру ссылки

```python
link = TextSeek(text).extract_one(
    Extract.link(sample="https://example.com/auth/magic?token=abc&email=test@example.com")
)
```

### Произвольное регулярное выражение

```python
order = TextSeek(text).extract_one(Extract.regex(r"Order ID:\s*([A-Z0-9\-]+)"))
print(order.value)
```

## Методы

| Метод | Возвращает |
|---|---|
| `extract_one(spec)` | один результат или вызывает `ExtractNotFoundError` |
| `extract_first(spec)` | первый результат или `None` |
| `extract_all(spec)` | список результатов (возможно, пустой) |
| `contains(spec)` | `bool` |

Полная документация находится в `docs/`.
