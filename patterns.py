from typing import Tuple
import secrets

def hex_to_int(hex_str: str) -> int:
    """Convert a hex string to integer."""
    return int(hex_str, 16)

def int_to_hex(num: int, pad_length: int = 64) -> str:
    """Convert integer to padded hex string."""
    hex_str = hex(num)[2:]  # Remove '0x' prefix
    return hex_str.zfill(pad_length)

def calculate_position_in_range(key: str, range_start: str, range_end: str) -> float:
    """Calculate the relative position of a key within its range."""
    key_int = hex_to_int(key)
    start_int = hex_to_int(range_start)
    end_int = hex_to_int(range_end)
    
    range_size = end_int - start_int
    if range_size == 0:  # Handle single-value ranges
        return 100.0 if key_int == start_int else 0.0
    
    position_from_start = key_int - start_int
    return position_from_start / range_size * 100

def analyze_key(puzzle_num: int, key: str, range_start: str, range_end: str):
    """Analyze a key's properties within its range."""
    key_int = hex_to_int(key)
    start_int = hex_to_int(range_start)
    end_int = hex_to_int(range_end)
    position = calculate_position_in_range(key, range_start, range_end)
    
    range_size = end_int - start_int
    
    print(f"\nPuzzle {puzzle_num}")
    print(f"Range: {range_start}:{range_end}")
    print(f"Range in decimal: {start_int:,} to {end_int:,}")
    print(f"Range size: {range_size:,}")
    print(f"Key: {key}")
    print(f"Decimal: {key_int:,}")
    print(f"Position in range: {position:.2f}%")
    
    if range_size > 0:
        print(f"Distance from start: {key_int - start_int:,}")
        print(f"Distance from end: {end_int - key_int:,}")

def main():
    # Known puzzle keys and their ranges
    puzzles = [
        # Early puzzles
        (1, "0000000000000000000000000000000000000000000000000000000000000001", "1", "1"),
        (2, "0000000000000000000000000000000000000000000000000000000000000003", "2", "3"),
        (3, "0000000000000000000000000000000000000000000000000000000000000007", "4", "7"),
        
        # Mid-range puzzles
        (17, "000000000000000000000000000000000000000000000000000000000001764f", "10000", "1ffff"),
        (18, "000000000000000000000000000000000000000000000000000000000003080d", "20000", "3ffff"),
        (19, "00000000000000000000000000000000000000000000000000000000000d2c55", "80000", "fffff"),
        
        # Higher difficulty puzzles
        (26, "000000000000000000000000000000000000000000000000000000000340326e", "2000000", "3ffffff"),
        (27, "0000000000000000000000000000000000000000000000000000000006ac3875", "4000000", "7ffffff"),
        (28, "000000000000000000000000000000000000000000000000000000000d916ce8", "8000000", "fffffff"),
        (29, "0000000000000000000000000000000000000000000000000000000017e2551e", "10000000", "1fffffff"),
        (30, "000000000000000000000000000000000000000000000000000000003d94cd64", "20000000", "3fffffff")
    ]

    # Analyze each puzzle
    for puzzle_num, key, range_start, range_end in puzzles:
        analyze_key(puzzle_num, key, range_start, range_end)
        
    # Calculate average position for later puzzles (excluding 1-3)
    later_positions = [
        calculate_position_in_range(key, range_start, range_end)
        for puzzle_num, key, range_start, range_end in puzzles[3:]
    ]
    avg_position = sum(later_positions) / len(later_positions)
    print(f"\nAverage position in range (excluding puzzles 1-3): {avg_position:.2f}%")
    
    # Calculate position differences between consecutive puzzles
    print("\nPosition differences between consecutive puzzles:")
    for i in range(3, len(puzzles)-1):
        pos1 = calculate_position_in_range(puzzles[i][1], puzzles[i][2], puzzles[i][3])
        pos2 = calculate_position_in_range(puzzles[i+1][1], puzzles[i+1][2], puzzles[i+1][3])
        diff = pos2 - pos1
        print(f"Puzzle {puzzles[i][0]} to {puzzles[i+1][0]}: {diff:.2f}%")

if __name__ == "__main__":
    main()