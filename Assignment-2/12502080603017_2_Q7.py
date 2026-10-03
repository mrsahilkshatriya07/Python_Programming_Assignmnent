import json
import sys
from collections import defaultdict


def read_json_lines(file_path: str):
    """
    Generator Stage 1: File Streaming
    Yields raw line strings one at a time without loading the full file into RAM.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line_str = line.strip()
                if line_str:
                    yield line_str
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)


def parse_and_validate_records(lines_generator):
    """
    Generator Stage 2: JSON Parsing and Data Validation Filter
    Yields parsed valid records, or marks corrupted records.
    """
    for line in lines_generator:
        try:
            record = json.loads(line)
            
            # Verify required fields exist
            if "device_id" not in record or "temperature_c" not in record:
                yield (None, True)  # Corrupted record (missing key)
                continue

            device_id = str(record["device_id"])
            raw_temp = record["temperature_c"]

            # Validate numeric conversion for temperature
            temperature = float(raw_temp)

            # Yield valid processed tuple: (device_id, temperature, is_corrupted)
            yield (device_id, temperature, False)

        except (json.JSONDecodeError, ValueError, TypeError):
            # Handles malformed JSON string or non-numeric temperature values
            # If device_id can still be parsed, we pass it along, otherwise mark as unknown/general corrupted
            try:
                record = json.loads(line)
                dev_id = str(record.get("device_id")) if record.get("device_id") else None
                yield (dev_id, None, True)
            except Exception:
                yield (None, None, True)


class DeviceStats:
    """Helper class to track streaming aggregation stats for each device."""
    __slots__ = ['count', 'min_temp', 'max_temp', 'sum_temp', 'corrupted_count']

    def __init__(self):
        self.count = 0
        self.min_temp = float('inf')
        self.max_temp = float('-inf')
        self.sum_temp = 0.0
        self.corrupted_count = 0

    def add_valid(self, temp: float):
        self.count += 1
        self.sum_temp += temp
        if temp < self.min_temp:
            self.min_temp = temp
        if temp > self.max_temp:
            self.max_temp = temp

    def add_corrupted(self):
        self.corrupted_count += 1


def process_sensor_etl_pipeline(file_path: str):
    """
    Stage 3: Streaming Aggregations & Summary Generation
    Expected Time Complexity: O(number of records)
    Expected Space Complexity: O(number of devices)
    """
    lines_gen = read_json_lines(file_path)
    records_gen = parse_and_validate_records(lines_gen)

    # Aggregator map: device_id -> DeviceStats
    device_metrics = defaultdict(DeviceStats)
    general_corrupted = 0

    # Stream through generator pipeline
    for dev_id, temp, is_corrupted in records_gen:
        if is_corrupted:
            if dev_id:
                device_metrics[dev_id].add_corrupted()
            else:
                general_corrupted += 1
        else:
            device_metrics[dev_id].add_valid(temp)

    # Output results in lexicographical order of device IDs
    for dev_id in sorted(device_metrics.keys()):
        stats = device_metrics[dev_id]
        
        if stats.count > 0:
            avg_temp = stats.sum_temp / stats.count
            min_str = int(stats.min_temp) if stats.min_temp.is_integer() else f"{stats.min_temp}"
            max_str = int(stats.max_temp) if stats.max_temp.is_integer() else f"{stats.max_temp}"
            
            print(
                f"{dev_id} count={stats.count} min={min_str} "
                f"max={max_str} avg={avg_temp:.2f} corrupted={stats.corrupted_count}"
            )
        else:
            # Handles devices that only contained corrupted records
            print(f"{dev_id} count=0 min=N/A max=N/A avg=N/A corrupted={stats.corrupted_count}")


if __name__ == "__main__":
    # Example usage:
    file_path = "sensor_data.jsonl"
    process_sensor_etl_pipeline(file_path)
