import json
import random
import time


MAX_FISH = 10

class Fish:
    def __init__(self, name, weight_min, weight_max, catch_rate):
        self.name = name
        self.weight_min = weight_min
        self.weight_max = weight_max
        self.catch_rate = catch_rate

    def get_weight(self):
        return random.uniform(self.weight_min, self.weight_max)

class Lake:
    def __init__(self, name, fish_types):
        self.name = name
        self.fish_types = fish_types

    def get_random_fish(self, bait):
        adjusted_fish = [
            (fish, fish.catch_rate * bait.catch_rate_modifier)
            for fish in self.fish_types
        ]
        total_weight = sum(adjusted_rate for _, adjusted_rate in adjusted_fish)
        fish = random.choices(
            [fish for fish, _ in adjusted_fish],
            weights=[adjusted_rate / total_weight for _, adjusted_rate in adjusted_fish],
            k=1
        )
        return fish[0]

class Bait:
    def __init__(self, name, catch_rate_modifier):
        self.name = name
        self.catch_rate_modifier = catch_rate_modifier

class FishingGame:
    def __init__(self, lakes, baits):
        self.lakes = lakes
        self.baits = baits
        self.current_lake = None
        self.current_bait = None
        self.catch_history = []
        self.coins = 10 
        self.start_time = None
        self.game_mode = None

    def show_lakes(self):
        print("Available lakes:")
        for lake in self.lakes:
            print(f"- {lake.name}")

    def show_baits(self):
        print("Available baits:")
        for bait in self.baits:
            print(f"- {bait.name} (Catch rate modifier: {bait.catch_rate_modifier})")

    def change_location(self, lake_name):
        for lake in self.lakes:
            if lake.name == lake_name:
                self.current_lake = lake
                print(f"Moved to {lake_name}.")
                return
        print("Lake not found.")

    def change_bait(self, bait_name):
        for bait in self.baits:
            if bait.name == bait_name:
                self.current_bait = bait
                print(f"Changed bait to {bait_name}.")
                return
        print("Bait not found.")

    def cast_line(self):
        if not self.current_lake:
            print("You need to select a lake first.")
            return
        if not self.current_bait:
            print("You need to select a bait first.")
            return

        fish = self.current_lake.get_random_fish(self.current_bait)
        
        final_catch_rate = min(fish.catch_rate * self.current_bait.catch_rate_modifier, 0.98)
        if random.random() < final_catch_rate:
            weight = fish.get_weight()
            self.catch_history.append((fish.name, weight))
            print(f"Wow! You caught a {fish.name} weighing {weight:.2f} kg!")
        else:
            print("Oops.The fish got away!")

    def show_catch(self):
        if not self.catch_history:
            print("No fish caught yet.")
        else:
            for fish, weight in self.catch_history:
                print(f"{fish} weighing {weight:.2f} kg")

    def sell_fish(self):
        total_weight = sum(weight for _, weight in self.catch_history)
        self.coins += total_weight
        self.catch_history = []
        print(f"Sold all fish for {total_weight:.2f} coins. Total coins: {self.coins:.2f}")

    def is_game_over(self):
        if self.game_mode == '10fish' and len(self.catch_history) >= 10:
            return True
        if self.game_mode == 'timed' and self.coins < 10:
            return True
        return False

    def start_timed_mode(self):
        self.start_time = time.time()

    def update_timed_mode(self):
        if self.start_time:
            elapsed_minutes = (time.time() - self.start_time) / 60
            if elapsed_minutes >= 1:
                self.coins -= 10
                self.start_time = time.time()
                print(f"1 minute passed. 10 coins deducted. Current coins: {self.coins:.2f}")
                if self.coins < 10:
                    print("Not enough coins to continue. Sell fish to continue or quit.")
                    self.show_catch()
                    while True:
                        sell_choice = input("Do you want to sell your fish to continue? (yes/no): ").strip().lower()
                        if sell_choice == 'yes':
                            self.sell_fish()
                            if self.coins >= 10:
                                print("You can continue fishing.")
                                self.start_time = time.time()
                                break
                            else:
                                print("Not enough coins to continue. Game over.")
                                return True
                        elif sell_choice == 'no':
                            print("Game over.")
                            return True
                        else:
                            print("You have to choose yes or no.")
        return False

def load_fish_data(file_path):
    with open(file_path, 'r') as file:
        fish_data = json.load(file)
    fish_list = [Fish(f['name'], f['weight_min'], f['weight_max'], f['catch_rate']) for f in fish_data]
    return fish_list

def load_lake_data(file_path, fish_list):
    with open(file_path, 'r') as file:
        lake_data = json.load(file)
    lakes = []
    for lake in lake_data:
        fish_types = [fish for fish in fish_list if fish.name in lake['fish_types']]
        lakes.append(Lake(lake['name'], fish_types))
    return lakes

def load_bait_data(file_path):
    with open(file_path, 'r') as file:
        bait_data = json.load(file)
    baits = [Bait(b['name'], b['catch_rate_modifier']) for b in bait_data]
    return baits

def main():
    print("Welcome to the Fishing Game! Good luck!")
    
    fish_list = load_fish_data('fish_data.json')
    lakes = load_lake_data('lake_data.json', fish_list)
    baits = load_bait_data('bait_data.json')
    game = FishingGame(lakes, baits)

    while not game.game_mode:
        mode = input("Choose game mode (10fish/timed): ").strip().lower()
        if mode in ['10fish', 'timed']:
            game.game_mode = mode
            if mode == 'timed':
                game.start_timed_mode()
        else:
            print("Invalid game mode. Choose either '10fish' or 'timed'.")

    game.show_lakes()
    game.show_baits()

    while not game.current_lake:
        lake_name = input("Select a lake: ").strip()
        game.change_location(lake_name)

    while not game.current_bait:
        bait_name = input("Select a bait: ").strip()
        game.change_bait(bait_name)

    while True:
        if game.is_game_over():
            if game.game_mode == '10fish' and len(game.catch_history) >= MAX_FISH:
                while True:
                    sell_choice = input(f"You have caught {MAX_FISH} fish. Do you want to sell them before ending the game? (yes/no): ").strip().lower()
                    if sell_choice == 'yes':
                        game.sell_fish()
                        break
                    elif sell_choice == 'no':
                        break
                    else:
                        print("You have to choose yes or no.")
                print(f"Game over! You caught {MAX_FISH} fish.")
            elif game.game_mode == 'timed' and game.coins < 10:
                print("Game over! You don't have enough coins to continue.")
            break

        if game.game_mode == 'timed' and game.update_timed_mode():
            break

        command = input("Enter command (cast, change bait, change location, show catch, sell fish, quit): ").strip().lower()
        if command == 'cast':
            game.cast_line()
        elif command == 'change bait':
            game.show_baits()
            bait_name = input("Enter new bait: ").strip()
            game.change_bait(bait_name)
        elif command == 'change location':
            game.show_lakes()
            lake_name = input("Enter lake name: ").strip()
            game.change_location(lake_name)
        elif command == 'show catch':
            game.show_catch()
        elif command == 'sell fish':
            game.sell_fish()
        elif command == 'quit':
            break
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
