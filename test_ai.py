import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.ai_service import AIService

ai = AIService()

for i in range(3):
    insight = ai.generate_insight(
        keyword='coffee shop',
        score=65.5,
        breakdown={
            'average_interest': 70,
            'momentum_score': 58,
            'consistency_score': 72
        }
    )
    print(f"\n--- Insight {i+1} ---")
    print(insight)
    print("-" * 50)