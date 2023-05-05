from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, constants, error
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import tempmail
import config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"""
Hello {update.effective_user.first_name}
Welcome to @FakeMaiilRobot.
""", reply_markup=buttons)


async def query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query: CallbackQuery = update.callback_query.data
    chat_id = update.callback_query.from_user.id
    try:

        # if email not exist
        if not context.user_data:
            if query == "generate":
                email = tempmail.generate()
                context.user_data["email"] = email
                await update.callback_query.edit_message_text(text=f"__**Your Temporary E-mail**__ : `{email}`", reply_markup=buttons, parse_mode=constants.ParseMode.MARKDOWN)
            else:
                await update.callback_query.edit_message_text(text="You Need to Generate an email", reply_markup=buttons)

        # elif user have an email
        elif context.user_data:
            email = context.user_data["email"]
            username, domain = email.split("@")

            if query == "refresh":
                try:
                    email_id, email_from, email_subject, email_date, email_text, files = tempmail.refresh(
                        username, domain)
                    files_text = "\n".join(files) if files else ""
                    text = f"""
➖➖➖➖➖➖➖➖➖
From: <{email_from}>
To: <{email}>
Date: {email_date}
Attachments: {files_text}
➖➖➖➖➖➖➖➖➖
Subject: {email_subject}
➖➖➖➖➖➖➖➖➖
{email_text}
"""
                    await context.bot.send_message(chat_id, text, disable_web_page_preview=True)

                except ValueError:
                    await update.callback_query.edit_message_text(text="No Messages Were Received..", parse_mode=constants.ParseMode.MARKDOWN, reply_markup=buttons)

            elif query == "my_email":
                await update.callback_query.edit_message_text(text=f"__**Your Temporary E-mail**__ : `{email}`", parse_mode=constants.ParseMode.MARKDOWN, reply_markup=buttons)

            elif query == "close":
                context.user_data.clear()
                await update.callback_query.edit_message_text(text="Session Closed✅\n/start")

            else:
                await update.callback_query.edit_message_text(text="To Change The Email, You Must Close The Session First", reply_markup=buttons, parse_mode=constants.ParseMode.MARKDOWN)

    except error.BadRequest:
        pass

    except (tempmail.requests.exceptions.ProxyError, tempmail.requests.exceptions.Timeout):
        await update.callback_query.edit_message_text(text="Service Unavailable Please Try Again Later", reply_markup=buttons)

if __name__ == "__main__":

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton('Generate📥', callback_data='generate')],
        [InlineKeyboardButton('Refresh🔄', callback_data='refresh'),
         InlineKeyboardButton('My Email📬', callback_data='my_email')],
        [InlineKeyboardButton('Close🚫', callback_data='close')]
    ])

    app = ApplicationBuilder().token(config.token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(query_handler))

    print("Bot is Alive")
    app.run_polling()
