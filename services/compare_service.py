import time
import logging
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)


class CompareService:

    def __init__(self):
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=(10, 25),
            retries=3,
            backoff_factor=0.5
        )

    def parse_keywords(self, query: str) -> list:
        separators = [' vs ', ' VS ', ' versus ', ' Vs ']
        for sep in separators:
            if sep in query:
                parts = query.split(sep, 1)
                return [p.strip() for p in parts if p.strip()]
        if ',' in query:
            parts = query.split(',', 1)
            return [p.strip() for p in parts if p.strip()]
        return [query.strip()]

    def fetch_comparison(self, keywords: list, timeframe: str = 'today 3-m') -> dict:
        # Retry logic untuk handle 429
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait = attempt * 10  # 10s, 20s
                    logger.info(f'Retry {attempt} — waiting {wait}s...')
                    time.sleep(wait)

                self.pytrends.build_payload(keywords, timeframe=timeframe)
                df = self.pytrends.interest_over_time()

                if df.empty:
                    return {'success': False, 'error': 'Data tidak ditemukan untuk keyword tersebut.'}

                kw_a = keywords[0]
                kw_b = keywords[1]

                data_a = [round(float(v), 1) for v in df[kw_a].tolist()]
                data_b = [round(float(v), 1) for v in df[kw_b].tolist()]
                labels = [str(d.date()) for d in df.index.tolist()]

                avg_a = round(sum(data_a) / len(data_a), 1)
                avg_b = round(sum(data_b) / len(data_b), 1)

                winner = kw_a if avg_a >= avg_b else kw_b
                margin = round(abs(avg_a - avg_b), 1)

                mid   = len(data_a) // 2
                mom_a = sum(data_a[mid:]) / len(data_a[mid:])
                mom_b = sum(data_b[mid:]) / len(data_b[mid:])
                momentum_winner = kw_a if mom_a >= mom_b else kw_b

                return {
                    'success':         True,
                    'keywords':        keywords,
                    'keyword_a':       kw_a,
                    'keyword_b':       kw_b,
                    'labels':          labels,
                    'data_a':          data_a,
                    'data_b':          data_b,
                    'avg_a':           avg_a,
                    'avg_b':           avg_b,
                    'winner':          winner,
                    'margin':          margin,
                    'momentum_winner': momentum_winner,
                }

            except Exception as e:
                err = str(e)
                logger.error(f'CompareService attempt {attempt+1} error: {err}')

                if '429' in err and attempt < max_retries - 1:
                    continue  # retry

                # Pesan error yang user-friendly
                if '429' in err:
                    return {
                        'success': False,
                        'error': 'Google Trends sedang membatasi request. Tunggu 1-2 menit lalu coba lagi.'
                    }
                return {'success': False, 'error': f'Gagal mengambil data: {err}'}

        return {'success': False, 'error': 'Gagal setelah beberapa percobaan. Coba lagi nanti.'}