import frappe
from iam.utils.keycloak import KeycloakAccess


def get_social_login(user_name):
    slk = frappe.get_list(
        'Social Login Key',
        filters={
            'enable_social_login': True
        },
        pluck='name',
        ignore_permissions=True
    )
    usl = frappe.get_list(
        "User Social Login",
        filters={
            'parent': user_name,
            'provider': ['in', slk]
        },
        pluck='userid',
        ignore_permissions=True
    )

    preferred_social = frappe.get_value('User', user_name, ["social_login"])

    if len(usl) > 0:
        return [usl[0], preferred_social]
    else:
        return [False, preferred_social]


def on_update_user(doc, method):
    social_login_name, preferred_social = get_social_login(doc.name)

    keycloak_instance = KeycloakAccess(social_login_name, preferred_social)

    _safe_obj = {
        'email': doc.name,
        'firstName': doc.first_name,
        'lastName': doc.last_name,
        'enabled': doc.enabled,
    }

    keycloak_instance.on_update(_safe_obj)

    new_password = doc.get_password('sso_new_password', False)
    is_temporary = doc.is_temporary_password
    required_actions = doc.required_actions

    if new_password:
        keycloak_instance.set_password(new_password, is_temporary)

        # Reset fields
        doc.sso_new_password = ''
        doc.is_temporary_password = False
        doc.save()

    if required_actions:
        keycloak_instance.set_action([required_actions])

        # Reset fields
        doc.required_actions = ''
        doc.save()


def on_trash_user(doc, method):
    social_login_name, preferred_social = get_social_login(doc.name)

    keycloak_instance = KeycloakAccess(social_login_name, preferred_social)

    keycloak_instance.trash()


def on_cancel_user(doc, method):
    social_login_name, preferred_social = get_social_login(doc.name)

    keycloak_instance = KeycloakAccess(social_login_name, preferred_social)

    keycloak_instance.on_update({
        'enabled': False
    })
