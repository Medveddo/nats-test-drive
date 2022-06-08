import asyncio
import os
import random
import nats
from nats.js.api import StreamConfig, RetentionPolicy, StorageType
from nats.errors import Error
from loguru import logger

NATS_URL = os.getenv("NATS_URL", "nats://:@127.0.0.1:4222")


async def main():
    nc = await nats.connect(NATS_URL, user="a", password="a")

    # Create JetStream context.
    js = nc.jetstream()
    
    NATS_STREAM_NAME = "sample-stream"
    NATS_SUBJECT = "messages"

    # sc = StreamConfig(name=NATS_STREAM_NAME, subjects=[NATS_SUBJECT], retention=RetentionPolicy.WORK_QUEUE, storage=StorageType.MEMORY)

    # Persist messages on 'foo's subject.
    # await js.add_stream(config=sc)
    i = 0
    while True:
        i += 1
        rnd = random.SystemRandom()
        a = rnd.randint(0, 10000)
        a = i
        ack = await js.publish(NATS_SUBJECT, f"hello world: {a}".encode(), headers={"X-Request-Id": f"{a*2}"})
        logger.debug(ack)
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(e)
        pass
