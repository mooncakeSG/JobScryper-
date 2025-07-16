import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from groq_resume_suggestion import get_groq_match_score_and_explanation
    print("✅ Successfully imported get_groq_match_score_and_explanation")
    
    # Test the function
    test_result = get_groq_match_score_and_explanation(
        "Software engineer with 5 years experience in Python and React",
        {"title": "Senior Software Engineer", "description": "Looking for Python developer"}
    )
    print(f"✅ Function works: {test_result}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Function failed: {e}") 