from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from .models import Post, Category
from datetime import datetime
from .filters import PostFilter
from .forms import PostForm
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import send_mail

class PostList(ListView):
    model = Post
    context_object_name = 'news'
    paginate_by = 10

    def get_template_names(self):
        if self.request.path == '/news/':
            self.template_name = 'list.html'
        elif self.request.path == '/news/search/':
            self.template_name = 'search.html'
        return self.template_name

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['filterset'] = self.filterset
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'details.html'
    context_object_name = 'new'

class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/post/article/create/':
            post.post_type = 'AT'
        post.save()
        return super().form_valid(form)

class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

class PostDelete(DeleteView):
    form_class = PostForm
    model = Post
    template_name = 'post_delete.html'

def author_now(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not user.groups.filter(name='authors').exists():
        user.groups.add(author_group)
    return redirect('post_list')

class CategoryListView(PostList):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = queryset.filter(category=self.category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    message = 'Теперь вы подписаны на рассылку новостей этой категории.'
    return render(request, 'subscribe.html', {'category':category, 'message':message})