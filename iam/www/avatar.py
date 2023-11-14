import os
from io import BytesIO

from PIL import Image

import frappe
from frappe.utils.caching import redis_cache


@frappe.whitelist(allow_guest=True, methods=["GET"])
def media(uid, w=96, h=96):
    file_type, image_buffer, file_type = _internal_media(uid, w=96, h=96)

    # Set the response content directly
    frappe.response['filename'] = f"{uid}_{w}x{h}.{file_type}"
    frappe.response['filecontent'] = image_buffer.getvalue()
    frappe.response['type'] = 'download'
    frappe.response['name'] = f"{uid}_{w}x{h}.{file_type}"


@redis_cache(ttl=60 * 360)
def _internal_media(uid, w=96, h=96):
    try:
        name, userid = frappe.get_value(
            "User Social Login",
            {
                'userid': uid,
            },
            ['parent', 'userid'],
        )

        user = frappe.get_doc('User', name)

        _file = frappe.get_doc("File", {"file_url": user.user_image})
    except:
        app_logo = frappe.db.get_single_value('Website Settings', 'app_logo')
        _file = frappe.get_doc("File", {"file_url": app_logo})

    # Get the path to the original image file on the server
    original_image_path = _file.get_full_path()

    if not os.path.exists(original_image_path):
        frappe.throw("Original image file not found.")

    # Open the original image
    original_image = Image.open(original_image_path)

    # Resize the image
    width = int(w)
    height = int(h)
    resized_image = original_image.resize((width, height))

    file_type = str(_file.file_type).replace('JPG', 'JPEG')

    # Save the resized image to a BytesIO object
    image_buffer = BytesIO()
    resized_image.save(image_buffer, format=file_type)
    image_buffer.seek(0)

    return [file_type, image_buffer, file_type]
