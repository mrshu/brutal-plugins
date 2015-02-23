from brutal.core.plugin import BotPlugin, cmd, match, event


class StickyNotes(BotPlugin):
    def setup(self, *args, **kwargs):
        self.notes = self.open_storage('sticky_notes')

    def sender(self, x, event):
        return lambda: self.msg(x, event=event)

    @cmd
    def stickynote(self, event):
        """Create a sticky note for a given user."""
        args = event.args

        if len(args) < 1:
            return "Sticky note needs to be adressed to someone."
        elif len(args) < 2:
            return "Sticky note needs to contain some actual note."
        else:
            user = event.args[0]
            content = ' '.join(event.args[1:])

        if user not in self.notes:
            self.notes[user] = []

        notes = self.notes[user]
        notes.append("{1} (sticky note from {0})".format(event.meta['nick'],
                                                         content))
        self.notes[user] = notes

        return "Sticky note for {0} prepared.".format(user)

    @event
    def send_notes(self, event):
        format_note = lambda x, y: "{0}: {1}".format(x, y)

        if event.event_type == 'join':
            nick = event.meta['nick']
            if nick in self.notes and len(self.notes[nick]) > 0:
                notes = self.notes[nick]
                last_note = notes.pop()
                while len(notes) >= 1:
                    note = notes.pop()
                    self.delay_task(len(notes),
                                    self.sender(format_note(nick, note), event))
                self.notes[nick] = []
                return format_note(nick, last_note)

    @cmd
    def list_stickynotes(self, event):
        """
        Lists users with pending sticky notes if no argument is given, sticky
        notes for given user otherwise.
        """
        args = event.args
        format_note = lambda x, y: "{0}. {1}".format(x, y)

        if len(args) == 0:
            return 'I have sticky notes for: ' + ', '.join(self.notes.keys())

        if len(args) == 1:
            nick = args[0]
            user_notes = self.notes[nick]
            first_note = format_note(1, user_notes.pop(0))
            for index, note in enumerate(user_notes, start=2):
                self.delay_task(index,
                                self.sender(format_note(index, note), event))
            return first_note
