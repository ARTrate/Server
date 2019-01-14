# Source: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s19.html (14.01.2019)


class RingBuffer:
    """ class that implements a not-yet-full buffer """
    def __init__(self, size_max):
        self.max = size_max
        self.data = []

    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max

        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:]+self.data[:self.cur]

        def get_sum(self):
            return sum(self.data)

        def get_len(self):
            return len(self.data)

        def reset(self):
            self.data = []
            self.cur = 0
            self.__class__ = RingBuffer

    def append(self, x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data

    def get_sum(self):
        return sum(self.data)

    def get_len(self):
            return len(self.data)

    def reset(self):
        self.data = []
        self.cur = 0
