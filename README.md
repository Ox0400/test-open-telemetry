### pre isntall
```shell
python3 -m pip install tornado requests opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-tornado opentelemetry-exporter-otlp opentelemetry-exporter-prometheus opentelemetry-exporter-zipkin opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-otlp-proto-http opentelemetry-instrumentation-tornado

```

### startup services

```shell
docker-compose up -d
docker-compose logs -f
```


### startup web server

```shell
OTEL_SERVICE_NAME=test-webapp python run_executor.py
```


### test web client

```shell
export OTEL_SERVICE_NAME=client-app
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
export OTEL_PYTHON_TORNADO_EXCLUDED_URLS='^/$,/actions/messages/notify*'
OTEL_SERVICE_NAME=webapp-cli python3 cli.py
```

### verify
- prometheus  http://localhost:9090/graph?g0.expr=otelcol_exporter_sent_spans&g0.tab=0&g0.stacked=0&g0.show_exemplars=1&g0.range_input=1h
- zipkin http://localhost:9411/zipkin/
- jaeger http://localhost:16686/search
- otel metrics http://localhost:8888/metrics

### ref
- trace http headers https://www.w3.org/TR/trace-context/#trace-context-http-headers-format
- resources attributes example https://github.com/open-telemetry/opentelemetry-python/blob/d4d7c67663cc22615748d632e1c8c5799e8eacae/opentelemetry-sdk/src/opentelemetry/sdk/resources/__init__.py#L36
- OpenTelemetry Environment Variable Specification https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/sdk-environment-variables.md
- Resource Semantic Conventions https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/resource/semantic_conventions/README.md
