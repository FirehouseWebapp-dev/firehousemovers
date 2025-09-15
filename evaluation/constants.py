"""
Constants for evaluation module to avoid hard-coded strings and reduce typos.
"""

# Evaluation status values
class EvaluationStatus:
    PENDING = "pending"
    COMPLETED = "completed"

# Display status values removed - templates use hardcoded strings directly

# Question types (from models)
class QuestionType:
    SHORT = "short"
    LONG = "long"
    STARS = "stars"
    EMOJI = "emoji"
    RATING = "rating"
    NUMBER = "number"
    BOOL = "bool"
    SELECT = "select"
    SECTION = "section"

# Numeric question types that use min/max values
NUMERIC_QUESTION_TYPES = [
    QuestionType.STARS,
    QuestionType.EMOJI,
    QuestionType.RATING,
    QuestionType.NUMBER,
]

# Text question types that need sanitization
TEXT_QUESTION_TYPES = [
    QuestionType.SHORT,
    QuestionType.LONG,
]
