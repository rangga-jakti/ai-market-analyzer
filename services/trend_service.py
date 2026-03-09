import time
import logging
import pandas as pd
from pytrends.request import TrendReq
from django.utils import timezone
from apps.analyzer.models import AnalysisRequest, TrendDataPoint

logger = logging.getLogger(__name__)

class TrendService:
    """
    Service untuk mengambil data dari Google Trends
    menggunakan pytrends library.
    """

    def __init__(self):
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=(10, 25),
            retries=2,
            backoff_factor=0.1
        )

    def fetch_trend_data(self, keyword: str, timeframe: str = 'today 3-m') -> dict:
        """
        Mengambil data trend dari Google Trends.

        Args:
            keyword: kata kunci yang akan dianalisis
            timeframe: rentang waktu ('today 3-m' = 3 bulan terakhir)

        Returns:
            dict berisi status dan data trend
        """
        try:
            logger.info(f"Fetching trend data for keyword: {keyword}")

            # Build payload — persiapkan request ke Google Trends
            self.pytrends.build_payload(
                kw_list=[keyword],
                timeframe=timeframe,
                geo='',  # worldwide
            )

            # Ambil data interest over time
            df = self.pytrends.interest_over_time()

            # Jika data kosong
            if df is None or df.empty:
                logger.warning(f"No trend data found for keyword: {keyword}")
                return {
                    'success': False,
                    'error': 'Tidak ada data trend untuk keyword ini.'
                }

            # Hapus kolom 'isPartial' jika ada
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])

            # Konversi ke list of dict
            trend_data = []
            for date, row in df.iterrows():
                trend_data.append({
                    'date': date.date(),
                    'value': int(row[keyword])
                })

            logger.info(f"Successfully fetched {len(trend_data)} data points")

            return {
                'success': True,
                'keyword': keyword,
                'timeframe': timeframe,
                'data_points': trend_data
            }

        except Exception as e:
            logger.error(f"Error fetching trend data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_trend_data(self, analysis: AnalysisRequest, trend_data: list) -> bool:
        """
        Menyimpan data trend points ke database.

        Args:
            analysis: instance AnalysisRequest
            trend_data: list of dict {date, value}

        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            # Hapus data lama jika ada (untuk re-analysis)
            TrendDataPoint.objects.filter(analysis=analysis).delete()

            # Bulk create untuk efisiensi
            data_points = [
                TrendDataPoint(
                    analysis=analysis,
                    date=point['date'],
                    interest_value=point['value']
                )
                for point in trend_data
            ]

            TrendDataPoint.objects.bulk_create(data_points)
            logger.info(f"Saved {len(data_points)} trend data points")
            return True

        except Exception as e:
            logger.error(f"Error saving trend data: {str(e)}")
            return False
        
    def get_trending_searches(self, country='ID'):
        import random
        pool = [
            'AI tools', 'coffee shop', 'thrift store', 'frozen food',
            'digital marketing', 'outfit aesthetic', 'skincare lokal',
            'franchise makanan', 'jastip luar negeri', 'konten kreator',
            'bisnis online', 'dropship', 'properti', 'EV motor listrik'
        ]
        
        try:
            from apps.analyzer.models import AnalysisRequest
            from django.db.models import Count
            top = list(AnalysisRequest.objects
                    .filter(status='completed')
                    .values_list('keyword', flat=True)
                    .annotate(c=Count('keyword'))
                    .order_by('-c')[:3])  # ambil 3 dari DB
            
            # Mix: 3 dari DB + 2 random dari pool
            pool_filtered = [x for x in pool if x not in top]
            random.shuffle(pool_filtered)
            return top + pool_filtered[:2]
        except:
            random.shuffle(pool)
            return pool[:5]