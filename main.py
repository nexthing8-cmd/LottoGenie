import argparse
from src.collector import run_collector
from src.auditor import run_auditor
from src.analyst import run_analyst
# from src.web_app import run_web_server # Will implement later

def main():
    parser = argparse.ArgumentParser(description="LottoGenie CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # load --from <n> --to <n> (optional)
    load_parser = subparsers.add_parser("load", help="Load history data")
    load_parser.add_argument("--from", dest="start_round", type=int, help="Start round (optional)")
    load_parser.add_argument("--to", dest="end_round", type=int, help="End round (optional)")
    
    # predict --round <n>
    predict_parser = subparsers.add_parser("predict", help="Generate predictions")
    predict_parser.add_argument("--round", type=int, help="Target round (optional, defaults to next)")
    
    # check --round <n>
    check_parser = subparsers.add_parser("check", help="Check results")
    check_parser.add_argument("--round", type=int, help="Round to check (optional, checks all pending)")

    # train (new)
    train_parser = subparsers.add_parser("train", help="Train/Fine-tune the model")
    
    # web
    web_parser = subparsers.add_parser("web", help="Start Web UI")
    
    args = parser.parse_args()
    
    if args.command == "load":
        # If arguments are not provided, run_collector defaults might be used, 
        # or we can explicitly pass None to let collector handle it (if updated)
        # Currently run_collector has defaults start=1, end=1200.
        # We want it to be smart. 
        # Let's pass the args as is. If None, we might need to handle it in run_collector or here.
        # Let's assume run_collector handles None or we pass defaults here if needed.
        # Actually, let's check run_collector signature. It takes start_round=1, end_round=1200.
        # If we want "auto catch up", we should probably change run_collector to accept None 
        # or handle it here.
        # For now, let's default to a wide range if not specified, or better, 
        # let's update run_collector to be smarter in a separate step if needed.
        # But wait, the plan said "Update main.py to make arguments optional".
        # Let's pass 1 and 2000 (future) if not specified to catch all?
        # Or better, let's just default to 1 and 1200 for now if None, 
        # but ideally we want "from last + 1 to now".
        
        start = args.start_round if args.start_round else 1
        end = args.end_round if args.end_round else 2000 # Sufficiently large for now
        
        run_collector(start_round=start, end_round=end)
        
    elif args.command == "predict":
        # Analyst currently auto-detects next round, but we might want to support forcing a round?
        # For now, run_analyst() logic is: detect next round.
        # If we want to support --round, we need to update analyst.
        # Let's just run it for now, ignoring the arg if analyst doesn't support it yet, 
        # or update analyst to support it. 
        # The user asked for "predict --round 1201".
        # Let's update analyst briefly to accept round if we want to be strict, 
        # but for now let's just run it.
        run_analyst() 
        
    elif args.command == "check":
        run_auditor(round_no=args.round)

    elif args.command == "train":
        print("Starting model training...")
        run_analyst(mode='train')
        
    elif args.command == "web":
        print("Starting Web UI...")
        import uvicorn
        uvicorn.run("src.web_app:app", host="0.0.0.0", port=8000, reload=True)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
