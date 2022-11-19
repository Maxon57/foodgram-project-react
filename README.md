# Foodgram_project

***
<details>
    <summary style="font-size: 16pt; font-weight: bold">Описание</summary>

[Foodgram](http://food-gram.online/signin): сайт, на котором пользователи могут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Сервис «Список покупок» позволит пользователям создавать список продуктов, 
которые нужно купить для приготовления выбранных блюд.

Проект использует базу данных PostgreSQL. Проект запускается в трёх контейнерах 
(nginx, PostgreSQL и Django) (контейнер frontend используется лишь для подготовки файлов) 
через docker-compose на сервере. Образ с проектом загружается на Docker Hub.
</details>

***
<details>
    <summary style="font-size: 16pt; font-weight: bold">Технологии</summary>

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=bal)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

</details>

***
<details>
    <summary style="font-size: 16pt; font-weight: bold">Запуск проекта</summary>

1. Скачайте на свою машину репозиторий с помощи команды:
   ```git clone https://github.com/Maxon57/foodgram-project-react.git```
2. Перейдите в директорию ./infra с помощи команды:
    ```cd infra```
3. Создайте файл .env и в нем пропишите:
    ```
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=<Имя БД>
    POSTGRES_USER=<Имя пользователя>
    POSTGRES_PASSWORD=<Пароль>
    DB_HOST=<Хост>
    DB_PORT=<Порт>
   ```
4. Выполните команду для создания и запуска контейнеров.
    ```
   docker compose up -d --build
   ```
5. В контейнере foodgram_backend выполните миграции, создайте суперпользователя и соберите статику.
    ```
    docker compose exec foodgram_backend python manage.py migrate
    docker compose exec foodgram_backend python manage.py createsuperuser
    docker compose exec foodgram_backend python manage.py collectstatic --no-input 
   ```
6. Загрузите в бд ингредиенты и теги командой ниже.
    ```
    docker compose exec foodgram_backend python test_data.py
   ```
7. Ниже представлены доступные адреса проекта:
   
    * http://localhost/ - главная страница сайта;
    * http://localhost/admin/ - админ панель;
    * http://localhost/api/docs/ - документация к API

> P.S. Возможно, что сайт временно не работает. Для этого свяжись со мной, чтобы я включил сервер

</details>

## Автор
[Максим Игнатов](https://github.com/Maxon57)
