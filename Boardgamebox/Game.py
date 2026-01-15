from random import shuffle

from Constants.Cards import ROLE_FASCIST, ROLE_HITLER


class Game(object):
    def __init__(self, cid, initiator):
        self.playerlist = {}
        self.player_sequence = []
        self.cid = cid
        self.board = None
        self.initiator = initiator
        self.dateinitvote = None

    def add_player(self, uid, player):
        self.playerlist[uid] = player

    def get_blue(self):
        for uid in self.playerlist:
            if self.playerlist[uid].role == ROLE_HITLER:
                return self.playerlist[uid]

    def get_fascists(self):
        fascists = []
        for uid in self.playerlist:
            if self.playerlist[uid].role == ROLE_FASCIST:
                fascists.append(self.playerlist[uid])
        return fascists

    def shuffle_player_sequence(self):
        for uid in self.playerlist:
            self.player_sequence.append(self.playerlist[uid])
        shuffle(self.player_sequence)

    def remove_from_player_sequence(self, player):
        self.player_sequence = [p for p in self.player_sequence if p.uid != player.uid]

    def print_roles(self):
        rtext = ""
        if self.board is None:
            # game was not started yet
            return rtext
        else:
            for p in self.playerlist:
                line = '\u200F' + self.playerlist[p].name + ' '
                if self.playerlist[p].is_dead:
                    line += '(مرده) '
                line += 'نقش مخفی‌اش ' + self.playerlist[p].role + '\n'
                rtext += line
            return rtext

