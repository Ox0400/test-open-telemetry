#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zhipeng
# @Email: zhipeng.py@gmail.com
# @Date:   2022-06-21 18:26:37
# @Last Modified By:    zhipeng
# @Last Modified: 2022-06-22 18:12:40


import os
# before import opentelemetry required
# os.environ['OTEL_SERVICE_NAME'] = 'test-webapp'
import time
import socket

import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from tornado.concurrent import futures
from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.netutil import bind_sockets

from opentelemetry.util._time import _time_ns
from opentelemetry.instrumentation.tornado import TornadoInstrumentor
from opentelemetry.instrumentation.tornado import _start_span
from opentelemetry import trace
# from opentelemetry.context import get_current
# from opentelemetry.trace.status import StatusCode
# from opentelemetry.sdk.resources import SERVICE_NAME


from generate_provider import tracer_provider


def server_request_hook(span, handler):
    handler._root = span
    handler._root_ctx = trace.set_span_in_context(span)
    print ('handler ~~', handler)
    print ('handler root~~', handler.root)
    print ('handler root ctx~~', handler.root_ctx)


trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

TornadoInstrumentor().instrument(server_request_hook=server_request_hook)

print ('tracer', dir(tracer))


class Inner(tornado.web.RequestHandler):
    _root = None
    _root_ctx = None
    _otel_trace_context_key = None

    @property
    def root(self):
        # https://github.com/open-telemetry/opentelemetry-python-contrib/blob/62e0a31ff9c95efa0110e7cd1bc23b59bc7bdcc8/instrumentation/opentelemetry-instrumentation-tornado/src/opentelemetry/instrumentation/tornado/__init__.py#L197
        self._root = self._root \
            or (self._otel_trace_context_key and self._otel_trace_context_key.span) \
            or _start_span(self.tracer, self, _time_ns()).span
        #print ('root ctx', self._otel_trace_context_key.span)
        print ('root span', self._root)
        return self._root

    @property
    def root_ctx(self):
        if not self._root_ctx:
            #print ('get_current', get_current())
            self._root_ctx = trace.set_span_in_context(self.root)
            print('00000 root ctx', type(self._root_ctx), self._root_ctx)
        print('11111 root ctx', type(self._root_ctx), self._root_ctx)
        return self._root_ctx

    @property
    def tracer(self):
        return self.application.tracer

    def on_finish(self):
        with self.tracer.start_as_current_span("audit_task", context=self.root_ctx):
            # with self.tracer.start_as_current_span("audit_task", ):
            time.sleep(0.05)

    # @tracer.start_as_current_span("root get")
    @gen.coroutine
    def get(self, *args, **kwargs):
        yield IOLoop.current().run_in_executor(None, self._get, *args, **kwargs)

    def finish(self, chunk=None):
        self.set_status(200)
        super(Inner, self).finish(chunk)
        self.flush()

    def set_status(self, status_code, *args, **kwargs):
        print('self.tracer', self.tracer, dir(self.tracer))
        super(Inner, self).set_status(status_code, *args, **kwargs)
        #print ('set status', self.root_span, StatusCode.OK)
        #self.root_span.status._status_code = StatusCode.OK
        # self.root_span.set_status(1)

    def sleep(self, t=2, msg=''):
        # with self.tracer.start_as_current_span("sleeping %ss" % t, context=self.ctx):
        print ('root span', self.root)
        print ('root ctx', self.root_ctx)
        with self.tracer.start_as_current_span("sleeping", context=self.root_ctx):
            for i in range(t):
                time.sleep(1)
                print ('blocking %s/%s' % (i+1, t))
            msg = ('done: %s/%s, %s' % (i+1, t, msg))
            self.write(msg)


class LongHandler(Inner):
    def _get(self):
        self.sleep(msg='coroutine + in executor')


class ShortHandler(Inner):

    def _get(self):
        with self.tracer.start_as_current_span("pew pass ..."):
            # with self.tracer.start_as_current_span("pew pass ...", context=self.ctx):
            print('pew')


class NewHandler(Inner):
    executor = futures.ThreadPoolExecutor()

    @gen.coroutine
    def get(self, *args, **kwargs):
        yield self._get(*args, **kwargs)

    @run_on_executor
    def _get(self, *args, **kwargs):
        self.sleep(msg='coroutine + on executor')


class OldHandler(Inner):
    executor = futures.ThreadPoolExecutor()

    @run_on_executor
    def get(self, *args, **kwargs):
        # with self.tracer.start_as_current_span('real get') as foo:
        #    print ('span foo', foo)
        #    self._get(*args, **kwargs)
        return self._get(*args, **kwargs)

    def _get(self, *args, **kwargs):
        self.sleep(msg='on executor')


class CustomHttpServer(HTTPServer):
    def bind(self, port, address=None, family=socket.AF_UNSPEC, backlog=128, reuse_port=True):
        """
        overwrite base bind function
        make sure reuse_port is True for bind_sockets
        """
        sockets = bind_sockets(
            port, address=address, family=family,
            backlog=backlog, reuse_port=reuse_port
        )
        if self._started:
            self.add_sockets(sockets)
        else:
            self._pending_sockets.extend(sockets)


class Master(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/long", LongHandler),
            (r"/short", ShortHandler),
            (r"/old", OldHandler),
            (r"/new", NewHandler),
        ]
        super(self.__class__, self).__init__(
            handlers, debug=True

        )
        self.tracer = tracer
        server = CustomHttpServer(self,)
        server.bind(7080, address='0.0.0.0', reuse_port=True)
        server.start(1)
        self.io_loop = ioloop = IOLoop.current()

    def engarde(self):
        self.io_loop.start()


if __name__ == "__main__":
    keeper = Master()
    # keeper.listen(7080)
    keeper.engarde()
