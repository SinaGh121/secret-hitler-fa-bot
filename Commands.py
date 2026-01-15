import logging as log
import os
from pathlib import Path

import datetime



from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode


import MainController
import GamesController
from Constants.Config import load_stats, save_stats
from Boardgamebox.Board import Board
from Boardgamebox.Game import Game
from Boardgamebox.Player import Player
from Constants.Config import ADMIN

# Enable logging
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "logging.log"

log.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=log.INFO,
                filename=str(LOG_FILE))

logger = log.getLogger(__name__)

commands = [  # command description used in the "help" command
    '\u061C\u200E/help\u200E - فهرست دستورهای موجود را نمایش می‌دهد',
    '\u061C\u200E/start\u200E - توضیح کوتاهی دربارهٔ راز هیتلر ارائه می‌دهد',
    '\u061C\u200E/symbols\u200E - همهٔ نمادهای ممکنِ صفحه را نمایش می‌دهد',
    '\u061C\u200E/rules\u200E - پیوندی به قوانین رسمی راز هیتلر می‌دهد',
    '\u061C\u200E/newgame\u200E - یک بازی جدید ایجاد می‌کند',
    '\u061C\u200E/join\u200E - به یک بازی موجود می‌پیوندد',
    '\u061C\u200E/startgame\u200E - پس از پیوستن همهٔ بازیکنان، بازی را آغاز می‌کند',
    '\u061C\u200E/cancelgame\u200E - بازی موجود را لغو می‌کند؛ تمام داده‌های بازی از بین می‌رود',
    '\u061C\u200E/board\u200E - صفحهٔ فعلی را با مسیرهای سیاست فاشیست و لیبرال، ترتیب ریاست‌جمهوری و شمارندهٔ انتخابات نشان می‌دهد',
    '\u061C\u200E/ping\u200E - وضعیت اتصال بات را بررسی می‌کند',
    '\u061C\u200E/version\u200E - نسخهٔ بات و شناسهٔ استقرار را نمایش می‌دهد',
    '\u061C\u200E/votes\u200E - رأی هر بازیکن را نمایش می‌دهد',
    '\u061C\u200E/calltovote\u200E - بازیکنان را برای رأی‌گیری فرا می‌خواند'
]


symbols = [  # board status symbols
    u'\u200F\u25FB\uFE0F خانهٔ خالی بدون قدرت ویژه',
    u'\u200F\u2716\uFE0F خانهٔ پوشیده‌شده با کارت',
    u'\u200F\U0001F52E قدرت ریاست‌جمهوری: بررسی سیاست‌ها',
    u'\u200F\U0001F50E قدرت ریاست‌جمهوری: بررسی وفاداری',
    u'\u200F\U0001F5E1 قدرت ریاست‌جمهوری: اعدام',
    u'\u200F\U0001F454 قدرت ریاست‌جمهوری: برگزاری انتخابات ویژه',
    u'\u200F\U0001F54A پیروزی لیبرال‌ها',
    u'\u200F\u2620 پیروزی فاشیست‌ها'
]


def command_symbols(bot, update):
    cid = update.message.chat_id
    symbol_text = '\u200Fنمادهای زیر ممکن است روی صفحه ظاهر شوند:\n'
    for i in symbols:
        symbol_text += i + '\n'
    bot.send_message(cid, symbol_text)


def command_board(bot, update):
    cid = update.message.chat_id
    if cid in GamesController.games.keys():
        if GamesController.games[cid].board:
            bot.send_message(cid, GamesController.games[cid].board.print_board())
        else:
            bot.send_message(
                cid,
                '\u200Fهیچ بازی در حال اجرا در این چت وجود ندارد. با \u200E/startgame\u200E بازی را آغاز کنید'
            )
    else:
        bot.send_message(
            cid,
            '\u200Fهیچ بازی‌ای در این چت وجود ندارد. با \u200E/newgame\u200E یک بازی جدید بسازید'
        )


def command_start(bot, update):
    cid = update.message.chat_id
    bot.send_message(
        cid,
        '\u200F"«راز هیتلر» یک بازی نقش‌پنهان اجتماعی برای ۵ تا ۱۰ نفر است دربارهٔ پیدا کردن و متوقف کردن راز هیتلر. '
        'اکثریتِ بازیکنان لیبرال هستند؛ اگر بتوانند به یکدیگر اعتماد کنند، رأی کافی برای کنترل میز و پیروزی در بازی خواهند داشت. '
        'اما بعضی بازیکنان فاشیست‌اند؛ آن‌ها هر چه لازم باشد می‌گویند تا انتخاب شوند، برنامهٔ خود را اجرا کنند و دیگران را مقصر پیامدها جلوه دهند. '
        'لیبرال‌ها باید با هم همکاری کنند تا حقیقت را کشف کنند پیش از آنکه فاشیست‌ها رهبر سنگدل خود را منصوب کرده و بازی را ببرند."\n'
        '- توضیح رسمی راز هیتلر\n\n'
        'مرا به یک گروه اضافه کنید و برای ساخت بازی \u200E/newgame\u200E را بنویسید!'
    )
    command_help(bot, update)


def command_rules(bot, update):
    cid = update.message.chat_id
    btn = [[InlineKeyboardButton('\u200Fقوانین', url="http://www.secrethitler.com/assets/Secret_Hitler_Rules.pdf")]]
    rulesMarkup = InlineKeyboardMarkup(btn)
    bot.send_message(cid, '\u200Fقوانین رسمی راز هیتلر را بخوانید:', reply_markup=rulesMarkup)


# version info
def _build_version_text():
    app_version = os.getenv("APP_VERSION", "").strip()


    lines = ["\u200Fنسخهٔ بات:"]
    lines.append("نسخهٔ برنامه: " + (app_version if app_version else "نامشخص"))
    return "\n".join(lines)


def command_version(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, _build_version_text())


# pings the bot
def command_ping(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, 'pong')


# prints statistics, only ADMIN
def command_stats(bot, update):
    cid = update.message.chat_id
    if cid == ADMIN:
        stats = load_stats()
        stattext = (
            '\u200F+++ آمار +++\n'
            'پیروزی لیبرال‌ها (سیاست‌ها): ' + str(stats.get("libwin_policies")) + '\n'
            'پیروزی لیبرال‌ها (کشتن هیتلر): ' + str(stats.get("libwin_kill")) + '\n'
            'پیروزی فاشیست‌ها (سیاست‌ها): ' + str(stats.get("fascwin_policies")) + '\n'
            'پیروزی فاشیست‌ها (هیتلر به‌عنوان صدراعظم): ' + str(stats.get("fascwin_blue")) + '\n'
            'بازی‌های لغوشده: ' + str(stats.get("cancelled")) + '\n\n'
            'تعداد کل گروه‌ها: ' + str(len(stats.get("groups"))) + '\n'
            'بازی‌های در حال اجرا: ' + str(len(GamesController.games))
        )
        bot.send_message(cid, stattext)


# help page
def command_help(bot, update):
    cid = update.message.chat_id
    help_text = '\u200Fدستورهای زیر در دسترس هستند:\n'
    for i in commands:
        help_text += i + '\n'
    bot.send_message(cid, help_text)


def command_newgame(bot, update):
    cid = update.message.chat_id
    game = GamesController.games.get(cid, None)
    groupType = update.message.chat.type
    if groupType not in ['group', 'supergroup']:
        bot.send_message(
            cid,
            '\u200Fابتدا باید مرا به یک گروه اضافه کنید و سپس دستور \u200E/newgame\u200E را در همان گروه وارد کنید!'
        )
    elif game:
        bot.send_message(
            cid,
            '\u200Fهم‌اکنون یک بازی در حال اجرا است؛ برای پایان دادن به آن، دستور \u200E/cancelgame\u200E را وارد کنید!'
        )
    else:
        GamesController.games[cid] = Game(cid, update.message.from_user.id)
        stats = load_stats()
        if cid not in stats.get("groups"):
            stats.get("groups").append(cid)
            save_stats(stats)
        bot.send_message(
            cid,
            '\u200Fبازی جدید ساخته شد! هر بازیکن باید با دستور \u200E/join\u200E به بازی بپیوندد.\n'
            'آغازگر بازی (یا مدیر) نیز می‌تواند \u200E/join\u200E کند و پس از پیوستن همه، دستور '
            '\u200E/startgame\u200E را وارد نماید!'
        )


def command_join(bot, update):
    groupName = update.message.chat.title
    cid = update.message.chat_id
    groupType = update.message.chat.type
    game = GamesController.games.get(cid, None)
    fname = update.message.from_user.first_name

    if groupType not in ['group', 'supergroup']:
        bot.send_message(
            cid,
            '\u200Fابتدا باید مرا به یک گروه اضافه کنید و سپس دستور \u200E/newgame\u200E را در همان گروه وارد کنید!'
        )
    elif not game:
        bot.send_message(
            cid,
            '\u200Fهیچ بازی‌ای در این چت وجود ندارد. با دستور \u200E/newgame\u200E یک بازی جدید بسازید.'
        )
    elif game.board:
        bot.send_message(
            cid,
            '\u200Fبازی آغاز شده است. لطفاً منتظر بازی بعدی بمانید!'
        )
    elif update.message.from_user.id in game.playerlist:
        bot.send_message(
            game.cid,
            '\u200Fشما قبلاً به بازی پیوسته‌اید، %s!' % fname
        )
    elif len(game.playerlist) >= 10:
        bot.send_message(
            game.cid,
            '\u200Fبه حداکثر تعداد بازیکنان رسیده‌اید. لطفاً بازی را با دستور \u200E/startgame\u200E آغاز کنید!'
        )
    else:
        uid = update.message.from_user.id
        player = Player(fname, uid)
        try:
            bot.send_message(
                uid,
                '\u200Fشما به بازی در %s پیوستید. به‌زودی نقش مخفی شما را اعلام خواهم کرد.' % groupName
            )
            game.add_player(uid, player)
        except Exception:
            bot.send_message(
                game.cid,
                '\u200F%s، نمی‌توانم پیام خصوصی برایتان بفرستم. لطفاً به \u200E@thesecretbluebot\u200E بروید و '
                'روی «\u200EStart\u200E» کلیک کنید.\nسپس باید دوباره دستور \u200E/join\u200E را ارسال کنید.' % fname
            )
        else:
            log.info("%s (%d) joined a game in %d" % (fname, uid, game.cid))
            if len(game.playerlist) > 4:
                bot.send_message(
                    game.cid,
                    '\u200F%s به بازی پیوست. اگر این آخرین بازیکن است و می‌خواهید بازی را با %d بازیکن آغاز کنید، '
                    'دستور \u200E/startgame\u200E را وارد کنید!' % (fname, len(game.playerlist))
                )
            elif len(game.playerlist) == 1:
                bot.send_message(
                    game.cid,
                    '\u200F%s به بازی پیوست. هم‌اکنون %d بازیکن در بازی است و شما به ۵ تا ۱۰ بازیکن نیاز دارید.'
                    % (fname, len(game.playerlist))
                )
            else:
                bot.send_message(
                    game.cid,
                    '\u200F%s به بازی پیوست. هم‌اکنون %d بازیکن در بازی هستند و شما به ۵ تا ۱۰ بازیکن نیاز دارید.'
                    % (fname, len(game.playerlist))
                )


def command_startgame(bot, update):
    log.info('command_startgame called')
    cid = update.message.chat_id
    game = GamesController.games.get(cid, None)
    if not game:
        bot.send_message(
            cid,
            '\u200Fهیچ بازی‌ای در این چت وجود ندارد. با دستور \u200E/newgame\u200E یک بازی جدید بسازید'
        )
    elif game.board:
        bot.send_message(
            cid,
            '\u200Fبازی هم‌اکنون در حال اجرا است!'
        )
    elif update.message.from_user.id != game.initiator and bot.getChatMember(cid, update.message.from_user.id).status not in ("administrator", "creator"):
        bot.send_message(
            game.cid,
            '\u200Fفقط آغازگر بازی یا مدیر گروه می‌تواند با دستور \u200E/startgame\u200E بازی را آغاز کند'
        )
    elif len(game.playerlist) < 5:
        bot.send_message(
            game.cid,
            '\u200Fتعداد بازیکنان کافی نیست (حداقل ۵، حداکثر ۱۰). با دستور \u200E/join\u200E به بازی بپیوندید'
        )
    else:
        player_number = len(game.playerlist)
        MainController.inform_players(bot, game, game.cid, player_number)
        MainController.inform_fascists(bot, game, player_number)
        game.board = Board(player_number, game)
        log.info(game.board)
        log.info("len(games) Command_startgame: " + str(len(GamesController.games)))
        game.shuffle_player_sequence()
        game.board.state.player_counter = 0
        bot.send_message(game.cid, game.board.print_board())
        MainController.start_round(bot, game)


def command_cancelgame(bot, update):
    log.info('command_cancelgame called')
    cid = update.message.chat_id
    if cid in GamesController.games.keys():
        game = GamesController.games[cid]
        status = bot.getChatMember(cid, update.message.from_user.id).status
        if update.message.from_user.id == game.initiator or status in ("administrator", "creator"):
            MainController.end_game(bot, game, 99)
        else:
            bot.send_message(
                cid,
                '\u200Fفقط آغازگر بازی یا مدیر گروه می‌تواند با دستور \u200E/cancelgame\u200E بازی را لغو کند'
            )
    else:
        bot.send_message(
            cid,
            '\u200Fهیچ بازی‌ای در این چت وجود ندارد. با دستور \u200E/newgame\u200E یک بازی جدید بسازید'
        )


def command_votes(bot, update):
    try:
        # Send message of executing command
        cid = update.message.chat_id
        # Check if there is a current game
        if cid in GamesController.games.keys():
            game = GamesController.games.get(cid, None)
            if not game.dateinitvote:
                bot.send_message(cid, '\u200Fرأی‌گیری هنوز شروع نشده است.')
            else:
                start = game.dateinitvote
                stop = datetime.datetime.now()
                elapsed = stop - start
                if elapsed > datetime.timedelta(minutes=1):
                    history_text = (
                        '\u200Fتاریخچهٔ رأی‌گیری برای رئیس‌جمهور %s و صدراعظم %s:\n\n'
                        % (game.board.state.nominated_president.name, game.board.state.nominated_chancellor.name)
                    )
                    for player in game.player_sequence:
                        if player.uid in game.board.state.last_votes:
                            history_text += '%s رأی خود را ثبت کرد.\n' % game.playerlist[player.uid].name
                        else:
                            history_text += '%s رأی خود را ثبت نکرد.\n' % game.playerlist[player.uid].name
                    bot.send_message(cid, history_text)
                else:
                    bot.send_message(cid, '\u200Fبرای مشاهدهٔ رأی‌ها باید پنج دقیقه بگذرد')
        else:
            bot.send_message(
                cid,
                '\u200Fهیچ بازی‌ای در این چت وجود ندارد. با دستور \u200E/newgame\u200E یک بازی جدید بسازید'
            )
    except Exception as e:
        bot.send_message(cid, str(e))


def command_calltovote(bot, update):
    try:
        # Send message of executing command
        cid = update.message.chat_id
        # Check if there is a current game
        if cid in GamesController.games.keys():
            game = GamesController.games.get(cid, None)
            if not game.dateinitvote:
                bot.send_message(cid, '\u200Fرأی‌گیری هنوز شروع نشده است.')
            else:
                start = game.dateinitvote
                stop = datetime.datetime.now()
                elapsed = stop - start
                if elapsed > datetime.timedelta(minutes=1):
                    history_text = ''
                    for player in game.player_sequence:
                        # If the player is not in last_votes send him reminder
                        if player.uid not in game.board.state.last_votes:
                            history_text += '\u200Fزمان رأی‌دادن است [%s](tg://user?id=%d).\n' % (
                                game.playerlist[player.uid].name, player.uid
                            )
                    bot.send_message(cid, text=history_text, parse_mode=ParseMode.MARKDOWN)
                else:
                    bot.send_message(cid, '\u200Fبرای مشاهدهٔ یادآوری رأی‌گیری باید پنج دقیقه بگذرد')
        else:
            bot.send_message(
                cid,
                '\u200Fهیچ بازی‌ای در این چت وجود ندارد. با دستور \u200E/newgame\u200E یک بازی جدید بسازید'
            )
    except Exception as e:
        bot.send_message(cid, str(e))
