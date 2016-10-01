#!/usr/bin/python2
import socket
import json
import os
import random
import sys
from socket import error as SocketError
import errno
sys.path.append("../..")
import src.game.game_constants as game_consts
from src.game.character import *
from src.game.gamemap import *

# Game map that you can use to query 
gameMap = GameMap()

# --------------------------- SET THIS IS UP -------------------------
teamName = "Test"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "char1",
                 "ClassId": "Assassin"},
                {"CharacterName": "char2",
                 "ClassId": "Assassin"},
                {"CharacterName": "char3",
                 "ClassId": "Assassin"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    # Setup helper variables
    actions = []
    myteam = []
    enemyteam = []
    # Find each team and serialize the objects
    for team in serverResponse["Teams"]:
        if team["Id"] == serverResponse["PlayerInfo"]["TeamId"]:
            for characterJson in team["Characters"]:
                character = Character()
                character.serialize(characterJson)
                myteam.append(character)
        else:
            for characterJson in team["Characters"]:
                character = Character()
                character.serialize(characterJson)
                enemyteam.append(character)
# ------------------ You shouldn't change above but you can ---------------

    for character in myteam:
        if character.name == "char1":
            actions.append(char1Move(character,myteam, enemyteam))
        elif character.name == "char2":
            actions.append(char2Move(character,myteam, enemyteam))
        elif character.name == "char3":
            actions.append(char3Move(character,myteam, enemyteam))
        else:
            print "WE FUCKED UP->_>P>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    # If we found a target
    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }
# ---------------------------------------------------------------------

def char1Move(char, myteam, enemyteam):
    target = find_prioritized_enemy(enemyteam)
    action = None
    if target:
        for character in myteam:
            # If I am in range, either move towards target
            if character.in_range_of(target, gameMap):
                # Am I already trying to cast something?
                if character.casting is None:
                    cast = False
                    for abilityId, cooldown in character.abilities.items():
                        # Do I have an ability not on cooldown
                        if cooldown == 0:
                            # If I can, then cast it
                            ability = game_consts.abilitiesList[int(abilityId)]
                            # Get ability
                            action = {
                                "Action": "Cast",
                                "CharacterId": char.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(abilityId)
                            }
                            cast = True
                            break
                    # Was I able to cast something? Either wise attack
                    if not cast:
                        action = {
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        }
            else: # Not in range, move towards
                action = {
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                }
    else:
        target = get_a_target(enemyteam)
        action = {
                "Action": "Move",
                "CharacterId": char.id,
                "TargetId": target.id,
            }
    return action


def char2Move(char, myteam, enemyteam):
  action = char1Move(char, myteam, enemyteam)

  #logic goes here
  return action

def char3Move(char, myteam, enemyteam):
  action = char1Move(char, myteam, enemyteam)
  #logic goes here
  return action

def find_prioritized_enemy(characters):
    #order these to choose enemies by the lowest valued enemy
    priorities = ["Druid", "Enchanter", "Assassin", "Archer", "Sorcerer", "Wizard","Warrior", "Paladin"]
    result = None

    priority = len(priorities)
    for char in characters:
        if not char.is_dead():
            currpriority = priorities.index(char.classId)
            if priority < currpriority:
                result = char
                priority = currpriority
    return result

def find_weakest_member(characters):
    min = 2000
    result = None
    for enemy in characters:
        if enemy.attributes.get_attribute("health") < min:
            min = enemy.attributes.get_attribute("health")
            result = enemy
    return result

def get_a_target(enemyteam):
    target = None
    for character in enemyteam:
        if not character.is_dead():
            target = character
            break
    return target

# Main method
# @competitors DO NOT MODIFY
if __name__ == "__main__":
    # Config
    conn = ('localhost', 1337)
    if len(sys.argv) > 2:
        conn = (sys.argv[1], int(sys.argv[2]))

    # Handshake
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(conn)

    # Initial connection
    s.sendall(json.dumps(initialResponse()) + '\n')

    # Initialize test client
    game_running = True
    members = None

    # Run game
    try:
        data = s.recv(1024)
        while len(data) > 0 and game_running:
            value = None
            if "\n" in data:
                data = data.split('\n')
                if len(data) > 1 and data[1] != "":
                    data = data[1]
                    data += s.recv(1024)
                else:
                    value = json.loads(data[0])

                    # Check game status
                    if 'winner' in value:
                        game_running = False

                    # Send next turn (if appropriate)
                    else:
                        msg = processTurn(value) if "PlayerInfo" in value else initialResponse()
                        s.sendall(json.dumps(msg) + '\n')
                        data = s.recv(1024)
            else:
                data += s.recv(1024)
    except SocketError as e:
        if e.errno != errno.ECONNRESET:
            raise  # Not error we are looking for
        pass  # Handle error here.
    s.close()
