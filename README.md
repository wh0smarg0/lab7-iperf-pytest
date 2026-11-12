# Automated Network Testing with Pytest and iperf

**Лабораторна робота №7 — Частина 2. Автоматизація тестування**

## Опис проєкту

Проєкт реалізує автоматизоване тестування пропускної здатності TCP-з'єднання між двома комп'ютерами за допомогою **iperf2**, **Pytest**, **Paramiko** та **subprocess**.

Автоматизація забезпечує:

- Віддалений запуск iperf-сервера на Windows через SSH.
- Генерацію TCP-трафіку з Ubuntu протягом 10 секунд.
- Отримання та обробку результатів вимірювання.
- Перевірку обсягу переданих даних (Transfer) і пропускної здатності (Bandwidth).
- Параметризоване та негативне тестування.
- Автоматичне завершення роботи сервера після тестування.

## Тестове середовище

| Компонент | Конфігурація |
|---|---|
| Клієнт | Ubuntu 24.04 (VirtualBox) |
| Сервер | Windows |
| IP клієнта | 192.168.100.1 |
| IP сервера | 192.168.100.100 |
| Мережевий протокол | TCP |
| Порт iperf | 5001 |
| SSH | OpenSSH, порт 22 |
| Python | 3.12 |
| Тестовий фреймворк | Pytest |
| SSH-бібліотека | Paramiko |
| Генератор трафіку | iperf2 2.1.9 |

## Структура проєкту

```text
lab7-iperf-pytest/
|── check_filter.py
|── check_parser.py
|── check_ssh.py
├── conftest.py
├── test_iperf.py
├── parser.py
├── client.py
├── test_negative.py
├── requirements.txt
├── .gitignore
└── README.md
```

**Призначення файлів:**

- `conftest.py` — фікстури Pytest для запуску сервера, генерації трафіку та завершення тестування.
- `test_iperf.py` — автоматизовані перевірки Transfer і Bandwidth.
- `parser.py` — обробка текстового виводу iperf.
- `client.py` — допоміжні функції для клієнта.
- `check_ssh.py` — перевірка SSH-з'єднання.
- `requirements.txt` — Python-залежності проєкту.

## Встановлення та налаштування

### 1. Клонування репозиторію

```bash
git clone https://github.com/wh0smarg0/lab7-iperf-pytest.git
cd lab7-iperf-pytest
```

### 2. Створення віртуального середовища

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Встановлення залежностей

```bash
pip install -r requirements.txt
```

На Ubuntu також необхідно встановити iperf2:

```bash
sudo apt update
sudo apt install iperf
```

### 4. Налаштування Windows-сервера

На Windows необхідно:

1. Установити iperf2 та OpenSSH Server.
2. Переконатися, що SSH-підключення доступне на порту 22.
3. Дозволити вхідні TCP-з'єднання на порт 5001.
4. Створити завдання Windows Task Scheduler з назвою `LabIperfServer`, яке запускає `C:\iperf\iperf.exe -s -p 5001` незалежно від SSH-сесії.

Для перевірки доступності сервера з Ubuntu:

```bash
ping -c 4 192.168.100.100
nc -zv -w 3 192.168.100.100 22
```

### 5. Налаштування змінних середовища

```bash
export IPERF_HOST="192.168.100.100"
export IPERF_SSH_USER="deadport"
read -rsp "SSH password: " IPERF_SSH_PASSWORD
echo
export IPERF_SSH_PASSWORD
```

SSH-пароль не зберігається у вихідному коді та не завантажується до GitHub.

## Запуск автоматизованих тестів

### Усі позитивні перевірки

```bash
python -m pytest test_iperf.py -v -s --tb=short -k "not bitrate_negative"
```

Очікуваний результат:

```text
5 passed, 1 deselected
```

### Перевірка Transfer

```bash
python -m pytest test_iperf.py::test_transfer -v -s --tb=short
```

Критерій успішності: **Transfer > 2 MBytes** для кожного інтервалу.

### Перевірка Bandwidth

```bash
python -m pytest test_iperf.py::test_bitrate -v -s --tb=short
```

Критерій успішності: **Bandwidth > 20 Mbit/s** для кожного інтервалу.

### Параметризоване тестування

```bash
python -m pytest test_iperf.py::test_bitrate_threshold -v -s --tb=short
```

Використовуються такі набори параметрів:

| Поріг (Mbit/s) | Очікуваний результат |
|---|---|
| 20 | True |
| 25 | True |
| 100000 | False |

### Негативне тестування

```bash
python -m pytest test_iperf.py::test_bitrate_negative -v -s --tb=short
```

Для негативного сценарію встановлено поріг 100 Mbit/s. Якщо фактична швидкість не перевищує цей поріг, Pytest формує `AssertionError`.

Це очікувана поведінка навмисно негативного тесту.

## Результати тестування

Під час експериментального тестування отримано такі результати:

| Показник | Результат |
|---|---|
| Тривалість тестування | 10 секунд |
| Кількість інтервалів | 10 |
| Загальний обсяг переданих даних | 111 MBytes |
| Середня пропускна здатність | 92,8 Mbit/s |
| Transfer за інтервал | 11,0–11,4 MBytes |
| Bandwidth за інтервал | 92,3–95,4 Mbit/s |
| Позитивні перевірки | 5 PASSED |
| Негативний сценарій | 1 FAILED (очікувано) |

## Виявлений дефект та його усунення

Під час розроблення автоматизації було виявлено проблему з життєвим циклом віддаленого iperf-сервера.

Початкова реалізація використовувала PowerShell `Start-Process` через SSH. Після завершення SSH-сесії процес iperf не залишався стабільно активним, через що клієнт не міг підключитися до порту 5001.

**Рішення:** запуск сервера перенесено до Windows Task Scheduler.

Для віддаленого запуску використовується команда:

```python
ssh.exec_command("schtasks /Run /TN LabIperfServer")
```

Після внесення змін автоматизовані тести виконувалися успішно.

## Висновок

У межах лабораторної роботи реалізовано автоматизовану систему тестування TCP-з'єднання з використанням Pytest, Paramiko та iperf2.

Розроблено фікстури для керування сервером і клієнтом, парсер результатів вимірювання, позитивні, негативні та параметризовані тести.

Експериментальні результати підтвердили виконання заданих критеріїв: Transfer > 2 MBytes і Bandwidth > 20 Mbit/s.
