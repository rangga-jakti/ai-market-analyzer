import os
import random
import logging
from groq import Groq

logger = logging.getLogger(__name__)


class AIService:
    """
    Service untuk generate business insight menggunakan
    Groq LLM (LLaMA 3). Setiap insight dijamin unik karena
    kombinasi temperature tinggi + rotating personas.
    """

    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY tidak ditemukan di .env")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    # Persona yang dirotasi secara acak setiap request
    PERSONAS = [
    {
        "name": "Hype Builder",
        "style": """Kamu adalah business coach yang energetik dan penuh semangat.
Gaya kamu: singkat, bold, pakai kalimat pendek yang menghantam.
Maksimal 3 kalimat. Tiap kalimat harus berasa seperti wake-up call.
Sesekali pakai kapitalisasi untuk emphasis. Tidak ada basa-basi."""
    },
    {
        "name": "Skeptic Investor",
        "style": """Kamu adalah investor kawakan yang skeptis tapi fair.
Gaya kamu: mulai dengan realita pahit, lalu beri satu peluang konkret, 
akhiri dengan verdict tegas. Nada dingin dan calculated.
Maksimal 3 kalimat. Tidak pakai kata-kata motivasi klise."""
    },
    {
        "name": "Street Strategist",
        "style": """Kamu adalah entrepreneur jalanan yang sudah gagal berkali-kali 
dan akhirnya sukses. Gaya kamu: blak-blakan, pakai analogi sederhana,
bicara seperti teman yang jujur. Maksimal 3 kalimat.
Sesekali pakai pertanyaan retoris yang menusuk."""
    },
    {
        "name": "Data Whisperer",
        "style": """Kamu adalah analis data yang bisa 'membaca' angka seperti cerita.
Gaya kamu: terjemahkan data jadi narasi yang vivid dan mudah dibayangkan.
Pakai perbandingan dan konteks nyata. Maksimal 3 kalimat.
Hindari jargon. Buat orang awam pun langsung paham situasinya."""
    },
    {
        "name": "Contrarian Thinker",
        "style": """Kamu adalah pemikir yang selalu melihat dari sudut yang tidak 
terduga. Gaya kamu: mulai dengan insight yang counterintuitive, 
lalu jelaskan kenapa itu justru peluang atau jebakan.
Maksimal 3 kalimat. Buat pembaca berpikir ulang asumsi mereka."""
    },
    {
        "name": "Storyteller",
        "style": """Kamu adalah penulis bisnis yang suka bercerita.
Gaya kamu: buka dengan satu gambaran situasi yang relatable,
lalu hubungkan ke peluang dari data ini secara natural.
Maksimal 3 kalimat. Mengalir seperti prosa, bukan laporan."""
    },
]

    def generate_insight(self, keyword: str, score: float, breakdown: dict) -> str:
        """
        Generate business insight menggunakan Groq LLM.
        Setiap call menggunakan persona berbeda + temperature tinggi
        sehingga jawaban selalu unik dan tidak repetitif.
        """
        try:
            # Pilih persona secara acak
            persona = random.choice(self.PERSONAS)
            
            # Seed acak untuk memaksa variasi lebih ekstrem
            style_intensifier = random.choice([
                "Jadilah SANGAT singkat dan menghantam — maksimal 2 kalimat.",
                "Gunakan gaya storytelling — buka dengan satu analogi kehidupan nyata.",
                "Mulai dengan pertanyaan retoris yang bikin pembaca berpikir.",
                "Beri verdict paling keras yang bisa kamu berikan berdasarkan data ini.",
                "Bicara seolah kamu sedang ngobrol santai di warung kopi.",
                "Fokus hanya pada SATU insight terpenting — buang yang lain.",
            ])

            avg     = breakdown.get('average_interest', 0)
            momentum = breakdown.get('momentum_score', 50)
            consistency = breakdown.get('consistency_score', 50)

            # Tentukan konteks tren
            if score >= 75:
                trend_context = "sangat kuat dan menjanjikan"
            elif score >= 50:
                trend_context = "positif dan sedang berkembang"
            elif score >= 25:
                trend_context = "moderat dengan potensi yang perlu digali"
            else:
                trend_context = "lemah dan perlu pertimbangan ulang"

            momentum_context = "sedang naik" if momentum >= 55 else \
                               "relatif stabil" if momentum >= 45 else "sedang menurun"

            # Prompt yang dikirim ke LLM
            prompt = f"""
Keyword: "{keyword}"
Trend Score: {score}/100 — tren {trend_context}
Momentum: {momentum_context}
Konsistensi: {"tinggi" if consistency >= 60 else "rendah"}

Tulis business insight dalam Bahasa Indonesia.
Maksimal 3 kalimat — tidak boleh lebih.
Jangan sebut angka secara harfiah. Interpretasikan jadi cerita.
Jangan pakai bullet points. Jangan basa-basi pembuka seperti "Berdasarkan data...".
Langsung masuk ke insight yang tajam dan berkarakter sesuai persona kamu.
Instruksi tambahan: {style_intensifier}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": persona["style"]
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.85,   # tinggi = jawaban lebih bervariasi
                max_tokens=300,
            )

            insight = response.choices[0].message.content.strip()
            logger.info(f"Insight generated by persona: {persona['name']}")
            return insight

        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            # Fallback ke rule-based jika API gagal
            return self._fallback_insight(keyword, score, breakdown)

    def _fallback_insight(self, keyword: str, score: float, breakdown: dict) -> str:
        """
        Fallback jika Groq API tidak tersedia.
        Tetap menghasilkan insight yang bervariasi via template rotation.
        """
        momentum = breakdown.get('momentum_score', 50)
        consistency = breakdown.get('consistency_score', 50)

        templates = [
            f"Pasar '{keyword}' mencatat skor {score}/100 — {'peluang yang layak dikejar' if score >= 50 else 'perlu strategi yang lebih matang'}. "
            f"Momentum {'sedang berpihak padamu' if momentum >= 50 else 'belum mendukung masuk sekarang'}. "
            f"{'Konsistensi tren yang tinggi menjadi sinyal demand yang dapat diandalkan.' if consistency >= 60 else 'Fluktuasi pasar menuntut adaptasi strategi yang cepat.'} "
            f"{'Segera validasi ide bisnismu sebelum kompetitor bergerak lebih dulu.' if score >= 50 else 'Pertimbangkan pivot atau eksplorasi segmen yang lebih niche.'}",

            f"Dari data yang terkumpul, '{keyword}' {'menunjukkan sinyal yang menggembirakan' if score >= 50 else 'belum menunjukkan tanda-tanda yang kuat'}. "
            f"{'Pasar sedang bergerak naik — window of opportunity terbuka lebar.' if momentum >= 55 else 'Timing entry perlu dipertimbangkan lebih matang.'} "
            f"Rekomendasi: {'mulai riset kompetitor dan bangun MVP secepatnya.' if score >= 60 else 'lakukan uji pasar skala kecil sebelum komitmen penuh.'}",
        ]

        return random.choice(templates)