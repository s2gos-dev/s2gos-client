import time

from s2gos.server.services.local import JobContext, LocalService, get_job_context

service = LocalService(
    title="S2GOS API Server (local dummy for testing)",
    description="Local test server implementing the OGC API - Processes 1.0 Standard",
)


@service.process_info(id="sleep_a_while", title="Dummy sleep processor")
def sleep_a_while(
    duration: float = 10.0,
    fail: bool = False,
) -> float:
    """A dummy processor.

    Args:
        duration: minimal sleep duration in seconds
        fail: whether to wake up too early

    Returns:
        The effective amount of sleep in seconds
    """
    ctx = get_job_context()

    t0 = time.time()
    for i in range(101):
        ctx.report_progress(progress=i)
        if fail and i == 50:
            raise RuntimeError("Woke up too early")
        time.sleep(duration / 100)
    return time.time() - t0
