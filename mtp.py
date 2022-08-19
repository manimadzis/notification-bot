import asyncio
import time

import aioschedule


async def job_that_executes_once():
    # Do some work that only needs to happen once...
    print("123")
    return aioschedule.CancelJob


aioschedule.every(1).seconds.do(job_that_executes_once)


async def main():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
