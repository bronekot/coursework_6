# Сервис email-рассылок

   git clone https://github.com/your-username/email-mailing-service.git

```

2. Установите зависимости:
```

   poetry install

```

3. Настройте переменные окружения в файле `.env`:
```

   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   EMAIL_HOST=your_smtp_host
   EMAIL_PORT=your_smtp_port
   EMAIL_HOST_USER=your_email
   EMAIL_HOST_PASSWORD=your_email_password
   EMAIL_USE_TLS=True

```

4. Выполните миграции:
```

   python manage.py migrate

```

5. Создайте суперпользователя:
```

   python manage.py createsuperuser

```

6. Запустите сервер:
```

   python manage.py runserver

```

## Использование

1. Зарегистрируйтесь или войдите в систему.
2. Подтвердите свой email (требуется для создания рассылок).
3. Добавьте клиентов в систему.
4. Создайте шаблоны сообщений.
5. Настройте рассылку, выбрав получателей, шаблон и периодичность.
6. Отключайте рассылки в личном кабинете.

## Разработка

Для запуска тестов используйте команду:
```

python manage.py test

```

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле `LICENSE`.

## Контакты

Если у вас есть вопросы или предложения, пожалуйста, создайте issue в этом репозитории.
```

Это Django-приложение для управления email-рассылками, разработанное для эффективной коммуникации с клиентами.

`<span><span class="token title">`##`<span class="token title">` Основные функции `<span>`

`<span><span class="token list">`-`<span>` Управление клиентами: добавление, просмотр и редактирование контактов.
`<span><span class="token list">`-`<span>` Создание рассылок: настройка периодичности и выбор получателей.
`<span><span class="token list">`-`<span>` Шаблоны сообщений: создание и использование готовых шаблонов для рассылок.
`<span><span class="token list">`-`<span>` Статистика: отслеживание эффективности рассылок.
`<span><span class="token list">`-`<span>` Блог: публикация и просмотр статей, связанных с email-маркетингом.

`<span><span class="token title">`##`<span class="token title">` Технологии `<span>`

`<span><span class="token list">`-`<span>` Python 3.x
`<span><span class="token list">`-`<span>` Django 5.1
`<span><span class="token list">`-`<span>` PostgreSQL
`<span><span class="token list">`-`<span>` Bootstrap 5
`<span><span class="token list">`-`<span>` Django APScheduler для выполнения периодических задач

`<span><span class="token title">`##`<span class="token title">` Установка и запуск `<span>`

<span></span><span class="token list">1.</span><span> Клонируйте репозиторий:</span></code></div></div></div></div></pre>
