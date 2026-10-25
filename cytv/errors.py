class UserError(RuntimeError):
    """An installer-owned message which contains no remote data or credentials."""


class TVRejected(UserError):
    """A definite negative TV reply, distinct from an unknown connection outcome."""


class ExistingRoot(UserError):
    """A previous Root deployment needs an explicit reinstall decision."""


class TVCommandError(UserError):
    """A failed SSH command with a numeric status, never remote output."""
    def __init__(self, exit_status):
        super().__init__('TV command failed. Run cytv doctor; retain the operation journal.')
        self.exit_status = exit_status if type(exit_status) is int and -1 <= exit_status <= 255 else None


class DeveloperKeyError(UserError):
    """A Key Server failure with a fixed reason code, never key material."""
    def __init__(self, message, reason_code):
        super().__init__(message)
        self.reason_code = reason_code if reason_code in (
            'key-server-unavailable', 'response-redirect', 'response-size',
            'response-format', 'key-unlock') else 'unknown'


class TVConnectionError(UserError):
    """An SSAP failure with allowlisted protocol metadata, never remote text."""
    def __init__(self, message, close_code=None, reason_code='connection-closed'):
        super().__init__(message)
        self.close_code = close_code if isinstance(close_code, int) and 1000 <= close_code <= 4999 else None
        self.reason_code = reason_code if reason_code in ('tv-not-ready', 'connection-closed', 'pairing-timeout') else 'connection-closed'


class TVNotReady(TVConnectionError):
    def __init__(self):
        super().__init__('TV is asleep or still starting. Turn it on with the remote and wait for the Home screen.',
                         close_code=1008, reason_code='tv-not-ready')
