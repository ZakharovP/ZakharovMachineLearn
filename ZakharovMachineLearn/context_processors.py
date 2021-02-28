from . import settings

def ad_visibility(request):
    return {
        'is_ad_visible': settings.ADVERTISMENT
    }