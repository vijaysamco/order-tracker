import sys

from opentelemetry import _logs, metrics, trace
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import ConsoleLogRecordExporter, SimpleLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    InMemoryMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


resource = Resource.create({"service.name": "order-tracker"})

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

metric_reader = InMemoryMetricReader()
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
request_counter = metrics.get_meter(__name__).create_counter(
    "http.server.request.count",
    unit="{request}",
    description="Number of HTTP requests handled by the application",
)


def export_metrics():
    metrics_data = metric_reader.get_metrics_data()
    if metrics_data is not None:
        ConsoleMetricExporter(out=sys.stdout).export(metrics_data)


logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    SimpleLogRecordProcessor(ConsoleLogRecordExporter())
)
_logs.set_logger_provider(logger_provider)
lookup_logger = logger_provider.get_logger("order_tracker.lookups")