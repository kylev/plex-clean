"""Plex Exception classes."""


class PlexError(Exception):
    pass


class PlexTypeError(PlexError, TypeError):
    pass


class PlexValueError(PlexError, ValueError):
    pass


class InvalidRegex(PlexError):
    pass


class InvalidToken(PlexError):
    def __init__(self, token_number, message):
        PlexError.__init__(self, "Token number %d: %s" % (token_number, message))


class InvalidScanner(PlexError):
    pass


class AmbiguousAction(PlexError):
    def __init__(self):
        PlexError.__init__("Two tokens with different actions can match the "
                           "same string")


class UnrecognizedInput(PlexError):
    def __init__(self, scanner, state_name):
        self.scanner = scanner
        self.position = scanner.position()
        self.state_name = state_name

    def __str__(self):
        return "'%s', line %d, char %d: Token not recognised in state %s" \
                % (self.position + (repr(self.state_name),))



