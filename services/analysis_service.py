import logging
from apps.analyzer.models import AnalysisRequest
from services.trend_service import TrendService
from services.scoring_service import ScoringService
from services.ai_service import AIService

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Orchestrator service — menggabungkan semua service
    menjadi satu alur analisis yang lengkap.
    """

    def __init__(self):
        self.trend_service = TrendService()
        self.scoring_service = ScoringService()
        self.ai_service = AIService()

    def run_analysis(self, keyword: str, user=None) -> dict:
        """
        Menjalankan analisis lengkap untuk sebuah keyword.
        """
        analysis = AnalysisRequest.objects.create(
            keyword=keyword,
            status='processing',
            user=user  # ← tambahkan ini
        )

        try:
            logger.info(f"Step 1: Fetching trend data for '{keyword}'")
            trend_result = self.trend_service.fetch_trend_data(keyword)

            if not trend_result['success']:
                analysis.status = 'failed'
                analysis.save()
                return {
                    'success': False,
                    'error': trend_result['error']
                }

            self.trend_service.save_trend_data(
                analysis,
                trend_result['data_points']
            )

            logger.info(f"Step 3: Calculating score")
            score_result = self.scoring_service.calculate_score(
                trend_result['data_points']
            )

            logger.info(f"Step 4: Generating AI insight")
            insight = self.ai_service.generate_insight(
                keyword=keyword,
                score=score_result['score'],
                breakdown=score_result['breakdown']
            )

            analysis.trend_score = score_result['score']
            analysis.ai_insight = insight
            analysis.status = 'completed'
            analysis.save()

            return {
                'success': True,
                'analysis_id': analysis.id,
                'keyword': keyword,
                'trend_score': score_result['score'],
                'score_label': self.scoring_service.get_score_label(
                    score_result['score']
                ),
                'breakdown': score_result['breakdown'],
                'ai_insight': insight,
                'data_points': trend_result['data_points']
            }

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            analysis.status = 'failed'
            analysis.save()
            return {
                'success': False,
                'error': f"Analisis gagal: {str(e)}"
            }