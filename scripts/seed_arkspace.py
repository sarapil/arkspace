"""ARKSpace Sample Data Seeder"""
import frappe
from datetime import datetime, timedelta, date
import random

def run():
    print("\n🌱 ARKSpace Sample Data Seeder")
    print("=" * 50)

    # ── 1. Branches ──
    print("\n📍 Creating Branches...")
    branch_names = ["الإسكندرية - الفرع الرئيسي", "القاهرة", "الجيزة"]
    branches = []
    for bn in branch_names:
        if not frappe.db.exists("Branch", bn):
            doc = frappe.get_doc({"doctype": "Branch", "branch": bn})
            doc.insert(ignore_permissions=True)
            print(f"  ✅ {bn}")
        else:
            print(f"  ⏭️ {bn} exists")
        branches.append(bn)
    frappe.db.commit()

    # ── 2. Space Types ──
    print("\n🏷️ Creating Space Types...")
    space_types_data = [
        {"type_name": "Hot Desk", "type_name_ar": "مكتب مشترك", "icon": "fa-solid fa-chair", "color": "#3B82F6", "default_capacity": 1, "hourly_booking": 1, "daily_booking": 1, "monthly_booking": 1},
        {"type_name": "Dedicated Desk", "type_name_ar": "مكتب مخصص", "icon": "fa-solid fa-desktop", "color": "#8B5CF6", "default_capacity": 1, "hourly_booking": 0, "daily_booking": 1, "monthly_booking": 1},
        {"type_name": "Private Office", "type_name_ar": "مكتب خاص", "icon": "fa-solid fa-door-closed", "color": "#059669", "default_capacity": 4, "hourly_booking": 0, "daily_booking": 1, "monthly_booking": 1},
        {"type_name": "Meeting Room", "type_name_ar": "قاعة اجتماعات", "icon": "fa-solid fa-users", "color": "#DC2626", "default_capacity": 10, "hourly_booking": 1, "daily_booking": 1, "monthly_booking": 0},
        {"type_name": "Event Space", "type_name_ar": "قاعة فعاليات", "icon": "fa-solid fa-calendar-star", "color": "#D97706", "default_capacity": 50, "hourly_booking": 1, "daily_booking": 1, "monthly_booking": 0},
        {"type_name": "Virtual Office", "type_name_ar": "مكتب افتراضي", "icon": "fa-solid fa-globe", "color": "#6366F1", "default_capacity": 0, "hourly_booking": 0, "daily_booking": 0, "monthly_booking": 1},
    ]
    space_types = []
    for st in space_types_data:
        if not frappe.db.exists("Space Type", st["type_name"]):
            doc = frappe.get_doc({"doctype": "Space Type", **st})
            doc.insert(ignore_permissions=True)
            print(f"  ✅ {st['type_name']}")
        else:
            print(f"  ⏭️ {st['type_name']} exists")
        space_types.append(st["type_name"])
    frappe.db.commit()

    # ── 3. Amenities ──
    print("\n🛎️ Creating Amenities...")
    amenities_data = [
        {"amenity_name": "WiFi", "amenity_name_ar": "واي فاي", "icon": "fa-solid fa-wifi"},
        {"amenity_name": "Printer", "amenity_name_ar": "طابعة", "icon": "fa-solid fa-print"},
        {"amenity_name": "Kitchen", "amenity_name_ar": "مطبخ", "icon": "fa-solid fa-utensils"},
        {"amenity_name": "Parking", "amenity_name_ar": "موقف سيارات", "icon": "fa-solid fa-square-parking"},
        {"amenity_name": "Projector", "amenity_name_ar": "بروجكتر", "icon": "fa-solid fa-chalkboard"},
        {"amenity_name": "Whiteboard", "amenity_name_ar": "سبورة", "icon": "fa-solid fa-chalkboard-user"},
        {"amenity_name": "Locker", "amenity_name_ar": "خزانة", "icon": "fa-solid fa-lock"},
        {"amenity_name": "Coffee Bar", "amenity_name_ar": "ركن القهوة", "icon": "fa-solid fa-mug-hot"},
        {"amenity_name": "Phone Booth", "amenity_name_ar": "كابينة هاتف", "icon": "fa-solid fa-phone"},
        {"amenity_name": "Standing Desk", "amenity_name_ar": "مكتب واقف", "icon": "fa-solid fa-arrow-up"},
    ]
    amenity_names = []
    for am in amenities_data:
        if not frappe.db.exists("Amenity", am["amenity_name"]):
            doc = frappe.get_doc({"doctype": "Amenity", **am})
            doc.insert(ignore_permissions=True)
            print(f"  ✅ {am['amenity_name']}")
        else:
            print(f"  ⏭️ {am['amenity_name']} exists")
        amenity_names.append(am["amenity_name"])
    frappe.db.commit()

    # ── 4. Co-working Spaces ──
    print("\n🏢 Creating Co-working Spaces...")
    spaces_data = [
        # Alexandria Branch (سموحة - ستانلي - المندرة)
        {"space_name": "سموحة - المنطقة المفتوحة أ", "space_name_ar": "المنطقة المفتوحة أ - سموحة", "space_type": "Hot Desk", "branch": branches[0], "floor": "1", "capacity": 20, "area_sqm": 200, "hourly_rate": 25, "daily_rate": 150, "monthly_rate": 2000, "status": "Available", "amenities": ["WiFi", "Printer", "Coffee Bar", "Kitchen"]},
        {"space_name": "سموحة - المنطقة المفتوحة ب", "space_name_ar": "المنطقة المفتوحة ب - سموحة", "space_type": "Hot Desk", "branch": branches[0], "floor": "1", "capacity": 15, "area_sqm": 150, "hourly_rate": 30, "daily_rate": 180, "monthly_rate": 2500, "status": "Available", "amenities": ["WiFi", "Coffee Bar", "Standing Desk"]},
        {"space_name": "ستانلي - مكاتب مخصصة", "space_name_ar": "منطقة مخصصة - ستانلي", "space_type": "Dedicated Desk", "branch": branches[0], "floor": "2", "capacity": 10, "area_sqm": 100, "hourly_rate": 0, "daily_rate": 200, "monthly_rate": 3500, "status": "Available", "amenities": ["WiFi", "Printer", "Locker", "Coffee Bar"]},
        {"space_name": "ستانلي - مكتب خاص 101", "space_name_ar": "مكتب خاص 101 - ستانلي", "space_type": "Private Office", "branch": branches[0], "floor": "2", "capacity": 4, "area_sqm": 30, "hourly_rate": 0, "daily_rate": 500, "monthly_rate": 8000, "status": "Occupied", "amenities": ["WiFi", "Printer", "Locker", "Phone Booth"]},
        {"space_name": "ستانلي - مكتب خاص 102", "space_name_ar": "مكتب خاص 102 - ستانلي", "space_type": "Private Office", "branch": branches[0], "floor": "2", "capacity": 6, "area_sqm": 45, "hourly_rate": 0, "daily_rate": 700, "monthly_rate": 12000, "status": "Available", "amenities": ["WiFi", "Printer", "Whiteboard"]},
        {"space_name": "المندرة - قاعة اجتماعات", "space_name_ar": "قاعة اجتماعات المندرة", "space_type": "Meeting Room", "branch": branches[0], "floor": "3", "capacity": 12, "area_sqm": 40, "hourly_rate": 200, "daily_rate": 1200, "monthly_rate": 0, "status": "Available", "amenities": ["WiFi", "Projector", "Whiteboard", "Coffee Bar"]},
        {"space_name": "سموحة - قاعة اجتماعات", "space_name_ar": "قاعة اجتماعات سموحة", "space_type": "Meeting Room", "branch": branches[0], "floor": "3", "capacity": 8, "area_sqm": 25, "hourly_rate": 150, "daily_rate": 900, "monthly_rate": 0, "status": "Available", "amenities": ["WiFi", "Projector", "Whiteboard"]},
        {"space_name": "سموحة - قاعة الفعاليات", "space_name_ar": "قاعة الفعاليات - سموحة", "space_type": "Event Space", "branch": branches[0], "floor": "Ground", "capacity": 80, "area_sqm": 300, "hourly_rate": 500, "daily_rate": 3000, "monthly_rate": 0, "status": "Available", "amenities": ["WiFi", "Projector", "Parking"]},
        # Cairo Branch (مدينة نصر - المعادي - التجمع الخامس)
        {"space_name": "مدينة نصر - مكاتب مشتركة", "space_name_ar": "مكاتب مشتركة مدينة نصر", "space_type": "Hot Desk", "branch": branches[1], "floor": "1", "capacity": 25, "area_sqm": 250, "hourly_rate": 20, "daily_rate": 120, "monthly_rate": 1800, "status": "Available", "amenities": ["WiFi", "Kitchen", "Coffee Bar"]},
        {"space_name": "المعادي - مكتب خاص", "space_name_ar": "مكتب خاص المعادي", "space_type": "Private Office", "branch": branches[1], "floor": "2", "capacity": 5, "area_sqm": 35, "hourly_rate": 0, "daily_rate": 450, "monthly_rate": 7000, "status": "Available", "amenities": ["WiFi", "Printer", "Locker"]},
        {"space_name": "التجمع الخامس - قاعة اجتماعات", "space_name_ar": "قاعة اجتماعات التجمع الخامس", "space_type": "Meeting Room", "branch": branches[1], "floor": "2", "capacity": 10, "area_sqm": 30, "hourly_rate": 180, "daily_rate": 1000, "monthly_rate": 0, "status": "Available", "amenities": ["WiFi", "Projector", "Whiteboard"]},
        # Giza Branch (الدقي - المهندسين)
        {"space_name": "الدقي - مكاتب مشتركة", "space_name_ar": "مكاتب مشتركة الدقي", "space_type": "Hot Desk", "branch": branches[2], "floor": "1", "capacity": 18, "area_sqm": 180, "hourly_rate": 20, "daily_rate": 100, "monthly_rate": 1500, "status": "Available", "amenities": ["WiFi", "Kitchen", "Parking"]},
        {"space_name": "المهندسين - جناح خاص", "space_name_ar": "جناح خاص المهندسين", "space_type": "Private Office", "branch": branches[2], "floor": "2", "capacity": 3, "area_sqm": 25, "hourly_rate": 0, "daily_rate": 400, "monthly_rate": 6000, "status": "Maintenance", "amenities": ["WiFi", "Printer"]},
    ]

    space_names = []
    for sp in spaces_data:
        existing = frappe.db.exists("Co-working Space", {"space_name": sp["space_name"]})
        if not existing:
            amenities_list = sp.pop("amenities")
            doc = frappe.get_doc({"doctype": "Co-working Space", **sp})
            for a in amenities_list:
                doc.append("amenities", {"amenity": a})
            doc.insert(ignore_permissions=True)
            space_names.append(doc.name)
            print(f"  ✅ {sp['space_name']} ({doc.name})")
        else:
            space_names.append(existing)
            sp.pop("amenities", None)
            print(f"  ⏭️ {sp['space_name']} exists")
    frappe.db.commit()
    print(f"  Total spaces: {len(space_names)}")

    # ── 5. Customers (Members) ──
    print("\n👤 Creating Member Customers...")
    members_data = [
        {"customer_name": "أحمد مصطفى", "customer_type": "Individual", "customer_group": "Individual", "territory": "Egypt"},
        {"customer_name": "سارة الشناوي", "customer_type": "Individual", "customer_group": "Individual", "territory": "Egypt"},
        {"customer_name": "محمد عبد الحميد", "customer_type": "Individual", "customer_group": "Individual", "territory": "Egypt"},
        {"customer_name": "نورهان السيد", "customer_type": "Individual", "customer_group": "Individual", "territory": "Egypt"},
        {"customer_name": "خالد حسن", "customer_type": "Individual", "customer_group": "Individual", "territory": "Egypt"},
        {"customer_name": "شركة النيل للتقنية", "customer_type": "Company", "customer_group": "Commercial", "territory": "Egypt"},
        {"customer_name": "مؤسسة الأهرام الرقمية", "customer_type": "Company", "customer_group": "Commercial", "territory": "Egypt"},
        {"customer_name": "شركة الدلتا للاستشارات", "customer_type": "Company", "customer_group": "Commercial", "territory": "Egypt"},
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
            print(f"  ⏭️ {md['customer_name']} exists")
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
            print(f"  ✅ {pd_item['plan_name']} ({doc.name}) - {pd_item['monthly_price']} EGP/month")
        else:
            plan_names.append(existing)
            print(f"  ⏭️ {pd_item['plan_name']} exists")
    frappe.db.commit()

    print("\n✅ Phase 1 seeding complete!")
    print(f"  Branches: {len(branches)}")
    print(f"  Space Types: {len(space_types)}")
    print(f"  Amenities: {len(amenity_names)}")
    print(f"  Co-working Spaces: {len(space_names)}")
    print(f"  Members: {len(member_names)}")
    print(f"  Membership Plans: {len(plan_names)}")
    
    # Store for phase 2
    frappe.flags.seed_data = {
        "branches": branches,
        "space_types": space_types,
        "amenity_names": amenity_names,
        "space_names": space_names,
        "member_names": member_names,
        "plan_names": plan_names
    }

run()
