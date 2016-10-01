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
                 "ClassId": "Paladin"},
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

    # Choose a target
    target = None
    for character in enemyteam:
        if not character.is_dead():
            target = character
            break
    for character in myteam:
      action = None
      if character.name == "char1":
        action = char1Move(character,myteam, enemyteam)
      elif character.name == "char2":
        action = char2Move(character,myteam, enemyteam)
      elif character.name == "char3":
        action = char1Move(character,myteam, enemyteam)
      
      if action:
        actions.append(action)
    
    # If we found a target
    # Send actions to the server
    # print(actions)
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


def char1Move(char, myteam, enemyteam):
  if char.is_dead():
    return None

  # target = None
  # distance_max = sys.maxint
  # for enemy in enemyteam:
  #   distance = abs(char.position[0] - enemy.position[0] + char.position[1] - enemy.position[1])
  #   if not enemy.is_dead() and  distance < distance_max:
  #     distance_max = distance
  #     target = enemy;

  # target = None
  # distance_max = 0
  # for enemy in enemyteam:
  #   distance = abs(char.position[0] - enemy.position[0] + char.position[1] - enemy.position[1])
  #   if not enemy.is_dead() and  distance > distance_max:
  #     distance_max = distance
  #     target = enemy;

  target = None
  distance_min = sys.maxint
  for enemy in enemyteam:
    distance = abs(char.position[0] - enemy.position[0] + char.position[1] - enemy.position[1])
    if not enemy.is_dead() and  distance < distance_min:
      distance_min = distance
      target = enemy;

  if not target:
    return None
  # target = chooseTarget(enemyteam)

  print(target.name)

  action = {}
  if target != None:
    if (char.can_use_ability(11) and char.in_ability_range_of(target, gameMap, 11)):
      action = {
        "Action": "Cast",
        "CharacterId": char.id,
        "TargetId": target.id,
        "AbilityId": 11
    }
   
    elif char.in_range_of(target,gameMap) :
      print("attack")
      action = { "Action": "Attack",
          "CharacterId": char.id,
          "TargetId": target.id
          }
    else:

      action = {
        "Action": "Move",
        "CharacterId": char.id,
        "TargetId": target.id,
      }
  #logic goes here

  return action

def char2Move(character, myteam, enemyteam):
  if character.is_dead() or character.casting is not None:
    return None

  target = None

  #if stunned
  for team_member in myteam:
    if not team_member.is_dead() and team_member.attributes.get_attribute("Stunned"):
      target = team_member
  #unstunn
  if target != None:
   
    if (character.can_use_ability(1) and character.in_ability_range_of(target, gameMap, 1)):
      print("unstunn")
      action = {
            "Action": "Cast",
            "CharacterId": character.id,
            "TargetId": target.id,
              "AbilityId": 0
            }
      return action

  #target the one with the greatest damage
  # damage_max = 0
  # for enemy in enemyteam:
  #   print(enemy.attributes.get_attribute("Damage"))
  #   if enemy.attributes.get_attribute("Damage") > damage_max:
  #     target = enemy
  #     damage_max  = enemy.attributes.get_attribute("Damage")


  armor_max = sys.maxint
  for enemy in enemyteam:
    if enemy.attributes.get_attribute("Armor") < armor_max:
      target = enemy
      damage_max  = enemy.attributes.get_attribute("Armor")


  action = {}
  if target != None:
    #stunning
    if (character.can_use_ability(14) and character.in_ability_range_of(target, gameMap, 14)):
      action = {
        "Action": "Cast",
        "CharacterId": character.id,
        "TargetId": target.id,
        "AbilityId": 14
      }
    #improves health
    elif (character.can_use_ability(3) and character.in_ability_range_of(target, gameMap, 3)):
      character_getting_health = myteam[0]
      if (myteam[1].attributes.get_attribute("Health") > myteam[0].attributes.get_attribute("Health")):
        character_getting_health = myteam[1] 
        action ={
          "Action": "Cast",
          "CharacterId": character.id,
          "TargetId": character_getting_health.id,
          "AbilityId": 3
      }     
    else:
      action = {
        "Action": "Move",
        "CharacterId": character.id,
        "TargetId": target.id,
      }
  return action

def char3Move(char, myteam, enemyteam):
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
