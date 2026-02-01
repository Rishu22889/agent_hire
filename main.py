"""
Original main.py - now uses the refactored backend engine.
Maintains backward compatibility while leveraging the new reusable function.
"""
from backend.engine import run_autopilot_from_files

def main():
    """Run autopilot using the original file-based approach."""
    print("Running autonomous job application engine...")
    
    result = run_autopilot_from_files()
    
    if not result["success"]:
        print(f"ERROR: {result['error']}")
        return
    
    summary = result["summary"]
    tracker = result["tracker"]
    
    print(f"Processing completed for student")
    
    # Print summary (preserving original format)
    print("\n==== JOB APPLICATION SUMMARY ====")
    print(f"Queued:    {summary['queued']}")
    print(f"Skipped:   {summary['skipped']}")
    print(f"Submitted: {summary['submitted']}")
    print(f"Retried:   {summary['retried']}")
    print(f"Failed:    {summary['failed']}")
    print("===============================")
    print(f"Full record saved in '{tracker.logpath}'")

if __name__ == "__main__":
    main()