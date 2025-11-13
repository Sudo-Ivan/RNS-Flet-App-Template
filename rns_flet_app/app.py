"""
This module provides the entry point and platform-specific launchers for the
RNS Flet App, a template for building RNS applications with Flet.
"""

import argparse

import flet as ft
from flet import AppView, Page

from . import rns
from . import lxmf
from . import lxst

messages_list = []
page_ref = None
send_fields = {"recipient": None, "title": None, "message": None}


async def main(page: Page):
    """Initialize and launch the RNS Flet App application.

    Sets up the loading screen, initializes Reticulum network and services,
    and builds the main UI.
    """
    global page_ref
    page_ref = page
    page.title = "RNS Flet App"
    page.theme_mode = ft.ThemeMode.DARK

    loader = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.SURFACE,
        content=ft.Column(
            [
                ft.ProgressRing(color=ft.Colors.PRIMARY, width=50, height=50),
                ft.Container(height=20),
                ft.Text(
                    "Initializing Services...",
                    size=16,
                    color=ft.Colors.ON_SURFACE,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
    )
    page.add(loader)
    page.update()

    if not rns.initialize_reticulum():
        print("Failed to initialize Reticulum network")
        return

    identity = rns.create_identity()
    if not identity:
        print("Failed to create identity")
        return

    if not lxmf.initialize_lxmf(identity, "rns_flet_app_messaging", display_name="RNS Flet App"):
        print("Failed to initialize LXMF")
    else:
        def message_callback(message):
            import RNS
            global messages_list, page_ref

            sender_hash = None
            if hasattr(message, 'source_hash'):
                sender_hash = message.source_hash
            elif hasattr(message, 'source'):
                sender_hash = message.source

            sender_name = "Anonymous"
            if sender_hash:
                try:
                    if RNS.Transport.destinations:
                        for dest in RNS.Transport.destinations:
                            if hasattr(dest, 'hash') and dest.hash == sender_hash:
                                if hasattr(dest, 'display_name') and dest.display_name:
                                    sender_name = dest.display_name
                                elif hasattr(dest, 'app_data') and dest.app_data:
                                    try:
                                        sender_name = dest.app_data.decode('utf-8')
                                    except:
                                        pass
                                break
                except Exception as e:
                    print(f"Error getting sender name: {e}")

                sender_hash_str = sender_hash.hex() if hasattr(sender_hash, 'hex') else str(sender_hash)[:16]
            else:
                sender_hash_str = "Unknown"

            content = ""
            if hasattr(message, 'content'):
                content_raw = message.content
                if isinstance(content_raw, bytes):
                    try:
                        content = content_raw.decode('utf-8')
                    except:
                        content = str(content_raw)
                elif content_raw:
                    content = str(content_raw)

            title = ""
            if hasattr(message, 'title'):
                title_raw = message.title
                if isinstance(title_raw, bytes):
                    try:
                        title = title_raw.decode('utf-8')
                    except:
                        title = str(title_raw)
                elif title_raw:
                    title = str(title_raw)

            msg_data = {
                "sender_name": sender_name,
                "sender_hash": sender_hash_str,
                "sender_hash_bytes": sender_hash,
                "title": title,
                "content": content
            }
            messages_list.insert(0, msg_data)

            if page_ref:
                def update_ui():
                    page_ref.controls.clear()
                    build_ui(page_ref)
                    page_ref.update()
                page_ref.run_thread(update_ui)

        if lxmf.lxmf_manager.router:
            lxmf.lxmf_manager.router.register_delivery_callback(message_callback)

    if not lxst.initialize_lxst(identity, "rns_flet_app_streaming"):
        print("Failed to initialize LXST")

    try:
        if hasattr(lxmf.lxmf_manager, 'destination') and lxmf.lxmf_manager.destination:
            lxmf.lxmf_manager.destination.announce()
            print("LXMF destination announced on network")
    except Exception as e:
        print(f"Failed to announce LXMF destination: {e}")

    identity_hash = rns.get_identity_hash()
    if identity_hash:
        print(f"RNS Identity: {identity_hash.hex()}")

        if hasattr(lxmf.lxmf_manager, 'destination') and lxmf.lxmf_manager.destination:
            lxmf_address = lxmf.lxmf_manager.destination.hash.hex()
            print(f"LXMF Address: {lxmf_address}")
        else:
            print("LXMF Address: Not initialized")

        if lxst.lxst_manager.identity:
            lxst_hash = lxst.lxst_manager.identity.hash
            print(f"LXST Address: {lxst_hash.hex()}")
        else:
            print("LXST Address: Not initialized")

    def init_ui():
        import time

        time.sleep(0.5)

        page.controls.clear()
        build_ui(page)
        page.update()

    page.run_thread(init_ui)


def build_ui(page: Page):
    """Build and configure the main application UI with address information.

    Args:
        page: Flet page instance to build UI on.
    """
    page.theme_mode = ft.ThemeMode.DARK

    identity_hash = rns.get_identity_hash()
    identity_text = identity_hash.hex() if identity_hash else "Not available"

    lxmf_address = "Not initialized"
    if hasattr(lxmf.lxmf_manager, 'destination') and lxmf.lxmf_manager.destination:
        lxmf_address = lxmf.lxmf_manager.destination.hash.hex()

    lxst_address = "Not initialized"
    if lxst.lxst_manager.identity:
        lxst_address = lxst.lxst_manager.identity.hash.hex()

    main_content = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            [
                ft.Text(
                    "RNS Flet App",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=30),
                ft.Text(
                    "Network Addresses",
                    size=20,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text("RNS Identity", size=16, weight=ft.FontWeight.W_500),
                        ft.Container(
                            content=ft.Text(
                                identity_text,
                                size=14,
                                font_family="monospace",
                                color=ft.Colors.PRIMARY,
                                selectable=True
                            ),
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            padding=10,
                            border_radius=5,
                        ),
                    ]),
                    margin=ft.margin.only(bottom=15)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("LXMF Address", size=16, weight=ft.FontWeight.W_500),
                        ft.Container(
                            content=ft.Text(
                                lxmf_address,
                                size=14,
                                font_family="monospace",
                                color=ft.Colors.SECONDARY,
                                selectable=True
                            ),
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            padding=10,
                            border_radius=5,
                        ),
                    ]),
                    margin=ft.margin.only(bottom=15)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("LXST Address", size=16, weight=ft.FontWeight.W_500),
                        ft.Container(
                            content=ft.Text(
                                lxst_address,
                                size=14,
                                font_family="monospace",
                                color=ft.Colors.TERTIARY,
                                selectable=True
                            ),
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            padding=10,
                            border_radius=5,
                        ),
                    ]),
                    margin=ft.margin.only(bottom=30)
                ),
                ft.Container(height=20),
                ft.Text(
                    "✓ Destinations announced on network",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.SECONDARY,
                ),
                ft.Container(height=30),
                ft.Text(
                    "Messages",
                    size=20,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=10),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=20,
    )

    send_fields["recipient"] = ft.TextField(
        label="Recipient Address",
        hint_text="Enter destination hash",
        prefix_text="<",
        suffix_text=">",
        width=400,
    )
    send_fields["title"] = ft.TextField(
        label="Title (optional)",
        width=400,
    )
    send_fields["message"] = ft.TextField(
        label="Message",
        multiline=True,
        min_lines=3,
        width=400,
    )

    send_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Send Message", size=16, weight=ft.FontWeight.W_500),
                send_fields["recipient"],
                send_fields["title"],
                send_fields["message"],
                ft.ElevatedButton(
                    "Send",
                    on_click=lambda e: send_message(page),
                    icon=ft.Icons.SEND,
                ),
            ], tight=True),
            padding=15,
        ),
        margin=ft.margin.only(bottom=15),
    )

    main_content.content.controls.append(send_card)

    messages_column = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    for idx, msg in enumerate(messages_list):
        is_sent = msg.get("is_sent", False)

        if is_sent:
            sender_color = ft.Colors.SECONDARY
            bg_color = ft.Colors.SURFACE_CONTAINER_HIGHEST
            alignment = ft.MainAxisAlignment.END
        else:
            sender_color = ft.Colors.PRIMARY
            bg_color = None
            alignment = ft.MainAxisAlignment.START

        msg_controls = [
            ft.Row([
                ft.Text(
                    msg["sender_name"],
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=sender_color,
                ),
                ft.Container(expand=True),
                ft.Text(
                    f"<{msg['sender_hash']}>",
                    size=11,
                    font_family="monospace",
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    selectable=True,
                ),
            ]),
            ft.Container(height=8),
        ]

        if msg.get("title"):
            msg_controls.append(
                ft.Text(
                    msg["title"],
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.ON_SURFACE,
                )
            )

        if msg.get("content"):
            msg_controls.append(
                ft.Text(
                    msg["content"],
                    size=13,
                    color=ft.Colors.ON_SURFACE,
                )
            )

        if not is_sent:
            reply_button = ft.ElevatedButton(
                "Reply",
                on_click=lambda e, hash_str=msg["sender_hash"], hash_bytes=msg.get("sender_hash_bytes"): show_reply_dialog(page, hash_str, hash_bytes),
                icon=ft.Icons.REPLY,
            )
            msg_controls.append(ft.Container(height=10))
            msg_controls.append(reply_button)

        msg_card = ft.Card(
            content=ft.Container(
                content=ft.Column(msg_controls, tight=True),
                padding=15,
                bgcolor=bg_color,
            ),
            margin=ft.margin.only(bottom=10),
        )
        messages_column.controls.append(msg_card)

    if not messages_list:
        messages_column.controls.append(
            ft.Text(
                "No messages yet",
                size=14,
                color=ft.Colors.ON_SURFACE_VARIANT,
                text_align=ft.TextAlign.CENTER,
            )
        )

    messages_container = ft.Container(
        content=messages_column,
        expand=True,
        padding=10,
    )

    page.add(
        ft.Column(
            [
                main_content,
                ft.Divider(),
                messages_container,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    )


def send_message(page: Page):
    """Send an LXMF message."""
    try:
        recipient_field = send_fields["recipient"]
        title_field = send_fields["title"]
        message_field = send_fields["message"]

        if not recipient_field or not message_field:
            print("Fields not initialized")
            return

        recipient_hash = None
        recipient_hash_str = None

        if hasattr(recipient_field, 'data') and recipient_field.data:
            recipient_hash = recipient_field.data
            recipient_hash_str = recipient_hash.hex()
        else:
            recipient_hash_str = recipient_field.value.strip()
            if recipient_hash_str.startswith('<'):
                recipient_hash_str = recipient_hash_str[1:]
            if recipient_hash_str.endswith('>'):
                recipient_hash_str = recipient_hash_str[:-1]
            recipient_hash_str = recipient_hash_str.strip()

            if not recipient_hash_str:
                print("Recipient address required")
                return

            try:
                recipient_hash = bytes.fromhex(recipient_hash_str)
            except ValueError:
                print(f"Invalid hash format: {recipient_hash_str}")
                return

        if not recipient_hash:
            print("Failed to get recipient hash")
            return

        title = title_field.value.strip() if title_field and title_field.value else ""
        content = message_field.value.strip() if message_field else ""

        if not content:
            print("Message content required")
            return

        message = lxmf.create_message(recipient_hash, content, title=title if title else None)
        if message:
            if lxmf.send_message(message):
                print(f"Message sent to {recipient_hash_str[:16]}...")

                sent_msg_data = {
                    "sender_name": "You",
                    "sender_hash": recipient_hash_str,
                    "sender_hash_bytes": recipient_hash,
                    "title": title if title else "",
                    "content": content,
                    "is_sent": True
                }
                messages_list.insert(0, sent_msg_data)

                def update_ui():
                    page.controls.clear()
                    build_ui(page)
                    page.update()
                page.run_thread(update_ui)

                recipient_field.value = ""
                if hasattr(recipient_field, 'data'):
                    recipient_field.data = None
                if title_field:
                    title_field.value = ""
                if message_field:
                    message_field.value = ""
                page.update()
            else:
                print("Failed to send message")
        else:
            print("Failed to create message")
    except Exception as e:
        print(f"Error sending message: {e}")


def show_reply_dialog(page: Page, recipient_hash: str, recipient_hash_bytes=None):
    """Show reply dialog with pre-filled recipient."""
    try:
        recipient_field = send_fields["recipient"]
        message_field = send_fields["message"]

        if recipient_field:
            recipient_field.value = recipient_hash
            if recipient_hash_bytes:
                recipient_field.data = recipient_hash_bytes
        if message_field:
            message_field.focus()
        page.update()
    except Exception as e:
        print(f"Error showing reply dialog: {e}")


def run():
    """Run RNS Flet App with command line argument parsing."""
    parser = argparse.ArgumentParser(description="RNS Flet App")
    parser.add_argument(
        "-w", "--web", action="store_true", help="Launch in web browser mode"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=None, help="Port for web server"
    )
    args = parser.parse_args()

    if args.web:
        if args.port is not None:
            ft.app(main, view=AppView.WEB_BROWSER, port=args.port)
        else:
            ft.app(main, view=AppView.WEB_BROWSER)
    else:
        ft.app(main)


if __name__ == "__main__":
    run()


def web():
    """Launch RNS Flet App in web mode."""
    ft.app(main, view=AppView.WEB_BROWSER)


def android():
    """Launch RNS Flet App in Android mode."""
    ft.app(main, view=AppView.FLET_APP_WEB)


def ios():
    """Launch RNS Flet App in iOS mode."""
    ft.app(main, view=AppView.FLET_APP_WEB)
