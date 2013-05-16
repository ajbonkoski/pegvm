
class Inputter:
    def __init__(self, string):
        self.string = string
        self.position = 0
        self.position_save_stack = []

    def get_position(self):
        return self.position

    def get_next(self):
        ret = self.string[self.position]
        self.position += 1
        return ret

    def peek(self):
	if self.eof():
            return ''
       	return self.string[self.position]

    def peek_clean(self):
	ch = self.peek()
	return ch.replace('\n', '\\n')

    def save_state(self):
        self.position_save_stack.append(self.position)

    def restore_state(self):
        self.position = self.position_save_stack.pop()

    def pop_backup_state(self):
        self.position_save_stack.pop()

    def eof(self):
        return self.position == len(self.string)

