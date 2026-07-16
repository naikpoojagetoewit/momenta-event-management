from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.extensions import db
from app.models import EventType, Service, Gallery, Feedback, ContactMessage, User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    events = EventType.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).limit(9).all()
    gallery_images = Gallery.query.order_by(Gallery.created_at.desc()).limit(8).all()
    testimonials = (Feedback.query.filter(Feedback.rating >= 4)
                     .order_by(Feedback.created_at.desc()).limit(6).all())
    return render_template('home.html', events=events, services=services,
                            gallery_images=gallery_images, testimonials=testimonials)


@main_bp.route('/events')
def events():
    category = request.args.get('category')
    query = EventType.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    events_list = query.all()
    categories = ['Family Events', 'Special Events', 'Corporate Events', 'Custom Event']
    return render_template('events.html', events=events_list, categories=categories,
                            active_category=category)


@main_bp.route('/gallery')
def gallery():
    images = Gallery.query.order_by(Gallery.created_at.desc()).all()
    return render_template('gallery.html', images=images)


@main_bp.route('/services')
def services():
    services_list = Service.query.filter_by(is_active=True).all()
    grouped = {}
    for s in services_list:
        grouped.setdefault(s.category, []).append(s)
    return render_template('services.html', grouped=grouped)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        msg = ContactMessage(
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message'),
        )
        db.session.add(msg)
        db.session.commit()
        flash('Thanks for reaching out! Our team will contact you shortly.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html')


@main_bp.route('/about')
def about():
    return render_template('about.html')
