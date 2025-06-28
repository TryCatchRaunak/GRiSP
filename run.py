import os
from crewai import Crew
from dotenv import load_dotenv
import datetime

# Load .env variables (API keys, etc.)
load_dotenv()

# Ensure 'reports' folder exists
os.makedirs("reports", exist_ok=True)

def run_grisp_pipeline():
    # Load Crew and YAML config
    print("\n🧠 Initializing GRiSP — Global Risk & Stability Predictor...")
    crew = Crew.from_yaml("crew.yaml")

    # Kickoff pipeline
    print("\n🚀 Running full risk and stability analysis...\n")
    result = crew.kickoff()

    # Generate output file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_path = f"reports/final_report_{timestamp}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(result)

    # Display result summary
    print("\n✅ GRiSP Report Generated!")
    print(f"📄 Saved to: {report_path}")
    print("\n📊 Summary Preview:\n")
    print("=" * 60)
    print(result[:1500] + ("\n..." if len(result) > 1500 else ""))
    print("=" * 60)

if __name__ == "__main__":
    run_grisp_pipeline()
