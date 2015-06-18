from brutal.core.plugin import BotPlugin, cmd, event


class Note(object):
    def __init__(self, sender, receiver, msg, time=None):
        self.sender = sender
        self.receiver = receiver
        self.msg = msg
        self.time = time

    def fmt(self, form="{msg} (sticky note from {sender})"):
        return form.format(**self.__dict__)

    def __str__(self):
        return self.fmt("{receiver}: {msg} (sticky note from {sender})")


class StickyNotes(BotPlugin):
    def setup(self, *args, **kwargs):
        self.notes = self.open_storage('sticky_notes')

    def sender(self, x, event):
        return lambda: self.msg(str(x), event=event)

    @cmd
    def stickynote(self, event):
        """Create a sticky note for a given user."""
        args = event.args

        if len(args) < 1:
            return "Sticky note needs to be adressed to someone."
        elif len(args) < 2:
            return "Sticky note needs to contain some actual note."
        else:
            to_nick = args[0]
            from_nick = event.meta['nick']
            msg = ' '.join(args[1:])

        if to_nick not in self.notes:
            self.notes[to_nick] = []

        notes = self.notes[to_nick]
        notes.append(Note(from_nick, to_nick, msg))
        self.notes[to_nick] = notes

        return "Sticky note for {0} prepared.".format(to_nick)

    @event
    def send_notes(self, event):
        if event.event_type not in ['quit', 'part', 'kick']:
            nick = event.meta['nick']
            if nick in self.notes:
                notes = self.notes[nick]
                last_note = notes.pop()
                while len(notes) >= 1:
                    note = notes.pop()
                    self.delay_task(len(notes), self.sender(note), event)
                del self.notes[nick]
                return last_note

    @cmd
    def list_stickynotes(self, event):
        """
        Lists users with pending sticky notes if no argument is given, sticky
        notes for given user otherwise.
        """
        args = event.args
        format_note = lambda x, y: "{0}. {1}".format(x, y)
        LISTING_FORMAT = "{msg} (from {sender})"

        if len(args) == 0:
            nicks = filter(lambda x: self.notes[x] != [], self.notes.keys())
            if len(nicks) > 0:
                return 'I have sticky notes for: {0}'.format(', '.join(nicks))
            else:
                return 'No sticky notes prepared.'

        nick = args[0]
        if len(args) == 1 and nick in self.notes:
            user_notes = self.notes[nick]
            first_note = format_note(1, user_notes.pop(0).fmt(LISTING_FORMAT))
            for i, note in enumerate(user_notes, start=2):
                note_str = format_note(i, note.fmt(LISTING_FORMAT))
                self.delay_task(i, self.sender(note_str, event))
            return first_note

    @cmd
    def del_stickynote(self, event):
        args = event.args
        from_nick = event.meta['nick']

        if len(args) < 1:
            return "Missing nick argument."

        if len(args) < 2:
            return "Missing stickynote number argument."

        nick = args[0]
        note_num = args[1]

        if nick not in self.notes:
            return "No stickynotes for " + nick
        notes = self.notes[nick]

        if not note_num.isdigit() and note_num != 'last':
            return "Invalid stickynote number argument."

        note_num = -1 if note_num == 'last' else int(note_num)

        if note_num >= len(notes):
            return "User doesn't have that many stickynotes."

        if from_nick != notes[note_num].sender:
            return "Stickynote {0} isn't from you {1}.".format(note_num,
                                                               from_nick)

        notes.pop(note_num)
        self.notes[nick] = notes

        if not self.notes[nick]:
            del self.notes[nick]

        return "Stickynote deleted."
