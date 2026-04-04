// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * ARKSpace Setup Wizard Slides
 * شرائح معالج الإعداد
 */
frappe.provide("frappe.setup");

frappe.setup.on("before_load", function () {
	// Add ARKSpace slides to the setup wizard
	frappe.setup.slides_settings.push(
		// Slide 1: Welcome & Basics
		{
			name: "arkspace_welcome",
			title: __("Welcome to ARKSpace — مرحباً بكم"),
			icon: "fa-solid fa-cubes",
			fields: [
				{
					fieldtype: "Data",
					fieldname: "workspace_name",
					label: __("Workspace Name"),
					description: __("The name of your co-working space brand"),
					reqd: 1,
					default: "ARKSpace",
				},
				{ fieldtype: "Column Break" },
				{
					fieldtype: "Select",
					fieldname: "default_currency",
					label: __("Default Currency"),
					options: "AED\nSAR\nEGP\nUSD\nEUR\nGBP",
					default: "AED",
					reqd: 1,
				},
				{
					fieldtype: "Select",
					fieldname: "timezone",
					label: __("Timezone"),
					options:
						"Asia/Dubai\nAsia/Riyadh\nAfrica/Cairo\nEurope/Istanbul\nAmerica/New_York\nEurope/London",
					default: "Asia/Dubai",
					reqd: 1,
				},
			],
			onload: function (slide) {
				slide.$body.find(".section-description").html(`
					<div style="text-align:center; margin-bottom:20px;">
					<div style="text-align:center;">
						<img src="/assets/arkspace/images/arkspace-logo-animated.svg" alt="ARKSpace" style="width:80px; height:80px;">
						</div>
						<p style="color:var(--ark-text-secondary, #6B7280); margin-top:8px;">
							${__("Let's set up your co-working space in a few easy steps.")}
						</p>
					</div>
				`);
			},
		},

		// Slide 2: Branches
		{
			name: "arkspace_branches",
			title: __("Branches — الفروع"),
			icon: "fa-solid fa-map-marker-alt",
			fields: [
				{
					fieldtype: "Data",
					fieldname: "branch_1",
					label: __("Main Branch"),
					reqd: 1,
					default: __("Main Branch"),
				},
				{
					fieldtype: "Data",
					fieldname: "branch_2",
					label: __("Branch 2 (Optional)"),
				},
				{
					fieldtype: "Data",
					fieldname: "branch_3",
					label: __("Branch 3 (Optional)"),
				},
			],
		},

		// Slide 3: Space Types
		{
			name: "arkspace_spaces",
			title: __("Space Types — أنواع المساحات"),
			icon: "fa-solid fa-th-large",
			fields: [
				{
					fieldtype: "Check",
					fieldname: "type_hot_desk",
					label: __("Hot Desk — مكتب مشترك"),
					default: 1,
				},
				{
					fieldtype: "Check",
					fieldname: "type_dedicated_desk",
					label: __("Dedicated Desk — مكتب مخصص"),
					default: 1,
				},
				{
					fieldtype: "Check",
					fieldname: "type_private_office",
					label: __("Private Office — مكتب خاص"),
					default: 1,
				},
				{ fieldtype: "Column Break" },
				{
					fieldtype: "Check",
					fieldname: "type_meeting_room",
					label: __("Meeting Room — غرفة اجتماعات"),
					default: 1,
				},
				{
					fieldtype: "Check",
					fieldname: "type_event_space",
					label: __("Event Space — قاعة فعاليات"),
				},
				{
					fieldtype: "Check",
					fieldname: "type_virtual_office",
					label: __("Virtual Office — مكتب افتراضي"),
				},
			],
		},

		// Slide 4: First Membership Plan
		{
			name: "arkspace_plan",
			title: __("First Membership Plan — خطة العضوية الأولى"),
			icon: "fa-solid fa-id-card",
			fields: [
				{
					fieldtype: "Data",
					fieldname: "plan_name",
					label: __("Plan Name"),
					default: __("Basic Hot Desk"),
					reqd: 1,
				},
				{
					fieldtype: "Select",
					fieldname: "plan_type",
					label: __("Plan Type"),
					options:
						"Hot Desk\nDedicated Desk\nPrivate Office\nMeeting Room\nEvent Space\nVirtual Office",
					default: "Hot Desk",
					reqd: 1,
				},
				{ fieldtype: "Column Break" },
				{
					fieldtype: "Currency",
					fieldname: "monthly_price",
					label: __("Monthly Price"),
					reqd: 1,
					default: 1000,
				},
				{
					fieldtype: "Int",
					fieldname: "included_credits",
					label: __("Included Credits"),
					default: 20,
				},
			],
		}
	);
});
