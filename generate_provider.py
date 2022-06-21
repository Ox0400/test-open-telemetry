from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import ( OTLPLogExporter,)
from opentelemetry.exporter.otlp.proto.grpc._metric_exporter import ( OTLPMetricExporter,)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import ( OTLPSpanExporter,)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import ( OTLPSpanExporter as HTTPSpanExporter,)

from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

exporters = [
    OTLPSpanExporter,
    #HTTPSpanExporter,
    #OTLPLogExporter,
    #OTLPMetricExporter,
]
exporters_ins = {}

for exporter in exporters:
    try:
        exporters_ins[exporter] = exporter()
    except Exception as e:
        print ('Unexpected exception raised when instantiating %s' % exporter)

#trace.set_tracer_provider(TracerProvider())

tracer_provider = TracerProvider() #trace.get_tracer_provider()
for exporter in exporters_ins.values():
    print ('add span processor', exporter)
    tracer_provider.add_span_processor( BatchSpanProcessor(exporter))

tracer_provider.add_span_processor( BatchSpanProcessor(ConsoleSpanExporter()))

print ('tracer_provider.resource.attributes', tracer_provider.resource.attributes)
