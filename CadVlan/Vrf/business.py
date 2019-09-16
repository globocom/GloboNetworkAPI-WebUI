from CadVlan.Util.Decorators import cache_function
from CadVlan.settings import CACHE_EQUIPMENTS_TIMEOUT


@cache_function(CACHE_EQUIPMENTS_TIMEOUT)
def cache_vrf_list(vrf):
    vrf_list = dict(list=vrf)
    return vrf_list