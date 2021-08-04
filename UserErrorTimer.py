import time
class UserTimer:
    """ A timer class to avoid users spamming the bot with nonsense commands.
        Attributes:
          error_count:    The count amount of times the user entered an invalid command.
          cooldown_delay: The delay imposed on the user that is added to the timer.
          on_cooldown:    Status indicating if the user is on cool down i.e. the timer
                          has started for the user. Setter and getters.
          timer_started:  Status indicating whether the timer has started.

        Methods:
            start_timer: Start the timer on the instance of the class. Timer can be
                         extended in terms of seconds via the resume_time arg.
            timer_done:  Checks to see if the timer has elapsed.
    """
    def __init__(self) -> None:
        self.error_count = 0
        self.cooldown_delay = 0
        self.on_cooldown = False
        self.timer_started = False
        

    def start_timer(self, resume_time = 0):
        self.timer_started = True
        self.on_cooldown = True
        self.cooldown_delay = time.time() + resume_time 
        
    def timer_done(self) -> bool:
        # Ensure start_timer() was called first.
        if not self.timer_started:
            return False
        elif time.time() > self.cooldown_delay:
            self.error_count = 0
            self.cooldown_delay = 0
            self.on_cooldown = False
            self.timer_started = False
            return True
        else:
            return False # Timer state is not done
            