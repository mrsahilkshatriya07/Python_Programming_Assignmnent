"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 9
Topic: Threaded Job Scheduler Simulation
CO Mapping: CO-1, CO-2
Bloom Level: L5 (Evaluate)

Description:
    Simulates a multi-threaded job scheduler using event-driven priority queues:
    1. Priority Ordering: Higher priority first (higher numerical value = higher priority).
       Ties are broken by earlier arrival time, then original input sequence.
    2. Thread/Worker Scheduling: Maintains worker state using a Min-Heap tracking 
       worker availability times (earliest free worker gets assigned).
    3. Metrics: Calculates exact start/finish times per job and computes average waiting time.
"""

from dataclasses import dataclass
import heapq
import sys


@dataclass
class Job:
    arrival_time: int
    job_id: str
    priority: int
    duration: int
    resources: int
    input_order: int


def simulate_job_scheduler(w: int, n: int, jobs: list[Job]):
    """
    Simulates threaded job dispatching using an event-driven time-progression engine.
    
    Args:
        w: Number of available worker threads (W1, W2, ..., Ww)
        n: Total number of jobs
        jobs: List of Job dataclass instances
    """
    # Sort arrival events chronologically
    jobs_by_arrival = sorted(jobs, key=lambda j: j.arrival_time)

    # Ready queue Min-Heap key priority:
    # (-priority, arrival_time, input_order) -> Higher priority first
    ready_queue = []

    # Worker pool Min-Heap: (available_at_time, worker_id_number)
    # 1-indexed workers: W1, W2, ..., Ww
    free_workers = [(0, i) for i in range(1, w + 1)]
    heapq.heapify(free_workers)

    current_time = 0
    job_ptr = 0
    total_waiting_time = 0
    execution_report = []

    while job_ptr < n or ready_queue:
        # If ready queue is empty and next job arrives in future, jump simulation time
        if not ready_queue and job_ptr < n:
            next_arrival = jobs_by_arrival[job_ptr].arrival_time
            # Also consider when the earliest worker becomes free
            earliest_worker_time = free_workers[0][0]
            current_time = max(current_time, min(next_arrival, earliest_worker_time))

        # Push all jobs that have arrived by or at current_time into ready_queue
        while job_ptr < n and jobs_by_arrival[job_ptr].arrival_time <= current_time:
            job = jobs_by_arrival[job_ptr]
            heapq.heappush(
                ready_queue,
                (-job.priority, job.arrival_time, job.input_order, job)
            )
            job_ptr += 1

        # Dispatch jobs to available workers
        if ready_queue:
            # Check if any worker is free at or before current_time
            if free_workers[0][0] <= current_time:
                _, neg_prio, arr_time, inp_ord, job = heapq.heappop(ready_queue)
                worker_free_time, worker_id = heapq.heappop(free_workers)

                start_time = max(current_time, worker_free_time)
                finish_time = start_time + job.duration
                wait_time = start_time - job.arrival_time

                total_waiting_time += wait_time
                execution_report.append((job.job_id, f"W{worker_id}", start_time, finish_time, job.input_order))

                # Reinsert worker with updated available time
                heapq.heappush(free_workers, (finish_time, worker_id))
            else:
                # Workers are busy; advance time to the earliest worker completion time
                current_time = free_workers[0][0]
        else:
            # No ready jobs; advance time to next arrival
            if job_ptr < n:
                current_time = jobs_by_arrival[job_ptr].arrival_time

    # Sort final output report back to original job arrival / assignment order
    execution_report.sort(key=lambda x: x[2])  # Sort by start_time

    # Print Job Execution Log
    for job_id, worker_str, start_t, finish_t, _ in execution_report:
        print(f"{job_id} {worker_str} {start_t} {finish_t}")

    # Print Average Waiting Time
    avg_wait = total_waiting_time / float(n) if n > 0 else 0.0
    print(f"AVG_WAIT {avg_wait:.2f}")


def main():
    """Main function to parse standard stream input and execute simulation."""
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    iterator = iter(input_data)

    try:
        first_line = next(iterator).strip()
        while not first_line:
            first_line = next(iterator).strip()

        w_str, n_str = first_line.split()
        w = int(w_str)
        n = int(n_str)

        jobs = []
        input_order = 0

        for line in iterator:
            cleaned = line.strip()
            if not cleaned:
                continue

            parts = cleaned.split()
            arr_t = int(parts[0])
            j_id = parts[1]
            prio = int(parts[2])
            dur = int(parts[3])
            res = int(parts[4])

            jobs.append(Job(arr_t, j_id, prio, dur, res, input_order))
            input_order += 1

            if len(jobs) == n:
                break

        simulate_job_scheduler(w, n, jobs)

    except (StopIteration, ValueError):
        pass


if __name__ == "__main__":
    main()
