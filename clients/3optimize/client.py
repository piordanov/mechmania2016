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
turn = 0

# --------------------------- SET THIS IS UP -------------------------
teamName = "3optimize"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Assassin",
                 "ClassId": "Assassin"},
                {"CharacterName": "Assassin",
                 "ClassId": "Assassin"},
                {"CharacterName": "Archer",
                 "ClassId": "Archer"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    # Setup helper variables
    global turn
    turn+=1
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
    target = chooseTarget(enemyteam)
    if target:
      for character in myteam:
        action = None
        if character.name == "Assassin":
          action = charAssassinMove(character,myteam, enemyteam,target)
        elif character.name == "Archer":
         action = charArcherMove(character,myteam, enemyteam,target)
        else:
          print "WE FUCKED UP->_>P>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        if action:
            actions.append(action)
    return {
        'TeamName': teamName,
        'Actions': actions
    }
# ---------------------------------------------------------------------

def chooseTarget(enemyteam):
    target = enemyteam[0]
    minpos = (10,10)
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


def charAssassinMove(char, myteam, enemyteam, target):
  global turn
  action = { "Action": "Move",
      "CharacterId": char.id,
      "Location": char.position
      }

  if char.casting is not None or char.is_dead():
      return None

  if turn == 1 and char.position == tuple([0, 0]):
    action["Action"] = "Move"
    action["Location"] = tuple([1,0])
    print action["Location"]

  elif turn == 1 and char.position == tuple([gameMap.height-1,gameMap.height-1]):
    action["Action"] = "Move"
    action["Location"] = tuple([gameMap.height-2,gameMap.height-1])
    print action["Location"]

  elif char.can_use_ability(11, ret=False) and char.in_ability_range_of(target, gameMap, 11, ret=False) and char.casting is None:
    action["Action"]="Cast"
    action["AbilityId"]=int(11)
    action["TargetId"]= target.id


  elif char.in_range_of(target, gameMap):
    action["Action"] = "Attack"
    action["TargetId"] = target.id
  #logic goes here
  print action
  return action

def charArcherMove(char, myteam, enemyteam, target):
  global turn
  action = { "Action": "Move",
      "CharacterId": char.id,
      "Location": char.position
      }

  if turn == 0 and char.position == tuple([0,0]):
    action["Action"] = "Move"
    action["Location"] = tuple([1,0])

  if turn == 0 and char.position == tuple([gameMap.height-1,gameMap.height-1]):
    action["Action"] = "Move"
    action["Location"] = tuple([gameMap.height-2,gameMap.height-1])

  if char.can_use_ability(2, ret=False) and char.in_ability_range_of(target, gameMap, 2, ret=False) :
    action["Action"]="Cast"
    action["AbilityId"]=int(2)
    action["TargetId"]= target.id

  elif char.in_range_of(target, gameMap):
    action["Action"] = "Attack"
    action["TargetId"] = target.id

  print action

  return action

def get_dodge_action(char):
    selectPosition = None
    print "From: %s" % (char.position,)
    posbelow = tuple([char.position[0], char.position[1] - 1])
    posabove = tuple([char.position[0], char.position[1] + 1])
    posleft = tuple([char.position[0] - 1, char.position[1]])
    posright = tuple([char.position[0] + 1, char.position[1]])
    if gameMap.is_inbounds(posbelow):
        selectPosition = posbelow
    elif gameMap.is_inbounds(posleft):
        selectPosition = posleft
    elif gameMap.is_inbounds(posright):
        selectPosition = posright
    elif gameMap.is_inbounds(posabove):
        selectPosition = posabove

    selectPosition = tuple(selectPosition)
    print "To: %s" % (selectPosition,)

    return {"Action": "Move",
              "CharacterId": char.id,
              "Location": selectPosition
              }


def is_dodgeable_attack(char, enemyteam):
    for enemy in enemyteam:
        cast = enemy.casting
        #print enemy.can_use_ability(11)
        #print enemy.in_ability_range_of(char, gameMap, 11)
        if cast is not None:
            target = cast["TargetId"]
            # print cast["AbilityId"]
            # print enemy.can_use_ability(cast["AbilityId"])
            # print char.id == target
            if enemy.can_use_ability(cast["AbilityId"]) and char.id == target and cast['CurrentCastTime'] == 0:
                        #print "dodging"
                        return True
            #backstab anticipationenemy.in_ability_range_of(char, gameMap, 11)
        #if enemy.can_use_ability(11) and enemy.in_ability_range_of(char, gameMap, 11):
        #    return True
    return False



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
