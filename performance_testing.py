import statistics
import time
import requests

URL = "http://localhost:8000/recommendations/user"
PARAMS = {
    "identifier": "2WheelTravlr",
    "top_k": 50
}
TOTAL_RUNS = 100
PAUSE_BETWEEN_REQUESTS = 0.05  # Inter-request delay in seconds to prevent socket saturation (Very important)


def run_benchmark():
    """Executes N sequential HTTP GET requests to evaluate API latency and distribution."""
    print(f"Starting performance benchmark ({TOTAL_RUNS} total iterations)...\n")
    
    session = requests.Session()
    latencies = []

    for i in range(1, TOTAL_RUNS + 1):
        start_time = time.perf_counter()
        try:
            response = session.get(URL, params=PARAMS)
            end_time = time.perf_counter()
            
            elapsed_ms = (end_time - start_time) * 1000
            latencies.append(elapsed_ms)
            
            status = f"HTTP {response.status_code}"
            tag = "[Cold Call]" if i == 1 else f"[Req #{i:03d}]"
            
            print(f"Call {i:03d} {tag:<12}: {elapsed_ms:6.2f} ms | Status: {status}")
            
            time.sleep(PAUSE_BETWEEN_REQUESTS)
            
        except requests.exceptions.ConnectionError:
            print("Connection error: Unable to connect to target endpoint at http://localhost:8000")
            return

    # Data separation: Cold start vs. Warm execution
    cold_call_time = latencies[0]
    warm_calls = latencies[1:]
    
    # Statistical analysis
    avg_warm_time = statistics.mean(warm_calls)
    std_dev_warm = statistics.stdev(warm_calls)
    median_warm = statistics.median(warm_calls)
    min_warm_time = min(warm_calls)
    max_warm_time = max(warm_calls)
    
    quantiles = statistics.quantiles(warm_calls, n=100)
    p90_warm = quantiles[89]
    p99_warm = quantiles[98]
    
    if cold_call_time > avg_warm_time:
        speedup_pct = ((cold_call_time - avg_warm_time) / cold_call_time) * 100
        speedup_str = f"{speedup_pct:.1f}% faster after warm-up"
    else:
        slowdown_pct = ((avg_warm_time - cold_call_time) / cold_call_time) * 100
        speedup_str = f"{slowdown_pct:.1f}% slower after warm-up"

    print("\n" + "="*55)
    print("BENCHMARK SUMMARY REPORT (100 REQUESTS)")
    print("="*55)
    print(f"Cold Call Latency (1st Request) : {cold_call_time:6.2f} ms")
    print(f"Mean Warm Latency (Reqs #2-#100): {avg_warm_time:6.2f} ms")
    print(f"Standard Deviation (Warm)       : {std_dev_warm:6.2f} ms")
    print(f"Warm-up Differential            : {speedup_str}")
    print("-" * 55)
    print("LATENCY DISTRIBUTION (WARM STATE):")
    print(f"Min Latency                     : {min_warm_time:6.2f} ms")
    print(f"Median (p50)                    : {median_warm:6.2f} ms")
    print(f"p90 Latency                     : {p90_warm:6.2f} ms")
    print(f"p99 Latency                     : {p99_warm:6.2f} ms")
    print(f"Max Latency                     : {max_warm_time:6.2f} ms")
    print("="*55)


if __name__ == "__main__":
    run_benchmark()