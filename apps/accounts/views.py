from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

from .serializers import RegisterSerializer, UserSerializer

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
