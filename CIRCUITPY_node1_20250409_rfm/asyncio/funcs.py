# CIRCUITPY-CHANGE: SPDX
# SPDX-FileCopyrightText: 2019-2020 Damien P. George
#
# SPDX-License-Identifier: MIT

# MicroPython asyncio module
# MIT license; Copyright (c) 2019-2022 Damien P. George
#
# CIRCUITPY-CHANGE
# This code comes from MicroPython, and has not been run through black or pylint there.
# Altering these files significantly would make merging difficult, so we will not use
# pylint or black.
# pylint: skip-file
# fmt: off

from . import core


async def _run(waiter, aw):
    try:
        result = await aw
        status = True
    except BaseException as er:
        result = None
        status = er
    if waiter.data is None:
        # The waiter is still waiting, cancel it.
        if waiter.cancel():
            # Waiter was cancelled by us, change its CancelledError to an instance of
            # CancelledError that contains the status and result of waiting on aw.
            # If the wait_for task subsequently gets cancelled externally then this
            # instance will be reset to a CancelledError instance without arguments.
            waiter.data = core.CancelledError(status, result)

async def wait_for(aw, timeout, sleep=core.sleep):
    # CIRCUITPY-CHANGE: doc
    """Wait for the *aw* awaitable to complete, but cancel if it takes longer
    than *timeout* seconds. If *aw* is not a task then a task will be created
    from it.

    If a timeout occurs, it cancels the task and raises ``asyncio.TimeoutError``:
    this should be trapped by the caller.

    Returns the return value of *aw*.
    """

    aw = core._promote_to_task(aw)
    if timeout is None:
        return await aw

    # Run aw in a separate runner task that manages its exceptions.
    runner_task = core.create_task(_run(core.cur_task, aw))

    try:
        # Wait for the timeout to elapse.
        await sleep(timeout)
    except core.CancelledError as er:
        # CIRCUITPY-CHANGE: more general fetching of exception arg
        status = er.args[0] if er.args else None
        if status is None:
            # This wait_for was cancelled externally, so cancel aw and re-raise.
            runner_task.cancel()
            raise er
        elif status is True:
            # aw completed successfully and cancelled the sleep, so return aw's result.
            return er.args[1]
        else:
            # aw raised an exception, propagate it out to the caller.
            raise status

    # The sleep finished before aw, so cancel aw and raise TimeoutError.
    runner_task.cancel()
    await runner_task
    raise core.TimeoutError


def wait_for_ms(aw, timeout):
    # CIRCUITPY-CHANGE: doc
    """Similar to `wait_for` but *timeout* is an integer in milliseconds.

    This is a MicroPython extension.

    Returns a coroutine.
    """

    return wait_for(aw, timeout, core.sleep_ms)


class _Remove:
    @staticmethod
    def remove(t):
        pass


# CIRCUITPY-CHANGE: async
async def gather(*aws, return_exceptions=False):
    # CIRCUITPY-CHANGE: doc
    """Run all *aws* awaitables concurrently. Any *aws* that are not tasks
    are promoted to tasks.

    Returns a list of return values of all *aws*
    """
    # CIRCUITPY-CHANGE: no awaitables, so nothing to gather
    if not aws:
        return []

    def done(t, er):
        # Sub-task "t" has finished, with exception "er".
        nonlocal state
        if gather_task.data is not _Remove:
            # The main gather task has already been scheduled, so do nothing.
            # This happens if another sub-task already raised an exception and
            # woke the main gather task (via this done function), or if the main
            # gather task was cancelled externally.
            return
        elif not return_exceptions and not isinstance(er, StopIteration):
            # A sub-task raised an exception, indicate that to the gather task.
            state = er
        else:
            state -= 1
            if state:
                # Still some sub-tasks running.
                return
        # Gather waiting is done, schedule the main gather task.
        # CIRCUITPY-CHANGE: when 8.x support is discontinued, change to .push()
        core._task_queue.push_head(gather_task)

    # Prepare the sub-tasks for the gather.
    # The `state` variable counts the number of tasks to wait for, and can be negative
    # if the gather should not run at all (because a task already had an exception).
    ts = [core._promote_to_task(aw) for aw in aws]
    state = 0
    for i in range(len(ts)):
        if ts[i].state is True:
            # Task is running, register the callback to call when the task is done.
            ts[i].state = done
            state += 1
        elif not ts[i].state:
            # Task finished already.
            if not isinstance(ts[i].data, StopIteration):
                # Task finished by raising an exception.
                if not return_exceptions:
                    # Do not run this gather at all.
                    state = -len(ts)
        else:
            # Task being waited on, gather not currently supported for this case.
            raise RuntimeError("can't gather")

    # Set the state for execution of the gather.
    gather_task = core.cur_task
    cancel_all = False

    # Wait for a sub-task to need attention (if there are any to wait for).
    if state > 0:
        gather_task.data = _Remove
        try:
            await core._never()
        except core.CancelledError as er:
            cancel_all = True
            state = er

    # Clean up tasks.
    for i in range(len(ts)):
        if ts[i].state is done:
            # Sub-task is still running, deregister the callback and cancel if needed.
            ts[i].state = True
            if cancel_all:
                ts[i].cancel()
        elif isinstance(ts[i].data, StopIteration):
            # Sub-task ran to completion, get its return value.
            ts[i] = ts[i].data.value
        else:
            # Sub-task had an exception.
            if return_exceptions:
                # Get the sub-task exception to return in the list of return values.
                ts[i] = ts[i].data
            elif isinstance(state, int):
                # Raise the sub-task exception, if there is not already an exception to raise.
                state = ts[i].data

    # Either this gather was cancelled, or one of the sub-tasks raised an exception with
    # return_exceptions==False, so reraise the exception here.
    if state:
        raise state

    # Return the list of return values of each sub-task.
    return ts
