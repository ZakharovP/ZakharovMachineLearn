from . import settings

def ad_visibility(request):
    """
        Контекстный процессор, который определяет, показывать ли рекламу или нет.
        Зависит от настроек приложения.
    """
    return {
        'is_ad_visible': settings.ADVERTISMENT
    }