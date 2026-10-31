# AGENTS.md

This file provides guidance to agents working with code in this repository.

## Что это

Отдельный веб-прототип **меню новой игры на Godot — футбольного симулятора**: главное меню, выбор
команды и настройка составов. Задача — быстро перебирать UX на Svelte 5 + Vite, а готовые экраны и
правила переносить в Godot-игру. Это не карьерный режим: сервер отдаёт только канон (страны, лиги,
клубы, игроки, формы), без сейвов, матчей и симуляции.

**Функциональный ориентир — меню `../GameplayFootball-of_port` (ветка `of_port`):** главное меню,
настройки, выбор сторон и команд, параметры матча, план игры, лига, сеть и внутриигровые меню/HUD.
Перенимаем сценарии и набор экранов, но **не визуальный язык**: у новой игры собственная графика,
типографика и компоновка. Полный инвентарь — `docs/wiki/функционал-меню.md`.

Проект вырос из `../gf-career-prototype`: оттуда скопированы канон, данные и каркас дизайн-правил.
Кодовая база намеренно маленькая — не тащить сюда карьерные подсистемы.

**Актуальная картина проекта живёт в вики: `docs/wiki/index.md` — начинать оттуда.** Этот файл —
только то, что сломаешь, не зная, где посмотреть.

## Ядро архитектуры

- Сервер — `server.py` (FastAPI, порт 8766): read-only канон из `canon.db`
  (`/api/meta`, `/api/countries`, `/api/leagues`, `/api/clubs`, `/api/players`) и статика
  `/raster`. Моков нет.
- Клиент — `web/` (Svelte 5 + Vite, dev на 5174): заготовка главного меню, выбора команды и
  составов. Стили — `web/src/app.css`; UI сверяется с Figma (ссылка ниже).
- Данные — `data/json/` (экспорт из transfermarkt), `data/raster/` (лица игроков, эмблемы, флаги,
  формы клубов), `canon.db` и `ratings_output.json` для пересборки. Пути к фото шаблонные:
  `/raster/{players_faces|players_faces_cutout|teams_emblems|teams_flags|country_flags|leagues|teams_kits}/…`.

## Сборка / запуск

```bash
pip install -r requirements.txt
python scripts/build_canon_db.py   # пересборка canon.db из data/json + ratings_output.json
cd web && npm install && npm run build
cd .. && python server.py          # FastAPI + собранный Svelte на :8766
python -m pytest                   # тесты канона и API
```

Для разработки UI: `cd web && npm run dev` (Vite на :5174, проксирует `/api` и `/raster` на :8766).

## Устройство вики

- `docs/wiki/` — **текущее состояние**, одна страница на подсистему, кросс-ссылки вида
  `[[имя-страницы]]`, каталог в `docs/wiki/index.md`. Обновляй страницы после правки кода.
- `docs/wiki/глоссарий.md` — имена предметной области. `CONTEXT.md` в корне — только указатель.
- `log.md` (корень) — append-only хронология. Записи `## [YYYY-MM-DD] тип | описание`.

**Правило: после любого содержательного изменения обнови соответствующую страницу вики — не
создавай новый датированный документ.**

## Workflow

- Код и комментарии — на английском; вики и этот файл — на русском.
- Git: комментарии коммитов на английском, осмысленный subject.
- Хуки `.agent/hooks/` + плагин `.opencode/plugins/wiki.js` поддерживают контур вики механически:
  оглавление на старте сессии, подсказка «прочитай страницу» по пути правимого файла, stop-проверка.
  Карта «файл → страница» — в `wiki-hint.sh`.

## UI/UX: золотые правила

- **Визуальный язык — собственный, не из `of_port` и не из карьерного прототипа.** Зафиксирован в
  `docs/wiki/визуальный-стиль.md`: светлые плитки на размытом стадионе, инверсия при выборе, два
  акцента с разными ролями, острые углы без бордеров. Зелёно-лаймовая палитра
  `gf-career-prototype` — больше не источник стиля. Карьерный Figma
  (https://www.figma.com/design/sFScRV2E8CycOIf6qW2WQf/Untitled) — референс компоновки и
  взаимодействий, а не визуальной правды.
- **Один фокус на экран.** Основное управление — геймпад, как в EA FC. На экране всегда ровно один
  выбранный/сфокусированный элемент; остальные — контекст, без собственных highlight-состояний.
- **Hover = selected.** У элементов нет отдельного hover-состояния: наведение мыши переводит тот же
  единственный фокус/selected, что D-pad или стрелки. Визуальные состояния — только `default`,
  `selected`, `disabled`.
- **Никаких россыпей мелких кнопок.** Действия — крупные вертикальные элементы. Мелкие
  горизонтальные кнопки допустимы только в нижней легенде управления.
- **Стиль — диванно-телевизионный:** светлые плитки на размытом стадионе, острые углы и плотные швы
  вместо бордеров, крупная капсовая типографика. Элементы должны читаться с дивана.
- **Выбор = полная инверсия заливки.** Светлая плитка становится тёмно-индиго, заголовок — лаймовым.
  Дополнительно плитка слегка приподнимается: `scale` ~1.008 и сдвиг на 6px в сторону своего края
  экрана. Магента — служебный акцент, лайм — только «ты сейчас здесь».
- **Скролл только внутри списков/виджетов.** Страница не скроллится: контент экрана всегда
  помещается в viewport, длинные списки и запасные скроллятся внутри своих панелей.
- **Меню — сверху табами**, переключение `L1`/`R1`; не боковой сайдбар. В подменю табы скрываются:
  вместо них — путь «раздел › подраздел › …», выход `Esc`.
- **Нижняя легенда управления** показывает подсказки для **последнего введённого устройства**
  (геймпад: `A` — ввод, `B` — назад, `L1/R1` — табы; клавиатура: `Enter`, `Esc`, стрелки).
- **Выбор — как в EA FC:** крупный центральный объект (клуб/игрок) + панель деталей, переход
  `A`/`B`, а не три конкурирующих списка.

## Working principles

## 1. Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing: state assumptions, ask if uncertain, name what's confusing.

## 2. Simplicity First
Minimum code that solves the problem. Nothing speculative. No features beyond what was asked.

## 3. Surgical Changes
Touch only what you must. Match existing style. When your changes create orphans — remove what
YOUR changes made unused; don't delete pre-existing dead code unless asked.

## 4. Goal-Driven Execution
Define success criteria. Loop until verified. For multi-step tasks, state a brief plan with
verifiable checkpoints.

## Agent skills

### Issue tracker

GitHub Issues in `polite-cat-2001/gf-ui-prototype`, via `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context. See `docs/agents/domain.md`.
