import argparse
import sys
from pathlib import Path

from src.config import VIDEO_PATH, MODEL_PATH
from src.app import App


def main():
    parser = argparse.ArgumentParser(
        description="CrowdSense AI - AI-Powered Crowd Monitoring & Risk Analysis",
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Path to input video file. If omitted, uses default demo video.",
    )
    parser.add_argument(
        "--webcam",
        action="store_true",
        help="Use webcam instead of video file.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to YOLO model weights.",
    )
    parser.add_argument(
        "--no-tracking",
        action="store_true",
        help="Disable person tracking (Phase 1 detection-only mode).",
    )
    parser.add_argument(
        "--legacy-risk",
        action="store_true",
        help="Use legacy pressure-index risk engine instead of Phase 3 composite risk engine.",
    )
    parser.add_argument(
        "--no-events",
        action="store_true",
        help="Disable the Phase 4 event detection engine.",
    )
    parser.add_argument(
        "--log-events",
        action="store_true",
        help="Write detected events to a CSV log file in the logs/ directory.",
    )
    args = parser.parse_args()

    video_path = None
    if args.webcam:
        video_path = None
    elif args.video:
        video_path = Path(args.video)
    else:
        video_path = VIDEO_PATH

    model_path = Path(args.model) if args.model else MODEL_PATH

    try:
        app = App(video_path=video_path, model_path=model_path,
                  tracking=not args.no_tracking,
                  legacy_risk=args.legacy_risk,
                  events_enabled=not args.no_events,
                  log_events=args.log_events)
        app.run()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
