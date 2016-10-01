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
teamName = "PEAK"
turn = 0
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
    global turn
    turn+=1
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

    # Choose a target
    target=chooseTarget(enemyteam)
    for character in myteam:
      action=None
      if character.name == "char1":
        action = assMove(character,myteam, enemyteam, target)
      elif character.name == "char2":
        action = assMove(character,myteam, enemyteam, target)
      elif character.name == "char3":
        action = assMove(character,myteam, enemyteam, target)
      else:
        print "WE FUCKED UP->_>P>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

      if action:
	actions.append(action)



    # If we found a target
    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }
# ---------------------------------------------------------------------
def chooseTarget(enemyteam):
    target = enemyteam[0]
    for character in enemyteam:
        if not character.is_dead():
            target = character
    targetHealth = target.attributes.get_attribute("Health")
    for character in enemyteam:
	cHealth = character.attributes.get_attribute("Health")
        if not character.is_dead() and cHealth<targetHealth:
            target = character
	    targetHealth = cHealth
    return target


def assMove(char, myteam, enemyteam, target):
  global turn
  action = { "Action": "Attack",
      "CharacterId": char.id,
      "TargetId": target.id
      }
  dist = abs(myteam[0].position[0]-enemyteam[0].position[0]) + abs(myteam[0].position[1]-enemyteam[0].position[1])

  if should_break(char):
    action["Action"]="Cast"
    action["AbilityId"]=0
  elif char.in_ability_range_of(target, gameMap, 11) and char.can_use_ability(11):
    action["Action"]="Cast"
    action["AbilityId"]=11
    return action
  elif char.in_range_of(target, gameMap):
    return action
  elif dist==3 or dist == 4:
    action["Action"]="Cast"
    action["AbilityId"]=12
  else:
    action["Action"]="Move"
    return action


def should_break(char):
  attr = char.attributes
  if attr.get_attribute("Stunned")<0:
    return True
  return False

    

  #logic goes here
  return action

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
