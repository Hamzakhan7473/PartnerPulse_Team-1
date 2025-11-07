"""
Prometheus-based metrics factory and metrics implementations.

Uses the prometheus_client library
to create and manage Prometheus metrics.
"""

from collections.abc import Iterable

from prometheus_client import Counter as PrometheusCounter
from prometheus_client import Gauge as PrometheusGauge
from prometheus_client import Histogram as PrometheusHistogram
from prometheus_client import Summary as PrometheusSummary

from .metrics_factory import MetricsFactory


class PrometheusMetricsFactory(MetricsFactory):
    """
    Prometheus-based implementation of MetricsFactory.
    """

    class Counter(MetricsFactory.Counter):
        """
        Prometheus-based implementation of a counter metric.
        """

        def __init__(self, counter: PrometheusCounter):
            self._counter = counter

        def increment(self, value: float = 1, labels: dict[str, str] = {}):
            if labels:
                self._counter.labels(**labels).inc(value)
            else:
                self._counter.inc(value)

    class Gauge(MetricsFactory.Gauge):
        """
        Prometheus-based implementation of a gauge metric.
        """

        def __init__(self, gauge: PrometheusGauge):
            self._gauge = gauge

        def set(self, value: float, labels: dict[str, str] = {}):
            if labels:
                self._gauge.labels(**labels).set(value)
            else:
                self._gauge.set(value)

    class Histogram(MetricsFactory.Histogram):
        """
        Prometheus-based implementation of a histogram metric.
        """

        def __init__(self, histogram: PrometheusHistogram):
            self._histogram = histogram

        def observe(self, value: float, labels: dict[str, str] = {}):
            if labels:
                self._histogram.labels(**labels).observe(value)
            else:
                self._histogram.observe(value)

    class Summary(MetricsFactory.Summary):
        """
        Prometheus-based implementation of a summary metric.
        """

        def __init__(self, summary: PrometheusSummary):
            self._summary = summary

        def observe(self, value: float, labels: dict[str, str] = {}):
            if labels:
                self._summary.labels(**labels).observe(value)
            else:
                self._summary.observe(value)

    # Dictionary to store created metrics by name.
    _metrics: dict[str, Counter | Gauge | Histogram | Summary] = {}

    def get_counter(
        self,
        name: str,
        description: str,
        label_names: Iterable[str] = (),
    ) -> Counter:
        if name not in self._metrics:
            self._metrics[name] = PrometheusMetricsFactory.Counter(
                PrometheusCounter(name, description, labelnames=label_names)
            )
        counter = self._metrics[name]
        if not isinstance(counter, PrometheusMetricsFactory.Counter):
            raise ValueError(f"{name} is not the name of a Counter")

        return counter

    def get_gauge(
        self,
        name: str,
        description: str,
        label_names: Iterable[str] = (),
    ) -> Gauge:
        if name not in self._metrics:
            self._metrics[name] = PrometheusMetricsFactory.Gauge(
                PrometheusGauge(name, description, labelnames=label_names)
            )
        gauge = self._metrics[name]
        if not isinstance(gauge, PrometheusMetricsFactory.Gauge):
            raise ValueError(f"{name} is not the name of a Gauge")

        return gauge

    def get_histogram(
        self,
        name: str,
        description: str,
        label_names: Iterable[str] = (),
    ) -> Histogram:
        if name not in self._metrics:
            self._metrics[name] = PrometheusMetricsFactory.Histogram(
                PrometheusHistogram(name, description, labelnames=label_names)
            )
        histogram = self._metrics[name]
        if not isinstance(histogram, PrometheusMetricsFactory.Histogram):
            raise ValueError(f"{name} is not the name of a Histogram")

        return histogram

    def get_summary(
        self,
        name: str,
        description: str,
        label_names: Iterable[str] = (),
    ) -> Summary:
        if name not in self._metrics:
            self._metrics[name] = PrometheusMetricsFactory.Summary(
                PrometheusSummary(name, description, labelnames=label_names)
            )
        summary = self._metrics[name]
        if not isinstance(summary, PrometheusMetricsFactory.Summary):
            raise ValueError(f"{name} is not the name of a Summary")

        return summary
