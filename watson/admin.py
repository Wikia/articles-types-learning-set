from django.contrib import admin
from watson.models import Session, State, SessionArticle, ArticleData, Type, Kind, Quality, MobileQuality, ArticleMetrics, ExcludedWikis


def generate_article_set(modeladmin, request, queryset):
    for session in queryset:
        session.generate_session_article_set(int(session.pk))
generate_article_set.short_description = "Generate article set"


class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'size')
    actions = [generate_article_set]

    save_plus_action = [generate_article_set]


admin.site.register(Session, SessionAdmin)
admin.site.register(State)
admin.site.register(SessionArticle)
admin.site.register(ArticleData)
admin.site.register(Type)
admin.site.register(Kind)
admin.site.register(Quality)
admin.site.register(MobileQuality)
admin.site.register(ArticleMetrics)
admin.site.register(ExcludedWikis)