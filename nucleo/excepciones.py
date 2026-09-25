class TekniError(Exception):
    pass


class ErrorConexionRobot(TekniError):
    pass


class IAError(TekniError):
    pass


class AudioError(TekniError):
    pass