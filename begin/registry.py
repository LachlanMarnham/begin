class Registry:

    def __init__(self, name='default'):
        self.name = name
        self.targets = {}

    def register_target(self, *args, **kwargs):
        if args:
            function = args.pop()
            self._register_target(function)
        else:
            def decorator(function):
                self._register_target(function, **kwargs)
                return function
            return decorator

    def _register_target(self, function, **kwargs):
        print(kwargs)
        print(function.__name__)
        self.targets[(self.name, function.__name__)] = function
