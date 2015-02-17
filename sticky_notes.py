from brutal.core.plugin import BotPlugin, cmd, match


class StickyNotes(BotPlugin):
    def setup(self, *args, **kwargs):
        self.notes = self.open_storage('sticky_notes')

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

        self.notes[user].append("Note from {0}: {1}".format(user, content))

        return "Sticky note for {0} prepared.".format(user)

    @event
    def send_notes(event):
        if event.event_type == 'join':
            nick = event.meta['nick']
            if nick in self.notes:
                last_note = self.notes[nick].pop()
                for note in self.notes[nick]:
                    self.msg(note, event=event)
                return last_note
