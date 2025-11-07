"""
Abstract base classes for a metrics factory and its metrics.

Defines the interface for creating and managing different types
of metrics such as counters, gauges, histograms, and summaries.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable


class MetricsFactory(ABC):
    """
    Abstract base class for a metrics factory.
    """

    class Counter(ABC):
        """
        Abstract base class for a counter metric.
        """

        @abstractmethod
        def increment(self, value: float = 1, labels: dict[str, str] = {}):
            """
            Increment the counter by a specified value.

            Args:
                value (float, optional):
                    The amount to increment
                    the counter by (default: 1).
                labels (dict[str, str], optional):
                    Label name-value pairs
                    to associate with the increment.
                    If empty, no labels are used.
            """
            raise NotImplementedError

    class Gauge(ABC):
        """
        Abstract base class for a gauge metric.
        """

        @abstractmethod
        def set(self, value: float, labels: dict[str, str] = {}):
            """
            Set the gauge to a specified value.

            Args:
                value (float):
                    The value to set the gauge to.
                labels (dict[str, str], optional):
                    Label name-value pairs
                    to associate with the setting.
                    If empty, no labels are used.
            """
            raise NotImplementedError

    class Histogram(ABC):
        """
        Abstract base class for a histogram metric.
        """

        @abstractmethod
        def observe(self, value: float, labels: dict[str, str] = {}):
            """
            Observe a value and record it in the histogram.

            Args:
                value (float):
                    The value to observe.
                labels (dict[str, str], optional):
                    Label name-value pairs
                    to associate with the observation.
                    If empty, no labels are used.
            """
            raise NotImplementedError

    class Summary(ABC):
        """
        Abstract base class for a summary metric.
        """

        @abstractmethod
        def observe(self, value: float, labels: dict[str, str] = {}):
            """
            Observe a value and record it in the summary.

            Args:
                value (float):
                    The value to observe.
                labels (dict[str, str], optional):
                    Label name-value pairs
                    to associate with the observation.
                    If empty, no labels are used.
            """
            raise NotImplementedError

    @abstractmethod
    def get_counter(
        self,
        name: str,
        description: str,
        label_names: Iterable[str] = (),
    ) -> Counter:
        """
        Get a counter metric by name, creating it if it doesn't exist.

        Args:
            name (str):
                The name of the counter metric.
            description (str):
                A brief description of the counter metric.
            label_names (Iterable[str], optional):
                An iterable of label names for the counter.
                If empty, the counter will have no labels.

        Returns:
            Counter:
                An instance of the Counter metric.
        """
        raise NotImplementedError

    @abstractmethod
    def get_gauge(
        self,
        name: str,
        description: str,
        label_names: Iterable[str] = (),
    ) -> Gauge:
        """
        Get a gauge metric by name, creating it if it doesn't exist.

        Args:
            name (str):
                The name of the gauge metric.
            description (str):
                A brief description of the gauge metric.
            label_names (Iterable[str], optional):
                An iterable of label names for the gauge.
                If empty, the gauge will have no labels.

        Returns:
            Gauge:
                An instance of the Gauge metric.
        """
        raise NotImplementedError

    @abstractmethod
    def get_histogram(
        self,
        name: str,
        description: str,
        label_names: Iterable[str] = (),
    ) -> Histogram:
        """
        Get a histogram metric by name, creating it if it doesn't exist.

        Args:
            name (str):
                The name of the histogram metric.
            description (str):
                A brief description of the histogram metric.
            label_names (Iterable[str], optional):
                An iterable of label names for the histogram.
                If empty, the histogram will have no labels.

        Returns:
            Histogram:
                An instance of the Histogram metric.
        """
        raise NotImplementedError

    @abstractmethod
    def get_summary(
        self,
        name: str,
        description: str,
        label_names: Iterable[str] = (),
    ) -> Summary:
        """
        Get a summary metric by name, creating it if it doesn't exist.

        Args:
            name (str):
                The name of the summary metric.
            description (str):
                A brief description of the summary metric.
            label_names (Iterable[str], optional):
                An iterable of label names for the summary.
                If empty, the summary will have no labels.

        Returns:
            Summary:
                An instance of the Summary metric.
        """
        raise NotImplementedError
