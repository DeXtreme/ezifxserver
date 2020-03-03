from .views import SignalsViewset
from rest_framework.routers import SimpleRouter

router=SimpleRouter()
router.register(r"",SignalsViewset,basename="signals")
urlpatterns =router.urls
