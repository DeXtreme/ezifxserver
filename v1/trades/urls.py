from .views import TradesViewset
from rest_framework.routers import SimpleRouter

router=SimpleRouter()
router.register(r"",TradesViewset,basename="trades")
urlpatterns=router.urls