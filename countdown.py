
from brutal.core.plugin import BotPlugin, cmd

BAD_REQ = "Not a valid countdown request, try again!"
LOW_DELAY_MSG = "Requested delay is too low. Setting lowest possible(30)."

class Countdown(BotPlugin):
    counter = 0
    # countdown_delay represented in seconds
    countdown_delay = 0
    text = ""


    @cmd
    def countdown(self, event):
        """Creates countdowner that will count down from a specified value down 
           to 0 adn then reminds you the time is up."""

        if len(event.args) < 2:
            return BAD_REQ

        if not event.args[0].isdigit():
            return BAD_REQ

        second_arg = event.args[1]
        self.counter = int(event.args[0]) * 60

        if second_arg.isdigit():
            task_arg = event.args[2:]
            if not task_arg:
                return BAD_REQ
            else:
                # Setting delay to at least 30 seconds prevents too much spam.
                if int(second_arg) < 30:
                    self.msg(LOW_DELAY_MSG, event=event)
                    self.countdown_delay = 30
                else:
                    self.countdown_delay = int(second_arg)

                self.text = ' '.join(task_arg)
        else:
            task_arg = event.args[1:]
            if not task_arg:
                return BAD_REQ
            else:
                self.countdown_delay = 60
                self.text = ' '.join(task_arg)
    
        self.delay_task(self.countdown_delay, self.decrementer, event=event)
        
        return "Starting coundtown for {0}".format(self.text)


    def decrementer(self, event):
        self.counter -= self.countdown_delay
        if self.counter != 0:
                self.msg("T-{0}sec ( {1} )".format(self.counter, self.text), 
                     event=event)
                self.delay_task(self.countdown_delay, self.decrementer, 
                            event=event)
        else:
            self.msg("{0} is happening!".format(self.text), event=event)    
