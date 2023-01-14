from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from blog.models import Post, Comment
from django.utils import timezone
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.forms import PostForm, CommentForm
from django.urls import reverse_lazy
# Create your views here.


class AboutView(TemplateView):
    template_name = "about.html"


class PostListView(ListView):
    model = Post
    def get_queryset(self):
        return Post.objects.filter(publish_date__lte = timezone.now()).order_by('-publish_date')

class PostDetailView(DetailView):
    model = Post

class PostCreateView(CreateView, LoginRequiredMixin):
    # import mixins for authentication and authorization for creation
    login_url = 'login/' # almost like setting up the static files
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostUpdateView(UpdateView, LoginRequiredMixin):
    model = Post
    login_url = 'login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post


class PostDeleteView(DeleteView, LoginRequiredMixin):
    model = Post
    success_url = reverse_lazy('post_list')

    '''
    when you are deleting a post you don't want the success url to activate until you delete it.
    otherwise it'll jump to another page on the website
    to overcome this problem we use reverse_lazy - this waits until delete to give success url
    '''

class DraftListView(ListView, LoginRequiredMixin):
    model = Post
    login_url = "login/"
    redirect_field_name = "blog/post_list.html"

    def get_queryset(self):
        return Post.objects.filter(publish_date__isnull = True).order_by('create_date') # i.e select posts which have published date as null
    

###################################################################### comments

@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk = pk)

@login_required
def add_comments_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post # connecting comment to post object, foreign key reference
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm() # 
    return render(request, 'blog/comment_form.html', context= {'form':form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk = pk)
    comment.approve()
    return redirect('post_detail', pk = comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk = pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)