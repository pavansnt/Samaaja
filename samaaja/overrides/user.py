"""Overrides for User doctype"""

import frappe
from frappe.utils import random_string
from samaaja.utils.utils import make_image_public


def make_user_images_public(doc, method=None):
    """
    Make user_image and banner_image publicly accessible.

    Converts private file URLs to public ones using the make_image_public utility.
    Typically used in the before_save hook of the User doctype.
    """
    doc.user_image = make_image_public(doc.user_image)
    doc.banner_image = make_image_public(doc.banner_image)


def create_user_metadata(doc, method=None):
    """Create User Metadata when a User is created."""
    if (
        not frappe.db.exists("User Metadata", {"user": doc.name})
        and doc.name != "Administrator"
    ):
        frappe.get_doc({
            "doctype": "User Metadata",
            "user": doc.name
        }).insert(ignore_permissions=True)


def delete_user_metadata(doc, method=None):
    """Delete User Metadata associated with a User."""
    if frappe.db.exists("User Metadata", doc.name):
        frappe.delete_doc("User Metadata", doc.name)


def generate_unique_username(first_name=None, last_name=None, size=6):
    """Generate a unique username from first and last name."""

    first_name = (first_name or "").strip().lower()
    last_name = (last_name or "").strip().lower()

    prefix = "-".join(
        part for part in (first_name, last_name) if part
    )

    if not prefix:
        prefix = "user"

    # Remove periods and spaces from the prefix.
    prefix = prefix.replace(".", "").replace(" ", "")

    while True:
        candidate = f"{prefix}-{random_string(size)}"

        if not frappe.db.exists("User", {"username": candidate}):
            return candidate


def generate_username_if_missing(doc, method=None):
    """Generate a username when one is missing."""

    if doc.name in ("Administrator", "Guest"):
        return

    if not doc.username:
        doc.username = generate_unique_username(
            doc.first_name,
            doc.last_name
        )


def username(*args, **kwargs):
    """
    Backward-compatible username helper for existing Solve Ninja callers.

    Supports:
    - username(user_doc)
    - username(first_name, last_name)
    - username(first_name="Pavan", last_name="...")
    """

    if args and hasattr(args[0], "doctype"):
        return generate_username_if_missing(*args, **kwargs)

    first_name = (
        args[0] if len(args) > 0
        else kwargs.get("first_name")
    )
    last_name = (
        args[1] if len(args) > 1
        else kwargs.get("last_name")
    )

    return generate_unique_username(first_name, last_name)


# Alias for callers that use this alternative helper name.
generate_username = generate_unique_username
