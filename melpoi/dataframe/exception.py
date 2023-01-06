class MissingRunException(Exception):
    def __init__(self, *args, **kwargs):
        default_message = "Please use .run() method before accessing this attribute."
        if args:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(default_message, **kwargs)
