from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')
    # roles: client, admin, event_manager, team_member
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active_account = db.Column(db.Boolean, default=True)

    bookings = db.relationship('Booking', backref='client', lazy=True,
                                foreign_keys='Booking.user_id')
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    team_profile = db.relationship('TeamMember', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_event_manager(self):
        return self.role == 'event_manager'

    @property
    def is_team_member(self):
        return self.role == 'team_member'


class EventType(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False)  # Family/Special/Corporate/Custom
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, default=0.0)
    image_path = db.Column(db.String(255), default='img/event-default.jpg')
    is_active = db.Column(db.Boolean, default=True)

    bookings = db.relationship('Booking', backref='event_type', lazy=True)


class Service(db.Model):
    __tablename__ = 'services'

    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    # Decoration, Catering, Photography, Videography, Entertainment, Gifts, Venue
    tier = db.Column(db.String(60))  # e.g. Basic/Premium/Luxury
    price = db.Column(db.Float, nullable=False, default=0.0)
    unit = db.Column(db.String(30), default='per event')  # per event / per guest
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)


booking_services = db.Table(
    'booking_services_assoc',
    db.Column('booking_id', db.Integer, db.ForeignKey('bookings.booking_id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('services.service_id'), primary_key=True),
)


class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)

    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.String(20))
    house_no = db.Column(db.String(60))
    street = db.Column(db.String(120))
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    pincode = db.Column(db.String(10))
    venue = db.Column(db.String(255))
    guest_count = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='Pending')
    # Pending, Approved, Rejected, Assigned, In Progress, Completed
    manager_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    manager_stage = db.Column(db.String(40), default='Planning')
    # Planning, Decoration Started, Catering Ready, Photography Scheduled, Event Completed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    services = db.relationship('Service', secondary=booking_services, lazy='subquery',
                                backref=db.backref('bookings', lazy=True))
    payments = db.relationship('Payment', backref='booking', lazy=True)
    tasks = db.relationship('AssignedTask', backref='booking', lazy=True)
    feedback = db.relationship('Feedback', backref='booking', uselist=False)

    manager = db.relationship('User', foreign_keys=[manager_id])


class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(30))  # UPI, Credit Card, Debit Card, Net Banking
    transaction_id = db.Column(db.String(100), unique=True)
    payment_status = db.Column(db.String(30), default='Pending')  # Pending, Success, Failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TeamMember(db.Model):
    __tablename__ = 'team_members'

    member_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True, nullable=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(60), nullable=False)
    # Decoration, Catering, Photography, Videography, Gift Management, Support Staff
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)

    tasks = db.relationship('AssignedTask', backref='member', lazy=True)


class AssignedTask(db.Model):
    __tablename__ = 'assigned_tasks'

    task_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('team_members.member_id'), nullable=False)
    task_description = db.Column(db.String(255))
    task_status = db.Column(db.String(30), default='Assigned')
    # Assigned, In Progress, Completed
    file_path = db.Column(db.String(255))  # uploaded photo/video proof
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Gallery(db.Model):
    __tablename__ = 'gallery'

    image_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=True)
    title = db.Column(db.String(120))
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Feedback(db.Model):
    __tablename__ = 'feedback'

    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(150))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
