import frappe
from frappe import _


def social_login():
    return
    try:
        user_doc = frappe.get_doc("DocType", "User")

        user_doc.append("fields", {
            "fieldname": "sso_integration_tab",
            "fieldtype": "Tab Break",
            "label": "SSO Integration"
        })

        user_doc.append("fields", {
            "fieldname": "social_login",
            "fieldtype": "Link",
            "label": "Preferred Social Key",
            "options": "Social Login Key",
            "reqd": 1
        })

        user_doc.append("fields", {
            "fieldname": "column_break_uenj",
            "fieldtype": "Column Break"
        })

        user_doc.append("fields", {
            "fieldname": "sso_new_password",
            "fieldtype": "Password",
            "label": "New Password"
        })

        user_doc.append("fields", {
            "default": "0",
            "fieldname": "is_temporary_password",
            "fieldtype": "Check",
            "label": "Is Temporary Password"
        })

        user_doc.append("fields", {
            "fieldname": "required_actions",
            "fieldtype": "Select",
            "label": "Required Actions",
            "options": "\nCONFIGURE_TOTP\nterms_and_conditions\nUPDATE_PASSWORD\nUPDATE_PROFILE\nVERIFY_EMAIL\ndelete_account\nwebauthn-register\nwebauthn-register-passwordless\nupdate_user_locale"
        })

        user_doc.save()
    except:
        pass
