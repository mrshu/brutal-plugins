from brutal.core.plugin import BotPlugin, cmd

BAD_REQ = "Not a valid countdown request, try again!"
LOW_DELAY_MSG = "Requested delay is too low. Setting lowest possible(30)."
TEN_MINUTES = 600
ONE_MINUTE = 60
TEN_SECONDS = 10


class Countdown(BotPlugin):
    counter = 0
    DELAY_ABOVE_TEN = 300
    DELAY_MIN = 60
    DELAY_SEC = 10
    DELAY_LAST_TEN = 1
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
        c_time = int(event.args[0])
        if c_time <= 1:
            return BAD_REQ
        else:
            self.counter = c_time * 60
        # countdown text
        task_arg = event.args[1:]
        if not task_arg:
            return BAD_REQ
        else:
            self.text = ' '.join(task_arg)

        if self.counter > TEN_MINUTES:
            self.delay_task(self.DELAY_ABOVE_TEN,
                            self.decrementer,
                            event=event)
        elif TEN_MINUTES >= self.counter > ONE_MINUTE:
            self.delay_task(self.DELAY_MIN, self.decrementer, event=event)
        elif ONE_MINUTE >= self.counter > TEN_SECONDS:
            self.delay_task(self.DELAY_SEC, self.decrementer, event=event)

        return "Starting {0}min countdown for {1}".format(self.counter // 60,
                                                          self.text)

    def decrementer(self, event):
        if self.counter > TEN_MINUTES:
            self.counter -= self.DELAY_ABOVE_TEN
        elif TEN_MINUTES >= self.counter > ONE_MINUTE:
            self.counter -= self.DELAY_MIN
        elif ONE_MINUTE >= self.counter > TEN_SECONDS:
            self.counter -= self.DELAY_SEC
        elif TEN_SECONDS >= self.counter:
            self.counter -= self.DELAY_LAST_TEN

        if self.counter != 0:
            if self.counter > TEN_MINUTES:
                self.msg(self.format_msg("min"), event=event)
                self.delay_task(self.DELAY_ABOVE_TEN, self.decrementer,
                                event=event)

            elif TEN_MINUTES >= self.counter > ONE_MINUTE:
                self.msg(self.format_msg("min"), event=event)
                self.delay_task(self.DELAY_MIN, self.decrementer, event=event)

            elif ONE_MINUTE >= self.counter > TEN_SECONDS:
                self.msg(self.format_msg("sec"), event=event)
                self.delay_task(self.DELAY_SEC, self.decrementer, event=event)

            elif TEN_SECONDS >= self.counter:
                self.msg(self.format_msg("sec"), event=event)
                self.delay_task(self.DELAY_LAST_TEN, self.decrementer,
                                event=event)
        else:
            self.msg("{0} is happening!".format(self.text), event=event)

    def format_msg(self, time_unit):
        """Returns countdown message with 'self.counter' seconds or
           'self.counter' minutes depending on 'time_unit'."""
        if time_unit == "sec":
            return "T-{0}{1} ({2})".format(self.counter, time_unit, self.text)
        elif time_unit == "min":
            return "T-{0}{1} ({2})".format(self.counter // 60, time_unit,
                                           self.text)
