# Release checklist

## Product

- [x] Marketing landing и чёткое позиционирование
- [x] Регистрация и вход
- [x] Вопрос → retrieval → ответ → официальный пункт
- [x] Guardrail и безопасный `no_source`
- [x] История вопросов
- [x] Профиль пользователя
- [x] Feedback на ответ
- [x] Адаптивный интерфейс
- [ ] 100 размеченных контрольных вопросов
- [ ] Usability test на 5 людях

## Data

- [x] Официальный источник зафиксирован
- [x] Воспроизводимый sync с ИПС «Әділет»
- [x] Snapshot JSONL с hash и датой редакции
- [ ] Ручная проверка 20 случайных фрагментов двумя участниками

## Engineering

- [x] Django tests и system check
- [x] Frontend production build
- [x] GitHub Actions
- [x] Docker Compose config: PostgreSQL + Django + Nginx
- [ ] Docker image build on a machine with a running Docker daemon
- [x] `.env.example` без секретов
- [ ] Production domain, TLS и секреты
- [ ] Backup PostgreSQL

## Demo

- [x] Четырёхминутный demo script
- [x] Usability protocol
- [ ] Заполненные результаты теста
- [ ] Публичный URL
