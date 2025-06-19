import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from utils.file_parser import parse_credentials_file
from automation.schools_signup import automate_signup

ASK_FOR_FILE = 1
user_signup_count = {}

# Set your token here
TELEGRAM_BOT_TOKEN = "7713625659:AAENH1XKYd7cLscbkKtuXGJ7ITcDzq0h6R4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /signup <number> to begin.")

async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("Usage: /signup <number>")
        return ConversationHandler.END
    signup_count = int(args[0])
    user_signup_count[update.effective_user.id] = signup_count
    await update.message.reply_text("Please send the credentials file (gmail:password per line).")
    return ASK_FOR_FILE

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        await update.message.reply_text("Upload the credentials file.")
        return ASK_FOR_FILE
    file = await document.get_file()
    path = f"/data/data/com.termux/files/home/{document.file_unique_id}.txt"
    await file.download_to_drive(path)
    creds = parse_credentials_file(path)
    signup_count = user_signup_count.get(update.effective_user.id, len(creds))
    creds = creds[:signup_count]
    await update.message.reply_text(f"Processing {len(creds)} accounts. Please wait...")
    success, failed = await automate_signup(creds)
    msg = f"Finished!\n✅ Success: {len(success)}\n❌ Failed: {len(failed)}"
    if failed:
        msg += f"\nFailed emails:\n" + "\n".join(failed)
    await update.message.reply_text(msg)
    try:
        os.remove(path)
    except Exception:
        pass
    return ConversationHandler.END

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("signup", signup_command)],
        states={ASK_FOR_FILE: [MessageHandler(filters.Document.ALL, receive_file)]},
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
