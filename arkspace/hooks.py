app_name = "arkspace"
app_logo_url = "/assets/arkspace/images/arkspace-logo.svg"
app_title = "ARKSpace"
app_publisher = "Arkan Lab"
app_description = "Enterprise Co-Working Space Management + ARKANOOR Marketplace"
app_email = "dev@arkspace.io"
app_license = "mit"
app_icon = "/assets/arkspace/images/arkspace-logo-animated.svg"
app_logo = "/assets/arkspace/images/arkspace-logo-animated.svg"
app_color = "#1B365D"
app_home = "/desk"

# Required Apps
required_apps = ["erpnext"]

# --- v16: App Screen Integration ---------------------------------------------
# Shows ARKSpace on the Frappe v16 desktop apps screen

add_to_apps_screen = [
    {
        "name": "arkspace",
        "logo": "/assets/arkspace/images/arkspace-logo-animated.svg",
        "title": "ARKSpace",
        "route": "/desk/arkspace",
        "has_permission": "arkspace.permissions.has_app_permission",
    }
]

# --- Website Context (branding) -----------------------------------------------

website_context = {
    "favicon": "/assets/arkspace/images/favicon.svg",
    "splash_image": "/assets/arkspace/images/arkspace-splash.svg",
    "app_logo": "/assets/arkspace/images/arkspace-login.svg",
}

# --- Static Assets -----------------------------------------------------------

app_include_css = [
    "/assets/arkspace/css/arkspace-theme.css",
    "/assets/arkspace/css/arkspace-variables.css",
    "/assets/arkspace/css/design-system.css",
    "/assets/arkspace/css/arkspace.css",
]

app_include_js = [
    "/assets/arkspace/js/arkspace.js",
    "/assets/arkspace/js/arkspace_help.js",
    "/assets/arkspace/js/online_payments.js",
    "/assets/arkspace/js/dynamic_pricing.js",
    "/assets/arkspace/js/qr_checkin.js",
    "/assets/arkspace/js/visitor_management.js",
    "/assets/arkspace/js/day_pass.js",
    "/assets/arkspace/js/analytics.js",
    "/assets/arkspace/js/multi_location.js",
    "/assets/arkspace/js/community.js",
]

# --- Website Assets -----------------------------------------------------------

web_include_css = "/assets/arkspace/css/arkspace_portal.css"
web_include_js = "/assets/arkspace/js/arkspace_portal.js"

# --- Portal Menu Items --------------------------------------------------------

portal_menu_items = [
    {"title": "ARKSpace Dashboard", "route": "/arkspace_portal", "role": ""},
    {"title": "My Memberships", "route": "/memberships", "role": ""},
    {"title": "My Payments", "route": "/payments", "role": ""},
    {"title": "Book a Space", "route": "/arkspace_portal/book", "role": ""},
    {"title": "My Profile", "route": "/arkspace_portal/profile", "role": ""},
    {"title": "Day Pass", "route": "/day_pass", "role": ""},
    {"title": "Analytics", "route": "/analytics", "role": "ARKSpace Admin"},
    {"title": "Community", "route": "/community", "role": ""},
    {"title": "Events", "route": "/events", "role": ""},
    {"title": "Member Directory", "route": "/directory", "role": ""},
]

# --- DocType Events -----------------------------------------------------------

doc_events = {
    "DocType": {
        "after_insert": "arkspace.arkspace_documentation.readme_generator.create_doctype_readme",
        "on_update": "arkspace.arkspace_documentation.readme_generator.update_doctype_readme",
    },
    "Space Booking": {
        "on_submit": "arkspace.arkspace_integrations.billing.on_booking_submit",
        "on_cancel": "arkspace.arkspace_integrations.billing.on_booking_cancel",
    },
    "Membership": {
        "on_submit": "arkspace.arkspace_integrations.billing.on_membership_submit",
        "on_cancel": "arkspace.arkspace_integrations.billing.on_membership_cancel",
    },
    "Employee": {
        "after_insert": "arkspace.arkspace_integrations.billing.link_employee_to_customer",
        "on_update": "arkspace.arkspace_integrations.billing.link_employee_to_customer",
    },
    "Day Pass": {
        "on_submit": "arkspace.arkspace_integrations.billing.on_day_pass_submit",
        "on_cancel": "arkspace.arkspace_integrations.billing.on_day_pass_cancel",
    },
}

# --- Scheduled Tasks ----------------------------------------------------------

scheduler_events = {
    "cron": {
        "0 2 * * *": [
            "arkspace.arkspace_documentation.auto_generator.regenerate_documentation",
        ],
    },
    "daily": [
        "arkspace.tasks.check_membership_expiry",
        "arkspace.tasks.auto_renew_memberships",
        "arkspace.tasks.send_membership_expiry_reminders",
        "arkspace.tasks.generate_daily_occupancy_snapshot",
        "arkspace.tasks.bulk_generate_booking_qr_codes",
        "arkspace.tasks.expire_day_passes",
        "arkspace.tasks.capture_analytics_snapshot",
    ],
    "hourly": [
        "arkspace.tasks.mark_no_show_bookings",
        "arkspace.tasks.auto_checkout_expired_bookings",
        "arkspace.tasks.expire_stale_online_payments",
        "arkspace.tasks.auto_checkout_day_passes",
        "arkspace.tasks.update_community_event_statuses",
    ],
}

# --- Permissions --------------------------------------------------------------

has_permission = {
    "Co-working Space": "arkspace.permissions.has_space_permission",
    "Space Booking": "arkspace.permissions.has_booking_permission",
    "Membership": "arkspace.permissions.has_membership_permission",
}

permission_query_conditions = {
    "Co-working Space": "arkspace.permissions.get_space_conditions",
    "Space Booking": "arkspace.permissions.get_booking_conditions",
    "Membership": "arkspace.permissions.get_membership_conditions",
}

# --- Fixtures -----------------------------------------------------------------

fixtures = [
    {
        "dt": "Role",
        "filters": [["role_name", "like", "ARKSpace%"]],
    },
    {
        "dt": "Workflow",
        "filters": [["name", "in", ["Space Booking Approval", "Membership Lifecycle", "Lead Pipeline"]]],
    },
    {
        "dt": "Notification",
        "filters": [["name", "like", "ARKSpace%"]],
    },
    {
        "dt": "Number Card",
        "filters": [[
            "name", "in",
            ["Available Spaces", "Occupied Spaces", "Active Memberships", "Checked In Now"],
        ]],
    },
    {
        "dt": "Dashboard Chart",
        "filters": [["name", "like", "ARKSpace%"]],
    },
    {
        "dt": "Print Format",
        "filters": [["name", "in", ["Booking Confirmation", "Membership Card", "Membership Receipt"]]],
    },
]

# --- Jinja Customization -----------------------------------------------------

jinja = {
    "methods": [
        "arkspace.arkspace_design.icons.get_icon",
        "arkspace.arkspace_design.colors.get_color",
    ],
}

# --- Installation Hooks -------------------------------------------------------

# before_install = "arkspace.install.before_install"
after_install = "arkspace.install.after_install"

# --- v16: App Install / Uninstall Hooks ---------------------------------------
after_app_install = "arkspace.install.after_install"
before_app_uninstall = "arkspace.install.before_uninstall"

# --- Setup Wizard -------------------------------------------------------------

setup_wizard_requires = "assets/arkspace/js/setup_wizard.js"
setup_wizard_stages = "arkspace.setup_wizard.get_setup_stages"

# --- Migration Hooks ----------------------------------------------------------

after_migrate = "arkspace.setup.setup_arkspace"

# --- Override Methods ---------------------------------------------------------

# override_whitelisted_methods = {}

# --- Override DocType Class ---------------------------------------------------

# override_doctype_class = {}

# --- v16: URL Redirects -------------------------------------------------------
# Redirect legacy /app/ routes to /desk/ for v16 compatibility

website_redirects = [
    {"source": "/app/arkspace", "target": "/desk/arkspace"},
]

# --- URL Route Rules ----------------------------------------------------------
# Clean routes for about/onboarding pages

website_route_rules = [
    {"from_route": "/arkspace-about", "to_route": "arkspace-about"},
    {"from_route": "/arkspace-onboarding", "to_route": "ark-onboarding"},
    {"from_route": "/عن-arkspace", "to_route": "arkspace-about"},
]

# CAPS Integration — Capability-Based Access Control
# ------------------------------------------------------------
caps_capabilities = [
    {"name": "ARK_manage_spaces", "category": "Module", "description": "Manage coworking spaces"},
    {"name": "ARK_manage_members", "category": "Module", "description": "Manage memberships"},
    {"name": "ARK_manage_bookings", "category": "Module", "description": "Manage room bookings"},
    {"name": "ARK_manage_events", "category": "Module", "description": "Manage events and programs"},
    {"name": "ARK_manage_billing", "category": "Module", "description": "Manage billing and invoices"},
    {"name": "ARK_view_analytics", "category": "Report", "description": "View occupancy and revenue reports"},
    {"name": "ARK_manage_visitors", "category": "Action", "description": "Manage day passes and visitors"},
    {"name": "ARK_admin_settings", "category": "Module", "description": "Configure ARKSpace settings"},
]
