"""
LXMF functionality (messaging).
"""

import LXMF
import RNS


class LXMFManager:
    """Manages LXMF messaging functionality."""

    def __init__(self):
        self.router = None
        self.identity = None
        self.destination = None
        self.storage_path = None

    def initialize(self, identity, destination_name="rns_flet_app", storage_path=None, display_name=None):
        """Initialize LXMF with identity and destination.

        Args:
            identity: RNS Identity object
            destination_name: Name for the LXMF destination
            storage_path: Path for LXMF storage (optional)
            display_name: Display name for announcements (optional, defaults to destination_name)

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            import os
            import tempfile

            if storage_path is None:
                self.storage_path = os.path.join(tempfile.gettempdir(), "lxmf_storage")
            else:
                self.storage_path = storage_path

            os.makedirs(self.storage_path, exist_ok=True)

            self.router = LXMF.LXMRouter(identity=identity, storagepath=self.storage_path)

            # Use display_name if provided, otherwise use destination_name
            display = display_name if display_name else destination_name
            self.destination = self.router.register_delivery_identity(identity, display_name=display)

            if not self.destination:
                if hasattr(self.router, 'delivery_destinations') and self.router.delivery_destinations:
                    self.destination = list(self.router.delivery_destinations.values())[0]
                else:
                    self.destination = RNS.Destination(
                        identity,
                        RNS.Destination.IN,
                        RNS.Destination.SINGLE,
                        destination_name
                    )

            self.identity = identity
            return True
        except Exception as e:
            print(f"Failed to initialize LXMF: {e}")
            return False

    def create_message(self, destination_hash, content, title=None, fields=None):
        """Create a new LXMF message.

        Args:
            destination_hash: The destination address/hash (16-byte bytes or hex string)
            content: The message content (string)
            title: Optional message title
            fields: Optional dictionary of additional fields

        Returns:
            LXMF.LXMessage object or None if creation failed
        """
        try:
            if not self.destination:
                print("LXMF destination not initialized")
                return None

            if isinstance(destination_hash, str):
                try:
                    destination_hash = bytes.fromhex(destination_hash)
                except ValueError:
                    print(f"Invalid hash format: {destination_hash}")
                    return None

            if not len(destination_hash) == RNS.Reticulum.TRUNCATED_HASHLENGTH // 8:
                print(f"Invalid destination hash length: {len(destination_hash)}")
                return None

            identity = RNS.Identity.recall(destination_hash)

            if identity is None:
                print("Could not recall Identity for destination. Requesting path...")
                RNS.Transport.request_path(destination_hash)
                print("Path requested. Waiting for announce...")
                return None

            lxmf_destination = RNS.Destination(
                identity,
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                "lxmf",
                "delivery"
            )

            try:
                message = LXMF.LXMessage(
                    lxmf_destination,
                    self.destination,
                    content,
                    title=title if title else "",
                    desired_method=LXMF.LXMessage.DIRECT
                )
                message.try_propagation_on_fail = True

                if fields:
                    message.fields = fields

                return message
            except Exception as e:
                print(f"Failed to create LXMF message: {e}")
                return None
        except Exception as e:
            print(f"Failed to create LXMF message: {e}")
            return None

    def send_message(self, message):
        """Send an LXMF message.

        Args:
            message: The LXMF.LXMessage to send

        Returns:
            bool: True if sending was successful, False otherwise
        """
        try:
            if self.router:
                self.router.handle_outbound(message)
                return True
            else:
                print("LXMF router not initialized")
                return False
        except Exception as e:
            print(f"Failed to send LXMF message: {e}")
            return False

    def receive_messages(self):
        """Receive pending LXMF messages.

        Returns:
            list: List of received LXMF.LXMessage objects
        """
        try:
            if self.router and hasattr(self.router, 'inbound_queue'):
                messages = []
                while not self.router.inbound_queue.empty():
                    try:
                        message = self.router.inbound_queue.get_nowait()
                        messages.append(message)
                    except:
                        break
                return messages
            else:
                return []
        except Exception as e:
            print(f"Failed to receive LXMF messages: {e}")
            return []

    def get_router_stats(self):
        """Get router statistics.

        Returns:
            dict: Router statistics
        """
        if self.router:
            return {
                "outbound_queue_size": self.router.outbound_queue.qsize(),
                "inbound_queue_size": self.router.inbound_queue.qsize(),
                "delivery_rate": getattr(self.router, 'delivery_rate', 0)
            }
        return {}

    def announce(self):
        """Announce this destination on the network.

        Returns:
            bool: True if announcement was successful, False otherwise
        """
        try:
            if self.destination:
                self.destination.announce()
                return True
            return False
        except Exception as e:
            print(f"Failed to announce destination: {e}")
            return False

lxmf_manager = LXMFManager()

def initialize_lxmf(identity, destination_name="rns_flet_app", display_name=None):
    """Initialize LXMF functionality.

    Args:
        identity: RNS Identity object
        destination_name: Name for the destination
        display_name: Display name for announcements (optional)

    Returns:
        bool: True if initialization was successful, False otherwise
    """
    return lxmf_manager.initialize(identity, destination_name, storage_path=None, display_name=display_name)

def create_message(destination_hash, content, title=None, fields=None):
    """Create a new LXMF message.

    Args:
        destination_hash: The destination address/hash
        content: The message content
        title: Optional message title
        fields: Optional dictionary of additional fields

    Returns:
        LXMF message object or None if creation failed
    """
    return lxmf_manager.create_message(destination_hash, content, title, fields)

def send_message(message):
    """Send an LXMF message.

    Args:
        message: The LXMF message to send

    Returns:
        bool: True if sending was successful, False otherwise
    """
    return lxmf_manager.send_message(message)

def receive_messages():
    """Receive pending LXMF messages.

    Returns:
        list: List of received messages
    """
    return lxmf_manager.receive_messages()

def get_lxmf_stats():
    """Get LXMF statistics.

    Returns:
        dict: LXMF statistics
    """
    return lxmf_manager.get_router_stats()
