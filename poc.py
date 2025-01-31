import sys

def calculate_theoretical_key(range_start_hex: str, range_end_hex: str, position_percentage: float):
    """Calculate theoretical key position based on range and percentage."""
    
    # Convert hex ranges to decimal
    start = int(range_start_hex, 16)
    end = int(range_end_hex, 16)
    range_size = end - start
    
    # Calculate theoretical position
    theoretical_pos = int(start + (range_size * (position_percentage / 100)))
    
    # Calculate ±1% search range
    one_percent = int(range_size * 0.01)
    search_start = max(start, theoretical_pos - one_percent)
    search_end = min(end, theoretical_pos + one_percent)
    
    return {
        "range_info": {
            "start_dec": start,
            "end_dec": end,
            "size": range_size
        },
        "theoretical_key": {
            "decimal": theoretical_pos,
            "hex": f"{theoretical_pos:x}",
            "hex_padded": f"{theoretical_pos:064x}"  # Pad to 64 chars for BTC key format
        },
        "search_range": {
            "start_dec": search_start,
            "end_dec": search_end,
            "size": search_end - search_start,
            "start_hex": f"{search_start:x}",
            "end_hex": f"{search_end:x}"
        }
    }

def print_results(results):
    """Print results in a readable format."""
    print("\nRange Information:")
    print(f"Start (dec): {results['range_info']['start_dec']:,}")
    print(f"End (dec): {results['range_info']['end_dec']:,}")
    print(f"Range size: {results['range_info']['size']:,}")
    
    print("\nTheoretical Key:")
    print(f"Decimal: {results['theoretical_key']['decimal']:,}")
    print(f"Hex: 0x{results['theoretical_key']['hex']}")
    print(f"Full Bitcoin Key Format:")
    print(results['theoretical_key']['hex_padded'])
    
    print("\nRecommended Search Range (±1%):")
    print(f"Start: {results['search_range']['start_dec']:,}")
    print(f"End: {results['search_range']['end_dec']:,}")
    print(f"Search space size: {results['search_range']['size']:,}")
    print(f"Hex range: 0x{results['search_range']['start_hex']} - 0x{results['search_range']['end_hex']}")

def verify_known_key(results, known_key):
    """Verify if a known key falls within the predicted range."""
    if known_key.startswith('0x'):
        known_key = known_key[2:]
    key_value = int(known_key, 16)
    in_range = results['search_range']['start_dec'] <= key_value <= results['search_range']['end_dec']
    if in_range:
        position_in_range = (key_value - results['search_range']['start_dec']) / results['search_range']['size'] * 100
        return True, position_in_range
    return False, 0

def get_user_input():
    """Get puzzle parameters from user."""
    print("\nBitcoin Puzzle Key Finder")
    print("------------------------")
    
    range_start = input("Enter range start (hex, e.g., 10000000): ").strip()
    range_end = input("Enter range end (hex, e.g., 1fffffff): ").strip()
    
    while True:
        try:
            position = float(input("Enter position percentage (e.g., 49.28): ").strip())
            if 0 <= position <= 100:
                break
            print("Position must be between 0 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    verify = input("Do you have a known key to verify? (y/n): ").strip().lower()
    known_key = None
    if verify == 'y':
        known_key = input("Enter known key (hex): ").strip()
    
    return range_start, range_end, position, known_key

def main():
    while True:
        # Get puzzle parameters
        range_start, range_end, position, known_key = get_user_input()
        
        print(f"\nAnalyzing range {range_start}:{range_end} at position {position}%")
        
        try:
            results = calculate_theoretical_key(range_start, range_end, position)
            print_results(results)
            
            if known_key:
                is_in_range, position_in_range = verify_known_key(results, known_key)
                print(f"\nVerification against known key {known_key}:")
                print(f"Key falls within predicted range: {is_in_range}")
                if is_in_range:
                    print(f"Position within search range: {position_in_range:.2f}%")
                    print(f"Accuracy of prediction: {abs(results['theoretical_key']['decimal'] - int(known_key, 16)):,} units")
        
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        # Ask if user wants to try another puzzle
        if input("\nTry another puzzle? (y/n): ").strip().lower() != 'y':
            break

if __name__ == "__main__":
    main()