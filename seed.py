"""
Seed script - populates the database with demo data so the project runs
and looks complete immediately after cloning.

Usage:
    python seed.py
"""
from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models import (User, EventType, Service, TeamMember, Booking, Payment,
                         AssignedTask, Gallery, Feedback)

app = create_app()

GALLERY_IMAGES = [
    "1519741497674-611481863552", "1464366400600-7168b8af9bc3", "1478146059778-26028b07395a",
    "1511578314322-379afb476865", "1527529482837-4698179dc6ce", "1414235077428-338989a2e8c0",
    "1469371670807-013ccf25f16a", "1543007630-9710e4a00a20",
]


def run():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ---------------- Users ----------------
        admin = User(name='Momenta Admin', email='admin@momenta.com', phone='9000000001',
                     address='Momenta HQ, Bengaluru', role='admin')
        admin.set_password('admin123')

        manager = User(name='Priya Sharma', email='manager@momenta.com', phone='9000000002',
                        address='Bengaluru', role='event_manager')
        manager.set_password('manager123')

        team_user = User(name='Arjun Rao', email='team@momenta.com', phone='9000000003',
                          address='Bengaluru', role='team_member')
        team_user.set_password('team123')

        client = User(name='Rahul Verma', email='client@momenta.com', phone='9000000004',
                       address='Indiranagar, Bengaluru', role='client')
        client.set_password('client123')

        db.session.add_all([admin, manager, team_user, client])
        db.session.commit()

        # ---------------- Team Members ----------------
        members = [
            TeamMember(user_id=team_user.user_id, name='Arjun Rao', role='Decoration', phone='9000000003'),
            TeamMember(name='Sunita Iyer', role='Catering', phone='9000000005'),
            TeamMember(name='Karan Mehta', role='Photography', phone='9000000006'),
            TeamMember(name='Divya Nair', role='Videography', phone='9000000007'),
            TeamMember(name='Rohan Das', role='Gift Management', phone='9000000008'),
            TeamMember(name='Anjali Gupta', role='Support Staff', phone='9000000009'),
        ]
        db.session.add_all(members)
        db.session.commit()

        # ---------------- Event Types ----------------
        events_data = [
            ('Marriage', 'Family Events', 'A grand wedding celebration tailored to your traditions.', 150000),
            ('House Warming', 'Family Events', 'Traditional Griha Pravesh ceremony setup.', 25000),
            ('Baby Naming Ceremony', 'Family Events', 'Warm, intimate naming ceremony decor & catering.', 20000),
            ('Baby Shower', 'Family Events', 'Elegant baby shower styling and treats.', 22000),
            ('Birthday Celebration', 'Family Events', 'Themed birthday parties for all ages.', 15000),
            ('Marriage Anniversary', 'Family Events', 'Romantic anniversary celebration setup.', 30000),
            ("Valentine's Day Celebration", 'Special Events', 'Intimate romantic setup for couples.', 12000),
            ('Engagement Ceremony', 'Special Events', 'Beautiful ring ceremony décor and coordination.', 45000),
            ('Retirement Party', 'Special Events', 'A memorable send-off celebration.', 18000),
            ('Graduation Party', 'Special Events', 'Celebrate academic milestones in style.', 16000),
            ('Product Launch', 'Corporate Events', 'Professional product launch event management.', 80000),
            ('Conferences', 'Corporate Events', 'Full-scale conference planning & logistics.', 100000),
            ('Seminars', 'Corporate Events', 'Seminar setup with AV and catering.', 35000),
            ('Team Events', 'Corporate Events', 'Team outings and offsite celebrations.', 28000),
            ('Custom Event Request', 'Custom Event', "Tell us your vision - we'll build a custom plan.", 0),
        ]
        event_objs = []
        for name, cat, desc, price in events_data:
            e = EventType(event_name=name, category=cat, description=desc, base_price=price)
            db.session.add(e)
            event_objs.append(e)
        db.session.commit()

        # ---------------- Services ----------------
        services_data = [
            ('Basic Decoration', 'Decoration', 'Basic', 8000, 'per event', 'Simple elegant decor for smaller gatherings.'),
            ('Premium Decoration', 'Decoration', 'Premium', 18000, 'per event', 'Themed decor with floral and lighting design.'),
            ('Luxury Decoration', 'Decoration', 'Luxury', 35000, 'per event', 'Grand luxury decor with premium florals & drapery.'),
            ('Vegetarian Menu', 'Catering', None, 450, 'per guest', 'Multi-cuisine vegetarian buffet.'),
            ('Non-Vegetarian Menu', 'Catering', None, 600, 'per guest', 'Multi-cuisine non-vegetarian buffet.'),
            ('Premium Buffet', 'Catering', 'Premium', 900, 'per guest', 'Premium live counters and dessert stations.'),
            ('Event Photography', 'Photography', None, 15000, 'per event', 'Professional event photography coverage.'),
            ('Album Creation', 'Photography', None, 6000, 'per event', 'Curated premium photo album.'),
            ('HD Coverage', 'Videography', None, 12000, 'per event', 'Full HD event videography.'),
            ('Cinematic Coverage', 'Videography', 'Premium', 25000, 'per event', 'Cinematic highlight film.'),
            ('Drone Coverage', 'Videography', 'Premium', 10000, 'per event', 'Aerial drone shots and video.'),
            ('DJ Services', 'Entertainment', None, 15000, 'per event', 'Professional DJ with sound & lighting.'),
            ('Live Music', 'Entertainment', None, 22000, 'per event', 'Live band / singer performance.'),
            ('Return Gifts', 'Gifts', None, 150, 'per guest', 'Curated return gifts for guests.'),
            ('Customized Gifts', 'Gifts', 'Premium', 350, 'per guest', 'Personalized custom gift hampers.'),
            ('Venue Suggestions', 'Venue', None, 0, 'per event', 'Curated venue shortlist based on your needs.'),
            ('Venue Booking Support', 'Venue', None, 5000, 'per event', 'End-to-end venue booking assistance.'),
        ]
        for name, cat, tier, price, unit, desc in services_data:
            db.session.add(Service(service_name=name, category=cat, tier=tier, price=price,
                                    unit=unit, description=desc))
        db.session.commit()

        # ---------------- Gallery ----------------
        for i, img in enumerate(GALLERY_IMAGES):
            db.session.add(Gallery(
                event_id=event_objs[i % len(event_objs)].event_id,
                title=event_objs[i % len(event_objs)].event_name,
                image_path=f"https://images.unsplash.com/photo-{img}?auto=format&fit=crop&w=600&q=70",
            ))
        db.session.commit()

        # ---------------- Sample completed booking with feedback ----------------
        wedding = next(e for e in event_objs if e.event_name == 'Marriage')
        deco = Service.query.filter_by(service_name='Premium Decoration').first()
        catering = Service.query.filter_by(service_name='Non-Vegetarian Menu').first()
        photo = Service.query.filter_by(service_name='Event Photography').first()

        past_booking = Booking(
            user_id=client.user_id, event_id=wedding.event_id,
            event_date=date.today() - timedelta(days=20), event_time='18:00',
            house_no='12', street='100 Feet Road', city='Bengaluru', state='Karnataka', pincode='560038',
            venue='Grand Palace Banquet Hall', guest_count=200,
            description='Traditional South Indian wedding with reception.',
            total_amount=deco.price + catering.price * 200 + photo.price + wedding.base_price,
            status='Completed', manager_id=manager.user_id, manager_stage='Event Completed',
        )
        past_booking.services = [deco, catering, photo]
        db.session.add(past_booking)
        db.session.commit()

        db.session.add(Payment(booking_id=past_booking.booking_id, amount=past_booking.total_amount,
                                method='UPI', transaction_id='MOMDEMO0001', payment_status='Success'))
        db.session.add(Feedback(user_id=client.user_id, booking_id=past_booking.booking_id,
                                 rating=5, comments='Momenta made our wedding absolutely magical! Highly recommend.'))

        # ---------------- Sample upcoming booking (in progress) ----------------
        birthday = next(e for e in event_objs if e.event_name == 'Birthday Celebration')
        basic_deco = Service.query.filter_by(service_name='Basic Decoration').first()
        dj = Service.query.filter_by(service_name='DJ Services').first()

        upcoming_booking = Booking(
            user_id=client.user_id, event_id=birthday.event_id,
            event_date=date.today() + timedelta(days=15), event_time='17:00',
            house_no='45', street='Koramangala 5th Block', city='Bengaluru', state='Karnataka', pincode='560095',
            venue='Client Residence', guest_count=40,
            description='Kids birthday party with cartoon theme.',
            total_amount=basic_deco.price + dj.price + birthday.base_price,
            status='In Progress', manager_id=manager.user_id, manager_stage='Decoration Started',
        )
        upcoming_booking.services = [basic_deco, dj]
        db.session.add(upcoming_booking)
        db.session.commit()

        db.session.add(Payment(booking_id=upcoming_booking.booking_id, amount=upcoming_booking.total_amount,
                                method='Credit Card', transaction_id='MOMDEMO0002', payment_status='Success'))

        deco_member = TeamMember.query.filter_by(role='Decoration').first()
        db.session.add(AssignedTask(booking_id=upcoming_booking.booking_id, member_id=deco_member.member_id,
                                     task_description='Set up cartoon-themed balloon decor', task_status='In Progress'))
        db.session.commit()

        print("Database seeded successfully!")
        print("--------------------------------------------------")
        print("Demo logins:")
        print("  Admin         -> admin@momenta.com / admin123")
        print("  Event Manager -> manager@momenta.com / manager123")
        print("  Team Member   -> team@momenta.com / team123")
        print("  Client        -> client@momenta.com / client123")
        print("--------------------------------------------------")


if __name__ == '__main__':
    run()
