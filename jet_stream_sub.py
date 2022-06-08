import signal
import asyncio

import nats
from nats.js.api import StreamConfig, RetentionPolicy, StorageType
from nats.aio.msg import Msg

import os
from loguru import logger

NATS_URL = os.getenv("NATS_URL", "nats://:@127.0.0.1:4222")

async def main():
    nc = nats.NATS()

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

    await nc.connect(
        NATS_URL,
        reconnected_cb=reconnected_cb,
        disconnected_cb=disconnected_cb,
        max_reconnect_attempts=-1,
    )

    # Create JetStream context.
    js = nc.jetstream()
    

    NATS_STREAM_NAME = "sample-stream"
    NATS_SUBJECT = "messages"
    DELIVER_GROUP = "workers"

    # sc = StreamConfig(name=NATS_STREAM_NAME, subjects=[NATS_SUBJECT], retention=RetentionPolicy.WORK_QUEUE, storage=StorageType.MEMORY)

    # await js.add_stream(config=sc)


    async def cb(msg: Msg):
        logger.debug(msg)

    # Queue Async Subscribe
    await js.subscribe(NATS_SUBJECT, DELIVER_GROUP, cb=cb)

    logger.debug(f"Start listening subj='{NATS_SUBJECT}' with deliver_group='{DELIVER_GROUP}' ...")
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        pass

