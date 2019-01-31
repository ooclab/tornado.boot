#! /usr/bin/env python3

import time
import signal
import logging
from functools import partial
from importlib import import_module

import tornado.options
from eva.conf import settings

from codebase.app import make_app
from codebase.utils.sqlalchemy import dbc

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 0


# how to shutdown tornado web server gracefully, ref:
# - https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784
# - https://gist.github.com/mywaiting/4643396
def sig_handler(server, sig, _):
    io_loop = tornado.ioloop.IOLoop.instance()

    def stop_loop(deadline):
        now = time.time()
        # TODO: 怎样判断可以立即退出？
        if now < deadline:
            logging.info('Waiting for next tick')
            io_loop.add_timeout(now + 1, stop_loop, deadline)
        else:
            io_loop.stop()
            logging.info('Shutdown finally')

    def shutdown():
        logging.info('Stopping http server')
        server.stop()
        logging.info('Will shutdown in %s seconds ...',
                     MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        stop_loop(time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)

    logging.warning('Caught signal: %s', sig)
    io_loop.add_callback_from_signal(shutdown)


def main():

    # sync database
    if settings.SYNC_DATABASE == "true":
        import_module(settings.MODELS_MODULE)
        dbc.create_all()

    # 启动 Tornado
    app = make_app()
    server = tornado.httpserver.HTTPServer(app, xheaders=True)

    # 设置 options
    tornado.options.define("port", default=3000, help="listen port", type=int)
    if app.settings["debug"]:
        tornado.options.options.logging = "debug"
    tornado.options.parse_command_line()

    port = tornado.options.options.port
    sockets = tornado.netutil.bind_sockets(port)

    # 监听信号，优雅退出
    signal.signal(signal.SIGTERM, partial(sig_handler, server))
    signal.signal(signal.SIGINT, partial(sig_handler, server))

    server.add_sockets(sockets)
    logging.info("api server is running at %d", port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
