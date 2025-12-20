import csv
import os
import hashlib
from pathlib import Path

def load_decklists_data():
    """
    Load decklists data from CSV file into a dictionary keyed by 'id'.
    
    Returns:
        dict: Dictionary with decklist IDs as keys and decklist data as values
    """
    decklists = {}
    
    # Get the path to the CSV file
    current_dir = Path(__file__).parent
    csv_path = current_dir.parent / "card_evaluation_inputs" / "decklists.csv"
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                decklist_id = row['id']
                decklists[decklist_id] = row
        
        print(f"Loaded {len(decklists)} decklists from {csv_path}")
        
    except FileNotFoundError:
        print(f"Error: Could not find decklists.csv at {csv_path}")
    except Exception as e:
        print(f"Error loading decklists data: {e}")
    
    return decklists

def load_decklist_stats_data():
    """
    Load decklist stats data from CSV file into a dictionary keyed by 'decklist_id'.
    
    Returns:
        dict: Dictionary with decklist IDs as keys and stats data as values
    """
    decklist_stats = {}
    
    # Get the path to the CSV file
    current_dir = Path(__file__).parent
    csv_path = current_dir.parent / "card_evaluation_inputs" / "decklist_stats.csv"
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                decklist_id = row['decklist_id']
                decklist_stats[decklist_id] = row
        
        print(f"Loaded {len(decklist_stats)} decklist stats from {csv_path}")
        
    except FileNotFoundError:
        print(f"Error: Could not find decklist_stats.csv at {csv_path}")
    except Exception as e:
        print(f"Error loading decklist stats data: {e}")
    
    return decklist_stats

def load_popularity_data():
    """
    Load both decklists and decklist stats data.
    
    Returns:
        tuple: (decklists_dict, decklist_stats_dict)
    """
    print("Loading popularity data...")
    
    decklists = load_decklists_data()
    decklist_stats = load_decklist_stats_data()
    
    print(f"Successfully loaded data for {len(decklists)} decklists and {len(decklist_stats)} decklist stats")
    
    return decklists, decklist_stats

def remove_low_value_decklists(decklists, decklist_stats, min_likes):
    """
    Remove decklists that have fewer than min_likes, have previous_deck/next_deck values,
    or have duplicate slots from both decklists and decklist_stats.
    
    Args:
        decklists (dict): Dictionary of decklists keyed by 'id'.
        decklist_stats (dict): Dictionary of decklist stats keyed by 'decklist_id'.
        min_likes (int): Minimum number of likes required to keep a decklist.
    """
    to_remove = []
    removed_for_likes = 0
    removed_for_previous_next = 0
    removed_for_duplicate_slots = 0
    seen_slots_hashes = set()
    
    for decklist_id, stats in decklist_stats.items():
        should_remove = False
        
        # Check if likes are below minimum
        try:
            likes = int(stats.get('likes', 0))
            if likes < min_likes:
                should_remove = True
                removed_for_likes += 1
        except ValueError:
            print(f"Warning: Invalid likes value for decklist_id {decklist_id}: {stats.get('likes')}")
        
        # Check if decklist has previous_deck or next_deck values
        if decklist_id in decklists:
            decklist = decklists[decklist_id]
            previous_deck = decklist.get('previous_deck', '').strip()
            next_deck = decklist.get('next_deck', '').strip()
            
            if previous_deck or next_deck:
                should_remove = True
                removed_for_previous_next += 1
            
            # Check for duplicate slots
            if not should_remove:  # Only check if not already marked for removal
                slots = decklist.get('slots', '').strip()
                if slots:
                    # Create hash of the slots field
                    slots_hash = hashlib.md5(slots.encode('utf-8')).hexdigest()
                    
                    if slots_hash in seen_slots_hashes:
                        should_remove = True
                        removed_for_duplicate_slots += 1
                    else:
                        seen_slots_hashes.add(slots_hash)
        
        if should_remove:
            to_remove.append(decklist_id)
    
    for decklist_id in to_remove:
        if decklist_id in decklists:
            del decklists[decklist_id]
        if decklist_id in decklist_stats:
            del decklist_stats[decklist_id]
    
    print(f"Removed {len(to_remove)} decklists:")
    print(f"  - {removed_for_likes} with fewer than {min_likes} likes")
    print(f"  - {removed_for_previous_next} with previous_deck or next_deck values")
    print(f"  - {removed_for_duplicate_slots} with duplicate slots")

def main():
    """
    Main function to test the data loading functionality.
    """
    decklists, decklist_stats = load_popularity_data()

    remove_low_value_decklists(decklists, decklist_stats, min_likes=1)

        # Print some sample data to verify loading
    if decklists:
        print("\nSample decklist:")
        sample_id = next(iter(decklists))
        sample_decklist = decklists[sample_id]
        print(f"ID: {sample_id}")
        print(f"Name: {sample_decklist.get('name', 'N/A')}")
        print(f"Investigator: {sample_decklist.get('investigator_name', 'N/A')}")
        print(f"slots: {sample_decklist.get('slots', 'N/A')}")
        print(f"sideSlots: {sample_decklist.get('sideSlots', 'N/A')}")
    
    if decklist_stats:
        print("\nSample decklist stats:")
        sample_id = next(iter(decklist_stats))
        sample_stats = decklist_stats[sample_id]
        print(f"Decklist ID: {sample_id}")
        print(f"Favorites: {sample_stats.get('favorites', 'N/A')}")
        print(f"Likes: {sample_stats.get('likes', 'N/A')}")
        print(f"Comments: {sample_stats.get('comments', 'N/A')}")

if __name__ == "__main__":
    main()
