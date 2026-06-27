import re
from datetime import datetime, timedelta, timezone

from django.contrib.auth import authenticate, get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

from .models import LoginLog
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

SAMPLE_CONTENT = """<h1>Oydin tunda maktub</h1>
<p>Shahar hech qachon to'liq uxlamaydi. Hatto yarim tunda ham — kimdir derazadan tashqariga qaraydi, kimdir ko'chada yolg'iz yuradi, kimdir sovuq choy ustida o'tirib, yozilmagan maktubni o'ylaydi. Lola ham shunday odamlardan biriydi.</p>
<p>U stolga o'tirganida soat o'n birdan oshgandi. Qog'oz oq, qalam tayyor, lekin so'zlar kelmaydi. On yil — deydi u o'ziga. O'n yil o'tdi. Shuncha vaqtdan keyin nima deyish mumkin? "Eslayman" — juda oddiy. "Sog'indim" — yolg'on bo'ladi, chunki sog'inish ham ko'nikib ketadi bir vaqt.</p>
<h2>Birinchi satr</h2>
<p>Eng qiyin narsa — birinchi satr. Barcha maktublarda, barcha kitoblarda shunday. Bir marta boshlasang, qolgan so'zlar o'zlari keladi, go'yo ular doim shu yerda kutib turganday. Lekin o'sha birinchi satr — u boshqa narsani talab qiladi. Jasorat emas, balki taslim bo'lishni.</p>
<blockquote>Yozish — bu o'z ovozingni eshitishdan qo'rqmaslik.</blockquote>
<p>Lola qog'ozga tikildi. Ko'chada mashinaning o'tishi eshitildi, keyin jimlik. Keyin yana shamol — eski oynaning g'ichirlashi. U qalam uchini qog'ozga tegizdi va... to'xtadi.</p>
<p>Yo'q, bugun emas. Bugun u shunchaki o'tiradi. Ba'zan yozmaslik ham — yozish.</p>
<h2>Ikkinchi tong</h2>
<p>Ertalab uyg'onganda qog'oz hali ham oq edi. Lekin Lolaning ko'ngli biroz yengillashgandi. Tunda nimadir hal bo'lgan edi — u o'zi bilmasa ham. Ba'zan tun shu ishni qiladi: so'zsiz hal qiladi.</p>
<p>U choy qo'ydi. Derazadan tashqariga qaradi. Mahalla bolalari maktabga shoshardi, ular portfellarini ko'tarib, birining gapini biri kesib, kulishardi. Oddiy ertalab. Lekin Lola uchun bu ertalab boshqacha edi — u birinchi satrni topgan edi. U hali yozmagan, ammo his qilgan edi.</p>
<p><em>"Sening ismingni aytganda, tashqarida shamol esadi — bu tasodif emas deb o'ylayman."</em></p>
<p>Mana. Shu edi. O'n yillik birinchi satr.</p>"""

SAMPLE_DEFAULTS = {
    'meta': {'title': 'Oydin tunda maktub', 'author': '', 'year': 2025},
    'format': {'id': 'a5', 'label': 'A5', 'widthMm': 148, 'heightMm': 210},
    'margins': {'top': 18, 'bottom': 18, 'inner': 20, 'outer': 16},
    'numbering': {
        'enabled': True, 'startAtPage': 1, 'startFrom': 1,
        'position': 'bottom-center', 'style': 'arabic',
    },
    'typography': {
        'bodyFont': 'Spectral', 'bodySizePt': 11, 'lineHeight': 1.5,
        'paragraphIndent': True, 'justify': True, 'pageBreak': 'fill',
    },
}


def _create_sample_project(user):
    from apps.projects.models import Project
    Project.objects.create(
        owner=user,
        name='Oydin tunda maktub',
        content=SAMPLE_CONTENT,
        **SAMPLE_DEFAULTS,
    )


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def _auth_response_serializer(name):
    return inline_serializer(name=name, fields={
        'access': serializers.CharField(),
        'refresh': serializers.CharField(),
        'user': UserSerializer(),
    })


def _get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _word_count(html):
    text = re.sub(r'<[^>]+>', ' ', html or '')
    words = text.split()
    return len(words)


@extend_schema(tags=['Auth'])
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Ro\'yxatdan o\'tish',
        request=RegisterSerializer,
        responses={
            201: _auth_response_serializer('RegisterResponse'),
            400: OpenApiResponse(description='Validation error'),
        },
        auth=[],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _create_sample_project(user)
        return Response({
            **_tokens_for_user(user),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Auth'])
class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Kirish',
        request=inline_serializer(name='LoginRequest', fields={
            'email': serializers.EmailField(),
            'password': serializers.CharField(),
        }),
        responses={
            200: _auth_response_serializer('LoginResponse'),
            401: OpenApiResponse(description='Email yoki parol noto\'g\'ri'),
        },
        auth=[],
    )
    def post(self, request):
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {'detail': 'Email yoki parol noto\'g\'ri.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Record login
        LoginLog.objects.create(user=user, ip_address=_get_client_ip(request))
        return Response({
            **_tokens_for_user(user),
            'user': UserSerializer(user).data,
        })


@extend_schema(tags=['Auth'])
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Hozirgi foydalanuvchi',
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)


@extend_schema(tags=['Dashboard'])
class DashboardAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(summary='To\'liq analitika (faqat admin)')
    def get(self, request):
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)

        users = (
            User.objects
            .prefetch_related('projects', 'login_logs')
            .order_by('-date_joined')
        )

        logins_today = LoginLog.objects.filter(timestamp__gte=today_start).count()
        active_week = (
            LoginLog.objects
            .filter(timestamp__gte=week_ago)
            .values('user')
            .distinct()
            .count()
        )

        from apps.projects.models import Project
        total_projects = Project.objects.count()

        users_data = []
        for u in users:
            projects = list(u.projects.all())
            logs = list(u.login_logs.all()[:20])
            last_log = logs[0] if logs else None

            users_data.append({
                'id': str(u.id),
                'name': u.first_name or u.username,
                'email': u.username,
                'is_staff': u.is_staff,
                'date_joined': u.date_joined.isoformat(),
                'last_login': last_log.timestamp.isoformat() if last_log else None,
                'projects_count': len(projects),
                'projects': [
                    {
                        'id': str(p.id),
                        'name': p.name,
                        'created_at': p.created_at.isoformat(),
                        'updated_at': p.updated_at.isoformat(),
                        'word_count': _word_count(p.content),
                    }
                    for p in projects
                ],
                'login_logs': [
                    {'timestamp': log.timestamp.isoformat()}
                    for log in logs
                ],
            })

        return Response({
            'summary': {
                'total_users': users.count(),
                'total_projects': total_projects,
                'logins_today': logins_today,
                'active_users_week': active_week,
            },
            'users': users_data,
        })


def _fmt_date(dt):
    if dt is None:
        return None
    return dt.strftime('%d.%m.%Y')


def _fmt_datetime(dt):
    if dt is None:
        return None
    return dt.strftime('%d.%m.%Y %H:%M')


def _initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return parts[0][0] + parts[1][0]
    return (parts[0][0] if parts and parts[0] else '?')


@staff_member_required(login_url='/admin/login/')
def analytics_html(request):
    from apps.projects.models import Project

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    User = get_user_model()
    users_qs = User.objects.prefetch_related('projects', 'login_logs').order_by('-date_joined')

    logins_today = LoginLog.objects.filter(timestamp__gte=today_start).count()
    active_week = (
        LoginLog.objects.filter(timestamp__gte=week_ago)
        .values('user').distinct().count()
    )
    total_projects = Project.objects.count()
    total_users = users_qs.count()

    users = []
    for u in users_qs:
        name = u.first_name or u.username
        logs = list(u.login_logs.all()[:20])
        last_log = logs[0] if logs else None
        projects = list(u.projects.all())

        users.append({
            'name': name,
            'email': u.username,
            'is_staff': u.is_staff,
            'initials': _initials(name).upper(),
            'date_joined': _fmt_date(u.date_joined),
            'last_login': _fmt_datetime(last_log.timestamp) if last_log else None,
            'projects_count': len(projects),
            'login_count': len(logs),
            'projects': [
                {
                    'name': p.name,
                    'word_count': _word_count(p.content),
                    'updated_at': _fmt_date(p.updated_at),
                }
                for p in projects
            ],
            'login_logs': [
                {'ts': _fmt_datetime(log.timestamp)}
                for log in logs
            ],
        })

    summary_cards = [
        {'label': 'Foydalanuvchilar', 'value': total_users, 'sub': "jami ro'yxatdan o'tgan"},
        {'label': 'Kitoblar', 'value': total_projects, 'sub': 'jami yaratilgan'},
        {'label': 'Bugungi kirish', 'value': logins_today, 'sub': 'login soni bugun'},
        {'label': 'Faol (7 kun)', 'value': active_week, 'sub': "so'nggi haftada kirgan"},
    ]

    return render(request, 'analytics.html', {
        'today': now.strftime('%d %B %Y'),
        'summary_cards': summary_cards,
        'users': users,
    })
