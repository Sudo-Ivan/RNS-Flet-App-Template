"""
RNS (Reticulum Network Stack) initialization and management.
"""

import RNS


class RNSManager:
    """Manages RNS initialization and identity handling."""

    def __init__(self):
        self.identity = None
        self.initialized = False

    def initialize(self):
        """Initialize the Reticulum network.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            if not self.initialized:
                RNS.Reticulum()
                self.initialized = True
            return True
        except (OSError, ValueError) as e:
            print(f"Failed to initialize Reticulum: {e}")
            return False

    def create_identity(self):
        """Create or load an RNS identity.

        Tries to load existing identity from storage, creates new one if not found.

        Returns:
            RNS.Identity: The identity or None if creation failed
        """
        try:
            import os

            config_path = RNS.Reticulum.configpath
            storage_dir = os.path.join(os.path.dirname(config_path), 'storage')
            identity_file = os.path.join(storage_dir, 'identity')

            if os.path.exists(identity_file):
                self.identity = RNS.Identity.from_file(identity_file)
                return self.identity
            else:
                self.identity = RNS.Identity()
                os.makedirs(storage_dir, exist_ok=True)
                self.identity.to_file(identity_file)
                return self.identity
        except Exception as e:
            print(f"Failed to create/load identity: {e}")
            return None

    def load_identity(self, identity_data):
        """Load an identity from data.

        Args:
            identity_data: Identity data (bytes)

        Returns:
            RNS.Identity: The loaded identity or None if loading failed
        """
        try:
            self.identity = RNS.Identity.from_bytes(identity_data)
            return self.identity
        except Exception as e:
            print(f"Failed to load identity: {e}")
            return None

    def save_identity(self):
        """Save the current identity.

        Returns:
            bytes: Identity data or None if saving failed
        """
        try:
            if self.identity:
                return self.identity.to_bytes()
            return None
        except Exception as e:
            print(f"Failed to save identity: {e}")
            return None

    def get_identity_hash(self):
        """Get the identity hash.

        Returns:
            bytes: Identity hash or None
        """
        if self.identity:
            return self.identity.hash
        return None

    def get_status(self):
        """Get the current status of the Reticulum network.

        Returns:
            dict: Status information about the Reticulum network.
        """
        if self.initialized and RNS.Reticulum.is_connected():
            return {
                "connected": True,
                "interfaces": len(RNS.Reticulum.get_interfaces()),
                "peers": len(RNS.Reticulum.get_peers()),
                "identity_hash": self.get_identity_hash().hex() if self.identity else None
            }
        else:
            return {
                "connected": False,
                "interfaces": 0,
                "peers": 0,
                "identity_hash": None
            }


rns_manager = RNSManager()


def initialize_reticulum():
    """Initialize the Reticulum network.

    Returns:
        bool: True if initialization was successful, False otherwise.
    """
    return rns_manager.initialize()


def create_identity():
    """Create a new RNS identity.

    Returns:
        RNS.Identity: The created identity or None if creation failed
    """
    return rns_manager.create_identity()


def load_identity(identity_data):
    """Load an identity from data.

    Args:
        identity_data: Identity data (bytes)

    Returns:
        RNS.Identity: The loaded identity or None if loading failed
    """
    return rns_manager.load_identity(identity_data)


def save_identity():
    """Save the current identity.

    Returns:
        bytes: Identity data or None if saving failed
    """
    return rns_manager.save_identity()


def get_identity_hash():
    """Get the identity hash.

    Returns:
        bytes: Identity hash or None
    """
    return rns_manager.get_identity_hash()


def get_reticulum_status():
    """Get the current status of the Reticulum network.

    Returns:
        dict: Status information about the Reticulum network.
    """
    return rns_manager.get_status()
