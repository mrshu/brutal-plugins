
from brutal.core.plugin import BotPlugin, cmd

class Countdown(BotPlugin):
    minutes = 0
    #in seconds
    countdown_delay = 0
    text = ""


    @cmd
    def countdown(self, event):
        """Creates timer and returns reminder after it expires."""
        
        if len(event.args) < 2:
            return "Not a valid countdown request, try again!"

        if not (event.args[0]).isdigit():
            return "Not a valid countdown request, try again!"

        second_arg = event.args[1]
        self.minutes = int(event.args[0]) 
        if(second_arg.isdigit()):
            self.countdown_delay = int(second_arg)
            self.text = ' '.join(event.args[2:])
        else:
            self.countdown_delay = 60
            self.text = ' '.join(event.args[1:])
    
        self.delay_task(self.countdown_delay, self.dec, event=event)
        
        return "Starting coundtown for {0}".format(self.text)


    def dec(self, event):
        self.minutes -= 1
        if self.minutes != 0:
            self.msg("T-{0} ( {1} )".format(self.minutes, self.text), event=event)
            self.delay_task(self.countdown_delay, self.dec, event=event)
        else:
            self.msg("It's happening! {0}".format(self.text), event=event)    
