# Foodgram - «Продуктовый помощник»

Foodgram, «Продуктовый помощник» - онлайн-сервис и API для него.

## Описание

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Использованные технологии

* Python 3.9
* Django 3.2.14
* Django Rest Framework 3.12.4
* Simple-JWT 4.8.0
* Docker 20.10
* Nginx 1.18

## Шаблон наполнения env-файла

### Создайте файл окружения <./backend/.env> с параметрами:

```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY=<Django SECRET_KEY>
```

## Запуск проекта

### Клонировать репозиторий и перейти в него в командной строке:

```python
git@github.com:Rkuznecov17/foodgram-project-react.git
cd foodgram-project-react/backend/foodgram
```

### Перейти в директорию infra/ и собрать docker-compose:

```python
cd infra/
sudo docker-compose up -d --build
```

### Запустить docker-compose:

```python
docker-compose up
```

## Применить миграции:

```python
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Создать суперпользователя:

```python
docker-compose exec web python manage.py createsuperuser
```

### Cобрать статические файлы::

```python
docker-compose exec web python manage.py collectstatic --no-input
```

### Заполнение базы данными:

```python
docker-compose exec web python manage.py import_ingredients
```

## Автор

Студент 38 когорты Факультета Бэкэнд-разработки, Яндекс.Практикум:

* Федченко Рома
