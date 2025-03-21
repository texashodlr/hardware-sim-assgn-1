import csv
import glob
import re
import os

# Replace with actual warp lane activity per warp (W1 has 1 lane, W2 has 2, ..., W32 has 32)
# For example, if W1 always has 1 active lane, W2 has 2, ..., customize as needed
active_lanes = [i for i in range(1, 33)]  # W1=1 lane, W2=2 lanes, ..., W32=32 lanes

def parse_warp_line(line):
    matches = re.findall(r'W(\d+):(\d+)', line)
    warp_counts = [0] * 32  # Default all warps to 0

    for warp_num_str, count_str in matches:
        warp_idx = int(warp_num_str) - 1
        if 0 <= warp_idx < 32:
            warp_counts[warp_idx] = int(count_str)

    return warp_counts

def calculate_simd_efficiency(warp_counts):
    weighted_sum = 0
    total_instructions = sum(warp_counts)
    for i in range(32):
        efficiency = active_lanes[i] / 32  # Per-instruction efficiency
        weighted_sum += warp_counts[i] * efficiency

    if total_instructions == 0:
        return 0.0  # Avoid division by zero

    overall_efficiency = weighted_sum / total_instructions
    return overall_efficiency

def process_files(input_pattern, output_csv):
    files = glob.glob(input_pattern)
    filtered_files = [f for f in files if re.search(r'\.o\d+$', f)]  # Matches *.o[digits]
    all_rows = []

    for file_path in filtered_files:
        base_name = os.path.basename(file_path)
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('Stall:'):
                    warp_counts = parse_warp_line(line)
                    simd_efficiency = calculate_simd_efficiency(warp_counts)
                    row = [base_name] + warp_counts + [simd_efficiency]
                    all_rows.append(row)

    # Write to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ['Filename'] + [f'W{i}' for i in range(1, 33)] + ['SIMD_Efficiency']
        writer.writerow(header)
        writer.writerows(all_rows)

    print(f"Processed {len(filtered_files)} files with {len(all_rows)} total rows into '{output_csv}'.")

# Example usage: update the path as needed
process_files('*.o*', 'warp_instructions_with_efficiency.csv')
