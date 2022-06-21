import os
#os.environ['OTEL_SERVICE_NAME'] = 'webapp-cli'
#os.environ['OTEL_EXPORTER_OTLP_ENDPOINT']='http://localhost:4317'

from sys import argv

from requests import get, Session
from opentelemetry import trace
from opentelemetry.propagate import inject
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.trace.status import StatusCode
from generate_provider import tracer_provider
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer_provider().get_tracer(__name__)


uri = 'new?hello=1'
if len(argv) == 1:
    pass
else:
    uri = argv[1]

with tracer.start_as_current_span("client") as root:
    req = Session()

    with tracer.start_as_current_span("client-server"):
        headers = {}
        inject(headers)
        res = req.get( "http://localhost:7080/%s" % uri, headers=headers,)
        print(res.request.headers)
        print(res.headers)
        assert res.status_code == 200

        #res = req.get( "http://localhost:7080/short", headers=headers,)
        #print(res.request.headers)
        #print(res.headers)
        #assert res.status_code == 200
        #root.status._status_code = StatusCode.OK
