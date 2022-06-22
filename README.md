### pre isntall
```shell
python3 -m pip install tornado requests opentelemetry-exporter-otlp opentelemetry-exporter-prometheus opentelemetry-exporter-zipkin opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-otlp-proto-http

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
OTEL_SERVICE_NAME=webapp-cli python3 cli.py
```

### verify logs
- prometheus  http://localhost:9090/graph?g0.expr=otelcol_exporter_sent_spans&g0.tab=0&g0.stacked=0&g0.show_exemplars=1&g0.range_input=1h
- zipkin http://localhost:9411/zipkin/
- jaeger http://localhost:16686/search
- otel metrics http://localhost:8888/metrics
