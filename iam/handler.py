import frappe


@frappe.whitelist(allow_guest=True)
def web_logout():
    redirect_to = frappe.local.request.args.get("redirect-to")

    frappe.local.login_manager.logout()
    frappe.db.commit()

    if redirect_to:
        frappe.local.flags.redirect_location = redirect_to
        raise frappe.Redirect
