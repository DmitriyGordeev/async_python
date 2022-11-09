import asyncio


""" just a quick cheat-sheet for python's async syntax """


async def foo(fut):
    await asyncio.sleep(3)
    print('foo()')
    fut.set_result(1)


async def bar():
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    asyncio.create_task(foo(future))
    result = await future
    print("result =", result)


async def main():
    # loop = asyncio.get_event_loop()
    # r = loop.run_until_complete(asyncio.wait([
    #     loop.create_task(bar())
    # ]))
    await bar()


if __name__ == "__main__":
    asyncio.run(main())
