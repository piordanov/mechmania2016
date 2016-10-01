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
                 "ClassId": "Sorcerer"},
                {"CharacterName": "char2",
                 "ClassId": "Druid"},
                {"CharacterName": "char3",
                 "ClassId": "Paladin"},
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
    target = None
    for character in enemyteam:
        if not character.is_dead():
            target = character
            break
   
    for character in myteam:
      action=None
      if character.name == "char1":
        action = sorcMove(character,myteam, enemyteam, target)
      elif character.name == "char2":
        action = druidMove(character,myteam, enemyteam, target)
      elif character.name == "char3":
        action = paly1Move(character,myteam, enemyteam, target)
      else:
        print "WE FUCKED UP->_>P>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
      if action:
	actions.append(action)
    # If we found a target
    # Send actions to the server
    print actions
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


def sorcMove(char, myteam, enemyteam, target):
  global turn
  action = { "Action": "Attack",
      "CharacterId": char.id,
      "TargetId": enemyteam[0].id
      }
  #predict when they are 3 away
  if turn<3:
    return None
  elif turn<7:
    print turn
    action["Action"]="Cast"
    action["TargetId"]=char.id
    action["AbilityId"]=8 #cutting for power
    return action

  if not char.in_range_of(target, gameMap):
    action["Action"]= "Move"
    action["TargetId"]= target.id

  #logic goes here
  return action

def paly1Move(char, myteam, enemyteam, target):
  return palyMove(char, myteam, enemyteam, target, None)


def paly2Move(char, myteam, enemyteam, target):
  return palyMove(char, myteam, enemyteam, target, target)

def palyMove(char, myteam, enemyteam, target, stunTarget):
  global turn
  action = { "Action": "Attack",
      "CharacterId": char.id,
      "TargetId": target.id
      }
  if char.casting:
    return None
  elif turn==1:
    return None
  elif turn<5:
    return action
  elif turn ==5:
    action["Action"]="Cast"
    action["TargetId"]=myteam[0].id #make this better to target sorcer
    action["AbilityId"]=3 #cutting for power
    return action
  elif char.can_use_ability(14) and stunTarget:
    #do good stunning
    action["Action"]="Cast"
    action["TargetId"]=stunTarget.id #make this better to target sorcer
    action["AbilityId"]=14 #cutting for power
    return action 
  elif char.in_range_of(target, gameMap):
    return action;
  else:
    action["Action"]="Move"
    return action



  #logic goes here
  return action

def palyMove(char, myteam, enemyteam, target, rootTarget):
  global turn
  action = { "Action": "Attack",
      "CharacterId": char.id,
      "TargetId": target.id
      }
  if char.casting:
    return None
  elif turn==1:
    return None
  elif turn<5:
    return action
  elif turn ==5:
    action["Action"]="Cast"
    action["TargetId"]=myteam[0].id #make this better to target sorcer
    action["AbilityId"]=3 #cutting for power
    return action
  elif char.can_use_ability(14) and stunTarget:
    #do good stunning
    action["Action"]="Cast"
    action["TargetId"]=stunTarget.id #make this better to target sorcer
    action["AbilityId"]=14 #cutting for power
    return action 
  elif char.in_range_of(target, gameMap):
    return action;
  else:
    action["Action"]="Move"
    return action



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
