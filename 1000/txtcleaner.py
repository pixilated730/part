import json
import re
from datetime import datetime

def parse_puzzle_line(text):
    """Parse a single puzzle entry from the text."""
    pattern = r"""
        (\d+)\s+                           # Puzzle number
        ([0-9a-f]+):([0-9a-f]+)\s+        # Range start:end
        (0{48}[0-9a-f]+)\s+               # Private key
        C\s+([1-9A-HJ-NP-Za-km-z]+)\s+    # Bitcoin address
        .*?                                # Skip middle content
        SOLVED\s*                          # Solved marker
        ([\d.]+)%\s+                       # Position percentage
        (\d{4}-\d{2}-\d{2})\s+by\s+       # Date
        ([0-9A-Za-z]+)                     # Solver
    """
    match = re.search(pattern, text, re.VERBOSE | re.DOTALL)
    if match:
        puzzle_num, range_start, range_end, private_key, btc_address, \
        position, solve_date, solver = match.groups()
        
        return {
            "puzzle_number": int(puzzle_num),
            "range_start": range_start,
            "range_end": range_end,
            "private_key": private_key,
            "btc_address": btc_address,
            "position_percentage": float(position),
            "solve_date": solve_date,
            "solver": solver
        }
    return None

def clean_puzzle_data(text):
    """Clean and structure the puzzle data."""
    # Split text into puzzle entries (split on puzzle numbers)
    entries = re.split(r'\n(?=\d+\s+[0-9a-f]+:[0-9a-f]+\s+)', text.strip())
    puzzles = []
    
    for entry in entries:
        if entry.strip():
            parsed = parse_puzzle_line(entry.strip())
            if parsed:
                puzzles.append(parsed)
    
    return puzzles

def analyze_puzzle_data(puzzles):
    """Analyze the cleaned puzzle data."""
    if not puzzles:
        return {
            'error': 'No puzzle data found',
            'total_puzzles': 0,
            'unique_solvers': 0,
            'top_solvers': [],
            'position_stats': {},
            'first_solve': None,
            'last_solve': None
        }

    # Sort puzzles by solve date
    puzzles.sort(key=lambda x: x['solve_date'])
    
    solver_counts = {}
    position_stats = {
        'min': float('inf'),
        'max': float('-inf'),
        'total': 0,
        'count': len(puzzles)
    }
    
    # Additional analysis for range patterns
    range_patterns = []
    
    for puzzle in puzzles:
        # Solver statistics
        solver = puzzle['solver']
        solver_counts[solver] = solver_counts.get(solver, 0) + 1
        
        # Position statistics
        pos = puzzle['position_percentage']
        position_stats['min'] = min(position_stats['min'], pos)
        position_stats['max'] = max(position_stats['max'], pos)
        position_stats['total'] += pos
        
        # Range analysis
        range_start = int(puzzle['range_start'], 16)
        range_end = int(puzzle['range_end'], 16)
        key_value = int(puzzle['private_key'], 16)
        
        range_size = range_end - range_start
        position_in_range = ((key_value - range_start) / range_size * 100) if range_size > 0 else 100
        
        range_patterns.append({
            'puzzle_number': puzzle['puzzle_number'],
            'range_start_hex': puzzle['range_start'],
            'range_end_hex': puzzle['range_end'],
            'range_start_decimal': range_start,
            'range_end_decimal': range_end,
            'range_size': range_size,
            'key_decimal': key_value,
            'position_in_range': position_in_range,
            'distance_from_start': key_value - range_start,
            'distance_from_end': range_end - key_value
        })
    
    if position_stats['count'] > 0:
        position_stats['average'] = position_stats['total'] / position_stats['count']
    else:
        position_stats['average'] = 0
        position_stats['min'] = 0
        position_stats['max'] = 0
    
    analysis = {
        'total_puzzles': len(puzzles),
        'unique_solvers': len(solver_counts),
        'top_solvers': [{'solver': s, 'count': c} for s, c in 
                       sorted(solver_counts.items(), key=lambda x: x[1], reverse=True)[:5]],
        'position_stats': position_stats,
        'first_solve': puzzles[0]['solve_date'] if puzzles else None,
        'last_solve': puzzles[-1]['solve_date'] if puzzles else None,
        'solver_stats': [{'solver': solver, 'puzzles_solved': count} 
                        for solver, count in solver_counts.items()],
        'range_patterns': range_patterns
    }
    
    return analysis

def main():
    try:
        # Read the input file as text
        with open('prevsolv.txt', 'r') as file:
            data = file.read()
        
        # Clean and parse the data
        puzzles = clean_puzzle_data(data)
        if not puzzles:
            print("Error: No valid puzzle data found in input file")
            return
        
        # Save cleaned data
        save_json(puzzles, 'cleaned_puzzles.json')
        print("Cleaned puzzle data saved to cleaned_puzzles.json")
        
        # Analyze and save analysis
        analysis = analyze_puzzle_data(puzzles)
        save_json(analysis, 'puzzle_analysis.json')
        print("Analysis results saved to puzzle_analysis.json")
        
        # Print summary
        print("\nBitcoin Puzzle Analysis Summary:")
        print(f"Total Solved Puzzles: {analysis['total_puzzles']}")
        print(f"Unique Solvers: {analysis['unique_solvers']}")
        print("\nTop 5 Solvers:")
        for solver in analysis['top_solvers']:
            print(f"  {solver['solver']}: {solver['count']} puzzles")
        print("\nPosition Statistics:")
        print(f"  Minimum: {analysis['position_stats']['min']:.2f}%")
        print(f"  Maximum: {analysis['position_stats']['max']:.2f}%")
        print(f"  Average: {analysis['position_stats']['average']:.2f}%")
        print(f"\nFirst Solve: {analysis['first_solve']}")
        print(f"Last Solve: {analysis['last_solve']}")
        
        # Print range pattern summary for first few puzzles
        print("\nRange Pattern Examples (first 3 puzzles):")
        for pattern in analysis['range_patterns'][:3]:
            print(f"\nPuzzle {pattern['puzzle_number']}:")
            print(f"  Range: {pattern['range_start_hex']}:{pattern['range_end_hex']}")
            print(f"  Position in range: {pattern['position_in_range']:.2f}%")
            print(f"  Distance from start: {pattern['distance_from_start']:,}")
            print(f"  Distance from end: {pattern['distance_from_end']:,}")
        
    except FileNotFoundError:
        print("Error: Input file 'prevsolv.txt' not found")
    except Exception as e:
        print(f"Error processing data: {str(e)}")

def save_json(data, filename):
    """Save data to a JSON file with proper formatting."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()