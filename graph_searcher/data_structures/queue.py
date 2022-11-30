class Queue:
    """
    A simple queue implementation.
    """

    def __init__(self):
        self.__queue = []

    def __str__(self):
        return str(self.__queue)

    def __repr__(self):
        return str(self.__queue)

    def __len__(self):
        return len(self.__queue)

    def enqueue(self, item):
        self.__queue.append(item)

    def dequeue(self):
        return self.__queue.pop(0)

    def is_empty(self):
        return len(self.__queue) == 0

    def peek(self):
        return self.__queue[0]

    def size(self):
        return len(self.__queue)
