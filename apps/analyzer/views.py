import logging
import statistics
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.analyzer.models import AnalysisRequest
from services.analysis_service import AnalysisService
from services.compare_service import CompareService
from services.trend_service import TrendService

logger = logging.getLogger(__name__)


# ─── AUTH VIEWS ─────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('analyzer:homepage')

    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            return render(request, 'auth/register.html', {'error': 'Username dan password wajib diisi.'})
        if password1 != password2:
            return render(request, 'auth/register.html', {'error': 'Password tidak cocok.', 'username': username, 'email': email})
        if len(password1) < 8:
            return render(request, 'auth/register.html', {'error': 'Password minimal 8 karakter.', 'username': username, 'email': email})
        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {'error': f'Username "{username}" sudah dipakai.', 'email': email})

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect('analyzer:homepage')

    return render(request, 'auth/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('analyzer:homepage')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url and next_url != '/analyze/':
                return redirect(next_url)
            return redirect('analyzer:homepage')
        else:
            return render(request, 'auth/login.html', {'error': 'Username atau password salah.', 'username': username})

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('analyzer:login')


# ─── ANALYZER VIEWS ─────────────────────────────────────────

@login_required
def homepage(request):
    trend_service = TrendService()
    trending = trend_service.get_trending_searches()
    return render(request, 'analyzer/homepage.html', {'trending': trending})


@login_required
@require_http_methods(["POST"])
def analyze(request):
    keyword = request.POST.get('keyword', '').strip()

    if not keyword:
        return render(request, 'analyzer/homepage.html', {
            'error': 'Keyword tidak boleh kosong.'
        })

    service = AnalysisService()
    result  = service.run_analysis(keyword, user=request.user)

    if not result['success']:
        return render(request, 'analyzer/homepage.html', {
            'error': result.get('error', 'Terjadi kesalahan.')
        })

    return render(request, 'analyzer/result.html', {'result': result})


@login_required
def dashboard(request):
    analyses = AnalysisRequest.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-created_at')[:20]

    return render(request, 'analyzer/dashboard.html', {'analyses': analyses})


@login_required
def analysis_detail(request, pk):
    analysis    = get_object_or_404(AnalysisRequest, pk=pk, user=request.user)
    data_points = analysis.trend_data_points.all()

    values = [dp.interest_value for dp in data_points]
    if values:
        avg_interest   = round(sum(values) / len(values), 1)
        recent         = values[-14:] if len(values) >= 14 else values
        older          = values[:len(values)-14] if len(values) >= 28 else values
        recent_avg     = sum(recent) / len(recent)
        older_avg      = sum(older) / len(older) if older else recent_avg
        ratio          = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        momentum_score = round(min(100, max(0, (ratio + 1) * 50)), 1)
        std            = statistics.stdev(values) if len(values) > 1 else 0
        mean           = sum(values) / len(values)
        cv             = std / mean if mean > 0 else 1
        consistency_score = round(min(100, max(0, (1 - cv) * 100)), 1)
    else:
        avg_interest = momentum_score = consistency_score = 0

    return render(request, 'analyzer/detail.html', {
        'analysis':          analysis,
        'data_points':       data_points,
        'avg_interest':      avg_interest,
        'momentum_score':    momentum_score,
        'consistency_score': consistency_score,
    })


@login_required
def compare_page(request):
    return render(request, 'analyzer/compare.html')


@login_required
@require_http_methods(["POST"])
def compare_analyze(request):
    query = request.POST.get('query', '').strip()

    if not query:
        return render(request, 'analyzer/compare.html', {'error': 'Input tidak boleh kosong.'})

    service  = CompareService()
    keywords = service.parse_keywords(query)

    if len(keywords) < 2:
        return render(request, 'analyzer/compare.html', {
            'error': 'Gunakan format: keyword1 vs keyword2',
            'query': query
        })

    result = service.fetch_comparison(keywords)

    if not result['success']:
        return render(request, 'analyzer/compare.html', {
            'error': result['error'],
            'query': query
        })

    return render(request, 'analyzer/compare_result.html', {'result': result})