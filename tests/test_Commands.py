from __future__ import absolute_import
import os
import random
import unittest

from telegram import User
from Commands import *
import GamesController
from Boardgamebox.Board import Board
from Boardgamebox.Game import Game
from Boardgamebox.Player import Player

from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from ptbtest import ChatGenerator
from ptbtest import MessageGenerator
from ptbtest import Mockbot
from ptbtest import UserGenerator


class TestCommands(unittest.TestCase):
    def setUp(self):
        # For use within the tests we nee some stuff. Starting with a Mockbot
        self.bot = Mockbot()
        # Updater expects a Request-like object on the bot
        self.bot.request = type("RequestStub", (), {"con_pool_size": 100})()
        # Updater polling tries to remove a webhook
        self.bot.delete_webhook = lambda *args, **kwargs: True
        # ptbtest Mockbot uses an old User signature; patch per-instance for PTB 12.8
        mockbot = self.bot
        def _patched_get_me(*_args, **_kwargs):
            mockbot.bot = User(0, "Mockbot", True, last_name="Bot", username=mockbot._username)
            return mockbot.bot

        mockbot.getMe = _patched_get_me
        def _patched_get_user(self_gen, first_name=None, last_name=None, username=None, id=None):
            if not first_name:
                first_name = random.choice(self_gen.FIRST_NAMES)
            if not last_name:
                last_name = random.choice(self_gen.LAST_NAMES)
            if not username:
                username = first_name + last_name
            return User(id or self_gen.gen_id(), first_name, False, last_name=last_name, username=username)

        UserGenerator.get_user = _patched_get_user
        # Some generators for users and chats
        self.ug = UserGenerator()
        self.cg = ChatGenerator()
        # And a Messagegenerator and updater (for use with the bot.)
        self.mg = MessageGenerator(self.bot)
        self.updater = Updater(bot=self.bot)
        GamesController.init()


    def test_ping(self):
        # Then register the handler with he updater's dispatcher and start polling
        self.updater.dispatcher.add_handler(CommandHandler("ping", command_ping))
        # create with random user
        update = self.mg.get_message(text="/ping", parse_mode="Markdown")
        self.updater.dispatcher.process_update(update)
        # sent_messages is the list with calls to the bot's outbound actions. Since we hope the message we inserted
        # only triggered one sendMessage action it's length should be 1.
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], "pong")


    def test_start(self):
        self.updater.dispatcher.add_handler(CommandHandler("start", command_start))
        update = self.mg.get_message(text="/start", parse_mode="Markdown")
        self.updater.dispatcher.process_update(update)
        self.assertEqual(len(self.bot.sent_messages), 2)
        start = self.bot.sent_messages[0]
        self.assertEqual(start['method'], "sendMessage")
        self.assertIn("\u0631\u0627\u0632 \u0647\u06cc\u062a\u0644\u0631", start['text'])
        help = self.bot.sent_messages[1]
        self.assertEqual(help['method'], "sendMessage")
        self.assertIn("\u062f\u0633\u062a\u0648\u0631\u0647\u0627\u06cc \u0632\u06cc\u0631 \u062f\u0631 \u062f\u0633\u062a\u0631\u0633 \u0647\u0633\u062a\u0646\u062f", help['text'])


    def test_symbols(self):
        self.updater.dispatcher.add_handler(CommandHandler("symbols", command_symbols))
        update = self.mg.get_message(text="/symbols", parse_mode="Markdown")
        self.updater.dispatcher.process_update(update)
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertIn("\u0646\u0645\u0627\u062f\u0647\u0627\u06cc \u0632\u06cc\u0631 \u0645\u0645\u06a9\u0646 \u0627\u0633\u062a \u0631\u0648\u06cc \u0635\u0641\u062d\u0647 \u0638\u0627\u0647\u0631 \u0634\u0648\u0646\u062f", sent['text'])


    def test_version(self):
        old_app = os.environ.get("APP_VERSION")
        old_sha = os.environ.get("GIT_SHA")
        old_source = os.environ.get("SOURCE_VERSION")
        old_github = os.environ.get("GITHUB_SHA")
        try:
            os.environ["APP_VERSION"] = "v10"
            os.environ["GIT_SHA"] = "81b1208"
            os.environ.pop("SOURCE_VERSION", None)
            os.environ.pop("GITHUB_SHA", None)
            self.updater.dispatcher.add_handler(CommandHandler("version", command_version))
            update = self.mg.get_message(text="/version", parse_mode="Markdown")
            self.updater.dispatcher.process_update(update)
            self.assertEqual(len(self.bot.sent_messages), 1)
            sent = self.bot.sent_messages[0]
            self.assertEqual(sent["method"], "sendMessage")
            self.assertIn("\u0646\u0633\u062e\u0647", sent["text"])
            self.assertIn("81b1208", sent["text"])
            self.assertNotIn("v10", sent["text"])
            self.assertNotIn("\n", sent["text"])
        finally:
            if old_app is None:
                os.environ.pop("APP_VERSION", None)
            else:
                os.environ["APP_VERSION"] = old_app
            if old_sha is None:
                os.environ.pop("GIT_SHA", None)
            else:
                os.environ["GIT_SHA"] = old_sha
            if old_source is None:
                os.environ.pop("SOURCE_VERSION", None)
            else:
                os.environ["SOURCE_VERSION"] = old_source
            if old_github is None:
                os.environ.pop("GITHUB_SHA", None)
            else:
                os.environ["GITHUB_SHA"] = old_github

    def test_board_when_there_is_no_game(self):
        self.updater.dispatcher.add_handler(CommandHandler("board", command_board))
        update = self.mg.get_message(text="/board", parse_mode="Markdown")
        self.updater.dispatcher.process_update(update)
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertIn("\u0647\u06cc\u0686 \u0628\u0627\u0632\u06cc\u200c\u0627\u06cc \u062f\u0631 \u0627\u06cc\u0646 \u0686\u062a \u0648\u062c\u0648\u062f \u0646\u062f\u0627\u0631\u062f", sent['text'])


    def test_board_when_game_is_not_running(self):
        game = Game(-999, 12345)
        GamesController.games[-999] = game
        self.updater.dispatcher.add_handler(CommandHandler("board", command_board))
        chat = self.cg.get_chat(cid=-999)
        update = self.mg.get_message(chat=chat, text="/board", parse_mode="Markdown")
        self.updater.dispatcher.process_update(update)
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertIn("\u0647\u06cc\u0686 \u0628\u0627\u0632\u06cc \u062f\u0631 \u062d\u0627\u0644 \u0627\u062c\u0631\u0627 \u062f\u0631 \u0627\u06cc\u0646 \u0686\u062a \u0648\u062c\u0648\u062f \u0646\u062f\u0627\u0631\u062f", sent['text'])


    def test_board_when_game_is_running(self):
        game = Game(-999, 12345)
        game.board = Board(5, game)
        GamesController.games[-999] = game
        self.updater.dispatcher.add_handler(CommandHandler("board", command_board))
        chat = self.cg.get_chat(cid=-999)
        update = self.mg.get_message(chat=chat, text="/board", parse_mode="Markdown")
        self.updater.dispatcher.process_update(update)
        self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[0]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertIn("\u200F--- \u0627\u0642\u062f\u0627\u0645\u0627\u062a \u0644\u06cc\u0628\u0631\u0627\u0644\u200c\u0647\u0627 ---", sent['text'])
