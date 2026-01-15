#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fork of Secret-Blue (https://github.com/d0tcc/Secret-Blue)
Original author : Julian Schrittwieser
Fork maintainer : Sina Ghaderi
License         : CC BY-NC-SA 4.0 – see LICENSE file
"""
__author__ = "Julian Schrittwieser (original), Sina Ghaderi (fork)"
__maintainer__ = "Sina Ghaderi"

import logging as log
import random
import re
from random import randrange
from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler)

import Commands
from Constants.Cards import (
    ACTION_CHOOSE,
    ACTION_INSPECT,
    ACTION_KILL,
    ACTION_POLICY,
    PARTY_FASCIST,
    PARTY_LIBERAL,
    POLICY_FASCIST,
    POLICY_LIBERAL,
    ROLE_FASCIST,
    ROLE_HITLER,
    ROLE_LIBERAL,
    playerSets,
)
from Constants.Config import TOKEN, load_stats, save_stats
from Boardgamebox.Game import Game
from Boardgamebox.Player import Player
import GamesController

import datetime

# Enable logging
log.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=log.INFO,
                # filename='../logs/logging.log'
                )

logger = log.getLogger(__name__)

POLICY_CALLBACK_PATTERN = "(-[0-9]*)_(%s|%s|veto)" % (POLICY_LIBERAL, POLICY_FASCIST)


def initialize_testdata():
    # Sample game for quicker tests
    testgame = Game(-1001113216265, 15771023)
    GamesController.games[-1001113216265] = testgame
    players = [Player("سینا", 320853702), Player("Gustav", 305333239), Player("شیرین", 318940765), Player("Susi", 290308460), Player("Renate", 312027975)]
    for player in players:
        testgame.add_player(player.uid, player)


##
#
# Beginning of round
#
##
def start_round(bot, game):
    log.info('start_round called')
    if game.board.state.chosen_president is None:
        game.board.state.nominated_president = game.player_sequence[game.board.state.player_counter]
    else:
        game.board.state.nominated_president = game.board.state.chosen_president
        game.board.state.chosen_president = None
    bot.send_message(
    game.cid,
    "\u200Fنامزد بعدی ریاست‌جمهوری %s است.\n%s، لطفاً در گفت‌وگوی خصوصی یک صدراعظم معرفی کن!" %
    (game.board.state.nominated_president.name, game.board.state.nominated_president.name)
)
    choose_chancellor(bot, game)
    # --> nominate_chosen_chancellor --> vote --> handle_voting --> count_votes --> voting_aftermath --> draw_policies
    # --> choose_policy --> pass_two_policies --> choose_policy --> enact_policy --> start_round


def choose_chancellor(bot, game):
    log.info('choose_chancellor called')
    strcid = str(game.cid)
    pres_uid = 0
    chan_uid = 0
    btns = []
    if game.board.state.president is not None:
        pres_uid = game.board.state.president.uid
    if game.board.state.chancellor is not None:
        chan_uid = game.board.state.chancellor.uid
    for uid in game.playerlist:
        # If there are only five players left in the
        # game, only the last elected Chancellor is
        # ineligible to be Chancellor Candidate; the
        # last President may be nominated.
        if len(game.player_sequence) > 5:
            if uid != game.board.state.nominated_president.uid and game.playerlist[
                uid].is_dead == False and uid != pres_uid and uid != chan_uid:
                name = game.playerlist[uid].name
                btns.append([InlineKeyboardButton(name, callback_data=strcid + "_chan_" + str(uid))])
        else:
            if uid != game.board.state.nominated_president.uid and game.playerlist[
                uid].is_dead == False and uid != chan_uid:
                name = game.playerlist[uid].name
                btns.append([InlineKeyboardButton(name, callback_data=strcid + "_chan_" + str(uid))])

    chancellorMarkup = InlineKeyboardMarkup(btns)
    bot.send_message(game.board.state.nominated_president.uid, game.board.print_board())
    bot.send_message(
    game.board.state.nominated_president.uid,
    '\u200Fلطفاً صدراعظم خود را معرفی کن!',
    reply_markup=chancellorMarkup
)



def nominate_chosen_chancellor(bot, update):
    log.info('nominate_chosen_chancellor called')
    log.info(GamesController.games.keys())
    callback = update.callback_query
    regex = re.search("(-[0-9]*)_chan_([0-9]*)", callback.data)
    cid = int(regex.group(1))
    chosen_uid = int(regex.group(2))
    try:
        game = GamesController.games.get(cid, None)
        log.info(game)
        log.info(game.board)
        game.board.state.nominated_chancellor = game.playerlist[chosen_uid]
        log.info("President %s (%d) nominated %s (%d)" % (
            game.board.state.nominated_president.name, game.board.state.nominated_president.uid,
            game.board.state.nominated_chancellor.name, game.board.state.nominated_chancellor.uid))
        bot.edit_message_text(
            '\u200Fشما %s را به‌عنوان صدراعظم نامزد کردید!' %
            game.board.state.nominated_chancellor.name,
            callback.from_user.id,
            callback.message.message_id
        )
        bot.send_message(
            game.cid,
            '\u200Fرئیس‌جمهور %s، %s را به‌عنوان صدراعظم نامزد کرد. لطفاً اکنون رأی دهید!' %
            (game.board.state.nominated_president.name, game.board.state.nominated_chancellor.name)
        )
        vote(bot, game)
    except AttributeError as e:
        log.error("nominate_chosen_chancellor: Game or board should not be None! Error: " + str(e))
    except Exception as e:
        log.error("Unknown error: " + str(e))


def vote(bot, game):
    log.info('vote called')
    # When voting starts we start the counter to see later with the vote/calltovote command we can see who voted.
    game.dateinitvote = datetime.datetime.now()
    strcid = str(game.cid)
    btns = [[InlineKeyboardButton('\u200Fبله', callback_data=strcid + "_Ja"),
             InlineKeyboardButton('\u200Fخیر', callback_data=strcid + "_Nein")]]
    voteMarkup = InlineKeyboardMarkup(btns)
    for uid in game.playerlist:
        if not game.playerlist[uid].is_dead:
            if game.playerlist[uid] is not game.board.state.nominated_president:
                # the nominated president already got the board before nominating a chancellor
                bot.send_message(uid, game.board.print_board())
            bot.send_message(
                uid,
                '\u200Fآیا می‌خواهید %s را به‌عنوان رئیس‌جمهور و %s را به‌عنوان صدراعظم انتخاب کنید؟' % (
                    game.board.state.nominated_president.name,
                    game.board.state.nominated_chancellor.name
                ),
                reply_markup=voteMarkup
            )


def handle_voting(bot, update):
    callback = update.callback_query
    log.info('handle_voting called: %s' % callback.data)
    regex = re.search("(-[0-9]*)_(.*)", callback.data)
    cid = int(regex.group(1))
    answer = regex.group(2)
    try:
        game = GamesController.games[cid]
        uid = callback.from_user.id
        bot.edit_message_text(
            '\u200Fاز رأی شما متشکرم: %s برای رئیس‌جمهور %s و صدراعظم %s' %
            (answer, game.board.state.nominated_president.name, game.board.state.nominated_chancellor.name),
            uid,
            callback.message.message_id
        )
        log.info("Player %s (%d) voted %s" % (callback.from_user.first_name, uid, answer))
        if uid not in game.board.state.last_votes:
            game.board.state.last_votes[uid] = answer
        if len(game.board.state.last_votes) == len(game.player_sequence):
            count_votes(bot, game)
    except:
        log.error("handle_voting: Game or board should not be None!")


def count_votes(bot, game):
    log.info('count_votes called')
    # Voted Ended
    game.dateinitvote = None
    voting_text = ""
    voting_success = False
    for player in game.player_sequence:
        if game.board.state.last_votes[player.uid] == "Ja":
            voting_text += game.playerlist[player.uid].name + " voted Ja!\n"
        elif game.board.state.last_votes[player.uid] == "Nein":
            voting_text += game.playerlist[player.uid].name + " voted Nein!\n"
    if list(game.board.state.last_votes.values()).count("Ja") > (
        len(game.player_sequence) / 2):  # because player_sequence doesnt include dead
        # VOTING WAS SUCCESSFUL
        log.info("Voting successful")
        voting_text += "\u200Fدرود بر رئیس‌جمهور %s! درود بر صدراعظم %s!" % (
            game.board.state.nominated_president.name, game.board.state.nominated_chancellor.name
        )
        game.board.state.chancellor = game.board.state.nominated_chancellor
        game.board.state.president = game.board.state.nominated_president
        game.board.state.nominated_president = None
        game.board.state.nominated_chancellor = None
        voting_success = True
        bot.send_message(game.cid, voting_text)
        voting_aftermath(bot, game, voting_success)
    else:
        log.info("Voting failed")
        voting_text += '\u200Fمردم دو نامزد را نپسندیدند!'
        game.board.state.nominated_president = None
        game.board.state.nominated_chancellor = None
        game.board.state.failed_votes += 1
        bot.send_message(game.cid, voting_text)
        if game.board.state.failed_votes == 3:
            do_anarchy(bot, game)
        else:
            voting_aftermath(bot, game, voting_success)


def voting_aftermath(bot, game, voting_success):
    log.info('voting_aftermath called')
    game.board.state.last_votes = {}
    if voting_success:
        if game.board.state.fascist_track >= 3 and game.board.state.chancellor.role == ROLE_HITLER:
            # fascists win, because Hitler was elected as chancellor after 3 fascist policies
            game.board.state.game_endcode = -2
            end_game(bot, game, game.board.state.game_endcode)
        elif game.board.state.fascist_track >= 3 and game.board.state.chancellor.role != ROLE_HITLER and game.board.state.chancellor not in game.board.state.not_blues:
            game.board.state.not_blues.append(game.board.state.chancellor)
            draw_policies(bot, game)
        else:
            # voting was successful and Hitler was not nominated as chancellor after 3 fascist policies
            draw_policies(bot, game)
    else:
        bot.send_message(game.cid, game.board.print_board())
        start_next_round(bot, game)


def draw_policies(bot, game):
    log.info('draw_policies called')
    strcid = str(game.cid)
    game.board.state.veto_refused = False
    # shuffle discard pile with rest if rest < 3
    shuffle_policy_pile(bot, game)
    btns = []
    for i in range(3):
        game.board.state.drawn_policies.append(game.board.policies.pop(0))
    for policy in game.board.state.drawn_policies:
        btns.append([InlineKeyboardButton(policy, callback_data=strcid + "_" + policy)])

    choosePolicyMarkup = InlineKeyboardMarkup(btns)
    bot.send_message(
        game.board.state.president.uid,
        '\u200Fشما ۳ کارت سیاست کشیدید. کدام‌یک را می‌خواهید کنار بگذارید؟',
        reply_markup=choosePolicyMarkup
    )


def choose_policy(bot, update):
    log.info('choose_policy called')
    callback = update.callback_query
    regex = re.search("(-[0-9]*)_(.*)", callback.data)
    cid = int(regex.group(1))
    answer = regex.group(2)
    try:
        game = GamesController.games[cid]
        strcid = str(game.cid)
        uid = callback.from_user.id
        if len(game.board.state.drawn_policies) == 3:
            log.info("Player %s (%d) discarded %s" % (callback.from_user.first_name, uid, answer))
            bot.edit_message_text(
                '\u200Fکارت سیاست %s کنار گذاشته خواهد شد!' % answer,
                uid,
                callback.message.message_id
            )
            # remove policy from drawn cards and add to discard pile, pass the other two policies
            for i in range(3):
                if game.board.state.drawn_policies[i] == answer:
                    game.board.discards.append(game.board.state.drawn_policies.pop(i))
                    break
            pass_two_policies(bot, game)
        elif len(game.board.state.drawn_policies) == 2:
            if answer == "veto":
                log.info("Player %s (%d) suggested a veto" % (callback.from_user.first_name, uid))
                bot.edit_message_text(
                    '\u200Fشما پیشنهاد \u200EVeto\u200E به رئیس‌جمهور %s دادید' %
                    game.board.state.president.name,
                    uid,
                    callback.message.message_id
                )
                bot.send_message(
                    game.cid,
                    '\u200Fصدراعظم %s پیشنهاد \u200EVeto\u200E به رئیس‌جمهور %s داد.' % (
                        game.board.state.chancellor.name, game.board.state.president.name)
                )

                btns = [[InlineKeyboardButton('\u200Fوتو! (پذیرش پیشنهاد)', callback_data=strcid + "_yesveto")],
                        [InlineKeyboardButton('\u200Fبدون وتو! (رد پیشنهاد)', callback_data=strcid + "_noveto")]]

                vetoMarkup = InlineKeyboardMarkup(btns)
                bot.send_message(
                    game.board.state.president.uid,
                    '\u200Fصدراعظم %s پیشنهاد \u200EVeto\u200E داده است. آیا می‌خواهید \u200Eveto\u200E کنید '
                    '(این کارت‌ها را کنار بگذارید)؟' % game.board.state.chancellor.name,
                    reply_markup=vetoMarkup
                )
            else:
                log.info("Player %s (%d) chose a %s policy" % (callback.from_user.first_name, uid, answer))
                bot.edit_message_text(
                    '\u200Fکارت سیاست %s اجرا خواهد شد!' % answer,
                    uid,
                    callback.message.message_id
                )
                # remove policy from drawn cards and enact, discard the other card
                for i in range(2):
                    if game.board.state.drawn_policies[i] == answer:
                        game.board.state.drawn_policies.pop(i)
                        break
                game.board.discards.append(game.board.state.drawn_policies.pop(0))
                assert len(game.board.state.drawn_policies) == 0
                enact_policy(bot, game, answer, False)
        else:
            log.error("choose_policy: drawn_policies should be 3 or 2, but was " + str(
                len(game.board.state.drawn_policies)))
    except:
        log.error("choose_policy: Game or board should not be None!")


def pass_two_policies(bot, game):
    log.info('pass_two_policies called')
    strcid = str(game.cid)
    btns = []
    for policy in game.board.state.drawn_policies:
        btns.append([InlineKeyboardButton(policy, callback_data=strcid + "_" + policy)])
    if game.board.state.fascist_track == 5 and not game.board.state.veto_refused:
        btns.append([InlineKeyboardButton('\u200Fوتو', callback_data=strcid + "_veto")])
        choosePolicyMarkup = InlineKeyboardMarkup(btns)
        bot.send_message(
            game.cid,
            '\u200Fرئیس‌جمهور %s دو کارت سیاست به صدراعظم %s داد.' % (
                game.board.state.president.name, game.board.state.chancellor.name
            )
        )
        bot.send_message(
            game.board.state.chancellor.uid,
            '\u200Fرئیس‌جمهور %s دو کارت سیاست به شما داد. کدام را می‌خواهید اجرا کنید؟ همچنین می‌توانید از قدرت وتو استفاده کنید.' %
            game.board.state.president.name,
            reply_markup=choosePolicyMarkup
        )

    elif game.board.state.veto_refused:
        choosePolicyMarkup = InlineKeyboardMarkup(btns)
        bot.send_message(
            game.board.state.chancellor.uid,
            '\u200Fرئیس‌جمهور %s پیشنهاد وتوی شما را رد کرد. اکنون باید انتخاب کنید؛ کدام را می‌خواهید اجرا کنید؟' %
            game.board.state.president.name,
            reply_markup=choosePolicyMarkup
        )

    elif game.board.state.fascist_track < 5:
        choosePolicyMarkup = InlineKeyboardMarkup(btns)
        bot.send_message(
            game.board.state.chancellor.uid,
            '\u200Fرئیس‌جمهور %s دو کارت سیاست به شما داد. کدام را می‌خواهید اجرا کنید؟' %
            game.board.state.president.name,
            reply_markup=choosePolicyMarkup
        )


def enact_policy(bot, game, policy, anarchy):
    log.info('enact_policy called')
    if policy == POLICY_LIBERAL:
        game.board.state.liberal_track += 1
    elif policy == POLICY_FASCIST:
        game.board.state.fascist_track += 1
    game.board.state.failed_votes = 0  # reset counter
    if not anarchy:
        bot.send_message(
            game.cid,
            '\u200Fرئیس‌جمهور %s و صدراعظم %s یک سیاست %s تصویب کردند!' %
            (game.board.state.president.name, game.board.state.chancellor.name, policy)
        )
    else:
        bot.send_message(
            game.cid,
            '\u200Fسیاست بالایی تصویب شد: %s' % policy
        )
    sleep(3)
    bot.send_message(game.cid, game.board.print_board())
    # end of round
    if game.board.state.liberal_track == 5:
        game.board.state.game_endcode = 1
        end_game(bot, game, game.board.state.game_endcode)  # liberals win with 5 liberal policies
    if game.board.state.fascist_track == 6:
        game.board.state.game_endcode = -1
        end_game(bot, game, game.board.state.game_endcode)  # fascists win with 6 fascist policies
    sleep(3)
    # End of legislative session, shuffle if necessary 
    shuffle_policy_pile(bot, game)    
    if not anarchy:
        if policy == POLICY_FASCIST:
            action = game.board.fascist_track_actions[game.board.state.fascist_track - 1]
            if action is None and game.board.state.fascist_track == 6:
                pass
            elif action is None:
                start_next_round(bot, game)
            elif action == ACTION_POLICY:
                bot.send_message(
                    game.cid,
                    "\u200Fقدرت ریاست‌جمهوری فعال شد: بررسی سیاست‌ها " + u"\U0001F52E" +
                    "\n\u200Fرئیس‌جمهور %s اکنون از سه کارت سیاست بعدی در دسته باخبر است. "
                    "رئیس‌جمهور می‌تواند بنا به صلاحدید نتایج بررسی خود را به اشتراک بگذارد "
                    "(یا دربارهٔ آن دروغ بگوید!)." % game.board.state.president.name
                )
                action_policy(bot, game)
            elif action == ACTION_KILL:
                bot.send_message(
                    game.cid,
                    "\u200Fقدرت ریاست‌جمهوری فعال شد: اعدام " + u"\U0001F5E1" +
                    "\n\u200Fرئیس‌جمهور %s باید یک نفر را حذف کند. می‌توانید اکنون دربارهٔ این تصمیم "
                    "بحث کنید ولی رأی نهایی با رئیس‌جمهور است." % game.board.state.president.name
                )
                action_kill(bot, game)
            elif action == ACTION_INSPECT:
                bot.send_message(
                    game.cid,
                    "\u200Fقدرت ریاست‌جمهوری فعال شد: بررسی وفاداری " + u"\U0001F50E" +
                    "\n\u200Fرئیس‌جمهور %s می‌تواند عضویت حزبی یک بازیکن را مشاهده کند. "
                    "رئیس‌جمهور می‌تواند نتایج بررسی را به‌دلخواه خود به اشتراک بگذارد "
                    "(یا دربارهٔ آن دروغ بگوید!)." % game.board.state.president.name
                )
                action_inspect(bot, game)
            elif action == ACTION_CHOOSE:
                bot.send_message(
                    game.cid,
                    "\u200Fقدرت ریاست‌جمهوری فعال شد: برگزاری انتخابات ویژه " + u"\U0001F454" +
                    "\n\u200Fرئیس‌جمهور %s می‌تواند نامزد بعدی ریاست‌جمهوری را انتخاب کند. سپس ترتیب نوبت "
                    "به حالت عادی بازمی‌گردد." % game.board.state.president.name
                )

                action_choose(bot, game)
        else:
            start_next_round(bot, game)
    else:
        start_next_round(bot, game)


def choose_veto(bot, update):
    log.info('choose_veto called')
    callback = update.callback_query
    regex = re.search("(-[0-9]*)_(.*)", callback.data)
    cid = int(regex.group(1))
    answer = regex.group(2)
    try:
        game = GamesController.games[cid]
        uid = callback.from_user.id
        if answer == "yesveto":
            log.info("Player %s (%d) accepted the veto" % (callback.from_user.first_name, uid))
            bot.edit_message_text(
                '\u200Fشما وتو را پذیرفتید!',
                uid,
                callback.message.message_id
            )

            bot.send_message(
                game.cid,
                '\u200Fرئیس‌جمهور %s وتوی صدراعظم %s را پذیرفت. هیچ سیاستی تصویب نشد، اما این یک انتخابات ناموفق محسوب می‌شود.' %
                (game.board.state.president.name, game.board.state.chancellor.name)
            )
            game.board.discards += game.board.state.drawn_policies
            game.board.state.drawn_policies = []
            game.board.state.failed_votes += 1
            if game.board.state.failed_votes == 3:
                do_anarchy(bot, game)
            else:
                bot.send_message(game.cid, game.board.print_board())
                start_next_round(bot, game)
        elif answer == "noveto":
            log.info("Player %s (%d) declined the veto" % (callback.from_user.first_name, uid))
            game.board.state.veto_refused = True
            bot.edit_message_text(
                '\u200Fشما وتو را رد کردید!',
                uid,
                callback.message.message_id
            )
            bot.send_message(
                game.cid,
                '\u200Fرئیس‌جمهور %s وتوی صدراعظم %s را رد کرد. اکنون صدراعظم باید یک سیاست را انتخاب کند!' % (
                    game.board.state.president.name, game.board.state.chancellor.name
                )
            )
            pass_two_policies(bot, game)
        else:
            log.error("choose_veto: Callback data can either be \"veto\" or \"noveto\", but not %s" % answer)
    except:
        log.error("choose_veto: Game or board should not be None!")


def do_anarchy(bot, game):
    log.info('do_anarchy called')
    bot.send_message(game.cid, game.board.print_board())
    bot.send_message(game.cid, '\u200Fهرج‌ومرج!!')
    game.board.state.president = None
    game.board.state.chancellor = None
    shuffle_policy_pile(bot, game)
    top_policy = game.board.policies.pop(0)
    game.board.state.last_votes = {}
    enact_policy(bot, game, top_policy, True)


def action_policy(bot, game):
    log.info('action_policy called')
    topPolicies = ""
    # shuffle discard pile with rest if rest < 3
    shuffle_policy_pile(bot, game)
    for i in range(3):
        topPolicies += game.board.policies[i] + "\n"
    bot.send_message(
        game.board.state.president.uid,
        '\u200Fسه کارت سیاست بالایی (از بالا به پایین):\n%s\nمی‌توانید دربارهٔ این موضوع دروغ بگویید.' %
        topPolicies
    )
    start_next_round(bot, game)


def action_kill(bot, game):
    log.info('action_kill called')
    strcid = str(game.cid)
    btns = []
    for uid in game.playerlist:
        if uid != game.board.state.president.uid and game.playerlist[uid].is_dead == False:
            name = game.playerlist[uid].name
            btns.append([InlineKeyboardButton(name, callback_data=strcid + "_kill_" + str(uid))])

    killMarkup = InlineKeyboardMarkup(btns)
    bot.send_message(game.board.state.president.uid, game.board.print_board())
    bot.send_message(
        game.board.state.president.uid,
        '\u200Fشما باید یک نفر را حذف کنید. می‌توانید دربارهٔ تصمیم خود با دیگران بحث کنید. عاقلانه انتخاب کنید!',
        reply_markup=killMarkup
    )


def choose_kill(bot, update):
    log.info('choose_kill called')
    callback = update.callback_query
    regex = re.search("(-[0-9]*)_kill_(.*)", callback.data)
    cid = int(regex.group(1))
    answer = int(regex.group(2))
    try:
        game = GamesController.games[cid]
        chosen = game.playerlist[answer]
        chosen.is_dead = True
        if game.player_sequence.index(chosen) <= game.board.state.player_counter:
            game.board.state.player_counter -= 1
        game.player_sequence.remove(chosen)
        game.board.state.dead += 1
        log.info("Player %s (%d) killed %s (%d)" % (
            callback.from_user.first_name, callback.from_user.id, chosen.name, chosen.uid))
        bot.edit_message_text(
            '\u200Fشما \u200E%s\u200E را کشتید!' % chosen.name,
            callback.from_user.id,
            callback.message.message_id
        )
        if chosen.role == ROLE_HITLER:
            bot.send_message(
                game.cid,
                '\u200Fرئیس‌جمهور ' + game.board.state.president.name + '، ' + chosen.name + ' را کشت.'
            )
            end_game(bot, game, 2)
        else:
            bot.send_message(
                game.cid,
                '\u200Fرئیس‌جمهور %s، %s را کشت؛ او هیتلر نبود. %s، تو اکنون مرده‌ای و دیگر اجازهٔ صحبت نداری!' %
                (game.board.state.president.name, chosen.name, chosen.name)
            )
            bot.send_message(game.cid, game.board.print_board())
            start_next_round(bot, game)
    except:
        log.error("choose_kill: Game or board should not be None!")


def action_choose(bot, game):
    log.info('action_choose called')
    strcid = str(game.cid)
    btns = []

    for uid in game.playerlist:
        if uid != game.board.state.president.uid and game.playerlist[uid].is_dead == False:
            name = game.playerlist[uid].name
            btns.append([InlineKeyboardButton(name, callback_data=strcid + "_choo_" + str(uid))])

    inspectMarkup = InlineKeyboardMarkup(btns)
    bot.send_message(game.board.state.president.uid, game.board.print_board())
    bot.send_message(
        game.board.state.president.uid,
        '\u200Fشما باید نامزد بعدی ریاست‌جمهوری را انتخاب کنید. سپس ترتیب نوبت به حالت عادی بازمی‌گردد. عاقلانه انتخاب کنید!',
        reply_markup=inspectMarkup
    )


def choose_choose(bot, update):
    log.info('choose_choose called')
    callback = update.callback_query
    regex = re.search("(-[0-9]*)_choo_(.*)", callback.data)
    cid = int(regex.group(1))
    answer = int(regex.group(2))
    try:
        game = GamesController.games[cid]
        chosen = game.playerlist[answer]
        game.board.state.chosen_president = chosen
        log.info(
            "Player %s (%d) chose %s (%d) as next president" % (
                callback.from_user.first_name, callback.from_user.id, chosen.name, chosen.uid))
        bot.edit_message_text(
            '\u200Fشما %s را به‌عنوان رئیس‌جمهور بعدی انتخاب کردید!' % chosen.name,
            callback.from_user.id,
            callback.message.message_id
        )
        bot.send_message(
            game.cid,
            '\u200Fرئیس‌جمهور %s، %s را به‌عنوان رئیس‌جمهور بعدی انتخاب کرد.' %
            (game.board.state.president.name, chosen.name)
        )
        start_next_round(bot, game)
    except:
        log.error("choose_choose: Game or board should not be None!")


def action_inspect(bot, game):
    log.info('action_inspect called')
    strcid = str(game.cid)
    btns = []
    for uid in game.playerlist:
        if uid != game.board.state.president.uid and game.playerlist[uid].is_dead == False and uid not in game.board.state.inspected_uids:
            name = game.playerlist[uid].name
            btns.append([InlineKeyboardButton(name, callback_data=strcid + "_insp_" + str(uid))])

    if not btns:
        bot.send_message(
            game.board.state.president.uid,
            '\u200Fهمهٔ بازیکنان قبلاً بازرسی شده‌اند و گزینهٔ معتبری باقی نمانده است.'
        )
        bot.send_message(
            game.cid,
            '\u200Fهیچ بازیکن بازرسی‌نشده‌ای باقی نمانده است؛ نوبت بعدی آغاز می‌شود.'
        )
        start_next_round(bot, game)
        return

    inspectMarkup = InlineKeyboardMarkup(btns)
    bot.send_message(game.board.state.president.uid, game.board.print_board())
    bot.send_message(
        game.board.state.president.uid,
        '\u200Fشما می‌توانید عضویت حزبی یک بازیکن را ببینید. عضویت چه کسی را می‌خواهید بدانید؟ عاقلانه انتخاب کنید!',
        reply_markup=inspectMarkup
    )


def choose_inspect(bot, update):
    log.info('choose_inspect called')
    callback = update.callback_query
    regex = re.search("(-[0-9]*)_insp_(.*)", callback.data)
    cid = int(regex.group(1))
    answer = int(regex.group(2))
    try:
        game = GamesController.games[cid]
        chosen = game.playerlist[answer]
        if answer in game.board.state.inspected_uids:
            bot.send_message(
                callback.from_user.id,
                '\u200Fاین بازیکن قبلاً بازرسی شده است. لطفاً بازیکن دیگری را انتخاب کنید.'
            )
            action_inspect(bot, game)
            return
        game.board.state.inspected_uids.add(answer)
        log.info(
            "Player %s (%d) inspects %s (%d)'s party membership (%s)" % (
                callback.from_user.first_name, callback.from_user.id, chosen.name, chosen.uid,
                chosen.party))
        bot.edit_message_text(
            '\u200Fعضویت حزبی %s، %s است' % (chosen.name, chosen.party),
            callback.from_user.id,
            callback.message.message_id
        )
        bot.send_message(
            game.cid,
            '\u200Fرئیس‌جمهور %s، %s را بازرسی کرد.' %
            (game.board.state.president.name, chosen.name)
        )
        start_next_round(bot, game)
    except:
        log.error("choose_inspect: Game or board should not be None!")


def start_next_round(bot, game):
    log.info('start_next_round called')
    # start next round if there is no winner (or /cancel)
    if game.board.state.game_endcode == 0:
        # start new round
        sleep(5)
        # if there is no special elected president in between
        if game.board.state.chosen_president is None:
            increment_player_counter(game)
        start_round(bot, game)


##
#
# End of round
#
##

def end_game(bot, game, game_endcode):
    log.info('end_game called')
    ##
    # game_endcode:
    #   -2  fascists win by electing Hitler as chancellor
    #   -1  fascists win with 6 fascist policies
    #   0   not ended
    #   1   liberals win with 5 liberal policies
    #   2   liberals win by killing Hitler
    #   99  game cancelled
    #
    stats = load_stats()

    if game_endcode == 99:
        if GamesController.games[game.cid].board is not None:
            bot.send_message(game.cid, '\u200Fبازی لغو شد!\n\n%s' % game.print_roles())
            # bot.send_message(ADMIN, "Game of Secret Blue canceled in group %d" % game.cid)
            stats['cancelled'] = stats['cancelled'] + 1
        else:
            bot.send_message(game.cid, '\u200Fبازی لغو شد!')
    else:
        if game_endcode == -2:
            bot.send_message(
                game.cid,
                '\u200Fپایان بازی! فاشیست‌ها با انتخاب هیتلر به‌عنوان صدراعظم پیروز شدند!\n\n%s' %
                game.print_roles()
            )
            stats['fascwin_blue'] = stats['fascwin_blue'] + 1
        if game_endcode == -1:
            bot.send_message(
                game.cid,
                '\u200Fپایان بازی! فاشیست‌ها با تصویب ۶ سیاست فاشیستی پیروز شدند!\n\n%s' % game.print_roles()
            )
            stats['fascwin_policies'] = stats['fascwin_policies'] + 1
        if game_endcode == 1:
            bot.send_message(
                game.cid,
                '\u200Fپایان بازی! لیبرال‌ها با تصویب ۵ سیاست لیبرال پیروز شدند!\n\n%s' % game.print_roles()
            )
            stats['libwin_policies'] = stats['libwin_policies'] + 1
        if game_endcode == 2:
            bot.send_message(
                game.cid,
                '\u200Fپایان بازی! لیبرال‌ها با کشتن هیتلر پیروز شدند!\n\n%s' % game.print_roles()
            )
            stats['libwin_kill'] = stats['libwin_kill'] + 1

            # bot.send_message(ADMIN, "Game of Secret Blue ended in group %d" % game.cid)

    save_stats(stats)
    del GamesController.games[game.cid]


def inform_players(bot, game, cid, player_number):
    log.info('inform_players called')
    bot.send_message(
        cid,
        '\u200Fبازی را با %d بازیکن شروع کنیم!\n%s\nبه چت خصوصی‌تان بروید و نقش مخفی خود را ببینید!' %
        (player_number, print_player_info(player_number))
    )
    available_roles = list(playerSets[player_number]["roles"])  # copy not reference because we need it again later
    for uid in game.playerlist:
        random_index = randrange(len(available_roles))
        role = available_roles.pop(random_index)
        party = get_membership(role)
        game.playerlist[uid].role = role
        game.playerlist[uid].party = party
        bot.send_message(
            uid,
            '\u200Fنقش مخفی شما: %s\nعضویت حزبی شما: %s' % (role, party)
        )


def print_player_info(player_number):
    if player_number == 5:
        return '\u200F۳ لیبرال، ۱ فاشیست و هیتلر وجود دارد. هیتلر می‌داند فاشیست چه کسی است.'
    elif player_number == 6:
        return '\u200F۴ لیبرال، ۱ فاشیست و هیتلر وجود دارد. هیتلر می‌داند فاشیست چه کسی است.'
    elif player_number == 7:
        return '\u200F۴ لیبرال، ۲ فاشیست و هیتلر وجود دارند. هیتلر نمی‌داند فاشیست‌ها چه کسانی هستند.'
    elif player_number == 8:
        return '\u200F۵ لیبرال، ۲ فاشیست و هیتلر وجود دارند. هیتلر نمی‌داند فاشیست‌ها چه کسانی هستند.'
    elif player_number == 9:
        return '\u200F۵ لیبرال، ۳ فاشیست و هیتلر وجود دارند. هیتلر نمی‌داند فاشیست‌ها چه کسانی هستند.'
    elif player_number == 10:
        return '\u200F۶ لیبرال، ۳ فاشیست و هیتلر وجود دارند. هیتلر نمی‌داند فاشیست‌ها چه کسانی هستند.'


def inform_fascists(bot, game, player_number):
    log.info('inform_fascists called')

    for uid in game.playerlist:
        role = game.playerlist[uid].role
        if role == ROLE_FASCIST:
            fascists = game.get_fascists()
            if player_number > 6:
                fstring = ""
                for f in fascists:
                    if f.uid != uid:
                        fstring += f.name + ", "
                fstring = fstring[:-2]
                bot.send_message(uid, '\u200Fهم‌حزبی‌های فاشیست شما: %s' % fstring)
            blue = game.get_blue()
            bot.send_message(uid, '\u200Fهیتلر این است: %s' % blue.name)
        elif role == ROLE_HITLER:
            if player_number <= 6:
                fascists = game.get_fascists()
                bot.send_message(uid, '\u200Fهم‌حزبی فاشیست شما: %s' % fascists[0].name)
        elif role == ROLE_LIBERAL:
            pass
        else:
            log.error("inform_fascists: can\'t handle the role %s" % role)


def get_membership(role):
    log.info('get_membership called')
    if role in (ROLE_FASCIST, ROLE_HITLER):
        return PARTY_FASCIST
    elif role == ROLE_LIBERAL:
        return PARTY_LIBERAL
    else:
        return None


def increment_player_counter(game):
    log.info('increment_player_counter called')
    if game.board.state.player_counter < len(game.player_sequence) - 1:
        game.board.state.player_counter += 1
    else:
        game.board.state.player_counter = 0


def shuffle_policy_pile(bot, game):
    log.info('shuffle_policy_pile called')
    if len(game.board.policies) < 3:
        game.board.discards += game.board.policies
        game.board.policies = random.sample(game.board.discards, len(game.board.discards))
        game.board.discards = []
        bot.send_message(
            game.cid,
            '\u200Fکارت‌های کافی در دستهٔ سیاست باقی نمانده بود؛ بقیه را با دستهٔ دورریز مخلوط کردم!'
        )


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    GamesController.init() #Call only once
    #initialize_testdata()

    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", Commands.command_start))
    dp.add_handler(CommandHandler("help", Commands.command_help))
    dp.add_handler(CommandHandler("board", Commands.command_board))
    dp.add_handler(CommandHandler("rules", Commands.command_rules))
    dp.add_handler(CommandHandler("version", Commands.command_version))
    dp.add_handler(CommandHandler("ping", Commands.command_ping))
    dp.add_handler(CommandHandler("symbols", Commands.command_symbols))
    dp.add_handler(CommandHandler("stats", Commands.command_stats))
    dp.add_handler(CommandHandler("newgame", Commands.command_newgame))
    dp.add_handler(CommandHandler("startgame", Commands.command_startgame))
    dp.add_handler(CommandHandler("cancelgame", Commands.command_cancelgame))
    dp.add_handler(CommandHandler("join", Commands.command_join))
    dp.add_handler(CommandHandler("votes", Commands.command_votes))
    dp.add_handler(CommandHandler("calltovote", Commands.command_calltovote))

    dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)_chan_(.*)", callback=nominate_chosen_chancellor))
    dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)_insp_(.*)", callback=choose_inspect))
    dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)_choo_(.*)", callback=choose_choose))
    dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)_kill_(.*)", callback=choose_kill))
    dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)_(yesveto|noveto)", callback=choose_veto))
    dp.add_handler(CallbackQueryHandler(pattern=POLICY_CALLBACK_PATTERN, callback=choose_policy))
    dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)_(Ja|Nein)", callback=handle_voting))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
