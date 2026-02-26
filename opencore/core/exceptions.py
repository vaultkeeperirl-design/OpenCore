class SwarmError(Exception):
    """Base exception for Swarm-related errors."""
    pass

class AgentNotFoundError(SwarmError):
    """Raised when an agent is not found."""
    pass

class AgentOperationError(SwarmError):
    """Raised when an operation on an agent is invalid (e.g. removing the main agent)."""
    pass
