import logging
import pandas as pd

logger = logging.getLogger(__name__)


class ScoringService:
    """
    Service untuk menghitung trend score dari data Google Trends.
    Score range: 0 - 100
    """

    def calculate_score(self, trend_data: list) -> dict:
        """
        Menghitung trend score berdasarkan beberapa faktor:
        1. Average interest (40% bobot)
        2. Recent momentum (40% bobot) — apakah tren naik atau turun
        3. Consistency (20% bobot) — seberapa stabil tren

        Args:
            trend_data: list of dict {date, value}

        Returns:
            dict berisi score dan breakdown detail
        """
        try:
            if not trend_data:
                return {'score': 0, 'breakdown': {}}

            values = [point['value'] for point in trend_data]
            df = pd.Series(values)

            # --- Faktor 1: Average Interest (0-100) ---
            avg_score = df.mean()

            # --- Faktor 2: Recent Momentum ---
            # Bandingkan rata-rata 2 minggu terakhir vs sebelumnya
            recent = df.tail(14).mean() if len(df) >= 14 else df.mean()
            older = df.head(len(df) - 14).mean() if len(df) >= 28 else df.mean()

            if older > 0:
                momentum_ratio = (recent - older) / older
                # Normalisasi ke 0-100 (ratio -1 s/d +1 → 0 s/d 100)
                momentum_score = min(100, max(0, (momentum_ratio + 1) * 50))
            else:
                momentum_score = 50

            # --- Faktor 3: Consistency ---
            # Semakin rendah std deviation, semakin konsisten
            std = df.std()
            mean = df.mean()
            if mean > 0:
                cv = std / mean  # coefficient of variation
                consistency_score = min(100, max(0, (1 - cv) * 100))
            else:
                consistency_score = 0

            # --- Final Score (weighted average) ---
            final_score = (
                (avg_score * 0.4) +
                (momentum_score * 0.4) +
                (consistency_score * 0.2)
            )

            final_score = round(min(100, max(0, final_score)), 2)

            breakdown = {
                'average_interest': round(avg_score, 2),
                'momentum_score': round(momentum_score, 2),
                'consistency_score': round(consistency_score, 2),
                'final_score': final_score
            }

            logger.info(f"Score calculated: {final_score} | Breakdown: {breakdown}")

            return {
                'score': final_score,
                'breakdown': breakdown
            }

        except Exception as e:
            logger.error(f"Error calculating score: {str(e)}")
            return {'score': 0, 'breakdown': {}}

    def get_score_label(self, score: float) -> str:
        """
        Mengkonversi score numerik ke label deskriptif.
        """
        if score >= 75:
            return 'Sangat Tinggi 🔥'
        elif score >= 50:
            return 'Tinggi 📈'
        elif score >= 25:
            return 'Sedang 📊'
        else:
            return 'Rendah 📉'