"""ARKSpace Sample Data Seeder — Complete"""
import frappe
from datetime import datetime, timedelta, date
import random

def run():
    frappe.flags.ignore_validate = True
    print("\n🌱 ARKSpace Sample Data Seeder")
    print("=" * 50)

    TERRITORY = "All Territories"

    # ── 1. Branches (already created) ──
    print("\n📍 Branches...")
    branch_names = ["الرياض - الفرع الرئيسي", "جدة", "الدمام"]
    branches = []
    for bn in branch_names:
        if not frappe.db.exists("Branch", bn):
            doc = frappe.get_doc({"doctype": "Branch", "branch": bn})
            doc.insert(ignore_permissions=True)
            print(f"  ✅ {bn}")
        else:
            print(f"  ⏭️ {bn}")
        branches.append(bn)
    frappe.db.commit()

    # ── 2. Space Types (already created) ──
    print("\n🏷️ Space Types...")
    space_types = frappe.get_all("Space Type", pluck="name")
    print(f"  Found {len(space_types)}: {space_types}")

    # ── 3. Amenities (already created) ──
    print("\n🛎️ Amenities...")
    amenity_names = frappe.get_all("Amenity", pluck="name")
    print(f"  Found {len(amenity_names)}: {amenity_names}")

    # ── 4. Co-working Spaces (already created) ──
    print("\n🏢 Co-working Spaces...")
    space_names = frappe.get_all("Co-working Space", pluck="name")
    print(f"  Found {len(space_names)}")

    # ── 5. Customers (Members) ──
    print("\n👤 Creating Member Customers...")
    members_data = [
        {"customer_name": "أحمد الراشد", "customer_type": "Individual", "customer_group": "Individual", "territory": TERRITORY},
        {"customer_name": "سارة المنصور", "customer_type": "Individual", "customer_group": "Individual", "territory": TERRITORY},
        {"customer_name": "محمد العتيبي", "customer_type": "Individual", "customer_group": "Individual", "territory": TERRITORY},
        {"customer_name": "نورة الدوسري", "customer_type": "Individual", "customer_group": "Individual", "territory": TERRITORY},
        {"customer_name": "خالد الشمري", "customer_type": "Individual", "customer_group": "Individual", "territory": TERRITORY},
        {"customer_name": "شركة التقنية المتقدمة", "customer_type": "Company", "customer_group": "Commercial", "territory": TERRITORY},
        {"customer_name": "مؤسسة الإبداع الرقمي", "customer_type": "Company", "customer_group": "Commercial", "territory": TERRITORY},
        {"customer_name": "شركة النجاح للاستشارات", "customer_type": "Company", "customer_group": "Commercial", "territory": TERRITORY},
    ]
    member_names = []
    for md in members_data:
        existing = frappe.db.exists("Customer", {"customer_name": md["customer_name"]})
        if not existing:
            doc = frappe.get_doc({"doctype": "Customer", **md})
            doc.insert(ignore_permissions=True)
            member_names.append(doc.name)
            print(f"  ✅ {md['customer_name']} ({doc.name})")
        else:
            member_names.append(existing)
            print(f"  ⏭️ {md['customer_name']}")
    frappe.db.commit()

    # ── 6. Membership Plans ──
    print("\n📋 Creating Membership Plans...")
    plans_data = [
        {"plan_name": "Basic Hot Desk", "plan_name_ar": "المكتب المشترك الأساسي", "plan_type": "Hot Desk", "space_type": "Hot Desk", "monthly_price": 1500, "quarterly_price": 4000, "yearly_price": 15000, "included_hours": 160, "included_credits": 50, "max_guests": 2, "meeting_room_hours": 4, "printing_pages": 100},
        {"plan_name": "Premium Hot Desk", "plan_name_ar": "المكتب المشترك المميز", "plan_type": "Hot Desk", "space_type": "Hot Desk", "monthly_price": 2500, "quarterly_price": 7000, "yearly_price": 25000, "included_hours": 0, "included_credits": 100, "max_guests": 5, "meeting_room_hours": 8, "printing_pages": 300},
        {"plan_name": "Dedicated Desk", "plan_name_ar": "المكتب المخصص", "plan_type": "Dedicated Desk", "space_type": "Dedicated Desk", "monthly_price": 3500, "quarterly_price": 9500, "yearly_price": 36000, "included_hours": 0, "included_credits": 150, "max_guests": 3, "meeting_room_hours": 10, "printing_pages": 500, "storage_gb": 5},
        {"plan_name": "Private Office - Small", "plan_name_ar": "المكتب الخاص - صغير", "plan_type": "Private Office", "space_type": "Private Office", "monthly_price": 8000, "quarterly_price": 22000, "yearly_price": 84000, "included_hours": 0, "included_credits": 200, "max_guests": 5, "meeting_room_hours": 20, "printing_pages": 1000, "storage_gb": 20},
        {"plan_name": "Private Office - Large", "plan_name_ar": "المكتب الخاص - كبير", "plan_type": "Private Office", "space_type": "Private Office", "monthly_price": 12000, "quarterly_price": 33000, "yearly_price": 130000, "included_hours": 0, "included_credits": 500, "max_guests": 10, "meeting_room_hours": 40, "printing_pages": 2000, "storage_gb": 50},
        {"plan_name": "Virtual Office", "plan_name_ar": "المكتب الافتراضي", "plan_type": "Virtual Office", "space_type": "Virtual Office", "monthly_price": 500, "quarterly_price": 1400, "yearly_price": 5000, "included_hours": 0, "included_credits": 20, "max_guests": 0, "meeting_room_hours": 2, "printing_pages": 0},
    ]
    plan_names = []
    for pd_item in plans_data:
        existing = frappe.db.exists("Membership Plan", {"plan_name": pd_item["plan_name"]})
        if not existing:
            doc = frappe.get_doc({"doctype": "Membership Plan", "is_active": 1, **pd_item})
            doc.insert(ignore_permissions=True)
            plan_names.append(doc.name)
            print(f"  ✅ {pd_item['plan_name']} ({doc.name})")
        else:
            plan_names.append(existing)
            print(f"  ⏭️ {pd_item['plan_name']}")
    frappe.db.commit()

    # ── 7. Memberships ──
    print("\n🎫 Creating Memberships...")
    today = date.today()
    membership_configs = [
        {"member_idx": 0, "plan_idx": 0, "billing_cycle": "Monthly", "start_offset": -60, "end_offset": -30, "status": "Expired"},
        {"member_idx": 0, "plan_idx": 1, "billing_cycle": "Monthly", "start_offset": -15, "end_offset": 15, "status": "Active"},
        {"member_idx": 1, "plan_idx": 2, "billing_cycle": "Quarterly", "start_offset": -30, "end_offset": 60, "status": "Active"},
        {"member_idx": 2, "plan_idx": 3, "billing_cycle": "Monthly", "start_offset": -10, "end_offset": 20, "status": "Active"},
        {"member_idx": 3, "plan_idx": 0, "billing_cycle": "Monthly", "start_offset": -45, "end_offset": -15, "status": "Expired"},
        {"member_idx": 4, "plan_idx": 4, "billing_cycle": "Yearly", "start_offset": -180, "end_offset": 185, "status": "Active"},
        {"member_idx": 5, "plan_idx": 3, "billing_cycle": "Monthly", "start_offset": -5, "end_offset": 25, "status": "Active"},
        {"member_idx": 6, "plan_idx": 5, "billing_cycle": "Monthly", "start_offset": -20, "end_offset": 10, "status": "Active"},
        {"member_idx": 7, "plan_idx": 1, "billing_cycle": "Quarterly", "start_offset": -50, "end_offset": 40, "status": "Active"},
    ]
    membership_names = []
    existing_count = frappe.db.count("Membership")
    if existing_count == 0:
        for mc in membership_configs:
            plan_doc = frappe.get_doc("Membership Plan", plan_names[mc["plan_idx"]])
            rate = plan_doc.monthly_price
            if mc["billing_cycle"] == "Quarterly" and plan_doc.quarterly_price:
                rate = plan_doc.quarterly_price
            elif mc["billing_cycle"] == "Yearly" and plan_doc.yearly_price:
                rate = plan_doc.yearly_price

            space_idx = mc["member_idx"] % len(space_names) if space_names else None
            doc = frappe.get_doc({
                "doctype": "Membership",
                "member": member_names[mc["member_idx"]],
                "membership_plan": plan_names[mc["plan_idx"]],
                "billing_cycle": mc["billing_cycle"],
                "start_date": today + timedelta(days=mc["start_offset"]),
                "end_date": today + timedelta(days=mc["end_offset"]),
                "status": mc["status"],
                "rate": rate,
                "auto_renew": 1 if mc["status"] == "Active" else 0,
                "branch": branches[mc["member_idx"] % len(branches)],
                "assigned_space": space_names[space_idx] if space_idx is not None else None,
            })
            doc.insert(ignore_permissions=True)
            # Submit active ones
            if mc["status"] == "Active":
                doc.submit()
            membership_names.append(doc.name)
            print(f"  ✅ {doc.name} - {doc.member_name or member_names[mc['member_idx']]} ({mc['status']})")
    else:
        membership_names = frappe.get_all("Membership", pluck="name")
        print(f"  ⏭️ {len(membership_names)} memberships already exist")
    frappe.db.commit()

    # ── 8. Space Bookings ──
    print("\n📅 Creating Space Bookings...")
    existing_bookings = frappe.db.count("Space Booking")
    booking_names = []
    if existing_bookings == 0:
        # Create bookings across different spaces, members, and dates
        booking_configs = [
            # Past bookings (checked out)
            {"member_idx": 0, "space_idx": 5, "type": "Hourly", "day_offset": -10, "hour": 9, "duration": 2, "rate": 200, "status": "Checked Out"},
            {"member_idx": 1, "space_idx": 5, "type": "Hourly", "day_offset": -8, "hour": 14, "duration": 3, "rate": 200, "status": "Checked Out"},
            {"member_idx": 2, "space_idx": 6, "type": "Hourly", "day_offset": -7, "hour": 10, "duration": 1, "rate": 150, "status": "Checked Out"},
            {"member_idx": 3, "space_idx": 0, "type": "Daily", "day_offset": -5, "hour": 8, "duration": 10, "rate": 150, "status": "Checked Out"},
            {"member_idx": 4, "space_idx": 7, "type": "Hourly", "day_offset": -3, "hour": 16, "duration": 4, "rate": 500, "status": "Checked Out"},
            # Today
            {"member_idx": 0, "space_idx": 0, "type": "Daily", "day_offset": 0, "hour": 8, "duration": 10, "rate": 150, "status": "Checked In"},
            {"member_idx": 5, "space_idx": 5, "type": "Hourly", "day_offset": 0, "hour": 11, "duration": 2, "rate": 200, "status": "Confirmed"},
            # Future bookings
            {"member_idx": 1, "space_idx": 5, "type": "Hourly", "day_offset": 1, "hour": 9, "duration": 3, "rate": 200, "status": "Confirmed"},
            {"member_idx": 6, "space_idx": 6, "type": "Hourly", "day_offset": 2, "hour": 14, "duration": 2, "rate": 150, "status": "Pending"},
            {"member_idx": 7, "space_idx": 7, "type": "Hourly", "day_offset": 3, "hour": 10, "duration": 5, "rate": 500, "status": "Confirmed"},
            {"member_idx": 2, "space_idx": 0, "type": "Daily", "day_offset": 5, "hour": 8, "duration": 10, "rate": 150, "status": "Pending"},
            {"member_idx": 3, "space_idx": 10, "type": "Hourly", "day_offset": 7, "hour": 13, "duration": 2, "rate": 180, "status": "Pending"},
            # Cancelled / No Show
            {"member_idx": 4, "space_idx": 5, "type": "Hourly", "day_offset": -2, "hour": 9, "duration": 1, "rate": 200, "status": "Cancelled"},
            {"member_idx": 3, "space_idx": 0, "type": "Daily", "day_offset": -1, "hour": 8, "duration": 10, "rate": 150, "status": "No Show"},
        ]
        for bc in booking_configs:
            if bc["space_idx"] >= len(space_names):
                continue
            start = datetime.combine(today + timedelta(days=bc["day_offset"]), datetime.min.time().replace(hour=bc["hour"]))
            end = start + timedelta(hours=bc["duration"])
            doc = frappe.get_doc({
                "doctype": "Space Booking",
                "space": space_names[bc["space_idx"]],
                "member": member_names[bc["member_idx"]],
                "booking_type": bc["type"],
                "start_datetime": start,
                "end_datetime": end,
                "rate": bc["rate"],
                "total_amount": bc["rate"] * (bc["duration"] if bc["type"] == "Hourly" else 1),
                "net_amount": bc["rate"] * (bc["duration"] if bc["type"] == "Hourly" else 1),
                "status": bc["status"],
            })
            if bc["status"] == "Checked In":
                doc.checked_in_at = start
            elif bc["status"] == "Checked Out":
                doc.checked_in_at = start
                doc.checked_out_at = end
            doc.insert(ignore_permissions=True)
            # Submit completed bookings
            if bc["status"] in ("Checked Out", "Confirmed", "Checked In"):
                doc.submit()
            booking_names.append(doc.name)
            print(f"  ✅ {doc.name} - {bc['type']} at space {bc['space_idx']} ({bc['status']})")
    else:
        booking_names = frappe.get_all("Space Booking", pluck="name")
        print(f"  ⏭️ {len(booking_names)} bookings already exist")
    frappe.db.commit()

    # ── 9. Workspace Leads (CRM) ──
    print("\n📞 Creating Workspace Leads...")
    existing_leads = frappe.db.count("Workspace Lead")
    lead_names = []
    if existing_leads == 0:
        leads_data = [
            {"lead_name": "فهد القحطاني", "email": "fahad@example.com", "phone": "+966501234567", "company_name": "شركة الأفق", "source": "Website", "status": "New", "interested_plan": plan_names[0], "team_size": 3, "budget_monthly": 5000, "branch": branches[0]},
            {"lead_name": "ريم السبيعي", "email": "reem@example.com", "phone": "+966502345678", "source": "Referral", "status": "Contacted", "interested_plan": plan_names[2], "team_size": 1, "budget_monthly": 4000, "branch": branches[0]},
            {"lead_name": "عبدالله الحربي", "email": "abdullah@example.com", "phone": "+966503456789", "company_name": "مجموعة الابتكار", "source": "Walk In", "status": "Tour Scheduled", "interested_plan": plan_names[3], "team_size": 6, "budget_monthly": 10000, "branch": branches[0]},
            {"lead_name": "هند العمري", "email": "hind@example.com", "phone": "+966504567890", "source": "Social Media", "status": "Negotiating", "interested_plan": plan_names[4], "team_size": 10, "budget_monthly": 15000, "branch": branches[1]},
            {"lead_name": "ماجد الغامدي", "email": "majed@example.com", "phone": "+966505678901", "company_name": "شركة الرؤية", "source": "Event", "status": "Converted", "interested_plan": plan_names[1], "team_size": 2, "budget_monthly": 3000, "branch": branches[1], "converted_customer": member_names[5]},
            {"lead_name": "لمياء العنزي", "email": "lamia@example.com", "phone": "+966506789012", "source": "Partner", "status": "Lost", "interested_plan": plan_names[5], "team_size": 1, "budget_monthly": 1000, "branch": branches[2]},
            {"lead_name": "تركي المطيري", "email": "turki@example.com", "phone": "+966507890123", "source": "Website", "status": "New", "interested_plan": plan_names[0], "team_size": 4, "budget_monthly": 6000, "branch": branches[2]},
        ]
        for ld in leads_data:
            doc = frappe.get_doc({"doctype": "Workspace Lead", **ld})
            doc.insert(ignore_permissions=True)
            lead_names.append(doc.name)
            print(f"  ✅ {doc.name} - {ld['lead_name']} ({ld['status']})")
    else:
        lead_names = frappe.get_all("Workspace Lead", pluck="name")
        print(f"  ⏭️ {len(lead_names)} leads already exist")
    frappe.db.commit()

    # ── 10. Workspace Tours ──
    print("\n🚶 Creating Workspace Tours...")
    existing_tours = frappe.db.count("Workspace Tour")
    if existing_tours == 0 and lead_names:
        tours_data = [
            {"lead": lead_names[2], "branch": branches[0], "scheduled_date": today + timedelta(days=1), "scheduled_time": "10:00:00", "status": "Scheduled", "duration_minutes": 45},
            {"lead": lead_names[3], "branch": branches[1], "scheduled_date": today - timedelta(days=3), "scheduled_time": "14:00:00", "status": "Completed", "duration_minutes": 60, "interest_level": 1, "outcome": "Interested"},
            {"lead": lead_names[4], "branch": branches[1], "scheduled_date": today - timedelta(days=10), "scheduled_time": "11:00:00", "status": "Completed", "duration_minutes": 30, "outcome": "Converted"},
            {"lead": lead_names[5], "branch": branches[2], "scheduled_date": today - timedelta(days=5), "scheduled_time": "09:00:00", "status": "No Show", "duration_minutes": 30},
        ]
        for td_item in tours_data:
            doc = frappe.get_doc({"doctype": "Workspace Tour", **td_item})
            doc.insert(ignore_permissions=True)
            print(f"  ✅ {doc.name} - {td_item['status']}")
    else:
        print(f"  ⏭️ Tours already exist or no leads")
    frappe.db.commit()

    # ── 11. Training Data ──
    print("\n🎓 Creating Training Data...")
    
    # Training Modules
    training_modules_data = [
        {"module_name": "مقدمة في العمل المشترك", "category": "Onboarding", "level": "Beginner", "status": "Published", "duration_hours": 2, "instructor": "أ. سلمان الأحمد", "description": "تعرف على أساسيات بيئة العمل المشترك وكيفية الاستفادة القصوى من المساحة"},
        {"module_name": "ريادة الأعمال للمبتدئين", "category": "Business", "level": "Beginner", "status": "Published", "duration_hours": 8, "instructor": "د. منال العتيبي", "description": "دورة شاملة في أساسيات ريادة الأعمال"},
        {"module_name": "التسويق الرقمي المتقدم", "category": "Business", "level": "Advanced", "status": "Published", "duration_hours": 12, "instructor": "أ. نايف الشهري", "description": "استراتيجيات التسويق الرقمي المتقدمة"},
        {"module_name": "البرمجة بلغة Python", "category": "Technical", "level": "Intermediate", "status": "Published", "duration_hours": 20, "instructor": "م. ياسر الدوسري", "description": "تعلم البرمجة بلغة بايثون من الصفر"},
        {"module_name": "التصميم الإبداعي", "category": "Creative", "level": "Beginner", "status": "Published", "duration_hours": 6, "instructor": "أ. لينا الحربي", "description": "أساسيات التصميم الجرافيكي والإبداعي"},
        {"module_name": "إدارة المشاريع الاحترافية", "category": "Business", "level": "Advanced", "status": "Draft", "duration_hours": 15, "instructor": "م. بدر الراشد"},
    ]
    tm_names = []
    for tm in training_modules_data:
        if not frappe.db.exists("Training Module", tm["module_name"]):
            doc = frappe.get_doc({"doctype": "Training Module", **tm})
            doc.insert(ignore_permissions=True)
            print(f"  ✅ Module: {tm['module_name']}")
        else:
            print(f"  ⏭️ Module: {tm['module_name']}")
        tm_names.append(tm["module_name"])
    frappe.db.commit()

    # Training Badges
    badges_data = [
        {"badge_name": "مرحبا بك", "badge_code": "WELCOME", "category": "Completion", "level": "Bronze", "points": 10, "description": "أكمل دورة التعريف بالمساحة", "icon": "fa-solid fa-hand-wave"},
        {"badge_name": "رائد أعمال مبتدئ", "badge_code": "ENTREPRENEUR_1", "category": "Completion", "level": "Silver", "points": 25, "description": "أكمل دورة ريادة الأعمال", "icon": "fa-solid fa-rocket"},
        {"badge_name": "المسوق الرقمي", "badge_code": "DIGITAL_MARKETER", "category": "Mastery", "level": "Gold", "points": 50, "description": "أتقن التسويق الرقمي", "icon": "fa-solid fa-bullhorn"},
        {"badge_name": "مبرمج بايثون", "badge_code": "PYTHON_DEV", "category": "Mastery", "level": "Gold", "points": 75, "description": "أتقن البرمجة بلغة بايثون", "icon": "fa-solid fa-code"},
        {"badge_name": "نجم المجتمع", "badge_code": "COMMUNITY_STAR", "category": "Community", "level": "Platinum", "points": 100, "description": "شارك في 10 فعاليات مجتمعية", "icon": "fa-solid fa-star"},
        {"badge_name": "حضور مثالي", "badge_code": "PERFECT_ATTENDANCE", "category": "Streak", "level": "Silver", "points": 30, "description": "حضور 30 يوم متتالي", "icon": "fa-solid fa-calendar-check"},
    ]
    badge_names = []
    for bd in badges_data:
        if not frappe.db.exists("Training Badge", bd["badge_name"]):
            doc = frappe.get_doc({"doctype": "Training Badge", "is_active": 1, **bd})
            doc.insert(ignore_permissions=True)
            print(f"  ✅ Badge: {bd['badge_name']}")
        else:
            print(f"  ⏭️ Badge: {bd['badge_name']}")
        badge_names.append(bd["badge_name"])
    frappe.db.commit()

    # Training Sessions
    existing_sessions = frappe.db.count("Training Session")
    session_names = []
    if existing_sessions == 0:
        sessions_data = [
            {"title": "جلسة تعريفية - الدفعة 5", "training_module": tm_names[0], "session_date": today - timedelta(days=7), "start_time": "10:00:00", "end_time": "12:00:00", "status": "Completed", "branch": branches[0], "space": space_names[5] if len(space_names) > 5 else None, "max_participants": 15, "is_free": 1},
            {"title": "ريادة الأعمال - الحلقة 1", "training_module": tm_names[1], "session_date": today - timedelta(days=3), "start_time": "14:00:00", "end_time": "16:00:00", "status": "Completed", "branch": branches[0], "space": space_names[5] if len(space_names) > 5 else None, "max_participants": 20, "is_free": 0, "fee_amount": 200},
            {"title": "ورشة التسويق الرقمي", "training_module": tm_names[2], "session_date": today + timedelta(days=2), "start_time": "09:00:00", "end_time": "13:00:00", "status": "Scheduled", "branch": branches[0], "space": space_names[7] if len(space_names) > 7 else None, "max_participants": 30, "is_free": 0, "fee_amount": 500},
            {"title": "بايثون للمبتدئين - الحلقة 1", "training_module": tm_names[3], "session_date": today + timedelta(days=5), "start_time": "18:00:00", "end_time": "20:00:00", "status": "Scheduled", "branch": branches[0], "max_participants": 25, "is_online": 1, "meeting_url": "https://meet.arkspace.sa/python-101", "is_free": 1},
            {"title": "التصميم الإبداعي - جلسة جدة", "training_module": tm_names[4], "session_date": today + timedelta(days=10), "start_time": "11:00:00", "end_time": "14:00:00", "status": "Scheduled", "branch": branches[1], "max_participants": 15, "is_free": 0, "fee_amount": 300},
        ]
        for sd in sessions_data:
            doc = frappe.get_doc({"doctype": "Training Session", **sd})
            doc.insert(ignore_permissions=True)
            if sd["status"] == "Completed":
                doc.submit()
            session_names.append(doc.name)
            print(f"  ✅ Session: {sd['title']} ({sd['status']})")
    else:
        session_names = frappe.get_all("Training Session", pluck="name")
        print(f"  ⏭️ {len(session_names)} sessions already exist")
    frappe.db.commit()

    # ── Summary ──
    print("\n" + "=" * 50)
    print("🎉 ARKSpace Sample Data Seeding Complete!")
    print("=" * 50)
    counts = {
        "Branches": frappe.db.count("Branch"),
        "Space Types": frappe.db.count("Space Type"),
        "Amenities": frappe.db.count("Amenity"),
        "Co-working Spaces": frappe.db.count("Co-working Space"),
        "Customers (Members)": frappe.db.count("Customer"),
        "Membership Plans": frappe.db.count("Membership Plan"),
        "Memberships": frappe.db.count("Membership"),
        "Space Bookings": frappe.db.count("Space Booking"),
        "Workspace Leads": frappe.db.count("Workspace Lead"),
        "Workspace Tours": frappe.db.count("Workspace Tour"),
        "Training Modules": frappe.db.count("Training Module"),
        "Training Badges": frappe.db.count("Training Badge"),
        "Training Sessions": frappe.db.count("Training Session"),
    }
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    run()
