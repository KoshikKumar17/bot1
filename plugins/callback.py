import os
from Script import script
from config import Config
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


#buttons
START_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Help', callback_data='help'),
        InlineKeyboardButton('About', callback_data='about')
        ],[
        InlineKeyboardButton('Owner', url='https://t.me/koshikkumar17'),
        InlineKeyboardButton('Made by', url='https://t.me/thekoshik')
        ],[
        InlineKeyboardButton('Close', callback_data='close')
        ]]
    )
HELP_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Back', callback_data='start')
        ]]
    )
ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Back', callback_data='start')
        ]]
    )

A = """{} with id tg://openmessage/?user_id={} used /start command."""

@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_chat_action(enums.ChatAction.TYPING) 
    k = await message.reply_text("**Processing...**", quote=True)
    await k.edit_text(text=script.START_TEXT, reply_markup=START_BUTTONS)
    try:
        await client.send_message(Config.LOGS, A.format(message.from_user.mention, message.from_user.id))
    except Exception as e:
            print(str(e))


@Client.on_callback_query()
async def cb_data(bot, update):
    if update.data == "start":
        await update.message.edit_text(
            text=script.START_TEXT,
            disable_web_page_preview=True,
            reply_markup=START_BUTTONS
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=script.HELP_TEXT,
            disable_web_page_preview=True,
            reply_markup=HELP_BUTTONS
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=script.ABOUT_TEXT,
            disable_web_page_preview=True,
            reply_markup=ABOUT_BUTTONS
        )
    elif update.data == "close":
        await update.message.delete()
