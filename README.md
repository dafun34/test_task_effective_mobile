# test_task_effective_mobile

Тестовое задание для компании Effective Mobile.

## Оглавление

- [Цель проекта](#цель-проекта)
- [Stack](#stack)
- [Система разграничения прав доступа](#система-разграничения-прав-доступа)
- [Аутентификация](#аутентификация)
- [Logout flow](#logout-flow)
- [Soft delete пользователей](#soft-delete-пользователей)
- [Авторизация](#авторизация)
  - [Основные сущности](#основные-сущности)
    - [Roles](#roles)
    - [Business Elements](#business-elements)
    - [Access Rules](#access-rules)
- [Логика owner/all permissions](#логика-ownerall-permissions)
- [Пример работы системы](#пример-работы-системы)
- [Проверка доступа](#проверка-доступа)
- [Архитектура проекта](#архитектура-проекта)
- [Основные endpoint](#основные-endpoint)
  - [Authentication](#authentication)
  - [Users](#users)
  - [Posts](#posts)
  - [Access rules](#access-rules-1)
- [Тестовые данные](#тестовые-данные)
- [Запуск приложения](#запуск-приложения)
- [Заполнение базы данных](#заполнение-базы-данных)
- [Тестовые пользователи](#тестовые-пользователи)
- [Примеры проверки permissions](#примеры-проверки-permissions)
  - [Чтение постов](#чтение-постов)
  - [Изменение постов](#изменение-постов)
- [Работа с ресурсом users](#работа-с-ресурсом-users)
- [Пример динамического изменения permissions](#пример-динамического-изменения-permissions)

---

## Цель проекта

Реализовать backend-приложение с собственной системой:

* аутентификации;
* авторизации;
* разграничения прав доступа к ресурсам.

В рамках проекта реализованы:

* JWT-аутентификация;
* logout с blacklist revoked tokens;
* soft delete пользователей;
* динамическая RBAC-система;
* разграничение доступа к собственным и чужим объектам;
* API для управления permissions;
* CRUD для тестовых бизнес-ресурсов (`users`, `posts`).
* seed-механизм для заполнения базы данных тестовыми данными.

---

# Stack

* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* Alembic
* JWT (`python-jose`)
* bcrypt / passlib
* Docker

---

# Система разграничения прав доступа

В проекте реализована собственная система аутентификации и авторизации на основе JWT и RBAC (Role-Based Access Control).

---

# Аутентификация

Аутентификация реализована с использованием JWT-токенов.

После успешного login пользователю выдается access token:

```http
Authorization: Bearer <token>
```

Токен содержит:

* `sub` — идентификатор пользователя
* `exp` — время истечения токена

Для хранения паролей используется хеширование через bcrypt.

При каждом запросе система:

1. извлекает JWT из Authorization header;
2. валидирует токен;
3. определяет пользователя, выполнившего запрос, через зависимость `current_user`.

Если пользователь не определен или токен невалиден — возвращается `401 Unauthorized`.

---

# Logout flow

В проекте реализован logout с отзывом JWT токена через blacklist-механизм.

Пользователь отправляет запрос:

```http
POST /logout
Authorization: Bearer <access_token>
```

Система:

1. извлекает JWT;
2. декодирует токен;
3. получает `exp`;
4. сохраняет токен в таблицу `revoked_tokens`.

При каждом защищенном запросе система дополнительно проверяет, не находится ли токен в blacklist.

Если токен был отозван, сервер возвращает:

```http
401 Unauthorized
```

```json
{
  "detail": "Token revoked, please log in"
}
```

Таким образом logout делает JWT недействительным до истечения срока его жизни.

---

# Soft delete пользователей

Удаление пользователя реализовано как soft delete.

При удалении аккаунта:

```text
is_active = False
```

Пользователь:

* остается в базе данных;
* больше не может выполнять login;
* не может обращаться к защищенным endpoint.

Если пользователь пытается использовать старый JWT после удаления аккаунта, система возвращает:

```http
401 Unauthorized
```

```json
{
  "detail": "User is inactive"
}
```

---

# Авторизация

Для авторизации реализована собственная RBAC-система.

## Основные сущности

### Roles

Роли пользователей:

```text
admin
user
```

Каждый пользователь имеет одну роль.

---

### Business Elements

Business elements — это ресурсы приложения, к которым применяется система доступа.

На данный момент реализованы следующие ресурсы:

```text
users
posts
```

---

### Access Rules

Права доступа хранятся в таблице `access_role_rules`.

Каждое правило связывает:

* роль;
* ресурс;
* набор разрешений.

Поддерживаются следующие permissions:

```text
read_permission
read_all_permission

create_permission

update_permission
update_all_permission

delete_permission
delete_all_permission
```

---

# Логика owner/all permissions

Система разделяет доступ:

* к собственным объектам;
* ко всем объектам.

Например:

```text
update_permission
```

разрешает изменять только собственные объекты.

```text
update_all_permission
```

разрешает изменять любые объекты.

---

# Пример работы системы

Обычный пользователь (`user`):

```text
posts:
- create_permission = true
- read_permission = true
- update_permission = true
- delete_permission = true

- read_all_permission = false
- update_all_permission = false
- delete_all_permission = false
```

Следовательно:

* пользователь может создавать посты;
* может видеть и изменять только свои посты;
* не может изменять чужие посты.

Администратор (`admin`) имеет полный доступ ко всем ресурсам.

---

# Проверка доступа

Перед выполнением действий система:

1. определяет текущего пользователя;
2. получает access rule для роли и ресурса;
3. проверяет соответствующее permission;
4. дополнительно проверяет ownership ресурса.

Если доступ запрещен — возвращается `403 Forbidden`.

---

# Архитектура проекта

Проект разделен на слои:

```text
repositories/            — слой работы с БД
services/                — бизнес-логика приложения
services/permissions.py  — проверка RBAC permissions
```

---

# Основные endpoint

## Authentication

```text
POST /register
POST /token
POST /logout
```

## Users

```text
GET    /users/me
PATCH  /users/me
DELETE /users/me

PATCH  /users/{user_id}
DELETE /users/{user_id}
```

## Posts

```text
POST   /posts
GET    /posts
GET    /posts/{id}
PATCH  /posts/{id}
DELETE /posts/{id}
```

## Access rules

```text
GET   /access-rules
PATCH /access-rules/{id}
```

---

# Тестовые данные

Для демонстрации работы системы реализован seed-механизм, создающий:

* роли;
* ресурсы;
* правила доступа;
* тестовых пользователей;
* тестовые посты.

---

# Запуск приложения

```bash
docker compose up --build
```

---

# Заполнение базы данных

```bash
docker compose exec -it app python app/seed/run.py
```

---

# Тестовые пользователи

```text
admin@example.com / admin123
user1@example.com / user123
user2@example.com / user123
```

---

# Примеры проверки permissions

## Чтение постов

```text
user1 → GET /posts
должен видеть только User1 posts

user2 → GET /posts
должен видеть только User2 posts

admin → GET /posts
должен видеть все посты
```

---

## Изменение постов

```text
user1 → PUT/PATCH/DELETE своего поста
должно работать

user1 → PUT/PATCH/DELETE чужого поста
должно возвращать 403 Forbidden

admin → PUT/PATCH/DELETE любого поста
должно работать
```

Да, стоит.
Сейчас README отлично показывает RBAC на `posts`, но не показывает, что система одинаково работает и для `users`.

Я бы добавил короткий блок после “Изменение постов”.

---

# Работа с ресурсом users

Система разграничения доступа одинаково применяется и к ресурсу `users`.

Обычный пользователь может:

```text
GET    /users/me
PATCH  /users/me
DELETE /users/me
```

То есть работать только со своим профилем.

---

Попытка изменить или удалить чужого пользователя:

```text
PATCH  /users/{other_user_id}
DELETE /users/{other_user_id}
```

приводит к:

```http
403 Forbidden
```

так как для роли `user`:

```text
update_all_permission = false
delete_all_permission = false
```

---

Администратор (`admin`) имеет:

```text
update_all_permission = true
delete_all_permission = true
```

поэтому может изменять и удалять любых пользователей.


---

# Пример динамического изменения permissions

## 1. Получение списка правил

Администратор получает список access rules:

```http
GET /access-rules
```

Ответ:

```json
[
  {
    "id": 4,
    "role": {
      "name": "user"
    },
    "element": {
      "name": "posts"
    },
    "create_permission": true
  }
]
```

Из ответа администратор определяет идентификатор нужного правила (`id = 4`).

---

## 2. Изменение permission

Администратор отключает создание постов для роли `user`:

```http
PATCH /access-rules/4
```

```json
{
  "create_permission": false
}
```

---

## 3. Проверка permissions

После изменения правила пользователь пытается создать пост:

```http
POST /posts
```

Система:

1. определяет пользователя по JWT;
2. получает access rule для роли `user` и ресурса `posts`;
3. проверяет `create_permission`.

Так как permission отключен:

```text
create_permission = false
```

система возвращает:

```http
403 Forbidden
```

```json
{
  "detail": "Not enough permissions"
}
```

Таким образом администратор может динамически управлять правами доступа без изменения кода приложения.
