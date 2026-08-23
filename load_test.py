import asyncio
import aiohttp
import random
import string
import time
import statistics
import csv
import sys


BASE_URL = "http://127.0.0.1:5000/"
ENDPOINT = BASE_URL + "/"

TESTS = [
    (100, 1),
    (500, 5),
    (1000, 10),
    # (2500, 25),
    # (5000, 50),
]

URL_LENGTH = 1_000       # Start with 1 KB, NOT 10 KB

REQUEST_TIMEOUT = 15     # Individual request timeout
TEST_TIMEOUT = 120       # Maximum time for one complete test

RESULT_FILE = "load_test_results.csv"


def random_string(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_long_url():
    half = URL_LENGTH // 2

    return (
        "https://example.com/"
        + random_string(half)
        + "?"
        + random_string(half)
    )


async def send_request(session, request_id):

    url = generate_long_url()

    start = time.perf_counter()

    try:
        async with session.post(
            ENDPOINT,
            data={"url": url},
            timeout=aiohttp.ClientTimeout(
                total=REQUEST_TIMEOUT
            )
        ) as response:

            await response.read()

            elapsed = time.perf_counter() - start

            return {
                "id": request_id,
                "status": response.status,
                "time": elapsed,
                "success": 200 <= response.status < 300,
                "error": ""
            }

    except asyncio.TimeoutError:

        elapsed = time.perf_counter() - start

        return {
            "id": request_id,
            "status": 0,
            "time": elapsed,
            "success": False,
            "error": "TIMEOUT"
        }

    except Exception as e:

        elapsed = time.perf_counter() - start

        return {
            "id": request_id,
            "status": 0,
            "time": elapsed,
            "success": False,
            "error": str(e)
        }


async def worker(session, queue, results):

    while True:

        request_id = await queue.get()

        if request_id is None:
            queue.task_done()
            return

        try:
            result = await send_request(
                session,
                request_id
            )

            results.append(result)

        finally:
            queue.task_done()


async def progress_monitor(
    results,
    total,
    start_time
):

    last_completed = 0

    while len(results) < total:

        completed = len(results)

        if completed != last_completed:

            elapsed = time.perf_counter() - start_time

            successful = sum(
                r["success"]
                for r in results
            )

            failed = completed - successful

            rate = (
                completed / elapsed
                if elapsed > 0
                else 0
            )

            avg = (
                statistics.mean(
                    r["time"]
                    for r in results
                )
                if results
                else 0
            )

            percent = (
                completed / total * 100
            )

            bar_length = 30

            filled = int(
                bar_length * completed / total
            )

            bar = (
                "█" * filled
                + "░" * (bar_length - filled)
            )

            print(
                f"\r[{bar}] "
                f"{completed}/{total} "
                f"({percent:5.1f}%) "
                f"| OK: {successful} "
                f"| FAIL: {failed} "
                f"| {rate:6.2f} req/s "
                f"| avg: {avg * 1000:7.1f} ms",
                end="",
                flush=True
            )

            last_completed = completed

        await asyncio.sleep(0.1)


async def run_test(
    total_requests,
    concurrency
):

    print()
    print("=" * 80)
    print("LOAD TEST")
    print("=" * 80)

    print(f"Endpoint       : {ENDPOINT}")
    print(f"Requests       : {total_requests:,}")
    print(f"Concurrency    : {concurrency}")
    print(f"URL length     : ~{URL_LENGTH:,} characters")
    print(f"Request timeout: {REQUEST_TIMEOUT}s")
    print(f"Test timeout   : {TEST_TIMEOUT}s")
    print()

    queue = asyncio.Queue()

    for i in range(total_requests):
        await queue.put(i)

    results = []

    connector = aiohttp.TCPConnector(
        limit=concurrency
    )

    start_time = time.perf_counter()

    try:

        async with aiohttp.ClientSession(
            connector=connector
        ) as session:

            workers = [
                asyncio.create_task(
                    worker(
                        session,
                        queue,
                        results
                    )
                )

                for _ in range(concurrency)
            ]

            monitor = asyncio.create_task(
                progress_monitor(
                    results,
                    total_requests,
                    start_time
                )
            )

            # Hard limit for the complete test
            try:

                await asyncio.wait_for(
                    queue.join(),
                    timeout=TEST_TIMEOUT
                )

            except asyncio.TimeoutError:

                print()
                print()
                print(
                    f"TEST TIMEOUT: "
                    f"{TEST_TIMEOUT} seconds reached."
                )

            monitor.cancel()

            try:
                await monitor
            except asyncio.CancelledError:
                pass

            # Stop workers
            for _ in workers:
                await queue.put(None)

            await asyncio.gather(
                *workers,
                return_exceptions=True
            )

    except KeyboardInterrupt:

        print()
        print()
        print("Test interrupted by user.")

    total_time = (
        time.perf_counter() - start_time
    )

    print()
    print()

    # ---------------------------------
    # Results
    # ---------------------------------

    successful = [
        r for r in results
        if r["success"]
    ]

    failed = [
        r for r in results
        if not r["success"]
    ]

    latencies = [
        r["time"]
        for r in results
    ]

    success_latencies = [
        r["time"]
        for r in successful
    ]

    print("-" * 80)
    print("RESULTS")
    print("-" * 80)

    print(
        f"Completed           : "
        f"{len(results):,}/{total_requests:,}"
    )

    print(
        f"Successful          : "
        f"{len(successful):,}"
    )

    print(
        f"Failed              : "
        f"{len(failed):,}"
    )

    if results:

        print(
            f"Success rate        : "
            f"{len(successful) / len(results) * 100:.2f}%"
        )

    print(
        f"Total elapsed       : "
        f"{total_time:.3f} s"
    )

    if latencies:

        print(
            f"Average latency     : "
            f"{statistics.mean(latencies) * 1000:.2f} ms"
        )

        print(
            f"Minimum latency     : "
            f"{min(latencies) * 1000:.2f} ms"
        )

        print(
            f"Maximum latency     : "
            f"{max(latencies) * 1000:.2f} ms"
        )

    if success_latencies:

        sorted_times = sorted(
            success_latencies
        )

        def percentile(p):

            index = int(
                len(sorted_times) * p / 100
            )

            index = min(
                index,
                len(sorted_times) - 1
            )

            return sorted_times[index]

        print(
            f"P50 latency         : "
            f"{percentile(50) * 1000:.2f} ms"
        )

        print(
            f"P95 latency         : "
            f"{percentile(95) * 1000:.2f} ms"
        )

        print(
            f"P99 latency         : "
            f"{percentile(99) * 1000:.2f} ms"
        )

    if total_time > 0:

        print(
            f"Throughput          : "
            f"{len(results) / total_time:.2f} req/s"
        )

    # ---------------------------------
    # HTTP status breakdown
    # ---------------------------------

    status_codes = {}

    for result in results:

        status = result["status"]

        status_codes[status] = (
            status_codes.get(status, 0) + 1
        )

    print()
    print("STATUS CODES")
    print("-" * 80)

    for status, count in sorted(
        status_codes.items()
    ):

        print(
            f"{status}: {count:,}"
        )

    # ---------------------------------
    # Errors
    # ---------------------------------

    errors = {}

    for result in failed:

        error = result["error"]

        errors[error] = (
            errors.get(error, 0) + 1
        )

    if errors:

        print()
        print("ERRORS")
        print("-" * 80)

        for error, count in errors.items():

            print(
                f"{error}: {count:,}"
            )

    print("=" * 80)

    return {
        "requests": total_requests,
        "completed": len(results),
        "concurrency": concurrency,
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": (
            len(successful) / len(results) * 100
            if results else 0
        ),
        "total_time": total_time,
        "avg_ms": (
            statistics.mean(latencies) * 1000
            if latencies else 0
        ),
        "min_ms": (
            min(latencies) * 1000
            if latencies else 0
        ),
        "max_ms": (
            max(latencies) * 1000
            if latencies else 0
        ),
        "p50_ms": (
            percentile(50) * 1000
            if success_latencies else 0
        ),
        "p95_ms": (
            percentile(95) * 1000
            if success_latencies else 0
        ),
        "p99_ms": (
            percentile(99) * 1000
            if success_latencies else 0
        ),
        "req_per_sec": (
            len(results) / total_time
            if total_time > 0 else 0
        )
    }


async def main():

    all_results = []

    try:

        for requests, concurrency in TESTS:

            result = await run_test(
                requests,
                concurrency
            )

            all_results.append(result)

            print()
            print("Cooling down for 5 seconds...")
            await asyncio.sleep(5)

    except KeyboardInterrupt:

        print()
        print()
        print("LOAD TEST STOPPED.")
        sys.exit(1)

    if not all_results:
        return

    # ---------------------------------
    # CSV
    # ---------------------------------

    with open(
        RESULT_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=all_results[0].keys()
        )

        writer.writeheader()
        writer.writerows(all_results)

    print()
    print("=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
    print(
        f"Results saved to: {RESULT_FILE}"
    )


if __name__ == "__main__":
    asyncio.run(main())