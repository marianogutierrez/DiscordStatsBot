# Standard Library Imports
import time

class UserTimer:
    """ A timer class to avoid users spamming the bot with nonsense commands.
        Attributes:
          error_count:    The count amount of times the user entered 
                          an invalid command.
          cooldown_delay: The delay imposed on the user that is 
                          added to the timer.
          on_cooldown:    Status indicating if the user is on cool down
                          i.e. the timer has started for the user.
          timer_started:  Status indicating whether the timer has started.
          time_created:   The current time the class instance was created. 
                          This can be helpful if you want to reset some 
                          behavior before starting a time for example. 
                          If this is checked, it should be updated 
                          immediately thereafter.
    """
    def __init__(self) -> None:
        self.error_count = 0
        self._cooldown_delay = 0
        self._on_cooldown = False
        self._timer_started = False
        self.time_created = time.time()
        
    @property
    def on_cooldown(self):
        return self._on_cooldown
    
    @property
    def cooldown_delay(self):
        return self._cooldown_delay

    @cooldown_delay.setter
    def cooldown_delay(self, delay):
        self._cooldown_delay = delay
 
    @property
    def timer_started(self):
        return self._timer_started

    def start_timer(self, resume_time=0):
        """ Start the timer for the instance. 
            Set the timer_started flag, and the 
            on on_cooldown flag for use in the caller 
            application. 
        """
        self._timer_started = True
        self._on_cooldown = True
        self._cooldown_delay = time.time() + resume_time 
        
    def timer_done(self) -> bool:
        """ Checks to see if the timer has finished.
            First, ensure that the timer was started to begin with.
            If the current time is greater than the cool down
            than the timer has elapsed. Otherwise, keep waiting.
        """
        # Ensure start_timer() was called first.
        if not self._timer_started:
            return False
        elif time.time() > self._cooldown_delay:
            self._error_count = 0
            self._cooldown_delay = 0
            self._on_cooldown = False
            self._timer_started = False
            return True
        else:
            return False # Timer state is not done
            