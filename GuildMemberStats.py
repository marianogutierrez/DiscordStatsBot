from datetime import datetime
import json
import re

#TODO: Clean up private variables etc. 
class GameStats():
    def __init__(self, given_name, date_first_added = None, date_last_played = None, 
                marked_game = False, times_launched = 0, days_launched = 0):

        self.__GameStats__ = True # metadata
        self.name = given_name
        self.date_first_added: datetime = date_first_added # set and forget
        self.date_last_played: datetime = date_last_played
        self.marked_game = marked_game 
        self.times_launched = 0
        self.days_launched = days_launched

    def increment_times_launched(self):
        self.times_launched += 1

    def update_last_time_played(self, date):
        self.date_last_played = date

    def mark_game(self, marked, title):
        """ Allow the user to mark a game they want to play """ 
        if marked:
            self.marked_game = True
        self.marked_game = False

    def get_name(self):
        return self.name

    #TODO: Take this out of the class, and make it a general function in like a utility file. 
    @staticmethod
    def decode_date(date_string: str) -> datetime:
        """ Decode a datetime object given a string representation 
            e.g. from a json file. 
        """
        if date_string == None:
            return None
        
        # Seperate date and time
        date_list = date_string.split(" ")
        date_str = date_list[0]
        time_str = date_list[1]

        # Process date
        split_date = date_str.split("-")
        year  = int(split_date[0])
        month = int(split_date[1])
        day   = int(split_date[2])

        # Process time
        split_time = re.split(":|\.",time_str)
        hour        = int(split_time[0])
        minute      = int(split_time[1])
        second      = int(split_time[2])
        microsecond = int(split_time[3])

        return datetime(year=year, month=month,day=day,hour=hour,
                        minute=minute,second=second,microsecond=microsecond)

    @classmethod
    def decode_game(cls, dict):
        """ Helper function to help with decoding games from json """
        game_obj = None
        if dict is not None and  "__GameStats__" in dict:
            last_played_date  =  cls.decode_date(dict["date_last_played"])
            first_played_date =  cls.decode_date(dict["date_first_added"])
            game_obj = GameStats(given_name = dict["name"], date_first_added=first_played_date,
                                 date_last_played=last_played_date, 
                                 marked_game=dict["marked_game"], times_launched=dict["times_launched"],
                                 days_launched=dict["days_launched"])

        return game_obj

# Each member has there own stats pack
# TODO: make decoder 
class MemberStatsPack(): 
    def __init__(self, most_launched = None, least_launched = None,
                last_game = None, restored_game_list = None):
        """The purpose of having all these arugements in the constructor is to
           be able to 'reload' the data into the class when read in from a JSON
           file.

           #Parameters:
            most_launched: A GameStats object that is the last launched game for this memeber.
            least_launched: A GameStats object that is the least launched game for this member.
        """
        self.__MemberStatsPack__ = True # metadata
        self.most_launched_game:  GameStats = most_launched
        self.least_launched_game: GameStats = least_launched
        self.last_game_launched:  GameStats = last_game
        
        if restored_game_list is not None: 
            self.game_dict = restored_game_list
        else:
            self.game_dict = {} # Key: Name of the game; Value: GameStats object
    
    # ========= Boiler Plate Functions ========= #
    def get_most_launched_game(self):
        return self.most_launched_game

    def get_least_launched_game(self):
        return self.least_launched_game

    def get_last_game_launched(self):
        return self.last_game_launched

    def previously_played(self, game_key: str) -> bool:
        """ Returns true, if a user has previously played the game queried """
        if game_key in self.game_dict:
            return True
        return False
    # ========================================== #

    def mark_game(self,game_name):
        self.game_dict[game_name].mark_game(game_name, True)


    def init_game_stats(self, current_game, date, marked):
        game_object = GameStats(given_name=current_game.name, date_first_added=date, date_last_played=date,
         marked_game=marked, times_launched=1, days_launched=1)
        self.game_dict[current_game.name] = game_object

    def update_game_stats(self, game: GameStats, start_date: datetime): # TODO: update to make sense
        """ Update the statistics for a game, given a game object that was already
            registered with the particular memeber. 

            Parameters:
            game: A game objecdt that is already within the member's game dictionary
            start_date: The date the user started playing the game. Retrieved via
            Discord Py's API. 
        """
        # Current game being queried, is the last game launched
        self.last_game_launched = self.game_dict[game.name]

        prev_game_stats = self.game_dict[game.name] # Gamestats
        # If the start time does not match then the user
        # quit the game or has decided to launch it again later.
        current_start_greater = start_date > prev_game_stats.date_last_played
        if current_start_greater:
            game.update_last_time_played(start_date)
            game.increment_times_launched()

        # if the day changes record the data too
        if current_start_greater and start_date.day > prev_game_stats.date_last_played.day:
            prev_game_stats.days_launched += 1

        self.update_most_launched() 
        self.update_least_launched()

    def update_most_launched(self):
        """ Returns the most launched game for this user """
        max = 0
        most_launched = None
        for game in self.game_dict: 
            if game.times_launched >= max:
                max = game.times_launched
                most_launched = game

        self.most_launched_game = most_launched

    def update_least_launched(self):
        min = 0
        least_launched = None
        for game in self.game_dict: 
            if game.times_launched >= min:
                min = game.times_launched
                least_launched = game

        self.least_launched_game = least_launched


    @classmethod
    def json_encoder(cls,obj):
        """ Helper function to decode all the goods in our stats pack """
        if isinstance(obj, datetime):
             return obj.__str__()
        else:
            return obj.__dict__

    @classmethod
    def json_decoder(cls, dict):
        if "__MemberStatsPack__" in dict:
            most_launched  = GameStats.decode_game(dict["most_launched_game"])
            least_launched = GameStats.decode_game(dict["least_launched_game"])
            last_launched  = GameStats.decode_game(dict["last_game_launched"])

            json_game_dict = dict["game_dict"]
            restored_game_list = {}

            for game_key in json_game_dict:
                restored_game_list[game_key] = GameStats.decode_game(json_game_dict[game_key])

            return MemberStatsPack(most_launched=most_launched, least_launched=least_launched,
                                   last_game=last_launched, restored_game_list=restored_game_list)



if __name__ == "__main__":
    thing1 = {}
    objGame = GameStats("billy", datetime.now(), marked_game = False)
    obj1 = MemberStatsPack(most_launched=objGame)
    obj1.game_dict["a"] = objGame
    thing1["b"] = obj1
    thing1["a"] = obj1
    thing2 = {}
    with open("GuildData.json", "w") as data_file:
        json.dump(thing1, data_file, indent=2, default=MemberStatsPack.json_encoder)

    with open("GuildData.json", "r") as f:
        thing2 = json.load(f)

    print(thing2)
 

    




