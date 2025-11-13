"""
This module provides LXST real-time streaming capabilities for the RNS Flet App.
LXST is a flexible real-time streaming system with support for audio processing,
codecs, and network transport over Reticulum.
"""

import LXST
import RNS


class LXSTManager:
    """Manages LXST streaming functionality."""

    def __init__(self):
        self.sources = {}
        self.sinks = {}
        self.pipelines = {}
        self.identity = None
        self.destination = None

    def initialize(self, identity, destination_name="rns_flet_app_stream"):
        """Initialize LXST with identity and destination.

        Args:
            identity: RNS Identity object
            destination_name: Name for the LXST destination

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self.identity = identity

            self.destination = RNS.Destination(
                identity,
                RNS.Destination.IN,
                RNS.Destination.SINGLE,
                destination_name
            )

            return True
        except Exception as e:
            print(f"Failed to initialize LXST: {e}")
            return False

    def create_audio_source(self, source_type="local", **kwargs):
        """Create a new audio source.

        Args:
            source_type: Type of source ("local", "remote", "file", etc.)
            **kwargs: Additional parameters for the source

        Returns:
            LXST source object or None if creation failed
        """
        try:
            if source_type == "local":
                source = LXST.LocalSource(**kwargs)
            elif source_type == "remote":
                source = LXST.Network.RemoteSource(**kwargs)
            elif source_type == "file":
                source = LXST.OpusFileSource(**kwargs)
            else:
                print(f"Unknown source type: {source_type}")
                return None

            source_id = f"source_{id(source)}"
            self.sources[source_id] = source
            return source
        except Exception as e:
            print(f"Failed to create audio source: {e}")
            return None

    def create_audio_sink(self, sink_type="local", **kwargs):
        """Create a new audio sink.

        Args:
            sink_type: Type of sink ("local", "remote", "null", etc.)
            **kwargs: Additional parameters for the sink

        Returns:
            LXST sink object or None if creation failed
        """
        try:
            if sink_type == "local":
                sink = LXST.LocalSink(**kwargs)
            elif sink_type == "remote":
                sink = LXST.Network.RemoteSink(**kwargs)
            elif sink_type == "null":
                sink = LXST.Network.Null(**kwargs)
            else:
                print(f"Unknown sink type: {sink_type}")
                return None

            sink_id = f"sink_{id(sink)}"
            self.sinks[sink_id] = sink
            return sink
        except Exception as e:
            print(f"Failed to create audio sink: {e}")
            return None

    def create_pipeline(self, source, sink, **kwargs):
        """Create an audio processing pipeline.

        Args:
            source: LXST source object
            sink: LXST sink object
            **kwargs: Additional pipeline parameters

        Returns:
            LXST pipeline object or None if creation failed
        """
        try:
            pipeline = LXST.Pipeline(source, sink, **kwargs)
            pipeline_id = f"pipeline_{id(pipeline)}"
            self.pipelines[pipeline_id] = pipeline
            return pipeline
        except Exception as e:
            print(f"Failed to create pipeline: {e}")
            return None

    def start_pipeline(self, pipeline):
        """Start an audio pipeline.

        Args:
            pipeline: The LXST pipeline to start

        Returns:
            bool: True if starting was successful, False otherwise
        """
        try:
            pipeline.start()
            return True
        except Exception as e:
            print(f"Failed to start pipeline: {e}")
            return False

    def stop_pipeline(self, pipeline):
        """Stop an audio pipeline.

        Args:
            pipeline: The LXST pipeline to stop

        Returns:
            bool: True if stopping was successful, False otherwise
        """
        try:
            pipeline.stop()
            return True
        except Exception as e:
            print(f"Failed to stop pipeline: {e}")
            return False

    def create_mixer(self, **kwargs):
        """Create an audio mixer.

        Args:
            **kwargs: Mixer parameters

        Returns:
            LXST mixer object or None if creation failed
        """
        try:
            mixer = LXST.Mixer(**kwargs)
            return mixer
        except Exception as e:
            print(f"Failed to create mixer: {e}")
            return None

    def create_telephone(self, destination_hash, **kwargs):
        """Create a telephone (voice call) connection.

        Args:
            destination_hash: Destination hash for the call
            **kwargs: Telephone parameters

        Returns:
            LXST telephone object or None if creation failed
        """
        try:
            telephone = LXST.Telephone(destination_hash, **kwargs)
            return telephone
        except Exception as e:
            print(f"Failed to create telephone: {e}")
            return None

    def get_pipeline_stats(self, pipeline):
        """Get statistics for a pipeline.

        Args:
            pipeline: The LXST pipeline

        Returns:
            dict: Pipeline statistics
        """
        try:
            return {
                "latency": getattr(pipeline, 'latency', 0),
                "bitrate": getattr(pipeline, 'bitrate', 0),
                "active": getattr(pipeline, 'active', False)
            }
        except Exception as e:
            print(f"Failed to get pipeline stats: {e}")
            return {}

    def list_active_pipelines(self):
        """List all active pipelines.

        Returns:
            list: List of active pipeline IDs
        """
        return [pipeline_id for pipeline_id, pipeline in self.pipelines.items()
                if getattr(pipeline, 'active', False)]

    def close_pipeline(self, pipeline_id):
        """Close and remove a pipeline.

        Args:
            pipeline_id: The pipeline ID to close

        Returns:
            bool: True if closing was successful, False otherwise
        """
        try:
            if pipeline_id in self.pipelines:
                pipeline = self.pipelines[pipeline_id]
                if hasattr(pipeline, 'active') and pipeline.active:
                    pipeline.stop()
                del self.pipelines[pipeline_id]
                return True
            return False
        except Exception as e:
            print(f"Failed to close pipeline {pipeline_id}: {e}")
            return False

    def announce_destination(self):
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


# Global instance for easy access
lxst_manager = LXSTManager()


def initialize_lxst(identity, destination_name="rns_flet_app_stream"):
    """Initialize LXST functionality.

    Args:
        identity: RNS Identity object
        destination_name: Name for the destination

    Returns:
        bool: True if initialization was successful, False otherwise
    """
    return lxst_manager.initialize(identity, destination_name)


def create_audio_source(source_type="local", **kwargs):
    """Create a new audio source.

    Args:
        source_type: Type of source ("local", "remote", "file", etc.)
        **kwargs: Additional parameters for the source

    Returns:
        LXST source object or None if creation failed
    """
    return lxst_manager.create_audio_source(source_type, **kwargs)


def create_audio_sink(sink_type="local", **kwargs):
    """Create a new audio sink.

    Args:
        sink_type: Type of sink ("local", "remote", "null", etc.)
        **kwargs: Additional parameters for the sink

    Returns:
        LXST sink object or None if creation failed
    """
    return lxst_manager.create_audio_sink(sink_type, **kwargs)


def create_pipeline(source, sink, **kwargs):
    """Create an audio processing pipeline.

    Args:
        source: LXST source object
        sink: LXST sink object
        **kwargs: Additional pipeline parameters

    Returns:
        LXST pipeline object or None if creation failed
    """
    return lxst_manager.create_pipeline(source, sink, **kwargs)


def start_pipeline(pipeline):
    """Start an audio pipeline.

    Args:
        pipeline: The LXST pipeline to start

    Returns:
        bool: True if starting was successful, False otherwise
    """
    return lxst_manager.start_pipeline(pipeline)


def stop_pipeline(pipeline):
    """Stop an audio pipeline.

    Args:
        pipeline: The LXST pipeline to stop

    Returns:
        bool: True if stopping was successful, False otherwise
    """
    return lxst_manager.stop_pipeline(pipeline)


def create_mixer(**kwargs):
    """Create an audio mixer.

    Args:
        **kwargs: Mixer parameters

    Returns:
        LXST mixer object or None if creation failed
    """
    return lxst_manager.create_mixer(**kwargs)


def create_telephone(destination_hash, **kwargs):
    """Create a telephone (voice call) connection.

    Args:
        destination_hash: Destination hash for the call
        **kwargs: Telephone parameters

    Returns:
        LXST telephone object or None if creation failed
    """
    return lxst_manager.create_telephone(destination_hash, **kwargs)


def get_pipeline_stats(pipeline):
    """Get statistics for a pipeline.

    Args:
        pipeline: The LXST pipeline

    Returns:
        dict: Pipeline statistics
    """
    return lxst_manager.get_pipeline_stats(pipeline)


def list_active_pipelines():
    """List all active pipelines.

    Returns:
        list: List of active pipeline IDs
    """
    return lxst_manager.list_active_pipelines()
