""""Inputter provides a simple interface to peek/get characters
from an input stream."""

class Inputter:

    def __init__(self, string):
        """Initialize a new Inputter with the provided string."""
        self.string = string
        self.position = 0
        self.position_save_stack = []

    def get_position(self):
        """Returns the position of the next character to be read."""
        return self.position

    def get_next(self):
        """Returns the next character, incrementing the internal
        position counter."""
        ret = self.string[self.position]
        self.position += 1
        return ret

    def peek(self):
        """Returns the next character. Does not increment the internal
        position counter. Returns '' on EOF. """
        if self.eof():
            return ''
        return self.string[self.position]

    def peek_clean(self):
        """Similair to peek(), but also escapes the newline character"""
        ch = self.peek()
        return ch.replace('\n', '\\n')

    def save_state(self):
        """Internally saves a copy of the inputter's current state, so
        it can be restored later"""
        self.position_save_stack.append(self.position)

    def restore_state(self):
        """Restores the internal state to a previously saved state."""
        self.position = self.position_save_stack.pop()

    def pop_backup_state(self):
        """Discards the most recently saved internal state."""
        self.position_save_stack.pop()

    def eof(self):
        """Returns wether the Inputter has reached the End-of-File"""
        return self.position == len(self.string)
