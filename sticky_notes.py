from brutal.core.plugin import BotPlugin, cmd, event


class Note:
    sender = ""
    reciever = ""
    msg = ""
    time = None

    def __init__(self, sender, reciever, msg, time=None):
        self.sender = sender
        self.reciever = reciever
        self.msg = msg
        self.time = time

    def __str__(self):
        return "{0}: {1} (sticky note from {2})".format(self.reciever,
                                                        self.msg, self.sender)


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
            to_nick = event.args[0]
            from_nick = event.meta['nick']
            msg = ' '.join(event.args[1:])

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
            if nick in self.notes and len(self.notes[nick]) > 0:
                notes = self.notes[nick]
                last_note = notes.pop()
                while len(notes) >= 1:
                    note = notes.pop()
                    self.delay_task(len(notes), self.sender(note), event)
                self.notes[nick] = []
                return last_note

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

        if note_num == 'last':
            note_num = -1
        else:
            note_num = int(note_num)

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
