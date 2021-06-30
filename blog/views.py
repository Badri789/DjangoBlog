from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import Account
from .models import Post, Comment, PostRating, Notification
from .forms import PostForm, CommentForm


def index(request):
    # პოსტის რეიტინგი დამოკიდებულია მისი ლაიქებისა და კომენტარების ჯამზე
    featured_posts = Post.objects.raw('''
                SELECT p.*, COUNT(distinct c.id) as comments,
                COUNT(distinct l.id) as likes,
                COALESCE(COUNT(distinct c.id),0) + COALESCE(COUNT(distinct l.id),0) as rating
                from blog_post p
                LEFT JOIN blog_comment c
                on c.post_id = p.id
                LEFT JOIN blog_postrating l
                on l.post_id = p.id and l.liked = true
                GROUP BY p.id
                ORDER by rating DESC;
    ''')

    latest_posts = Post.objects.all().order_by('-date_created')[:3]

    return render(request, 'blog/index.html', {
        'featured_posts': featured_posts[:3],
        'latest_posts': latest_posts
    })


def all_posts(request):
    posts = Post.objects.all().order_by('-date_created')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/all_posts.html', {
        'page_obj': page_obj
    })


def post_details(request, slug):
    post = get_object_or_404(Post, slug=slug)
    likes = PostRating.objects.filter(post=post, liked=True).count()
    dislikes = PostRating.objects.filter(post=post, liked=False).count()
    root_comments = Comment.objects.filter(post=post, root_comment__isnull=True).order_by('date_created')
    comment_count = Comment.objects.filter(post=post).count()
    root_comment_form = CommentForm(prefix='root')
    liked = -1
    if request.user.is_authenticated:
        try:
            liked = PostRating.objects.get(post=post, user=request.user).liked
        except PostRating.DoesNotExist:
            pass

    return render(request, 'blog/post_details.html', {
        'post': post,
        'likes': likes,
        'dislikes': dislikes,
        'root_comments': root_comments,
        'comment_count': comment_count,
        'root_comment_form': root_comment_form,
        'liked': liked
    })


def posts_by_tag(request, tag):
    posts = Post.objects.filter(tags__name=tag).order_by('-date')

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/all_posts.html', {
        'page_obj': page_obj
    })


def posts_by_user(request, username):
    user = Account.objects.get(username=username)
    posts = Post.objects.filter(created_by=user.pk).order_by('-date')

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/all_posts.html', {
        'page_obj': page_obj
    })


def search_posts(request):
    if 'q' in request.GET:
        q = request.GET['q']
        posts = Post.objects.filter(Q(title__icontains=q) | Q(tags__name__contains=q)).order_by('-date').distinct()
    else:
        return redirect('all-posts')

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/all_posts.html', {
        'page_obj': page_obj
    })


@login_required(login_url='/login')
def create_comment(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug)
        if 'save_comment' in request.POST:
            comment_form = CommentForm(request.POST, prefix='root')
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                if comment.author != post.created_by:
                    Notification.objects.create(type=3, to_user=post.created_by, from_user=request.user,
                                                post=post, comment=comment)
                return redirect('post-details', slug=slug)
            else:
                messages.error(request, 'Form Validation Error!', extra_tags='bi bi-x-circle-fill')
                return redirect('post-details', slug=slug)
        elif 'save_reply' in request.POST:
            # რაკი prefix-ად მაქვს save_reply, რომელიც რეალურად parent_id-ია, მაშინ ფორმის
            # body field-ის name უნდა იყოს id-body
            reply_form = CommentForm(request.POST, prefix=request.POST.get('parent_comment'))
            if reply_form.is_valid():
                comment_reply = reply_form.save(commit=False)
                comment_reply.author = request.user
                comment_reply.post = post
                reply_to_comment = Comment.objects.get(pk=request.POST.get('parent_comment'))
                comment_reply.parent_comment = reply_to_comment
                comment_reply.root_comment = Comment.objects.get(pk=request.POST.get('root_comment'))
                comment_reply.save()
                if comment_reply.author != reply_to_comment.author:
                    Notification.objects.create(type=4, to_user=reply_to_comment.author, from_user=request.user,
                                                post=post, comment=comment_reply)
                return redirect('post-details', slug=slug)
            else:
                messages.error(request, 'Form Validation Error!', extra_tags='bi bi-x-circle-fill')
                return redirect('post-details', slug=slug)


@login_required(login_url='/login')
def edit_comment(request, slug, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author and not request.user.is_superuser:
        return HttpResponse("You cannot edit other user's comments!")

    if request.method == 'POST':
        edit_form = CommentForm(request.POST, prefix=comment_id)
        if edit_form.is_valid():
            comment.body = edit_form.cleaned_data['body']
            comment.save()
            return redirect('post-details', slug=slug)
        else:
            messages.error(request, 'Form Validation Error!', extra_tags='bi bi-x-circle-fill')
            return redirect('post-details', slug=slug)


# ეს ერთი view ფუნქცია ამუშავებს, როგორც GET request-ებს,
# ასევე POST request-ებსაც.
@login_required(login_url='/login')
def create_post(request):
    # Request-ის ტიპის შემოწმება
    if request.method == 'POST':
        # ფორმიდან მიღებული ველებისა და ფაილების შეტანა PostForm კლასში ვალიდაციისთვის
        form = PostForm(request.POST, request.FILES)

        # ფორმის ვალიდურობის შემოწმება
        if form.is_valid():
            # ბაზაში შენახვა დაქომითების გარეშე, რადგან დასამატებელია created_by ველი
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()
            # save_m2m() აუცილებელია როდესაც ვიყენებთ commit=False-ს, რათა შეინახოს ManyToMany
            # რალაციები, ამ შემთხვევაში Tags
            form.save_m2m()
            return redirect('all-posts')  # ყველა პოსტის გვერდზე გადასვლა

    # თუკი ეს არის GET request, მაშინ მზადდება ცარიელი ფორმა გვერდზე გამოსატანად
    else:
        form = PostForm()

    # Template მიიღებს ცარიელ ფორმას GET request-ის შემთხვევაში.
    # თუკი POST request-ის შემდეგ ვალიდაცია წარუმატებლად დასრულდა
    # template მიიღებს არასწორად შევსებულ ფორმას თავისი error მესიჯებით
    return render(request, 'blog/create_post.html', {
        'form': form
    })


@login_required(login_url='/login')
def edit_post(request, slug):
    post = Post.objects.get(slug=slug)
    if request.user != post.created_by and not request.user.is_superuser:
        return HttpResponse("You cannot edit other user's posts!")

    if request.method == 'POST':
        # ვამოწმებთ არის თუ არა request-ში ფაილები ანუ
        # ტვირთავს თუ არა მომხმარებელი ახალ header სურათს
        if request.FILES:
            # instance-ით ვეუბნებით თუ რომელ პოსტს ვააფდეითებთ
            form = PostForm(request.POST, request.FILES, instance=post)
        else:
            # რაკი ახალი სურათი არ ატრვირთულა, initial პარამეტრით ფორმას ვავსებთ იმით რაც ბაზაშია
            form = PostForm(request.POST, initial={'header_image': post.header_image}, instance=post)
        if form.is_valid():
            form.save()
            return redirect('all-posts')
    else:
        # GET-ის შემთხვევაში instance პარამეტრი უზრონველყოფს update ფორმის pre-populate-ს
        form = PostForm(instance=post, initial={'header_image': post.header_image})

    return render(request, 'blog/edit_post.html', {
        'slug': slug,
        'form': form
    })


@login_required(login_url='/login')
def rate_post(request, slug):
    post = Post.objects.get(slug=slug)
    if request.user == post.created_by:
        return HttpResponse("You cannot rate you own post!")

    if request.method == 'POST':
        try:
            post_rating = PostRating.objects.get(post=post, user=request.user)
        except PostRating.DoesNotExist:
            post_rating = None
        if 'like' in request.POST:
            if post_rating and not post_rating.liked:
                post_rating.liked = True
                post_rating.save()
                Notification.objects.create(type=1, to_user=post.created_by, from_user=request.user, post=post)
            elif not post_rating:
                post_rating = PostRating(post=post, user=request.user, liked=True)
                post_rating.save()
                Notification.objects.create(type=1, to_user=post.created_by, from_user=request.user, post=post)
        elif 'dislike' in request.POST:
            if post_rating and post_rating.liked:
                post_rating.liked = False
                post_rating.save()
                Notification.objects.create(type=2, to_user=post.created_by, from_user=request.user, post=post)
            elif not post_rating:
                post_rating = PostRating(post=post, user=request.user, liked=False)
                post_rating.save()
                Notification.objects.create(type=2, to_user=post.created_by, from_user=request.user, post=post)
        return redirect('post-details', slug=slug)


@login_required(login_url='/login')
def all_notifications(request, username):
    if request.user != Account.objects.get(username=username):
        return HttpResponse("You cannot view other user's notifications!")

    notifications = Notification.objects.filter(to_user=request.user).order_by('-date')
    paginator = Paginator(notifications, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/all_notifications.html', {
        'page_obj': page_obj
    })


@login_required(login_url='/login')
def notification_view(request, notification_id, slug):
    notification = get_object_or_404(Notification, pk=notification_id)
    if request.user == notification.to_user:
        if not notification.user_has_seen:
            notification.user_has_seen = True
            notification.save()
        else:
            pass
    else:
        return HttpResponse("You cannot view other user's notifications!")

    return redirect('post-details', slug=slug)


@login_required(login_url='/login')
def delete_post(request, slug):
    post = Post.objects.get(slug=slug)
    if request.user != post.created_by and not request.user.is_superuser:
        return HttpResponse("You cannot delete other user's posts!")

    post.delete()

    return redirect('all-posts')
