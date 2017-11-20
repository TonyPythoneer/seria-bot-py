# -*- coding: utf-8 -*-
import asyncio
import os

from flask import Flask

flask_app = Flask(__name__)


@flask_app.route('/')
def hello():
    return 'Hello World!'


async def main():
    port = int(os.environ.get('PORT', 5000))
    future_tasks = [
        asyncio.ensure_future(flask_app.run(host='0.0.0.0', port=port)),
    ]

    return await asyncio.gather(*future_tasks)


if __name__ == '__main__':
    print('Application server gets started!')
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
