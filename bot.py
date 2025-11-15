import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN no configurado en Render")

ENLACE_ACTIVACION = "https://t.me/Edwarscolmenares"

BIENVENIDA = (
    "IA_REALIST – Servicio de IA Ultra Detallada\n\n"
    "Generamos imágenes, textos, videos y más con *nivel profesional*.\n"
    "Máxima calidad | Detalles reales | Entrega en minutos\n\n"
    "Pagos fáciles con *Telegram Stars*\n\n"
    "Elige tu plan por días:"
)

SERVICIOS = [
    {"nombre": "1 Día", "precio_stars": 250, "detalles": "Acceso rápido por 24h.\n\n• generaciones de IA\n• Resolución HD\n• Soporte básico\n• Ideal para pruebas", "id": "1dia"},
    {"nombre": "3 Días", "precio_stars": 700, "detalles": "Para proyectos cortos.\n\n• generaciones\n• Resolución Full HD\n• Videos cortos incluidos\n• Soporte prioritario", "id": "3dias"},
    {"nombre": "7 Días", "precio_stars": 1500, "detalles": "Acceso completo por una semana.\n\n• Generaciones ilimitadas\n• 4K + videos avanzados\n• API personalizada\n• Soporte 1:1 + garantía", "id": "7dias"}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Ver Planes", callback_data='lista')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(BIENVENIDA, reply_markup=reply_markup, parse_mode='Markdown')

async def lista_servicios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"{s['nombre']} → {s['precio_stars']} Stars", callback_data=f"ver_{s['id']}")] for s in SERVICIOS]
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='inicio')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Selecciona tu plan:", reply_markup=reply_markup)

async def ver_detalle(update: Update, context: ContextTypes.DEFAULT_TYPE):  # ← CORREGIDO
    query = update.callback_query
    await query.answer()
    servicio_id = query.data.split("_")[1]
    s = next(x for x in SERVICIOS if x["id"] == servicio_id)
    texto = f"*{s['nombre']}* → {s['precio_stars']} Stars\n\n{s['detalles']}\n\nPago seguro con Telegram Stars\nAcceso inmediato después del pago"
    keyboard = [
        [InlineKeyboardButton("Pagar con Stars", callback_data=f"pagar_{s['id']}")],
        [InlineKeyboardButton("Volver", callback_data='lista')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(texto, reply_markup=reply_markup, parse_mode='Markdown')

async def pagar_servicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    servicio_id = query.data.split("_")[1]
    s = next(x for x in SERVICIOS if x["id"] == servicio_id)

    await context.bot.send_invoice(
        chat_id=query.from_user.id,
        title=f"Acceso IA_REALIST - {s['nombre']}",
        description=s['detalles'],
        payload=f"iarealist-{s['id']}-{query.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Acceso", s['precio_stars'])],
        start_parameter="iarealist-payment"
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=query.invoice_payload.startswith('iarealist-'), error_message="Pago no válido.")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    plan = payment.invoice_payload.split("-")[1]
    nombres = {"1dia": "1 Día", "3dias": "3 Días", "7dias": "7 Días"}
    texto = (
        "*¡Pago exitoso!* ✅\n\n"
        f"Has comprado: *{nombres.get(plan, plan)}* ({payment.total_amount} Stars)\n\n"
        f"*Acceso listo:*\n[Activar IA_REALIST]({ENLACE_ACTIVACION})\n\n"
        "¡Empieza a crear!"
    )
    await update.message.reply_text(texto, parse_mode='Markdown', disable_web_page_preview=True)

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Ver Planes", callback_data='lista')]]
    await query.edit_message_text(BIENVENIDA, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

def main():
    print("IA_REALIST Bot - Iniciando en Render...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lista_servicios, pattern='lista'))
    app.add_handler(CallbackQueryHandler(ver_detalle, pattern='^ver_'))
    app.add_handler(CallbackQueryHandler(pagar_servicio, pattern='^pagar_'))
    app.add_handler(CallbackQueryHandler(inicio, pattern='inicio'))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    print("Bot 24/7 ACTIVO - Pagos con Stars ON")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
