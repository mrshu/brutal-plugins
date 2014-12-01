
from brutal.core.plugin import BotPlugin, cmd

BAD_REQ = "Not a valid countdown request, try again!"
LOW_DELAY_MSG = "Requested delay is too low. Setting lowest possible(30)."

class Countdown(BotPlugin):
    counter = 0
    delay_above_ten = 300
    delay_min = 60
    delay_sec = 10
    delay_last_ten = 1
    text = ""

    @cmd
    def countdown(self, event):
        """Creates countdowner that will count down from a specified value down
           to 0 and then reminds you the time is up."""

        if len(event.args) < 2:
            return BAD_REQ
        if not event.args[0].isdigit():
            return BAD_REQ
        # countdown time
        if int(event.args[0]) <= 1:
            return BAD_REQ
        else:
            self.counter = int(event.args[0]) * 60
        # countdown text
        task_arg = event.args[1:]
        if not task_arg:
            return BAD_REQ
        else:
            self.text = ' '.join(task_arg)

        if self.counter > self.delay_above_ten:
            self.delay_task(self.delay_above_ten, self.decrementer, event=event)
        elif self.counter > self.delay_min:
            self.delay_task(self.delay_min, self.decrementer, event=event)
        elif self.counter == self.delay_min:
            self.delay_task(self.delay_sec, self.decrementer, event=event)

        return "Starting {0}min coundtown for {1}".format(self.counter // 60,
                                                          self.text)


    def decrementer(self, event):
        if self.counter > self.delay_above_ten:
            self.counter -= self.delay_above_ten
        elif self.delay_above_ten >= self.counter > self.delay_min:
            self.counter -= self.delay_min
        elif self.delay_min >= self.counter > self.delay_sec:
            self.counter -= self.delay_sec
        elif self.delay_sec >= self.counter:
            self.counter -= self.delay_last_ten

        if self.counter != 0:
            if self.counter > self.delay_above_ten:
                self.msg("T-{0}min ({1})".format(self.counter // 60,
                                                       self.text), event=event)
                self.delay_task(self.delay_above_ten, self.decrementer, 
                                event=event)

            elif self.delay_above_ten >= self.counter > self.delay_min:
                self.msg("T-{0}min ({1})".format(self.counter // 60,
                                                       self.text), event=event)
                self.delay_task(self.delay_min, self.decrementer, event=event)

            elif self.delay_min >= self.counter > self.delay_sec:
                self.msg("T-{0}sec ({1})".format(self.counter, self.text),
                         event=event)
                self.delay_task(self.delay_sec, self.decrementer, event=event)

            elif self.delay_sec >= self.counter:
                self.msg("T-{0}sec ({1})".format(self.counter, self.text),
                         event=event)
                self.delay_task(self.delay_last_ten, self.decrementer, 
                                event=event)
        else:
            self.msg("{0} is happening!".format(self.text), event=event)
