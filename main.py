__author__ = 'dg'

from copy import deepcopy
from random import shuffle

class Card:
    def __init__(self, num=0, ace=False):
        self.value = num
        self.ace = ace

    def __str__(self):
        return "A" if self.ace else str(self.value)


class Deck(list):
    def __init__(self):
        cards = [Card(n) for n in range(2,10)]
        cards += [Card(10) for _ in range(4)]
        cards.append(Card(ace=True))
        cards = deepcopy(cards) + deepcopy(cards) + deepcopy(cards) + deepcopy(cards)
        list.__init__(self, cards)
        shuffle(self)
        self.discard = []

    def draw(self):
        if len(self):
            return self.pop(0)
        self += self.discard
        shuffle(self)
        return self.pop(0)


class Table:
    def __init__(self, decks=1):
        self.decks = decks
        self.deck = Deck()

        self.players = [Dealer()]

    def settup(self):
        for player in self.players:
            player.deck = self.deck

    def play(self):
        for player in self.players:
            self.deck.discard += player.hand
            player.hand = []

        for player in self.players: player.draw(2)

        for player in self.players[1:] + self.players[0:1]:
            player.act(self)

        for player in self.players[1:]:
            if player.total() > self.players[0].total():
                player.win()
            elif player.total() == self.players[0].total():
                player.tie()
            else: player.lose()

    def tablestate(self, peep):
        return {'t': self,
                'remaining': len(self.deck),
                'dealer': self.players[0].hand[0],
                'players': [str(p) for p in self.players[1:] if p is not peep]}


class Person:
    def __init__(self):
        self.hand = []
        self.money = 0
        self.deck = None

    def total(self):
        total=0
        aces=0
        for c in self.hand:
            if c.value:
                total += c.value
            else:
                aces += 1
                total += 11
        while total > 21 and aces > 0:
            aces -= 1
            total -= 10

        if total > 21: total = 0
        return total

    def draw(self, number=1):
        for _ in range(number):
            self.hand.append(self.deck.draw())

    def win(self):
        self.money += 2

    def lose(self):
        self.money -= 2

    def tie(self):
        pass

    def __str__(self):
        return ' '.join(str(c) for c in self.hand) + ' (=' + str(self.total()) + ')'


class Player(Person):
    def __init__(self):
        Person.__init__(self)

    def __str__(self):
        return 'you have: ' + Person.__str__(self)+ '; and $' + str(self.money)

    def act(self, table):
        table = table.tablestate(self)
        input()
        print('there are', table['remaining'], 'cards left in the deck')
        print('DEALER:', table['dealer'], '#')
        print('other players:', ', '.join(table['players']))
        while True:
            print(self)
            x = input('l to hit, enter to stand :: ')
            if x == 'l' or x == 'h':
                self.draw()
                if self.total() == 0:
                    print(self)
                    input('THOU HAST BEEN SHRECKED')
                    break
            else: break

    def win(self):
        print('yay you win!')
        Person.win(self)

    def lose(self):
        print('oh you lost')
        Person.lose(self)

    def tie(self):
        print('a tie! how delightful')



class Dealer(Person):
    def __init__(self):
        Person.__init__(self)

    def __str__(self):
        return ' DEALER: ' + Person.__str__(self)

    def act(self, p):
        while self.total() < 17:
            for peep in p.players:
                if self.total() < peep.total():
                    break  # continue in the while loop
            else: break

            self.draw()

            if self.total() == 0: break

class ShowyDealer(Dealer):
    def __init__(self):
        Dealer.__init__(self)

    def act(self, p):
        print('DEALER:',Person.__str__(self),'(' + str(self.total()) + ')')
        while self.total() < 17:
            for peep in p.players:
                if self.total() < peep.total():
                    break  # continue in the while loop
            else:
                break

            print('DEALER HITS: ', end = '')
            self.draw()
            print(Person.__str__(self),'(' + str(self.total()) + ')')

            if self.total() == 0:
                print('DEALER BUSTS')
                break


class GenericPlayer(Person):
    def act(self, p):
        while 0 < self.total() < 17:
            self.draw()

class HighLow(Person):
    def __init__(self):
        self.count = 0
        self.bet = 1
        Person.__init__(self)

    def act(self, p):
        self.bet = min(1, self.count)

        inview = [p.players[0].hand[0]]
        for hand in map(lambda x: x.hand, p.players[1:]):
            inview += hand

        for card in inview:
            if card.value < 6 and not card.ace:
                self.count += 1
            if card.value == 10 or card.ace:
                self.count -= 1

    def win(self):
        self.money += self.bet

    def lose(self):
        self.money -= self.bet




'''
t = Table(3)
t.players.append(GenericPlayer())
t.players.append(GenericPlayer())
t.players.append(Player())
t.players[0] = ShowyDealer(t)
t.settup()

while True:
    t.play()'''




t = Table(3)
for _ in range(3): t.players.append(GenericPlayer())
t.players.append(HighLow())
t.settup()

for i in range(5000):
    t.play()

print(' '.join(str(t.players[n].money) for n in range(1,5)))

print(sum(x.money for x in t.players[1:]))