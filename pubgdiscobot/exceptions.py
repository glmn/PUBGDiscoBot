class NotEnoughParams(Exception):
    def __init__(self, message='Not enough parameters passed'):
        super().__init__(message)
