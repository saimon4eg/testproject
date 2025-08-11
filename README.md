# Микросервис для службы международной доставки

Задание:
https://docs.google.com/document/d/1WoL-ysivtlwzbRFwqUfETMSmFOUw9Wpnf0P1ewIW89E/edit?tab=t.0

Для запуска всего проекта необходимо:

1. скопировать файл .env.example в .env:

```bash
cp .env.example .env
```
и заполнить его своими данными если требуется

2. запустить docker-compose:

```bash
docker-compose up -d
```

swagger будет доступен по адресу: http://localhost:8001/backend/api/docs