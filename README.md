# Web App Template

A web application project template based on Flask(Python).

<!-- MarkdownTOC -->

- [About](#about)
    - [Features](#features)
    - [Dependency](#dependency)
    - [Envionment Variables](#envionment-variables)
    - [Setup Database](#setup-database)
    - [Default Admin User](#default-admin-user)
    - [Run for development](#run-for-development)
    - [Run for production](#run-for-production)
    - [Run for production in supervisord](#run-for-production-in-supervisord)
    - [Update Translation](#update-translation)
    - [License](#license)

<!-- /MarkdownTOC -->

# About

Welcome to Web App Template project (WAT).
This project is aimed to provide the common programming works and let the developers focus on their business logic.

Notice that ths project is NOT a framework or someting else, it's just a semi-finished web app.
Copy the project to your workplace and be free to change any code in the project.

WAT is base on Flask, and of course you can use all the original programming APIs provided by Flask.

## Features

- Basic Authentication
    + Password
    + CAPTCHA (With `Pillow`)
- User Management
    + Add User
    + Edit User (include Resetting Password)
    + Enable / Disable User
    + Search User
- ACL Support
- User Operation Records
    + Search Record
- Multi-Language (With `Flask-Babel`)
    + English
    + Simplified Chinese
    + Traditional Chinese
    + Japanese
- Deploy Ready (With `gunicorn`, `supervisord`)

## Dependency

See `requirements.txt`

## Envionment Variables

|       Name     |                Description                |                Default                 |
|----------------|-------------------------------------------|----------------------------------------|
| ADMIN_EMAIL    | Admin email                               |                                        |
| SECRET_KEY     | Flask secret key                          | `h3bF9paWv9nNfAEo`                     |
| WAT_DB_DEV_URL | Database connection URL                   | `sqlite:///current-path/db-dev.sqlite` |
| WAT_DB_URL     | Database connection URL For Production    | `sqlite:///current-path/db.sqlite`     |
| FLASK_CONFIG   | Config name (`development`, `production`) | `default` (Same to `development`)      |

## Setup Database

```shell
python manage.py initdb
```

## Default Admin User

|     Email      |   Name  | Password |
|----------------|---------|----------|
| `$ADMIN_EMAIL` | `admin` | `admin!` |

## Run for development

```shell
./run-dev.sh
```

## Run for production

```shell
./run-deploy.sh
```

## Run for production in supervisord

```shell
supervisord
```

## Update Translation

```shell
./update-translations.sh
```

## License
[MIT](LICENSE)