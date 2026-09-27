# Bot Gastos

Bot de Telegram que divide gastos en partes iguales entre amigos y dice quién le debe a quién (minimizando la cantidad de transferencias). Sin base de datos, sin IA, costo $0.

## Uso (solo chat privado)

1. Escribile "hola" (o cualquier mensaje sin números): el bot pregunta si querés dividir gastos y explica el formato.
2. Mandale los datos: nombres separados por coma, un punto y los gastos.

```
Fran, Leon, Octa, Anto. Fran 12000, Anto 3000
```

También funciona con "y" (`Fran, Leon y Octa. Fran 100 y Leon 50`), con saltos de línea y con el formato anterior `/dividir ... | ...`.

Respuesta:

```
Total: $15.000 entre 4 personas

Resumen:
- Fran: puso $12.000 | le toca $3.750
- Leon: puso $0 | le toca $3.750
- Octa: puso $0 | le toca $3.750
- Anto: puso $3.000 | le toca $3.750

Para saldar cuentas:
- Leon le debe $3.750 a Fran
- Octa le debe $3.750 a Fran
- Anto le debe $750 a Fran
```

Reglas: participantes separados por coma, un `|`, y luego gastos `Nombre monto`. Montos válidos: `12000`, `12.000`, `$12.000`, `12.50`. Los nombres no distinguen mayúsculas. También se pueden separar los gastos con saltos de línea. Otros comandos: `/ayuda`, `/id`.

## Guía de puesta en marcha (pasos manuales)

### 1. Crear el bot en Telegram
1. Abrí Telegram y buscá **@BotFather** (el que tiene tilde azul de verificado).
2. Enviale `/newbot`.
3. Elegí un **nombre** (el que se ve, ej. `Dividir Gastos`).
4. Elegí un **username** que termine en `bot` (ej. `dividir_gastos_fran_bot`); debe ser único.
5. BotFather te responde con el **token** (algo como `123456789:AAF...`). Es una contraseña: no lo compartas ni lo subas a GitHub.
6. Opcional: `/setcommands` → elegí tu bot → pegá:
   ```
   dividir - Divide gastos entre amigos
   ayuda - Muestra la ayuda
   id - Muestra tu ID de Telegram
   ```
7. Si querés usarlo en un grupo: `/setprivacy` → tu bot → **Disable**, y agregalo al grupo. (Los comandos `/dividir` funcionan igual con privacidad activada, pero esto evita problemas.)

### 2. Configurar el proyecto en tu PC
En una terminal, dentro de la carpeta del proyecto:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Abrí `.env` y pegá el token en `TELEGRAM_BOT_TOKEN=`.

### 3. Restringir el acceso a vos y tus amigos
1. Iniciá el bot (paso 4) y cada persona le escribe `/id`.
2. Cada uno te pasa su número.
3. En `.env`: `ALLOWED_USER_IDS=111111111,222222222,333333333`
4. Reiniciá el bot (Ctrl+C y volver a correrlo).

Si `ALLOWED_USER_IDS` queda vacío, cualquiera que encuentre el bot puede usarlo.

### 4. Ejecutar
```bash
python run.py
```
El bot responde mientras esa terminal esté abierta (modo polling, gratis y sin servidor).

### 5. Correr los tests
```bash
pip install -r requirements-dev.txt
pytest
```

## Deploy 24/7 gratis (Render)

El bot corre solo, sin que tengas que dejar tu PC prendida. Es 100% gratis, sin tarjeta. La única contra: si nadie le escribe durante 15 minutos, Render "duerme" el servicio, y el próximo mensaje tarda ~30-50 segundos en responder mientras se despierta (después responde normal). El código detecta solo si está en Render y usa webhook en vez de polling; en tu PC sigue funcionando igual que antes.

### 1. Subir el proyecto a GitHub
Necesitás una cuenta de GitHub (gratis) y el proyecto en un repositorio. El `.env` con tu token **no se sube** (ya está en `.gitignore`).

```bash
git init
git add .
git commit -m "Bot de gastos"
```

Creá un repositorio nuevo en GitHub (podés dejarlo privado) y seguí las instrucciones que te da GitHub para el `git remote add` y `git push`.

### 2. Crear la cuenta en Render
1. Entrá a [render.com](https://render.com) y registrate (podés usar tu cuenta de GitHub).
2. **New +** → **Blueprint**.
3. Elegí el repositorio del bot. Render detecta el archivo `render.yaml` de este proyecto y configura el servicio solo.
4. Te va a pedir los valores de `TELEGRAM_BOT_TOKEN` y `ALLOWED_USER_IDS`: completalos con tu token de @BotFather y tus IDs (o dejá `ALLOWED_USER_IDS` vacío para uso público).
5. **Apply** / **Create**. Render instala las dependencias y arranca el bot.

### 3. Verificar
1. En el dashboard de Render, mirá los **Logs** del servicio: tiene que aparecer `Bot iniciado (webhook) en https://...`.
2. Escribile "hola" al bot en Telegram. Si tardó mucho la primera vez, es el servicio despertándose; el resto de mensajes van a ser rápidos.

### 4. Actualizar el bot más adelante
Cada vez que quieras subir un cambio de código:
```bash
git add .
git commit -m "Descripcion del cambio"
git push
```
Render redespliega solo al detectar el push.

### Opcional: evitar que se duerma
Un servicio externo y gratuito como [UptimeRobot](https://uptimerobot.com) puede pingear tu URL de Render cada 5 minutos para mantenerlo despierto. No es necesario, pero si te molesta la demora inicial, es una opción sin costo.

### Alternativas si en algún momento Render deja de servir
PythonAnywhere (gratis, no se duerme, pero su plan free solo permite conectarse a una lista limitada de sitios externos y no está garantizado que `api.telegram.org` esté permitido) u Oracle Cloud Always Free (VM real 24/7 sin dormirse, pero pide tarjeta para verificar identidad, sin cobrar).

## Estructura
```
bot_gastos/splitter.py    # lógica pura de división (centavos enteros)
bot_gastos/parser.py      # parseo del comando
bot_gastos/formatting.py  # formato de la respuesta
bot_gastos/bot.py         # handlers de Telegram
tests/                    # pytest
run.py                    # punto de entrada
```
