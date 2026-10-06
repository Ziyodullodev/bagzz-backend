# bagzz — Backend

Django REST API and Telegram bot for the bagzz handbag shop (Telegram Mini App). Frontend: `../bagzz-shop`.

- Sign-in with Telegram WebApp `initData` (HMAC check against the bot token), JWT for API calls.
- Catalogue of bags with categories, brands, stock, featured items, filtering, search and sorting.
- Server-side wishlist and cart per Telegram user.
- Checkout that reserves stock in a transaction, order history and cancel.
- Telegram messages to the customer and an admin chat on new orders and status changes.
- Django admin for categories, brands, products, stock and orders.
- Telegram bot over a webhook: `/start`, `/shop`, `/orders`, `/help` in Uzbek and English, with Mini App buttons.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env            # then set DJANGO_SECRET_KEY and TELEGRAM_BOT_TOKEN
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_catalog      # demo categories, brands and bags
.venv/bin/python manage.py createsuperuser   # for /admin
.venv/bin/python manage.py runserver 127.0.0.1:8020
```

Run the tests:

```bash
.venv/bin/python manage.py test apps
```

## Environment

See `.env.example`. The important ones:

| Variable | Purpose |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather. Used to verify `initData` and send messages. |
| `TELEGRAM_ADMIN_CHAT_ID` | Chat or group that receives new order alerts. Optional. |
| `TELEGRAM_DEV_AUTH` | `true` lets the app run in a normal browser as a dev user. Only works with `DJANGO_DEBUG=true`. |
| `FRONTEND_DIST` | Path to the built frontend; Django then serves the Mini App on the same domain. |
| `SHIPPING_FEE` | Flat delivery fee added to every order. |
| `POSTGRES_DB` … | Set to use PostgreSQL instead of SQLite (install `psycopg[binary]`). |

## API

All endpoints are under `/api/`. Send `Authorization: Bearer <access>` except where marked public.

| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/telegram/` | Public. `{init_data}` → `{access, refresh, user}` |
| POST | `/auth/refresh/` | `{refresh}` → new access token |
| GET, PATCH | `/auth/me/` | Current user, `phone` is editable |
| GET | `/categories/` | Public. Active categories with `product_count` and a `cover` product |
| GET | `/brands/` | Public. Active brands |
| GET | `/products/` | Public. `?category=tote-bags&brand=&featured=true&in_stock=true&search=black&ordering=price\|-price\|-rating\|-sold_count\|-created_at&min_price=&max_price=` |
| GET | `/products/{slug}/` | Public. Detail with `description`, `material_care`, `stock` |
| GET, POST | `/favorites/` | List wishlist, add `{product: slug}` |
| DELETE | `/favorites/{slug}/` | Remove from wishlist |
| GET, DELETE | `/cart/` | Cart with totals, or clear it |
| POST | `/cart/items/` | `{product, quantity?}` add or increment |
| PUT | `/cart/items/` | `{product, quantity}` set exact quantity, `0` removes |
| PATCH, DELETE | `/cart/items/{id}/` | Edit or remove a line |
| GET, POST | `/orders/` | History, or checkout `{phone, address, full_name?, comment?, payment_method: cash\|card}` |
| GET | `/orders/{id}/` | Order detail |
| POST | `/orders/{id}/cancel/` | Cancel a `new` order and return stock |

Checkout answers `409` when a bag ran out and `400` when the cart is empty.

Products without a photo carry a `look` (`shape`: `satchel` / `top_handle` / `tote`, plus `body`, `trim`,
`handle`, `hardware` colours) that the app uses to draw a placeholder bag. `material_care` is plain text:
lines starting with `- ` are shown as a list.

## Telegram bot

The bot runs on a webhook at `/api/telegram/webhook/`, so no extra process is needed.
Telegram signs every call with `TELEGRAM_WEBHOOK_SECRET`; requests without it get `403`.

```bash
.venv/bin/python manage.py setup_bot
```

This registers the webhook, the command list (English and Uzbek) and the Mini App menu button.
Run it again after changing `WEBAPP_URL` or the bot token.

## Deploy

See [deploy/PYTHONANYWHERE.md](deploy/PYTHONANYWHERE.md). One PythonAnywhere web app serves the API, the admin and the Mini App over HTTPS.
