import larv


class OnPressComponent(larv.Component):
    """
    Defines a component used for a trigger effect (initially designed to be
    used by the menu engine).
    Stores a function to be called when some event happens.

    In the menu context: every menu button will have a OnPressComponent so that
    when the player selects that option, the function stored in this component
    will be called.

    Usage:
        # create a function (can also use an existing one)
        def raiseEndException():
            raise larv.EndProgramException()

        # then create the component like this
        function = raiseEndException # without ()!!!
        args = ('test', 'i_dont_know')
        component = OnPressComponent(function, args)

        # then, when wanting to execute the function
        function = OnPressComponent.function
        args = OnPressComponent.args
        function(*args)

    """
    def __init__(self, function, args):
        self.function = function
        self.args = args
        self.kargs = None