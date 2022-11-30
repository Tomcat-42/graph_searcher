class Stack:

    def __init__(self, stack=[]):
        self.__stack = stack

    def __str__(self):
        return str(self.__stack)

    def __repr__(self):
        return str(self.__stack)

    def push(self, item):
        self.__stack.append(item)

    def pop(self):
        return self.__stack.pop()

    def peek(self):
        return self.__stack[-1]

    def is_empty(self):
        return len(self.__stack) == 0
