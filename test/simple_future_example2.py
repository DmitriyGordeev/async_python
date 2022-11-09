import asyncio
import time


""" just a quick cheat-sheet for python's async syntax """

async def foo():
    await asyncio.sleep(4)
    return "foo()"


async def caller():
    future = asyncio.ensure_future(foo())
    print("Another code is running here in meantime")

    time.sleep(2)
    print ("future.done() =", future.done())

    # and then wait for task t
    await future
    print ("future.done() =", future.done())
    print ("future.result() =", future.result())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(asyncio.wait([
        loop.create_task(caller())
    ]))

    # This won't work, because .run_until_complete() accepts coroutine
    # and here it's just a list:
    # loop.run_until_complete([
    #     loop.create_task(caller())
    # ])

    loop.close()
