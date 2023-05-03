import asyncio
from unittest import TestCase
import time


""" This file contains quick reminder of how to use asyncio functions and concepts 
with simple examples as separate test functions """

class TestAsync(TestCase):
    def test_async_examples(self):
        """ Basic task example """

        # Callback that we can assign to task that will be invoked on finish
        def callback(task):
            print("Callback example: Task is done, result =", task.result())

        async def coro(x):
            print("coro(): starting")
            # first do something
            v = 0
            for i in range(1000):
                for j in range(1000):
                    v += i - j
            print("coro(): before sleep()")
            # when we hit await we could execute something else,
            # here event loop continue main() while waiting for this coro() to finish
            await asyncio.sleep(5)
            print("coro(): finishing")
            return 5

        async def main():
            # create task and schedule, but it doesn't start immediately
            # first we execute everything before await
            t = asyncio.create_task(coro(5))
            t.add_done_callback(callback)
            for i in range(10):
                print("Action 1")

            print("main(): before main sleep")

            # once we hit await we start executing coro()
            await asyncio.sleep(1)

            # once coro() hit await inside it,
            # we return here and execute something else in a meantime
            print("main(): Action 2")

            # then wait for coro() to finish
            result = await t
            print (result)
            # or we could get result with:
            if t.done():
                print("main(): result is", t.result())

        asyncio.run(main())


    def test_asyncio_gather(self):
        """ asyncio.gather() example """
        async def sleeping(n, name):
            for i in range(5):
                print(f"{name}:\tsome useful code")
            print(f"{name}: before sleeping {n} sec")
            await asyncio.sleep(n)
            print(f"{name}:\tpost action {n}")

        async def main():
            start = time.time()
            coro_objects = [sleeping(1, "coro1"),
                            sleeping(3, "coro2"),
                            sleeping(2, "coro3")]

            for i in range(10):
                print (f"main: {i}")

            await asyncio.gather(*coro_objects)
            print(f"dt = {time.time() - start}")

            # DIAGRAM OF EXECUTION
            # here first coro has sleep(1), second sleep(3), third has sleep(2)
            # ===== - means executing something useful
            # ----------, - means await (sleeping for 1 sec)
            # main(): ========await----------------------------------------====
            # coro1:          ==await----------====
            # coro2:            ==await----------,----------,----------====
            # coro3:              ==await----------,----------,====

            # comments on diagram:
            # main function calls 'print's (marked as ===) then hits await (sleep() marked as ---), and we start coro1
            # when coro1 hits await we start coro2
            # when coro2 hits await we start coro3
            # when coro3 hits await it seems that event loop constantly updating until it finds a task,
            # that can be restored from await - in this case this first one will be coro1 because of the least sleeping time
            # then it will be coro3, and then coro2, after that asyncio.gather() is ready to finish and restore execution to main()

        asyncio.run(main())


    def test_get_all_tasks(self):
        """ Example of getting all running tasks """
        async def task_coro(value):
            print(f"task {value} is running")
            await asyncio.sleep(2)

        async def main():
            print("main coro started")
            started_tasks = [asyncio.create_task(task_coro(i)) for i in range(10)]

            # we created tasks earlier but create_task() doesn't start task automatically,
            # it only schedules it to event loop, main() is still busy executing this 'for' loop
            for i in range(10):
                print(f"main(): do something here {i}")

            # but when main() hits 'await', event loop have a chance to run other tasks in a meanwhile -
            # - the ones we scheduled with create_task() before
            await asyncio.sleep(0.1)

            # print all tasks that are still running (awaited)
            print("---------- Get all tasks() ------------")
            tasks = asyncio.all_tasks()
            for t in tasks:
                print(f"{t.get_name()}, {t.get_coro()}, {t.done()}")

            # here we await all tasks to give them a chance to finish properly
            for t in started_tasks:
                await t

        asyncio.run(main())


    def test_asyncio_gather_2(self):
        """ Another example of using asyncio.gather() """
        async def coro(sec):
            print(f"{sec} sleep now")
            await asyncio.sleep(sec)
            print(f"{sec} after sleep")
            return sec

        async def main():
            print("fmain()")

            group = asyncio.gather(coro(0.5), coro(2))

            print("main() before sleep")
            await asyncio.sleep(1)      # sleep will cause executions of coroutines created earlier
            print("main() after sleep")
            print("This will print False, because coro(2) has sleeping time higher than main():", group.done())
            print("That means we can execute something else here in a meantime while waiting for coro2 to finish in the background")

            # await for entire group
            # results is a list of returned values from each coro
            results = await group
            print(results)

        asyncio.run(main())


    def test_wait(self):
        """ Simple example of asyncio.wait() """
        async def coro(sec):
            print(f"{sec} sleep now")
            await asyncio.sleep(sec)
            print(f"{sec} after sleep")
            return sec

        async def main():
            tasks = [asyncio.create_task(coro(1)),
                     asyncio.create_task(coro(2))]

            print("main() before await")

            # done, pending = await asyncio.wait(tasks)
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            print("done:", done)
            print("pending:", pending)
            print("main() after await")

            # When FIRST_COMPLETED returns done and pending, pending contains coro2 which is not cancelled but running.
            # Here, when we await for the second time, we return to coro2 and finish its execution then return to main and print result
            await asyncio.wait(pending)
            print("after second wait")

        asyncio.run(main())


    def test_wait_for(self):
        """ Simple example of asyncio.wait_for() """
        async def coro(sec):
            print(f"{sec} sleep now")
            await asyncio.sleep(sec)
            # example of throwing exception from our coro()
            if sec == 2:
                raise RuntimeError("SomeError")
            print(f"{sec} after sleep")
            return sec * 2.4

        async def main():
            print("main executes something here ...")
            try:
                result = await asyncio.wait_for(coro(2), timeout=3)
            except asyncio.TimeoutError as e:
                print(e)
            except Exception as e:
                print("Here we catch exception from coro:", e)

        asyncio.run(main())


    def test_shield(self):
        """ Simple example of shielding task from cancellation """
        async def coro():
            print("coro(): start")
            await asyncio.sleep(1)
            print("coro(): end")
            return -1

        async def canceller(task_to_cancel):
            # example of a task that will cancel another task
            print("canceller(): start")
            await asyncio.sleep(0.25)
            task_to_cancel.cancel()
            print("canceller(): end")

        async def main():
            task = asyncio.create_task(coro())
            shielded_future = asyncio.shield(task)

            # sheduling canceller (it will run once event loop decides to start it)
            asyncio.create_task(canceller(shielded_future))
            try:
                await shielded_future
            except asyncio.CancelledError:
                print("main(): catching CancelledError")

            await asyncio.sleep(2)

            # shielded future will be in status 'Cancelled'
            print(f"shielded future:", shielded_future)

            # task will be in status 'Done' - it was shielded by shielded_future
            print(f"task:", task)
            print("main(): end")

        asyncio.run(main())


    def test_executor(self):
        """ Simple example of asyncio.to_thread()
        this will allow us to execute non-async function using event loop
        """

        def foo(a):
            print(f"foo({a})")
            time.sleep(20)
            return a * 5

        async def main():
            print("main preprocess")
            # wrapping non-async function into a coroutine object to be awaited
            coro = asyncio.to_thread(foo, 10)
            task = asyncio.create_task(coro)
            print("main is busy")
            await asyncio.sleep(2)

            # main is doing some useful code
            print("main action 1")
            print("main action 2")
            print("main action 3")

            # waiting for task to be finished properly
            await task

            print("main postprocess")

        asyncio.run(main())


    def test_asyncfor(self):
        class AsyncItr:
            def __init__(self):
                self.counter = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.counter >= 10:
                    raise StopAsyncIteration
                self.counter += 1
                await asyncio.sleep(0.6)
                return self.counter

        # example of another async function that does something in between
        # of async-for loop
        async def foo():
            print("foo start")
            await asyncio.sleep(3)
            print("foo end")

        async def main():
            # schedule some task (it doesn't start immediately)
            task = asyncio.create_task(foo())

            # start async for loop - each item is a coro that could be awaited
            # and give a chance to other scheduled task to run in between
            async for result in AsyncItr():
                print(result)

        asyncio.run(main())


    def test_async_generator(self):
        async def foo():
            print("start foo()")
            await asyncio.sleep(4)
            print("end foo()")

        async def agen():
            for i in range(10):
                await asyncio.sleep(1)
                yield i

        async def main():
            asyncio.create_task(foo())
            async for r in agen():
                print(r)

        asyncio.run(main())


    def test_async_context_managers(self):
        """ simple example of async with context manager """
        class AsyncContextManager:
            async def __aenter__(self):
                print("Enters")
                # simulate some long process
                await asyncio.sleep(2)
                return self

            async def __aexit__(self, exc_type, exc_value, exc_traceback):
                print("Exits")

        async def foo():
            print("starting foo")
            await asyncio.sleep(3)
            print("finishing foo")


        async def main():
            task = asyncio.create_task(foo())   # scheduling task, but it doesn't start right off the bat

            async with AsyncContextManager() as m:
                print ("some useful action")

            if not task.done():
                print("Task is not done() - awaiting")
                await task

        asyncio.run(main())


    def test_async_comprehension(self):
        """ Simple example of usage async comprehension """
        async def foo(n):
            print(f"starts foo({n})")
            await asyncio.sleep(n)
            print(f"finishing foo({n})")
            return n

        class AsyncItr:
            def __init__(self):
                self.counter = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                self.counter += 1
                if self.counter == 4:
                    raise StopAsyncIteration
                await asyncio.sleep(1)
                return foo(self.counter)


        async def main():
            aitr = AsyncItr()
            # iterating and awaiting
            L = [await f async for f in aitr]
            pass

        asyncio.run(main())