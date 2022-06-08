import asyncio
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
from loguru import logger

async def main():

    nc = await nats.connect("nats://localhost:4222")

    payload=b"Published message #1"
    subject="awesome.queue.1"
    ack = await nc.publish(
        subject=subject,
        payload=payload
    )
    logger.info(f"Published payload='{payload}' to subject='{subject}'. {ack}")

    await nc.drain()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(e)