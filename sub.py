import asyncio
import signal
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
from nats.aio.client import Client as NATS

from loguru import logger

async def main():

    nc = NATS()

    async def stop():
        await asyncio.sleep(1)
        asyncio.get_running_loop().stop()

    def signal_handler():
        if nc.is_closed:
            return
        logger.debug("Disconnecting...")
        asyncio.create_task(nc.close())
        asyncio.create_task(stop())

    for sig in ('SIGINT', 'SIGTERM'):
        asyncio.get_running_loop().add_signal_handler(getattr(signal, sig), signal_handler)

    async def disconnected_cb():
        logger.debug("Got disconnected...")

    async def reconnected_cb():
        logger.debug("Got reconnected...")

    await nc.connect("127.0.0.1",
                     reconnected_cb=reconnected_cb,
                     disconnected_cb=disconnected_cb,
                     max_reconnect_attempts=-1)

    async def help_request(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        logger.debug("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))
        # await nc.publish(reply, b'I can help')

    # Use queue named 'workers' for distributing requests
    # among subscribers.
    await nc.subscribe("awesome.queue.1", "workers", cb=help_request)

    logger.debug("Start listening 'awesome.queue.1' subject ...")
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.run_forever()
        loop.close()
    except Exception as e:
        logger.error(e)
        pass