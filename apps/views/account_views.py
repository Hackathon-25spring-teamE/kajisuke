from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404


from ..models import CustomUser

class MyPageView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'myaccount.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return get_object_or_404(CustomUser, pk=self.request.user.pk)
