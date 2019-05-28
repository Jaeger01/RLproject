import tcod as libtcod

import textwrap


class Message:
    def __init__(self, text, color=libtcod.white):
        self.text = text
        self.color = color


class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        # Split message into multiple lines if needed
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # If log full delete oldest line to make room
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a message object with text and color
            self.messages.append(Message(line, message.color))
