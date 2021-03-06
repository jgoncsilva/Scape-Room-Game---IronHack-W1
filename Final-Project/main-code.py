import copy
import pandas as pd
from datetime import datetime
from collections import OrderedDict
from dictionaries import *

# define which items/rooms are related

object_relations_init = {
    "game room": [couch, piano, door_a, snake],
    "living room": [dinning_table, door_c, door_d, safe, bookcase],
    "couch": [],
    "piano": [key_a],
    "outside": [door_d],
    "dining table": [],
    "safe": [key_d],
    "bookcase": [],
    "bedroom 1": [queen_bed, door_a, door_b, door_c],
    "bedroom 2": [dresser, double_bed, door_b, door_e],
    "double bed": [key_c],
    "dresser": [],
    "queen bed": [key_b],
    "door a": [game_room, bedroom_1],
    "door b": [bedroom_1, bedroom_2],
    "door c": [bedroom_1, living_room],
    "door d": [living_room, outside],
    "door e": [bedroom_2]
}

# define game state. Do not directly change this dict.
# Instead, when a new game starts, make a copy of this
# dict and use the copy to store gameplay state. This 
# way you can replay the game multiple times.

INIT_GAME_STATE = {
    "current_room": game_room,
    "keys_collected": [],
    "target_room": outside,
}


def linebreak():
    """
    Print a line break
    """
    print("\n\n")


# Before starts the game

users_deaths = OrderedDict()
users_wins = OrderedDict()

 #Before starts the game

start_time = 0

def start_game():
    global start_time
    global player_name
    start_time = datetime.now()
    player_name = input("So whats my name? wrong answers only: ").strip()
    print(player_name)
    """
    Start the game
    """
    print("You wake up on a couch and find yourself in a strange house with no windows which you have never been to before. You don't remember why you are here and what had happened before. You feel some unknown danger is approaching and you must get out of the house, NOW!")
    explore_room(game_state["current_room"])
    play_room(game_state["current_room"])


def play_room(room):
    """
    Play a room. First check if the room being played is the target room.
    If it is, the game will end with success. Otherwise, let player either 
    explore (list all items in this room) or examine an item found here.
    """

    game_state["current_room"] = room
    if (game_state["current_room"] == game_state["target_room"]):
        print("Congrats! You can sing: 'Oh AAAAA ohhhhh I'm still alive\n")

        # Total time
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        if player_name in users_wins.keys():
            users_wins[player_name] = min(total_time, users_wins[player_name])
        else:
            users_wins[player_name] = total_time

        pandaseries = pd.Series(users_wins)
        print(pandaseries.sort_values(ascending=True)[0:3])
        
        answer = input("Do you want to play again? Enter 'yes' or 'no'").strip().lower()
        if answer == 'yes':
            global object_relations
            game_state['keys_collected'] = []
            game_state['current_room'] = game_room
            game_state['target_room'] = outside
            object_relations = copy.deepcopy(object_relations_init)
            start_game()

    else:
        intended_action = input("What would you like to do? Type 'explore' or 'examine'?").strip().lower()
        if intended_action == "explore":
            explore_room(room)
            play_room(room)
        elif intended_action == "examine":
            examine_item(input("What would you like to examine?").strip().lower())
        else:
            print("Not sure what you mean. Type 'explore' or 'examine'.")
            play_room(room)
        linebreak()


def explore_room(room):
    """
    Explore a room. List all items belonging to this room.
    """
    items = [i["name"] for i in object_relations[room["name"]]]
    print("You explore the room. This is the " + room["name"] + ". You find " + ", ".join(items) + '\n')


def get_next_room_of_door(door, current_room):
    """
    From object_relations, find the two rooms connected to the given door.
    Return the room that is not the current_room.
    """
    connected_rooms = object_relations[door["name"]]
    for room in connected_rooms:
        if (not current_room == room):
            return room


def examine_item(item_name):
    """
    Examine an item which can be a door or furniture.
    First make sure the intended item belongs to the current room.
    Then check if the item is a door. Tell player if key hasn't been 
    collected yet. Otherwise ask player if they want to go to the next
    room. If the item is not a door, then check if it contains keys.
    Collect the key if found and update the game state. At the end,
    play either the current or the next room depending on the game state
    to keep playing.
    """
    current_room = game_state["current_room"]
    next_room = ""
    output = None

    for item in object_relations[current_room["name"]]:

        if (item["name"] == item_name):
            output = "You examine the " + item_name + ". "
            if (item["type"] == "door"):

                have_key = False
                for key in game_state["keys_collected"]:
                    if (key["target"] == item):
                        have_key = True
                if (have_key):
                    output += "You unlock it with a key you have.\n"
                    next_room = get_next_room_of_door(item, current_room)
                else:
                    output += "It is locked but you don't have the key."

            elif (item["type"] == "deadly"):
                print('''you're dead\n  
             ____
            / . .\\
            \  ---<
             \  /
   __________/ /
-=:___________/\n''')
                game_over()

            elif (item["type"] == 'trap'):
                next_room = game_room
                explore_room(next_room)
                play_room(next_room)

            elif (item["type"] == "safe"):
                print(output)
                output = ""
                if (input("Introduce the code to the safe ***: ").lower() == 'sos'):
                    # if the code is correct
                    if (item["name"] in object_relations and len(object_relations[item["name"]]) > 0):
                        item_found = object_relations[item["name"]].pop()
                        game_state["keys_collected"].append(item_found)
                        output = "You open the safe and find " + item_found["name"] + " inside.\n"
                    else:
                        output += "There isn't anything interesting inside.\n"
                else:
                    # if the code is not correct
                    output += "It is locked and the code is incorrect.\n"

            elif(item["type"] == "bookcase"):
                print(output + (item['description'] + "\n"))
                output = ""
                answer = input("What theme are you looking for?").strip().lower()
                if(answer.count('morse') > 0):
                    print(eng_to_morse_str)
                elif(answer.count('cod') > 0):
                    output += "You find a Cryptography book. You scan through the pages and land on a page about the origin of Morse Code.\n Time is running out. I need to get out of here.\n"
                else:
                    output += "No time for that. Time is running out. \n"
            else:
                if (item["name"] in object_relations and len(object_relations[item["name"]]) > 0):
                    item_found = object_relations[item["name"]].pop()
                    game_state["keys_collected"].append(item_found)
                    output += "You find " + item_found["name"] + ".\n"
                else:
                    output += (item['description'] + "\n") if 'description' in item.keys() else "There isn't anything interesting about it.\n"
            print(output)
            break

    if (output is None):
        print("The item you requested is not found in the current room.")
    if next_room and input("Do you want to go to the next room? Enter 'yes' or 'no'").strip().lower() == 'yes':
        explore_room(next_room)
        play_room(next_room)
    else:
        play_room(current_room)



def game_over():
    global users_deaths
    global player_name

    # Total time
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()

    if player_name in users_deaths.keys():
        users_deaths[player_name] = min(total_time, users_deaths[player_name])
    else:
        users_deaths[player_name] = total_time

    pandaseries = pd.Series(users_deaths)
    print(pandaseries.sort_values(ascending=True)[0:3])

    answer = input("Do you want to play again? Enter 'yes' or 'no'").strip().lower()
    if answer == 'yes':

        '''
        object_relations = object_relations_int.copy() 
        is ambiguous, it could be referring to a global variable, or it could be creating a new local variable called 
        "object_relations". In this case, Python defaults to assuming it is a local variable unless the global keyword 
        has already been used.
        '''

        global object_relations
        game_state['keys_collected'] = []
        game_state['current_room'] = game_room
        game_state['target_room'] = outside
        object_relations = copy.deepcopy(object_relations_init)

        start_game()

    elif answer == 'no':
        exit()
    else:
        print("that's not a valid answer")
        game_over()

global game_state
game_state = copy.deepcopy(INIT_GAME_STATE)
# A deep copy constructs a new compound object and then, recursively, inserts copies into it of the objects found in the original.
object_relations = copy.deepcopy(object_relations_init)

start_game()

