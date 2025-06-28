import os
import datetime
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Import the crew instance from crew.py (not from_yaml anymore!)
from crew_grisp import callCrew

# Ensure output directory exists
os.makedirs("reports", exist_ok=True)

def run_grisp_pipeline():
    print("\n🧠 Initializing GRiSP — Global Risk & Stability Predictor...")

    # Kickoff CrewAI execution
    print("\n🚀 Running full risk and stability analysis...\n")
    crew = callCrew()
    result = crew.kickoff()

    # Save output with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_path = f"reports/final_report_{timestamp}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(result)

    # Show summary preview
    print("\n✅ GRiSP Report Generated!")
    print(f"📄 Saved to: {report_path}")
    print("\n📊 Summary Preview:\n")
    print("=" * 60)
    print(result[:1500] + ("\n..." if len(result) > 1500 else ""))
    print("=" * 60)

if __name__ == "__main__":
    run_grisp_pipeline()