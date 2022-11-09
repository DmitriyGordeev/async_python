import asyncio


""" just a quick cheat-sheet for python's async syntax """

async def foo(n=100):
    for i in range(n):
        print(f"bar() = {i}")
        await asyncio.sleep(1)

    
async def async_gen(u: int = 10):
    i = 0
    while i < u:
        yield 2 ** i
        i += 1
        await asyncio.sleep(2)


if __name__ == "__main__":
    # Example of 'async for' usage
    # foo will be firing loop every 1 second but won't block async_gen execution,
    # so they are running together in asynchrounuos manner
    async def entry():
        asyncio.create_task(foo())
        ag1 = async_gen(10)
        async for j in ag1:
            print("ag1", j)
    asyncio.run(entry())


