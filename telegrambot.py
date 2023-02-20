# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import os
import logging
import json
import utility
from functools import wraps
from selenium.common.exceptions import TimeoutException
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, PicklePersistence, CallbackContext

TOKEN = os.environ['TOKEN_BetBot']
PORT = int(os.environ.get('PORT', '8443'))
whitelist = os.environ['whitelist'].split(",")
importo_puntata = 400
rendimento = 4
wait_timer = 10
timer_seconds = 60
last_bet = ''

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO)


def restricted(func):

  @wraps(func)
  async def wrapped(update, context, *args, **kwargs):
    user_id = update.effective_user.id
    if user_id not in whitelist:
      print(f"Unauthorized access denied for {user_id}.")
      return
    return await func(update, context, *args, **kwargs)

  return wrapped


async def wait(context):
  application.job_queue.run_repeating(callback_auto_message,
                                      timer_seconds,
                                      name='get_last_bet')
  return


async def callback_auto_message(context):
  global last_bet
  try:
    temp_last_bet = utility.get_last_bet(rendimento, importo_puntata)
  except Exception as e:
    error = str(type(e)) + "\n" + str(e.args)
    await context.bot.send_message(whitelist[0], error)
    job = context.job_queue.get_jobs_by_name('get_last_bet')
    job[0].schedule_removal()
    context.job_queue.run_once(wait, wait_timer, name='wait')
    return

  tmp_rendimenti = temp_last_bet.replace(" ", "").split("|")
  last_rendimenti = last_bet.replace(" ", "").split("|")
  if (len(tmp_rendimenti) != len(last_rendimenti)):
    last_bet = temp_last_bet
    for chat_id in whitelist:
      await context.bot.send_message(chat_id, text=last_bet)
  else:
    check_presences = [False for i in range(len(tmp_rendimenti))]
    i = 0
    for tmp_rendimento in tmp_rendimenti:
      for last_rendimento in last_rendimenti:
        if (tmp_rendimento == last_rendimento):
          check_presences[i] = True
      i = i + 1

    all_found = True
    for check_presence in check_presences:
      if (not check_presence):
        all_found = False

    if not all_found:
      last_bet = temp_last_bet
      for chat_id in whitelist:
        await context.bot.send_message(chat_id, text=last_bet)
    # else:
    #     for chat_id in whitelist:
    #         await context.bot.send_message(chat_id, text='Duplicato' + last_bet)


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=("Bet", update.effective_chat.id))


@restricted
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  message = update.message.text
  print(message)
  await update.message.reply_text(message)
  return


@restricted
async def getbet(update, context):
  result = utility.get_last_bet(4)
  await update.message.reply_text(result)


if __name__ == '__main__':

  application = ApplicationBuilder().token(TOKEN).build()

  application.add_handler(CommandHandler('start', start))
  application.add_handler(
    MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
  application.add_handler(CommandHandler('getbet', getbet))
  application.job_queue.run_repeating(callback_auto_message,
                                      timer_seconds,
                                      name='get_last_bet')

  application.run_polling()
