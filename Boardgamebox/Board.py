from Constants.Cards import (
    ACTION_CHOOSE,
    ACTION_INSPECT,
    ACTION_KILL,
    ACTION_POLICY,
    ACTION_WIN,
    playerSets,
    policies,
)
import random
from Boardgamebox.State import State


class Board(object):
    def __init__(self, playercount, game):
        self.state = State()
        self.num_players = playercount
        self.fascist_track_actions = playerSets[self.num_players]["track"]
        self.policies = random.sample(policies, len(policies))
        self.game = game
        self.discards = []
        self.previous = []

    def print_board(self):
        board = "\u200F--- اقدامات لیبرال‌ها ---\n"
        for i in range(5):
            if i < self.state.liberal_track:
                board += u"\U0001F7E6" + " " # blue square
            elif i >= self.state.liberal_track and i == 4:
                board += u"\U0001F54A" + " " #dove
            else:
                board += u"\u2B1C\uFE0F" + " " #empty
        board += "\n\u200F--- اقدامات فاشیست‌ها ---\n"
        for i in range(6):
            if i < self.state.fascist_track:
                board += u"\U0001F7E5" + " " # red square
            else:
                action = self.fascist_track_actions[i]
                if action is None:
                    board += u"\u2B1C\uFE0F" + " "  # empty
                elif action == ACTION_POLICY:
                    board += u"\U0001F52E" + " " # crystal
                elif action == ACTION_INSPECT:
                    board += u"\U0001F50E" + " " # inspection glass
                elif action == ACTION_KILL:
                    board += u"\U0001F5E1" + " " # knife
                elif action == ACTION_WIN:
                    board += u"\u2620" + " " # skull
                elif action == ACTION_CHOOSE:
                    board += u"\U0001F454" + " " # tie

        board += "\n\u200F--- شمارندهٔ انتخابات ---\n"
        for i in range(3):
            if i < self.state.failed_votes:
                board += u"\u2716\uFE0F" + " " #X
            else:
                board += u"\u2B1C\uFE0F" + " " #empty

        board += "\n\u200F--- ترتیب ریاست‌جمهوری  ---\n"
        for player in self.game.player_sequence:
            board += player.name + " " + u"\u27A1\uFE0F" + " "
        board = board[:-3]
        board += u"\U0001F501"
        board += "\n\n\u200Fهنوز " + str(len(self.policies)) + " کارت سیاست در دسته باقی مانده است."
        if self.state.fascist_track >= 3:
           board += "\n\n" + u"\u203C\uFE0F" + " \u200Fمراقب باشید: اگر هیتلر به عنوان صدراعظم انتخاب شود، فاشیست‌ها بازی را می‌برند! " + u"\u203C\uFE0F"
        if len(self.state.not_blues) > 0:
            board += "\n\n\u200Fما می‌دانیم که بازیکنان زیر هیتلر نیستند زیرا پس از سه سیاست فاشیستی به عنوان صدراعظم انتخاب شده‌اند:\n"
            for nh in self.state.not_blues:
                board += nh.name + ", "
            board = board[:-2]
        return board
