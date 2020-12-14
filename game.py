import qsharp
from random import randint
import time
from SimpleCardGame import PlayAndMeasure
from io import StringIO 
import sys

class Card:
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return self.name

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class Game:
    def __init__(self, card_frequencies, cards_per_player, player_names):
        self.card_frequencies = card_frequencies
        self.cards_per_player = cards_per_player    
        self.player_names = player_names

        self.cards = []
        self.players = []
        self.measurements = [0, 0]
        self.states = ['|0⟩\t1 + 0𝑖', '|1⟩\t0 + 0𝑖', '|2⟩\t0 + 0𝑖', '|3⟩\t0 + 0𝑖']
        self.player_turn = 0
        self.player_updates = {"win point": "You earned a point!",
                              "lose point": "You lost a point!",
                               "no win or loss": "You didn't win or lose a point!",
                              "win game": "You won the game!",
                              "lose game": "You lost the game!"}
        self.game_over = False
        
        self.q1_hist = []
        self.q2_hist = []

        self.initialize()

    def initialize(self):
        self.initialize_cards()
        self.initialize_players()
        self.deal_cards()
        
    def initialize_players(self):
        score = 0
        for name in self.player_names:
            player = Player(name)
            player.score = score
            self.players.append(player)
            
    def initialize_cards(self):
        for card_name in self.card_frequencies:
            freq = self.card_frequencies[card_name]
            for i in range(freq):
                self.cards.append(Card(card_name))
    
    def deal_cards(self):
        for i in range(self.cards_per_player):
            for j in range(len(self.players)):
                player = self.players[j]
                idx = randint(0,len(self.cards)-1)
                player.cards.append(self.cards[idx])
                self.cards.pop(idx)
                
    def deal_card(self, player_idx):
        card_idx = randint(0,len(self.cards)-1)
        self.players[player_idx].cards.append(self.cards[card_idx])
        self.cards.pop(card_idx)
    
    def update_player_turn(self):
        if self.player_turn == len(self.players) - 1:
            self.player_turn = 0
        else:
            self.player_turn += 1
    
    def prompt_player_cards(self):
        cards = self.players[self.player_turn].prompt_cards(self.states)
        return cards
    
    def update_measurements(self, cards):
        with Capturing() as output:
            self.measurements = PlayAndMeasure.simulate(gates=cards, pastGatesQ1=self.q1_hist, pastGatesQ2=self.q2_hist)
        self.states = output
    
    def update_scores(self):
        status = "no win or loss"
        if sum(self.measurements) == 2:
            self.players[self.player_turn].score += 1
            status = "win point"
        elif sum(self.measurements) == 0:
            self.players[self.player_turn].score -= 1
            status = "lose point"
        self.send_player_updates(status)

    def get_scores(self):
        return [player.score for player in self.players]
        
    def get_scores_update(self):
        scores = self.get_scores()
        updates = ["Current scores"]
        for i in range(len(self.players)):
            player = self.players[i]
            updates.append("{}: {}".format(player.name, scores[i]))
        return updates
    
    def send_player_updates(self, status):
        if status in self.player_updates:
            state_update = "The resulting measurements are: {}\n".format(self.measurements)
            update = self.player_updates[status]
            self.players[self.player_turn].update(state_update + update)
            
    def send_players_play_updates(self, player_idx, card_names):
        player = self.players[player_idx]
        result = "didn't win or lose"
        if sum(self.measurements) == 2:
            result = "won"
        elif sum(self.measurements) == 0:
            result = "lost"
        for i in range(len(self.players)):
            if i != player_idx:
                update = "{} played {} and {} a point.".format(player.name, card_names, result)
                self.players[i].update(update)
    
    def send_players_score_updates(self):
        scores = "\n".join(self.get_scores_update())
        for player in self.players:
            player.update(scores)
                
    def update_histories(self, card1, card2):
        self.q1_hist.append(card1)
        self.q2_hist.append(card2)
                
    def play_a_round(self):
        card_names = self.prompt_player_cards()
        
        # qsharp script
        self.update_measurements(card_names)
        self.update_scores()
        self.update_histories(*tuple(card_names))
        
        self.send_players_play_updates(self.player_turn, card_names)
        
        if self.check_end_game():
            self.end_game()
        
        self.send_players_score_updates()
        self.deal_card(self.player_turn)
        self.deal_card(self.player_turn)
        self.update_player_turn()
        print()

    def play(self):
        # Tests
        player1 = input("Player 1, what is your name? ")
        player2 = input("Player 2, what is your name? ")
        g = Game(card_frequencies={"X": 3, "SWAP": 2, "H": 4, "C": 3, "Y": 3, "Z": 3},
                cards_per_player=5,
                player_names=[player1, player2])

        # print([str(card) for card in g.cards])
        # print(g.players[0])
        # print(g.players[1])
        # print(g.get_scores())
        # print()
        time.sleep(1)
        # g.prompt_player_cards()
        g.run()

    def run(self):
        while not self.check_end_game():
            self.play_a_round()
        self.end_game()
        
    def end_game(self):
        max_score = sorted([player.score for player in self.players])[-1]
        max_players = [player for player in self.players if player.score == max_score]
        if len(max_players) == 1:
            update = "Game Over! {} is the winner. ".format(max_players[0].name)
        else:
            update = "Game Over! {} are the winners. ".format(", ".join([p.name for p in max_players]))
        
        for player in self.players:
            if player.score == max_score:
                update2 = "Congratulations!"
                player.update(update+update2)
            else:
                update2 = "Better luck next time."
                player.update(update+update2)     
            
    def check_end_game(self):
        return len(self.cards) == 0
    
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.cards = []
        
    def card_is_valid(self, card_selected):
        for card in self.cards:
            if card.name.lower() == card_selected.lower():
                return True
        return False
    
    def update_cards(self, card_name):
        for i in range(len(self.cards)):
            card = self.cards[i]
            if card.name.lower() == card_name.lower():
                self.cards.pop(i)
                return
        print("ERROR: Card {} not found".format(card_name))
    
    def prompt_cards(self, current_states):
        card1 = input("{}, it's your turn. What card would you like to play for Q1?\nCurrent state:\n{}\nYour cards: {}\nYour play: ".format(self.name, '\n'.join(current_states), [str(card) for card in self.cards]))
        while(not self.card_is_valid(card1)):
            card1 = input("Invalid selection. Please try again.\nCurrent state:\n{}\nYour cards:\n{}\n".format(int(current_states),[str(card) for card in self.cards])) ## TODO: give better instructions
        self.update_cards(card1)
        
        if card1.lower() == 'swap':
            return [card1.upper(), card1.upper()]
        
        card2 = input("{}, it's your turn. What card would you like to play for Q2?\nCurrent state:\n{}\nYour cards: {}\nYour play: ".format(self.name, '\n'.join(current_states), [str(card) for card in self.cards]))
        while(not self.card_is_valid(card2) or (card1.lower() == 'c' and card2.lower() == 'c') or card2.lower() == 'swap'):  # can only use one control card
            card2 = input("Invalid selection. Please try again.\nCurrent state:\n{}\nYour cards: {}\n".format(int(current_states),[str(card) for card in self.cards])) ## TODO: give better instructions
        self.update_cards(card2)
        
        return [card1.upper(), card2.upper()]
    
    def update(self, string):
        print("[{}] {}".format(self.name,string))
        
    def __str__(self):
        return "{}\nScore: {}\nCards in Hand:{}".format(self.name, self.score, [str(card) for card in self.cards])

def play_game():
    # Tests
    player1 = input("Player 1, what is your name? ")
    player2 = input("Player 2, what is your name? ")
    g = Game(card_frequencies={"X": 3, "SWAP": 2, "H": 4, "C": 3, "Y": 3, "Z": 3},
            cards_per_player=5,
            player_names=[player1, player2])

    # print([str(card) for card in g.cards])
    # print(g.players[0])
    # print(g.players[1])
    # print(g.get_scores())
    # print()
    time.sleep(1)
    # g.prompt_player_cards()
    g.run()
    
