# Техническое задание: библиотека для поиска и извлечения данных из текста

## 1. Название проекта

Рабочее название библиотеки:

```text
textseek
```

Название можно изменить позже. Главное назначение библиотеки — удобный поиск и извлечение структурированных данных из обычного текста.

---

## 2. Краткое описание

`textseek` — это небольшая Python-библиотека без внешних зависимостей для поиска и извлечения данных из текста.

Библиотека не должна быть привязана к конкретному источнику данных.

Текст может быть получен из:

- email-письма;
- SMS;
- HTML-страницы;
- API-ответа;
- логов;
- Telegram-сообщения;
- OCR;
- файла;
- любого другого источника.

Главная идея:

```python
from textseek import TextSeek, Extract

text = "Your verification code is 123456"

seek = TextSeek(text)

result = seek.extract_one(
    Extract.code(length=6, digits=True)
)

print(result.value)  # 123456
```

---

## 3. Основная цель библиотеки

Библиотека должна дать удобный, типизированный и расширяемый API для извлечения данных из текста.

Основные задачи:

1. Искать коды подтверждения.
2. Искать буквенно-цифровые коды.
3. Искать коды со спецсимволами.
4. Извлекать все ссылки из текста.
5. Возвращать ссылки не просто строкой, а объектом с доступом к частям ссылки.
6. Искать ссылки по домену, пути, query-параметрам или примеру ссылки.
7. Искать произвольные значения через regex.
8. Возвращать результат в виде типизированных объектов.
9. Документировать, какой метод что принимает, что возвращает и какие ошибки может выбросить.
10. Сделать хорошую документацию библиотеки через Mintlify.

---

## 4. Не цели проекта

Библиотека не должна быть почтовой библиотекой.

В ядре библиотеки не должно быть:

- IMAP;
- Gmail API;
- Outlook API;
- SMTP;
- HTTP-клиента;
- OAuth2;
- базы данных;
- парсинга конкретных провайдеров;
- внешних зависимостей.

Почта, SMS, API, браузер и другие источники текста должны быть внешним слоем.

Пример правильного использования:

```python
email_text = email.text + "\n" + email.html

code = TextSeek(email_text).extract_one(
    Extract.code(length=6)
)
```

Пример неправильной идеи для ядра:

```python
client = GmailClient(...)
code = client.get_confirmation_code(...)
```

Так делать не нужно, потому что это привяжет библиотеку к конкретному источнику данных.

---

## 5. Основной публичный API

Основной объект библиотеки:

```python
seek = TextSeek(text)
```

Основные методы:

```python
seek.extract_one(...)
seek.extract_first(...)
seek.extract_all(...)
seek.contains(...)
```

### 5.1 `extract_one`

Метод ищет одно совпадение.

Если совпадение найдено — возвращает объект результата.

Если совпадение не найдено — выбрасывает ошибку `ExtractNotFoundError`.

```python
result = seek.extract_one(
    Extract.code(length=6)
)
```

Ожидаемое поведение:

```python
print(result.value)
print(result.start)
print(result.end)
```

### 5.2 `extract_first`

Метод ищет первое совпадение.

Если совпадение найдено — возвращает объект результата.

Если совпадение не найдено — возвращает `None`.

```python
result = seek.extract_first(
    Extract.code(length=6)
)

if result is None:
    print("Код не найден")
else:
    print(result.value)
```

### 5.3 `extract_all`

Метод ищет все совпадения.

Если совпадений нет — возвращает пустой список.

```python
links = seek.extract_all(
    Extract.link()
)
```

### 5.4 `contains`

Метод проверяет, есть ли совпадение.

Возвращает `bool`.

```python
has_code = seek.contains(
    Extract.code(length=6)
)
```

---

## 6. Extract API

Для создания правил поиска используется объект `Extract`.

Пользователь не должен вручную создавать внутренние классы спецификаций.

Правильный API:

```python
Extract.code(...)
Extract.link(...)
Extract.regex(...)
```

---

## 7. Поиск кодов

### 7.1 Базовый пример

```python
result = seek.extract_one(
    Extract.code(length=6, digits=True)
)
```

Ищет код:

```text
123456
```

### 7.2 Буквенно-цифровой код

```python
result = seek.extract_one(
    Extract.code(
        length=8,
        digits=True,
        alphabet=True,
    )
)
```

Может найти:

```text
A1B2C3D4
```

### 7.3 Код со спецсимволами

```python
result = seek.extract_one(
    Extract.code(
        min_length=8,
        max_length=16,
        digits=True,
        alphabet=True,
        symbols=True,
    )
)
```

Может найти:

```text
A8F3-K2P9
```

или:

```text
abC_123-xY
```

### 7.4 Код рядом с фразой

```python
result = seek.extract_one(
    Extract.code(
        length=6,
        digits=True,
        near="verification code",
        window=300,
    )
)
```

Логика:

1. Найти фразу `verification code`.
2. Взять окно текста рядом с этой фразой.
3. Искать код внутри этого окна.

Это нужно, если в тексте есть несколько чисел, но только одно из них является кодом.

### 7.5 Настройки `Extract.code`

Предлагаемый интерфейс:

```python
Extract.code(
    length: int | None = None,
    min_length: int | None = None,
    max_length: int | None = None,

    digits: bool = True,
    alphabet: bool = False,
    symbols: bool = False,

    uppercase: bool = True,
    lowercase: bool = True,

    require_each_type: bool = False,

    near: str | None = None,
    window: int = 300,

    pattern: str | None = None,
)
```

Описание параметров:

| Параметр | Назначение |
|---|---|
| `length` | Точная длина кода |
| `min_length` | Минимальная длина кода |
| `max_length` | Максимальная длина кода |
| `digits` | Разрешить цифры |
| `alphabet` | Разрешить буквы |
| `symbols` | Разрешить спецсимволы |
| `uppercase` | Разрешить буквы верхнего регистра |
| `lowercase` | Разрешить буквы нижнего регистра |
| `require_each_type` | Требовать наличие каждого выбранного типа символов |
| `near` | Искать код рядом с указанной фразой |
| `window` | Размер окна поиска рядом с фразой |
| `pattern` | Пользовательский regex-паттерн |

---

## 8. Важное поведение `require_each_type`

Если пользователь пишет:

```python
Extract.code(
    length=8,
    digits=True,
    alphabet=True,
)
```

Это значит, что код может состоять из цифр и букв.

Подходящие значения:

```text
12345678
ABCDEFGH
A1B2C3D4
```

Если пользователь пишет:

```python
Extract.code(
    length=8,
    digits=True,
    alphabet=True,
    require_each_type=True,
)
```

Тогда код должен содержать хотя бы одну цифру и хотя бы одну букву.

Подходит:

```text
A1B2C3D4
```

Не подходит:

```text
12345678
ABCDEFGH
```

---

## 9. Извлечение ссылок

### 9.1 Извлечение всех ссылок

```python
links = seek.extract_all(
    Extract.link()
)
```

Пример текста:

```text
Open https://example.com/login or https://docs.example.com/help
```

Результат должен быть списком объектов `LinkResult`.

Важно: ссылка не должна возвращаться просто строкой.

---

## 10. Объект ссылки

Ссылка должна возвращаться объектом, чтобы пользователь мог удобно обращаться к её частям.

Пример:

```python
link = seek.extract_one(
    Extract.link(domain="example.com")
)

print(link.value)
print(link.scheme)
print(link.domain)
print(link.path)
print(link.query)
print(link.query_params)
```

Предлагаемая модель:

```python
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class LinkResult:
    value: str
    start: int
    end: int

    scheme: str
    domain: str
    host: str
    port: int | None
    path: str
    query: str
    fragment: str

    query_params: dict[str, list[str]]
```

Пример результата для ссылки:

```text
https://example.com/auth/magic?token=abc123&email=test@example.com#top
```

Поля:

```python
link.value         # "https://example.com/auth/magic?token=abc123&email=test@example.com#top"
link.scheme        # "https"
link.domain        # "example.com"
link.host          # "example.com"
link.port          # None
link.path          # "/auth/magic"
link.query         # "token=abc123&email=test@example.com"
link.fragment      # "top"
link.query_params  # {"token": ["abc123"], "email": ["test@example.com"]}
```

---

## 11. Фильтрация ссылок

### 11.1 По домену

```python
links = seek.extract_all(
    Extract.link(domain="example.com")
)
```

### 11.2 По пути

```python
links = seek.extract_all(
    Extract.link(
        domain="example.com",
        path="/auth/magic"
    )
)
```

### 11.3 По части пути

```python
links = seek.extract_all(
    Extract.link(
        domain="example.com",
        path_contains="magic"
    )
)
```

### 11.4 По query-параметрам

```python
links = seek.extract_all(
    Extract.link(
        domain="example.com",
        required_query=["token", "email"]
    )
)
```

### 11.5 По примеру ссылки

```python
link = seek.extract_one(
    Extract.link(
        sample="https://example.com/auth/magic?token=abc&email=test@example.com"
    )
)
```

Библиотека должна разобрать пример ссылки и понять:

```text
scheme: https
domain: example.com
path: /auth/magic
required_query: token, email
```

При поиске по примеру значения query-параметров сравнивать не нужно.

То есть пример:

```text
https://example.com/auth/magic?token=abc&email=test@example.com
```

должен найти:

```text
https://example.com/auth/magic?token=REAL_TOKEN&email=user@example.com
```

---

## 12. Настройки `Extract.link`

Предлагаемый интерфейс:

```python
Extract.link(
    sample: str | None = None,

    scheme: str | None = None,
    domain: str | None = None,
    path: str | None = None,
    path_contains: str | None = None,

    required_query: list[str] | None = None,
    allow_subdomains: bool = False,
)
```

Описание параметров:

| Параметр | Назначение |
|---|---|
| `sample` | Пример ссылки, по которому библиотека сама строит правила поиска |
| `scheme` | Фильтр по протоколу, например `https` |
| `domain` | Фильтр по домену |
| `path` | Точное совпадение пути |
| `path_contains` | Поиск части внутри пути |
| `required_query` | Обязательные query-параметры |
| `allow_subdomains` | Разрешить поддомены указанного домена |

---

## 13. Regex extractor

Для произвольного поиска должен быть `Extract.regex`.

Пример:

```python
result = seek.extract_one(
    Extract.regex(r"Order ID:\s*([A-Z0-9\-]+)")
)
```

Результат должен содержать:

```python
result.value
result.groups
result.groupdict
result.start
result.end
```

Предлагаемая модель:

```python
@dataclass(slots=True, frozen=True)
class RegexResult:
    value: str
    start: int
    end: int
    groups: tuple[str, ...]
    groupdict: dict[str, str]
```

Если в regex есть группы, то `value` должен быть первой группой.

Если групп нет, то `value` должен быть полным совпадением.

---

## 14. Общая модель результата

Для всех результатов обязательны поля:

```python
value: str
start: int
end: int
```

Где:

| Поле | Назначение |
|---|---|
| `value` | Найденное значение |
| `start` | Индекс начала совпадения в исходном тексте |
| `end` | Индекс конца совпадения в исходном тексте |

Пример:

```python
result = seek.extract_one(Extract.code(length=6))

print(result.value)
print(result.start)
print(result.end)
```

---

## 15. Типизация

Типизация — одно из ключевых требований проекта.

Библиотека должна использовать современную типизацию Python.

Требования:

1. Использовать аннотации типов во всех публичных методах.
2. Использовать `dataclass(slots=True, frozen=True)` для неизменяемых объектов результата.
3. Использовать `typing.Protocol`, если понадобится расширяемый интерфейс extractor-ов.
4. Использовать `Literal`, где это упрощает API.
5. Не использовать `Any` в публичном API без явной необходимости.
6. Документировать, какой метод какой тип возвращает.
7. Стремиться к поддержке хороших подсказок в IDE.

Пример желаемого результата:

```python
link = seek.extract_one(Extract.link())

link.query_params["token"][0]
```

IDE должна понимать, что `link` — это `LinkResult`.

---

## 16. Важная проблема типизации `extract_one`

Так как `extract_one()` принимает разные спецификации, желательно сделать перегрузки через `typing.overload`.

Пример:

```python
from typing import overload

class TextSeek:
    @overload
    def extract_one(self, spec: CodeSpec) -> CodeResult: ...

    @overload
    def extract_one(self, spec: LinkSpec) -> LinkResult: ...

    @overload
    def extract_one(self, spec: RegexSpec) -> RegexResult: ...

    def extract_one(self, spec: ExtractSpec) -> ExtractResult:
        ...
```

Тогда пользователь получает нормальные подсказки:

```python
code = seek.extract_one(Extract.code(length=6))
code.value

link = seek.extract_one(Extract.link())
link.query_params
```

---

## 17. Обработка ошибок

Библиотека должна иметь понятную и предсказуемую систему ошибок.

Базовые ошибки:

```python
class TextSeekError(Exception):
    """Базовая ошибка библиотеки."""


class ExtractNotFoundError(TextSeekError):
    """Совпадение не найдено."""


class InvalidExtractSpecError(TextSeekError):
    """Некорректная спецификация поиска."""


class InvalidSampleLinkError(TextSeekError):
    """Некорректный пример ссылки."""


class InvalidCodeSpecError(TextSeekError):
    """Некорректные настройки поиска кода."""


class RegexExtractError(TextSeekError):
    """Ошибка при работе с regex."""
```

Пример использования:

```python
try:
    code = seek.extract_one(Extract.code(length=6))
except ExtractNotFoundError:
    print("Код не найден")
except InvalidCodeSpecError:
    print("Некорректные настройки поиска кода")
```

---

## 18. Требования к документации

Документация — важная часть проекта.

Документация должна быть написана так, чтобы новый пользователь мог быстро понять:

1. Что делает библиотека.
2. Что она не делает.
3. Как установить библиотеку.
4. Как быстро извлечь код.
5. Как извлечь ссылки.
6. Как получить параметры ссылки.
7. Как искать по примеру ссылки.
8. Как искать через regex.
9. Какие методы есть у `TextSeek`.
10. Что возвращает каждый метод.
11. Какие ошибки может выбросить каждый метод.
12. Как расширять библиотеку своими extractor-ами.

---

## 19. Документация через Mintlify

Для документации использовать Mintlify.

Предлагаемая структура документации:

```text
docs/
├── mint.json
├── introduction.mdx
├── quickstart.mdx
├── concepts/
│   ├── textseek.mdx
│   ├── extract-specs.mdx
│   └── results.mdx
├── usage/
│   ├── extract-code.mdx
│   ├── extract-links.mdx
│   ├── link-by-sample.mdx
│   ├── regex-search.mdx
│   └── error-handling.mdx
├── api-reference/
│   ├── textseek.mdx
│   ├── extract.mdx
│   ├── results.mdx
│   └── errors.mdx
└── advanced/
    ├── custom-extractors.mdx
    └── typing.mdx
```

---

## 20. Что обязательно описать в API Reference

Для каждого публичного метода нужно описать:

1. Назначение метода.
2. Сигнатуру.
3. Параметры.
4. Возвращаемый тип.
5. Возможные ошибки.
6. Примеры использования.

Пример для `extract_one`:

````mdx
## `extract_one`

Ищет одно совпадение по указанной спецификации.

### Signature

```python
def extract_one(self, spec: ExtractSpec) -> ExtractResult
```

### Returns

Возвращает один из типов:

- `CodeResult`
- `LinkResult`
- `RegexResult`

Конкретный тип зависит от переданного `ExtractSpec`.

### Raises

- `ExtractNotFoundError`
- `InvalidExtractSpecError`
````

---

## 21. Архитектура проекта

Предлагаемая структура:

```text
textseek/
├── __init__.py
├── seek.py
├── specs.py
├── results.py
├── extractors/
│   ├── __init__.py
│   ├── base.py
│   ├── code.py
│   ├── link.py
│   └── regex.py
├── links.py
├── patterns.py
└── errors.py
```

Описание:

| Файл | Назначение |
|---|---|
| `seek.py` | Основной класс `TextSeek` |
| `specs.py` | Спецификации поиска и фабрика `Extract` |
| `results.py` | Объекты результата |
| `extractors/base.py` | Базовый интерфейс extractor-а |
| `extractors/code.py` | Логика поиска кодов |
| `extractors/link.py` | Логика поиска ссылок |
| `extractors/regex.py` | Логика regex-поиска |
| `links.py` | Разбор и нормализация ссылок |
| `patterns.py` | Генерация regex-паттернов |
| `errors.py` | Ошибки библиотеки |

---

## 22. Пример итогового использования

```python
from textseek import TextSeek, Extract

text = """
Hello!

Your confirmation code is A8F3-K2P9.

Magic link:
https://example.com/auth/magic?token=real-token-123&email=test@example.com
"""

seek = TextSeek(text)

code = seek.extract_one(
    Extract.code(
        min_length=8,
        max_length=12,
        digits=True,
        alphabet=True,
        symbols=True,
        near="confirmation code",
    )
)

link = seek.extract_one(
    Extract.link(
        sample="https://example.com/auth/magic?token=abc&email=test@example.com"
    )
)

print(code.value)
print(link.value)
print(link.domain)
print(link.path)
print(link.query_params["token"][0])
```

---

## 23. MVP

В первую версию библиотеки обязательно включить:

1. `TextSeek`.
2. `Extract.code`.
3. `Extract.link`.
4. `Extract.regex`.
5. `extract_one`.
6. `extract_first`.
7. `extract_all`.
8. `contains`.
9. `CodeResult`.
10. `LinkResult`.
11. `RegexResult`.
12. Базовые ошибки.
13. Полную типизацию публичного API.
14. Документацию через Mintlify.

---

## 24. Что можно добавить позже

В будущих версиях можно добавить:

- `Extract.email()`;
- `Extract.phone()`;
- `Extract.uuid()`;
- `Extract.jwt()`;
- `Extract.between(start, end)`;
- `Extract.near(label)`;
- `Extract.json_value(path)`;
- `Extract.html_links()`;
- поддержку нормализации HTML;
- scoring найденных совпадений;
- explain/debug режим, почему найдено именно это значение.

---

## 25. Критерии готовности

Библиотека считается готовой для первой версии, если:

1. Можно извлечь цифровой код из текста.
2. Можно извлечь буквенно-цифровой код из текста.
3. Можно извлечь код со спецсимволами.
4. Можно извлечь все ссылки.
5. Ссылки возвращаются объектами, а не строками.
6. У ссылок доступны `domain`, `path`, `query_params`.
7. Можно найти ссылку по примеру.
8. Можно найти произвольный текст через regex.
9. Все публичные методы типизированы.
10. Ошибки библиотеки документированы.
11. Документация Mintlify содержит quickstart, concepts, usage и api-reference.
12. В README есть минимальный пример использования.
