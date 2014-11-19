
from brutal.core.plugin import BotPlugin, cmd, event, match, threaded

class Countdown(BotPlugin):
    minutes = 0
    text = ""
    
    @cmd
    def countdown(self, event):
        """Creates a timer and returns a reminder after it expires."""
        if len(event.args) < 2:
            return "Not a valid countdown request, try again!"
        
        self.minutes = int(event.args[0]) 
        self.text = ' '.join(event.args[1:])
    
        self.delay_task(60, self.dec, event=event)
        
        return "Starting coundtown for {0}".format(self.text)
    
    def dec(self, event):
        self.minutes -= 1
        self.msg("T-{0} ( {1} )".format(self.minutes, self.text), event=event) 
        if self.minutes != 0:
            self.delay_task(60, self.dec, event=event)
