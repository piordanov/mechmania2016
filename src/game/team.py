from src.game.character import Character


class Team:

    total_teams = 0

    @staticmethod
    def get_new_team_id():
        Team.total_teams += 1
        return Team.total_teams

    @staticmethod
    def remove_all_teams():
        Team.total_teams = 0

    ########################

    def __init__(self, name):
        self.name = name
        self.characters = []
        self.id = Team.get_new_team_id()
        self.start_pos = (0,0) if self.id == 1 else (4,4)

    def add_character(self, json):
        new_character = Character()

        error = new_character.init(json, self.start_pos[0], self.start_pos[1])
        self.characters.append(new_character)

        if not error:
            return new_character
        return error

    def get_character(self, id=None, name=None):
        if id is None and name is None:
            return None

        for character in self.characters:
            if character.name == name or character.id == id:
                return character

    def get_remain_percent_health(self):
        total_health = 0
        total_max_health = 0
        for character in self.characters:
            total_health += character.attributes.get_attribute("Health")
            total_max_health += character.attributes.get_attribute("MaxHealth")
        return float(total_health) / float(total_max_health)

    def get_num_alive_char(self):
        alive_chars = 0
        for character in self.characters:
            if not character.dead:
                alive_chars += 1
        return alive_chars

    def size(self):
        return len(self.characters)

    def toJson(self):
        """ Returns information about the team as a json
        :return json: (json) 
        """

        json = {}
        json['Teamname'] = self.name
        json['Id'] = self.id
        json['Characters'] = []
        for character in self.characters:
            json['Characters'].append(character.deserialize())

        return json
