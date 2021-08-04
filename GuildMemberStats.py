# Standard Library imports
from __future__ import annotations
from datetime import datetime
import json
import re

# 3rd party imports
import discord

class GameStats():
    """ A helper class for the Member Stats Pack class. This class 
        represents a game that a user has launched in the past.
        This class really should not be used stand alone unless
        rebuilding from JSON

        Attributes:
            name: The name of the game.
            date_first_played: The date the game was first played.
            date_last_played:  The date the game was last played
            marked_game: If a game is 'marked' i.e. the user has 
                         put the game on their watch list to not
                         launch as often.
            times_launched: The number of times a game was launched.
            days_launched: The number of days a game was launched.
    """

    def __init__(self, given_name: str, 
                date_first_added: datetime = None, 
                date_last_played: datetime = None, 
                marked_game: bool = False, 
                times_launched: int = 0 , 
                days_launched: int  = 0):

        self.__GameStats__ = True # metadata to parse JSON file.
        self.name = given_name
        self.date_first_added: datetime = date_first_added
        self.date_last_played: datetime = date_last_played
        self.marked_game = marked_game 
        self.times_launched = times_launched
        self.days_launched = days_launched

    def increment_times_launched(self):
        self.times_launched += 1

    def mark_game(self, marked: bool):
        """ Allow the user to mark a game they want to play """ 
        if marked:
            self.marked_game = True
        else:
            self.marked_game = False

    @staticmethod
    def decode_date(date_string: str) -> datetime:
        """ Decode a datetime object given a string representation 
            e.g. creating a date object from a json file. 
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

        # Process time. The regex helps split by
        # microseconds, but the discord API does 
        # not currently support this.
        split_time = re.split(r":|\.",time_str)
        hour        = int(split_time[0])
        minute      = int(split_time[1])
        second      = int(split_time[2])

        return datetime(year=year, month=month,day=day,hour=hour,
                        minute=minute,second=second)

    @classmethod
    def decode_game(cls: GameStats, dict) -> GameStats:
        """ Helper function to help with decoding games from json 
        """
        game_obj = None

        if dict is not None and  "__GameStats__" in dict:
            last_played_date  =  cls.decode_date(dict["date_last_played"])
            first_played_date =  cls.decode_date(dict["date_first_added"])

            game_obj = GameStats(given_name = dict["name"],
                                date_first_added=first_played_date,
                                date_last_played=last_played_date,
                                marked_game=dict["marked_game"],
                                times_launched=dict["times_launched"],
                                days_launched=dict["days_launched"])

        return game_obj


# Each member has there own stats pack
class MemberStatsPack(): 
    """ The heart of the bots data. When a user registers with the bot, 
        the bot associates the user id with an instance of the member
        stats pack. This stats pack contains the relevant data that the 
        bot keeps track of e.g. the most launched game, the least 
        played game, and the last launched game.

        Attributes: 
            most_launched_game: The game that's been most launched.
            least_launched_game: The game that's been least launched.
            last_game_launched: The game that was launched last.
            game_dict: A dictionary of the games the user has launched.
    """

    def __init__(self, most_launched: GameStats = None, 
                least_launched:GameStats = None,
                last_game: GameStats = None, 
                restored_game_list: dict[GameStats] = None):
        """ The purpose of having all these args in the constructor is 
            to be able to 'reload' the data into the class when read in 
            from a JSON file. Generally, when a new member is registered,
            their stats pack will be purposefully barren and set to defualts.

            # Parameters:
               most_launched:   A GameStats object that is the last 
                                launched game for this memeber.
               least_launched:  A GameStats object that is the least 
                                launched game for this member.
               last_game:       The last game played.

               restored_game_list: By default this is empty aka None 
                                   (don't want the default to be shared on
                                   subsequent calls. However, when restored
                                   from a json file a dictionary containing 
                                   instance of gameobjects shall be assigned.)

        """
        self.__MemberStatsPack__ = True # metadata
        self.most_launched_game  = most_launched
        self.least_launched_game = least_launched
        self.last_game_launched  = last_game
        
        if restored_game_list is not None: 
            self.game_dict = restored_game_list
        else:
            self.game_dict = {} # Key: Name of the game; Value: GameStats object
    

    def init_game_stats(self, current_game: discord.Game, date: datetime, 
                        marked: bool = False):
        """ This function should be called when creating a new gamestats object
            that is to be entered into the user's tracked games.

            Parameters:
                current_game: The discord game object
                date: A datetime object for init'ing the game object
                marked: set a game as marked if desired
        """
        game_object = GameStats(given_name=current_game.name, 
                                date_first_added=date, 
                                date_last_played=date,
                                marked_game=marked, 
                                times_launched=1, 
                                days_launched=1)

        self.game_dict[current_game.name] = game_object
    
    def previously_played(self, game_key: str) -> bool:
        """ Returns true, if a user has 
            previously played the game queried 

            Parameters:
                game_key: The name of the game the user
                          previously played.
        """
        if game_key in self.game_dict:
            return True
        return False

    def mark_game(self,game_name):
        """ Mark a game in the members game dictionary.
            Parameters:
                game_name: Key to be used to access the dictionary
        """
        self.game_dict[game_name].mark_game(game_name, True)

    def is_game_marked(self, name_of_game: str):
        """ Given the name of the game return true if it's a 
            marked game.

            Parameters:
                name_of_game: The name of the game in the users's game
                              dictionary
        """
        return self.game_dict[name_of_game].marked_game

    def update_game_stats(self, game_activity: discord.Game, 
                          start_date: datetime=None, end_date: datetime=None):
        """ Update the statistics for a game, given a game object that was already
            registered with the particular memeber. 

            Parameters:
            game_activity: A game object that is already within the member's 
                           game dictionary.

            start_date: The date the user started playing the game. 
                        Retrieved viaDiscord Py's API. 
            end_date:   The date the user stoped playing a game. 
                        Retrieved viaDiscord Py's API. 
        """
        # Current game being queried, becomes the last game launched.
        self.last_game_launched = self.game_dict[game_activity.name]

        prev_game_stats = self.game_dict[game_activity.name]

        # TODO: Fix! f the start time does not match then the user
        # quit the game or has decided to launch it again later.
        current_start_greater = start_date > prev_game_stats.date_last_played
        prev_day= prev_game_stats.date_last_played.day

        if current_start_greater:
            prev_game_stats.date_last_played = start_date
            prev_game_stats.increment_times_launched()

            # if the day changes record that data too.
            # This should be nested underneath.
            if start_date.day > prev_day:
                prev_game_stats.days_launched += 1

        # Update games being processed.
        self.update_most_launched() 
        self.update_least_launched(givenMin=prev_game_stats.times_launched)

    def update_most_launched(self):
        """ Updates the most launched game.
            
            Tracks the time launched to determine when the most launched
            game should be updated. The game returned is the last one
            found in the dictionary should two games have the same
            amount of times launched. 
        """
        max = 0
        curr_game = None
        most_launched = None

        for game_name in self.game_dict: 
            curr_game = self.game_dict[game_name]
            if curr_game.times_launched >= max:
                max = curr_game.times_launched
                most_launched = curr_game

        self.most_launched_game = most_launched

    def update_least_launched(self, *, givenMin):
        """ Updates the least launched game.
                Parameters:
                    givenMin: The given min to establish a baseline.
                              to create a new least launched game.
            
            Tracks the time launched to determine when the least launched
            game should be updated. The game returned is the last one
            found in the dictionary should two games have the same
            amount of times launched. 
        """
        if self.least_launched_game is not None:
            min = self.least_launched_game.times_launched
        else:
            min = givenMin
    
        curr_game = None
        least_launched = None

        for game_name in self.game_dict: 
            curr_game = self.game_dict[game_name]
            if curr_game.times_launched <= min:
                min = curr_game.times_launched
                least_launched = curr_game

        self.least_launched_game = least_launched


    @classmethod
    def json_encoder(cls, obj):
        """ Helper function to decode all the goods in our stats pack.
             
            The class itself can use it's dictionary dunder method, but 
            datetime objects cannot be as easily encoded, so they are encoded
            as strings. 

            Parameters:
                Obj: The object that will be encoded.
                     These objects should be things that comprise member
                     stats pack e.g. like datetime objects.
         """
        if isinstance(obj, datetime):
             return obj.__str__()
        else:
            return obj.__dict__

    @classmethod
    def json_decoder(cls, dict):
        """ Returns a member stats pack instance from a json dictionary.

            Returns none, if the dictionary is empty, has no entires,
            or is not a MemberStatsPack.
        """
        if (dict is not None and len(dict) > 0 and
                "__MemberStatsPack__" in dict):
            decode_game = GameStats.decode_game

            most_launched  = decode_game(dict["most_launched_game"])
            least_launched = decode_game(dict["least_launched_game"])
            last_launched  = decode_game(dict["last_game_launched"])

            json_game_dict = dict["game_dict"]
            restored_game_list = {}

            for game_key in json_game_dict:
                decoded_game = decode_game(json_game_dict[game_key])
                restored_game_list[game_key] = decoded_game

            return MemberStatsPack(most_launched=most_launched, 
                                   least_launched=least_launched,
                                   last_game=last_launched, 
                                   restored_game_list=restored_game_list)
        else:
            return None



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