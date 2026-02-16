app_name = "arkspace"
app_title = "ARKSpace"
app_publisher = "ARKSpace Team"
app_description = "Enterprise Co-Working Space Management + ARKANOOR Marketplace"
app_email = "dev@arkspace.io"
app_license = "mit"
app_icon = "fa-solid fa-building"
app_color = "#1B365D"

# Required Apps
required_apps = ["erpnext"]

# --- Static Assets -----------------------------------------------------------

app_include_css = [
    "/assets/arkspace/css/design-system.css",
    "/assets/arkspace/css/arkspace.css",
]

app_include_js = [
    "/assets/arkspace/js/arkspace.js",
]

# --- Website Assets -----------------------------------------------------------

web_include_css = "/assets/arkspace/css/arkspace_portal.css"
web_include_js = "/assets/arkspace/js/arkspace_portal.js"

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
    ],
    "hourly": [
        "arkspace.tasks.mark_no_show_bookings",
        "arkspace.tasks.auto_checkout_expired_bookings",
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
        "filters": [["name", "in", ["Available Spaces", "Occupied Spaces", "Active Memberships", "Checked In Now"]]],
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

# --- Setup Wizard -------------------------------------------------------------

setup_wizard_requires = "assets/arkspace/js/setup_wizard.js"
setup_wizard_stages = "arkspace.setup_wizard.get_setup_stages"

# --- Migration Hooks ----------------------------------------------------------

after_migrate = "arkspace.setup.setup_arkspace"

# --- Override Methods ---------------------------------------------------------

# override_whitelisted_methods = {}

# --- Override DocType Class ---------------------------------------------------

# override_doctype_class = {}
