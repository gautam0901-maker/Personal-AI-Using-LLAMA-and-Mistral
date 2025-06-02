# app/main.py

import flet as ft
from chat_engine import ask_ollama
from voice_interface import start_wake_listener
from scheduler import start_scheduler
import json
import os
from datetime import datetime
# Memory management imports for chat history
from memory_manager import append_chat_log, remember, recall
import re
from chat_engine import get_weather

def main(page: ft.Page):
    start_scheduler()
    page.title = "Pekko for Gautam"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.scroll = ft.ScrollMode.AUTO
    chat_column = ft.ListView(spacing=10, auto_scroll=True, expand=True)

    # Personalized welcome message at startup
    now = datetime.now()
    greeting = f"👋 Hi Gautam! It's {now.strftime('%A, %I:%M %p')} — I'm here and ready for your command!"
    chat_column.controls.append(ft.Text(greeting, size=16, italic=True, color=ft.Colors.LIGHT_GREEN_ACCENT))
    page.update()

    input_field = ft.TextField(
        hint_text="Ask Pekko anything...",
        autofocus=True,
        expand=True,
        border_radius=20,
        border_color=ft.Colors.BLUE_300,
        on_submit=lambda e: send_message(e.control.value)
    )

    def show_reminders():
        with open("data/reminders.json", "r") as f:
            data = json.load(f)
        if not data:
            chat_column.controls.append(ft.Text("📭 No reminders found.", italic=True))
        else:
            chat_column.controls.append(ft.Text("📋 Your Reminders:", size=18, weight="bold"))
            for r in data:
                def make_delete_handler(task=r['task']):
                    def handler(e):
                        from scheduler import delete_reminder
                        delete_reminder(task)
                        show_reminders()  # refresh the UI with updated list
                    return handler

                chat_column.controls.append(
                    ft.Row([
                        ft.Text(f"🕓 {r['time']} → {r['task']} ✅" if r.get("notified") else f"🕓 {r['time']} → {r['task']}"),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED, tooltip="Delete", on_click=make_delete_handler())
                    ])
                )
        page.update()

    overview_button = ft.ElevatedButton("📋 View Reminders", on_click=lambda e: show_reminders())

    stats_button = ft.ElevatedButton("📊 Reminder Insights", on_click=lambda e: show_stats())


    def show_stats():
        with open("data/reminders.json", "r") as f:
            reminders = json.load(f)
        total = len(reminders)
        upcoming = sum(1 for r in reminders if not r.get("notified"))
        past = total - upcoming
        chat_column.controls.append(ft.Text(f"📈 You have {total} reminders — {upcoming} upcoming, {past} done.", italic=True))
        page.update()


    def detect_reminder(message):
        return bool(re.search(r"(remind me to|set reminder.*(for|to))", message, re.I))

    def send_message(message):
        if not message.strip():
            return
        if message.lower() in ["hi", "hello"]:
            now = datetime.now()
            greeting = f"Good {'morning' if now.hour < 12 else 'evening'}, Gautam! It's {now.strftime('%A')}."
            chat_column.controls.append(ft.Text(f"🤖 Pekko: {greeting}", italic=True))

        # Detect reminder intent
        if detect_reminder(message):
            message = f"[REMINDER MODE] {message}"

        # Weather intent check
        if "weather" in message.lower():
            city_match = re.search(r"(?:in|at)\s+([a-zA-Z\s]+)", message.lower())
            city = city_match.group(1).strip() if city_match else recall("last_city")
            if city:
                remember("last_city", city)
                response = get_weather(city)
                append_chat_log(message, response)
                chat_column.controls.remove(typing_text) if 'typing_text' in locals() else None
                chat_column.controls.append(
                    ft.Row([
                        ft.AnimatedSwitcher(
                            content=ft.Container(
                                content=ft.Text(
                                    response,
                                    color=ft.Colors.BLACK,
                                    size=14,
                                    no_wrap=False,
                                    max_lines=None,
                                    selectable=True,
                                    overflow=ft.TextOverflow.CLIP,
                                    width=400
                                ),
                                padding=8,
                                margin=4,
                                bgcolor=ft.Colors.GREY_200,
                                border_radius=20,
                                alignment=ft.alignment.center_left,
                                animate=ft.Animation(duration=400, curve=ft.AnimationCurve.EASE_IN_OUT),
                                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.GREY_400)
                            ),
                            transition=ft.AnimatedSwitcherTransition.SCALE,
                            duration=300
                        )
                    ], alignment=ft.MainAxisAlignment.START)
                )
                page.update()
                return
        # Only prepend chat history for general chat, not for weather/forecast/temperature/rain/humidity queries
        if not any(kw in message.lower() for kw in ["weather", "forecast", "temperature", "rain", "humidity"]):
            history = recall("chat_history")
            if isinstance(history, list):
                memory_context = "\n".join([f"{entry['user']} → {entry['pekko']}" for entry in history])
                message = f"{memory_context}\n\nUser: {message}"

        # Animated user message bubble
        chat_column.controls.append(
            ft.Row([
                ft.AnimatedSwitcher(
                    content=ft.Container(
                        content=ft.Text(
                            message,
                            color=ft.Colors.WHITE,
                            size=14,
                            no_wrap=False,
                            max_lines=None,
                            selectable=True,
                            overflow=ft.TextOverflow.CLIP,
                            width=400
                        ),
                        padding=8,
                        margin=4,
                        bgcolor=ft.Colors.BLUE_800,
                        border_radius=20,
                        alignment=ft.alignment.center_right,
                        animate=ft.Animation(duration=400, curve=ft.AnimationCurve.EASE_IN_OUT),
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLUE_200)
                    ),
                    transition=ft.AnimatedSwitcherTransition.SCALE,
                    duration=300
                )
            ], alignment=ft.MainAxisAlignment.END)
        )
        # Subtle animated spacing after user message
        chat_column.controls.append(
            ft.AnimatedSwitcher(content=ft.Container(height=8), duration=500)
        )
        page.update()

        # Typing indicator before calling ask_ollama
        typing_text = ft.Text("Pekko is typing...", italic=True, color=ft.Colors.GREY)
        chat_column.controls.append(typing_text)
        page.update()

        response = ask_ollama(message)

        # Save full chat message and response to memory
        append_chat_log(message, response)
        remember("last_input", message)
        remember("last_response", response)

        # Auto-save chat log and summary
        now_dt = datetime.now().strftime("%Y-%m-%d_%H-%M")
        log_dir = "data/chat_logs"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/chat_{now_dt}.txt", "w") as f:
            f.write(f"User: {message}\nPekko: {response}")
        # Save markdown summary
        with open(f"{log_dir}/summary_{now_dt}.md", "w") as f:
            f.write(f"### Chat Summary - {now_dt}\n\n- **User said**: {message}\n- **Pekko replied**: {response}")

        # Animated Pekko reply bubble
        chat_column.controls.append(
            ft.Row([
                ft.AnimatedSwitcher(
                    content=ft.Container(
                        content=ft.Text(
                            response,
                            color=ft.Colors.BLACK,
                            size=14,
                            no_wrap=False,
                            max_lines=None,
                            selectable=True,
                            overflow=ft.TextOverflow.CLIP,
                            width=400
                        ),
                        padding=8,
                        margin=4,
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=20,
                        alignment=ft.alignment.center_left,
                        animate=ft.Animation(duration=400, curve=ft.AnimationCurve.EASE_IN_OUT),
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.GREY_400)
                    ),
                    transition=ft.AnimatedSwitcherTransition.SCALE,
                    duration=300
                )
            ], alignment=ft.MainAxisAlignment.START)
        )
        # Subtle animated spacing after Pekko's message
        chat_column.controls.append(
            ft.AnimatedSwitcher(content=ft.Container(height=8), duration=500)
        )
        # Remove typing indicator after Pekko's response is shown
        chat_column.controls.remove(typing_text)

        # Log reminder confirmation in UI
        if "remind you" in response.lower():
            chat_column.controls.append(
                ft.Text(f"⏰ Reminder set.", italic=True, color=ft.Colors.GREEN)
            )

        input_field.value = ""
        page.update()


    def open_log_folder():
        import webbrowser
        path = os.path.abspath("data/chat_logs")
        webbrowser.open(f"file://{path}")

    view_logs_button = ft.ElevatedButton("🗂️ View Chat Logs", on_click=lambda e: open_log_folder())

    page.add(
        ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("📂 Menu", weight="bold"),
                    overview_button,
                    stats_button,
                    view_logs_button,
                    ft.Divider(),
                    ft.Text("💬 Ask Pekko:", weight="bold"),
                    ft.Row([
                        input_field,
                        ft.IconButton(icon=ft.Icons.SEND, tooltip="Send", on_click=lambda e: send_message(input_field.value))
                    ])
                ], spacing=20, expand=False, tight=True),
                width=220,
                padding=10,
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=10,
                alignment=ft.alignment.top_center,
                expand=False
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("🤖 Welcome to Pekko for Gautam!", size=24, weight="bold"),
                    ft.Text("✨ Ask me anything, I'm here to help!", size=16, italic=True, animate_opacity=2000),
                    ft.Container(
                        content=chat_column,
                        expand=True,
                        padding=10
                    )
                ], expand=True, spacing=20),
                padding=20,
                expand=True,
            )
        ])
    )

ft.app(target=main)