# Bot Gastos

Bot de Telegram que divide gastos en partes iguales entre amigos y dice quién le debe a quién (minimizando la cantidad de transferencias). Sin base de datos, sin IA, costo $0.

## Uso (solo chat privado)

1. Escribile "hola" (o cualquier mensaje sin números, deberas epeserar 30-45 segundos para que arranque el servidor y reenviar "hola"): el bot pregunta si querés dividir gastos y explica el formato.
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

## Deploy 24/7 gratis (Render)

Es 100% gratis, sin tarjeta. La única contra: si nadie le escribe durante 15 minutos, Render "duerme" el servicio, y el próximo mensaje tarda ~30-50 segundos en responder mientras se despierta (después responde normal). El código detecta solo si está en Render y usa webhook en vez de polling; en tu PC sigue funcionando igual que antes.

### Opcional: evitar que se duerma
Un servicio externo y gratuito como [UptimeRobot](https://uptimerobot.com) puede pingear tu URL de Render cada 5 minutos para mantenerlo despierto. No es necesario, pero si te molesta la demora inicial, es una opción sin costo.

### Alternativas si en algún momento Render deja de servir
PythonAnywhere (gratis, no se duerme, pero su plan free solo permite conectarse a una lista limitada de sitios externos y no está garantizado que `api.telegram.org` esté permitido) u Oracle Cloud Always Free (VM real 24/7 sin dormirse, pero pide tarjeta para verificar identidad, sin cobrar).
