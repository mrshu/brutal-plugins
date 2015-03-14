from brutal.core.plugin import BotPlugin, cmd
from brutal.core.utils import split_args_by


class Vote(BotPlugin):
    VOTING_NONE = 0
    VOTING_YESNO = 1
    VOTING_QUESTION = 2

    def setup(self, *args, **kwargs):
        self.reset()

    def reset(self):
        """Reset all voting variables"""
        self.voting = self.VOTING_NONE
        self.yeses = {}
        self.nos = {}
        self.answers = {}

    def voting_in_progress(self, question=False):
        if question:
            return self.voting == self.VOTING_QUESTION
        return self.voting is not self.VOTING_NONE

    def judgement(self, event=None, penalty=''):
        """Summarize votes and make decision"""
        # TODO: if voting succeeded, get op and punish user
        msg = 'unsuccessfully'
        if len(self.yeses) + len(self.nos) > 1 and \
                len(self.yeses) > len(self.nos):
            msg = 'successfully '

        msg += ' with {0}x yes, {1}x no'.format(len(self.yeses), len(self.nos))
        result = '{0} {1}'.format(penalty, event.args[0])

        self.reset()

        return 'Voting to {0} finished {1}'.format(result, msg)

    def vote_result(self, event=None, penalty=''):
        """Start voting for given penalty"""
        if self.voting_in_progress() or self.voting_in_progress(question=True):
            return 'Voting in progress...'

        args = event.args
        if not len(args):
            return 'No user specified'

        if '-' in args:
            args = split_args_by(args, '-')

        try:
            time = int(args[1])
        except:
            time = 60

        user = args[0]
        self.voting = self.VOTING_YESNO

        self.delay_task(time, self.judgement, event=event, penalty=penalty)

        return 'Voting to {0} {1} started for {2} secs. (!yes / !no)' \
            .format(penalty, user, time)

    @cmd
    def votekick(self, event):
        return self.vote_result(event, 'kick')

    @cmd
    def voteban(self, event):
        return self.vote_result(event, 'ban')

    @cmd
    def voteunban(self, event):
        return self.vote_result(event, 'unban')

    @cmd
    def votemute(self, event):
        return self.vote_result(event, 'mute')

    def yesno_result(self, event=None):
        """Return results of yes/no question"""
        y = [v for k, v in self.yeses.iteritems()]
        n = [v for k, v in self.nos.iteritems()]

        y = ' ({0})'.format(', '.join(y)) if len(y) else ''
        n = ' ({0})'.format(', '.join(n)) if len(n) else ''

        res = '{0}x yes{2}, {1}x no{3}'.format(len(self.yeses), len(self.nos),
                                               y, n)

        self.reset()
        return 'Results of {0}\'s question: {1}'.format(event.meta['nick'],
                                                        res)

    def question_helper(self, event, callback, yesno=False):
        """Helper which holds `ask` commands"""
        if self.voting_in_progress() or self.voting_in_progress(question=True):
            return 'Voting in progress...'

        args = split_args_by(event.args, '-')
        if not len(args):
            return 'No question specified'

        question = args[0]
        if not question.endswith('?'):
            question += '?'

        try:
            time = int(args[1])
        except:
            time = 60

        user = event.meta['nick']

        self.delay_task(time, callback, event=event)

        if yesno:
            self.voting = self.VOTING_YESNO
            return '{0} asks: {1} (!yes / !no)'.format(user, question)
        self.voting = self.VOTING_QUESTION
        return '{0} asks: {1} (!vote <answer>)'.format(user, question)

    @cmd
    def askyesno(self, event):
        """Ask a yes/no question

        Example:
            !askyesno Going to the pub?
            !askyesno Going to the pub? - 30
        """
        return self.question_helper(event, self.yesno_result, yesno=True)

    def question_result(self, event=None):
        """Return results of question"""
        res = ''
        for k, v in self.answers.iteritems():
            res += '{0} -> {1}, '.format(v[0], v[1])

        self.reset()
        return 'Results of {0}\'s question: {1}'.format(event.meta['nick'],
                                                        res)

    @cmd
    def ask(self, event):
        """Ask a question

        Examples:
            !ask What should I get done today?
            !ask What should I get done today? - 30
        """
        return self.question_helper(event, self.question_result)

    @cmd
    def vote(self, event):
        """Add user's own answer
        Only usable when answering to !askquestion"""
        if not self.voting_in_progress(question=True):
            return 'Cannot answer to anything...'

        args = event.args
        if not len(args):
            return

        self.answers[event.meta['host']] = [event.meta['nick'], ' '.join(args)]

    def voted_already(self, host):
        """Return whether user has already voted yes/no"""
        return (host in self.yeses) or (host in self.nos)

    @cmd
    def yes(self, event):
        """Agree with a question"""
        if self.voting_in_progress(question=True):
            return
        elif not self.voting_in_progress():
            return 'No voting in progress.'

        host = event.meta['host']
        if not self.voted_already(host):
            self.yeses[host] = event.meta['nick']

    @cmd
    def no(self, event):
        """Disagree with a question"""
        if self.voting_in_progress(question=True):
            return
        elif not self.voting_in_progress():
            return 'No voting in progress.'

        host = event.meta['host']
        if not self.voted_already(host):
            self.nos[host] = event.meta['nick']
