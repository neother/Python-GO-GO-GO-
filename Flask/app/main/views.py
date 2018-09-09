from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user

from . import main
from ..models import *
# from .forms import LoginForm, RegistrationForm
from app import db

from flask_login import logout_user, login_required, current_user
from ..email import send_email

from ..decorators import admin_required, permission_required

from .forms import *
from flask import current_app
#from flask_sqlalchemy import Pagination
#from flask_restful import request


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    # print(pagination.iter_pages())
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination)
    # show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        #user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    #form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id))
    comments = post.comments

    return render_template('post.html', posts=[post], form=form, comments=comments)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):

        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user.can(Permission.ADMIN):

        db.session.delete(post)
        db.session.commit()
        flash('The post has been deleted.')
    return redirect(url_for('main.index'))
    


@main.route('/disable/<int:id>')
@login_required
def disable(id):
    comment = Comment.query.get_or_404(id)
    if current_user.can(Permission.COMMENT):
        
        comment.disabled = True

        db.session.add(comment)

        db.session.commit()
       
        flash('The comment has been disable.')
    return redirect(url_for('main.post', id = comment.post_id))


@main.route('/enable/<int:id>')
@login_required
def enable(id):
    comment = Comment.query.get_or_404(id)
    if current_user.can(Permission.COMMENT):

        comment.disabled = False

        db.session.add(comment)

        db.session.commit()
       
        flash('The comment has been enable.')
    return redirect(url_for('main.post', id = comment.post_id))



@main.route('/aboutme')
def aboutme():
    form = AboutmeForm()
    return render_template('aboutme.html', form = form)
