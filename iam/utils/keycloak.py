from keycloak import KeycloakAdmin

import frappe


class KeycloakAccess:

    def __init__(self, social_key_id, preferred_social):
        self.social_key_id = social_key_id
        self.preferred_social = preferred_social

        self.doc = frappe.get_doc('Social Login Key', self.preferred_social)

        if not self.doc:
            raise frappe.DoesNotExistError

        client_id = self.doc.client_id
        password = self.doc.get_password('client_secret')

        self.keycloak = KeycloakAdmin(
            server_url=self.doc.base_url,
            realm_name=self.doc.custom_realm_name,
            client_secret_key=password,
            client_id=client_id,
            username=client_id,
            password=password,
            verify=True
        )

    def on_update(self, payload):
        user_email = payload.get('email')
        first_name = payload.get('first_name')
        last_name = payload.get('last_name')

        kc_user = self.keycloak.get_user_id(user_email)

        if not kc_user:
            user_id = self.keycloak.create_user({
                'email': user_email,
                'firstName': first_name,
                'lastName': last_name,
                'enabled': True,
            })

            usl = frappe.new_doc('User Social Login')
            usl.parent = user_email
            usl.parenttype = 'User'
            usl.parentfield = 'social_logins'
            usl.provider = self.preferred_social
            usl.userid = user_id
            usl.insert()

        elif kc_user and not self.social_key_id:

            usl = frappe.new_doc('User Social Login')
            usl.parent = user_email
            usl.parenttype = 'User'
            usl.parentfield = 'social_logins'
            usl.provider = self.preferred_social
            usl.userid = kc_user
            usl.insert()

            self.social_key_id = kc_user

            return self.keycloak.update_user(kc_user, payload)
        else:
            return self.keycloak.update_user(self.social_key_id, payload)

    def set_password(self, new_password, temporary=True):
        return self.keycloak.set_user_password(
            self.social_key_id,
            password=new_password,
            temporary=temporary
        )

    def set_action(self, payload=None):
        if payload is None:
            payload = []

        return self.keycloak.update_user(
            self.social_key_id,
            {'requiredActions': payload}
        )

    def trash(self):
        return self.keycloak.delete_user(self.social_key_id)

    def group_user_add(self, group_id):
        return self.keycloak.group_user_add(self.social_key_id, group_id)

    def group_user_remove(self, group_id):
        return self.keycloak.group_user_remove(self.social_key_id, group_id)

    def create_group(self, payload):
        return
