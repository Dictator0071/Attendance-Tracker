import flet as ft
import datetime
import sqlite3
import os
from googleapiclient.discovery import build

"""For the last build major of the important backend is done, 
 I have imported google calendar but not used it to check for 
 holidays need to do that and refine the UI for future use"""

# Load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    print("env can't be loaded")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyDUMMY-EXAMPLE-KEY-DEFAULT")

class tracker:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Attendance Tracker"
        self.page.bgcolor = "#0a0a0a"
        self.page.padding = 0
        self.page.fonts = {
            "Inter": "https://rsms.me/inter/font-files/Inter-Regular.woff2",
            "Inter Bold": "https://rsms.me/inter/font-files/Inter-Bold.woff2"
        }

        self.conn = sqlite3.connect("attendance.db")
        self.c = self.conn.cursor()

        self.sem_date = datetime.date(2025, 8, 4)
        self.attend_val = 75
        self.class_duration = 55
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.selected_date = datetime.date.today()  # Initialize selected date for calendar widget

        self.content_column = ft.Column(spacing= 10, expand= True)
        self.scroll_view = ft.Container(
            expand=True,
            padding= ft.Padding(0,40,0,70),
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=self.content_column,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                expand= True
            )
        )

        self.home_icon = ft.IconButton(
            icon=ft.Icons.HOME_ROUNDED,
            icon_color="#e0e0e0",
            bgcolor= None,
            on_click=lambda e: self.show_homepage(e)
        )
        self.chart_icon = ft.IconButton(
            icon=ft.Icons.INSERT_CHART_ROUNDED,
            icon_color="#e0e0e0",
            on_click=lambda e: self.show_chart_screen(e)
        )
        self.list_icon = ft.IconButton(
            icon=ft.Icons.LIST_ALT_ROUNDED,
            icon_color="#e0e0e0",
            on_click=lambda e: self.show_list_screen(e)
        )
        # Navigation Bar
        self.nav_bar = ft.Container(
            padding=ft.padding.symmetric(vertical=0, horizontal=0),
            expand=True,  # Expand to fill available space
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    self.home_icon,
                    self.chart_icon,
                    self.list_icon

                ],
                expand=True  # Row should also expand
            )
        )

        self.dlg = ft.AlertDialog(
            title=ft.Text("Add Transaction"),
            content=ft.TextField(label="Amount"),
            actions=[
                ft.TextButton("Cancel"),
                ft.TextButton("Add"),
            ],
        )

        self.fab = ft.FloatingActionButton(
            icon=ft.Icons.ADD_ROUNDED,  # Just pass the icon directly
            foreground_color="#ffd699", # Use icon_color for the color
            bgcolor="#404040",
            scale=1.1,
            bottom=self.page.height * 0.125,
            left=self.page.width * 0.8,
            on_click= self.create_sub_screen
        )

        self.main_stack = ft.Stack(
            controls=[
                # Home screen (your existing layout)
                ft.Column(
                    controls=[
                        ft.Container(
                            content=self.scroll_view,
                            expand=True
                        ),
                        ft.Container(
                            content=self.nav_bar,
                            height=90,
                            bgcolor="#1a1a1a",
                            border_radius=ft.BorderRadius(15, 15, 0, 0),
                        )
                    ],
                    expand=True,
                    spacing=0
                )
            ],
            expand=True
        )

        self.conn.execute("""CREATE TABLE IF NOT EXISTS attendance (
            subject text,
            req_attendance INTEGER,
            day text,
            timing INTEGER,
            classes_held INTEGER,
            classes_attended INTEGER
        )""")

        self.conn.commit()

        self.page.add(self.main_stack)
        self.page.overlay.append(self.fab)
        self.show_homepage(None)

    def update_db(self):
        self.c.execute("Select * FROM attendance")
        items = self.c.fetchall()
        self.conn.commit()
        for item in items:
            self.c.execute("UPDATE attendance SET classes_held = ? WHERE subject =?", (self.classes_held(self.sem_date, datetime.date.today(), item[0]), item[0]))
            self.conn.commit()



    def create_sub_screen(self, e):
        # Create the overlay screen

        # In create_sub_screen, before creating the slider
        self.attendance_label = ft.Text(
            f"Required Attendance: {self.attend_val}",
            size=18,
            color="#ffffff",
            font_family="Inter",
            weight="w600",
        )

        self.course_name = ft.TextField(
            hint_text="Course name",
            hint_style=ft.TextStyle(color="#888888", size=16),
            text_style=ft.TextStyle(color="#ffffff", size=16),
            bgcolor="#2a2a2a",
            border_color="#404040",
            focused_border_color="#ff6b35",
            border_radius=12,
            height=60,
            content_padding=ft.Padding(20, 15, 20, 15),
            border_width=1,
        )

        self.overlay_screen = ft.Container(
            bgcolor="#0a0a0a",  # Same as your page background
            expand=True,
            content=ft.Column(
                spacing=0,
                controls=[
                    # Header with back button
                    ft.Container(
                        padding=ft.Padding(20, 50, 20, 0),
                        content=ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                                    icon_color="#e0e0e0",
                                    icon_size=28,
                                    on_click=self.close_overlay_screen
                                )
                            ]
                        )
                    ),

                    # Scrollable content
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            spacing=30,
                            controls=[
                                # Title
                                ft.Container(
                                    padding=ft.Padding(20, 20, 20, 0),
                                    content=ft.Text(
                                        "Create a course",
                                        size=32,
                                        color="#ffffff",
                                        font_family="Inter",
                                        weight="w800",
                                    )
                                ),

                                # Course name input
                                ft.Container(
                                    padding=ft.Padding(20, 0, 20, 0),
                                    content= self.course_name
                                ),
                                # Required Attendance section
                                ft.Container(
                                    padding=ft.Padding(20, 0, 20, 0),
                                    content=ft.Column(
                                        spacing=15,
                                        controls=[
                                            self.attendance_label,
                                            # Custom slider
                                            ft.Container(
                                                padding=ft.Padding(0, 10, 0, 0),
                                                content=ft.Slider(
                                                    min=0,
                                                    max=100,
                                                    divisions=100,
                                                    value= self.attend_val,
                                                    active_color="#ff6b35",
                                                    inactive_color="#404040",
                                                    thumb_color="#ff6b35",
                                                    on_change=self.on_attendance_change
                                                )
                                            )
                                        ]
                                    )
                                ),

                                # Select schedule section
                                ft.Container(
                                    padding=ft.Padding(20, 0, 20, 0),
                                    content=ft.Column(
                                        spacing=15,
                                        alignment=ft.MainAxisAlignment.START,
                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Text(
                                                "Select schedule of classes",
                                                size=24,
                                                color="#ffffff",
                                                font_family="Inter",
                                                weight="w700",
                                            ),

                                            # Add Class button
                                            ft.Container(
                                                margin=ft.Margin(0, 10, 0, 0),
                                                content=ft.ElevatedButton(
                                                    content=ft.Text(
                                                        "Add Class",
                                                        size=16,
                                                        color="#ff6b35",
                                                        font_family="Inter",
                                                        weight="w500"
                                                    ),
                                                    bgcolor="transparent",
                                                    color="#ff6b35",
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(radius=25),
                                                        side=ft.BorderSide(2, "#ff6b35"),
                                                        padding=ft.Padding(25, 12, 25, 12),
                                                    ),
                                                    on_click=self.add_class_dialog
                                                )
                                            )
                                        ]
                                    )
                                ),
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        )
                    ),

                    # Save button at bottom
                    ft.Container(
                        padding=ft.Padding(20, 0, 20, 30),
                        content=ft.ElevatedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.SAVE_ROUNDED, color="#ffffff", size=20),
                                    ft.Text("Save", size=16, color="#ffffff", font_family="Inter", weight="w600")
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=8,
                                tight=True
                            ),
                            bgcolor="#ff6b35",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=25),
                                padding=ft.Padding(25, 15, 25, 15),
                            ),
                            width=self.page.width * 0.8,
                            on_click=self.save_course
                        )
                    )
                ]
            )
        )

        # Add the overlay screen to the stack
        self.main_stack.controls.append(self.overlay_screen)

        # Hide the FAB
        self.fab.visible = False

        self.page.update()

    def close_overlay_screen(self, e):
        # Remove the overlay screen (keep only the first screen - home)
        if len(self.main_stack.controls) > 1:
            self.main_stack.controls.pop()
        # Show the FAB again
        self.fab.visible = True
        self.page.update()

    def handle_attendance_click(self, e):
        # Shared handler for both Present and Absent buttons
        btn = e.control
        data = getattr(btn, "data", {}) or {}
        card = data.get("card")
        present_btn = data.get("present_btn")
        absent_btn = data.get("absent_btn")

        if not card:
            return

        # Grey out the card and reduce emphasis
        card.bgcolor = "#1f1f1f"
        card.opacity = 0.6

        # Disable both buttons and mute their styles
        for b in (present_btn, absent_btn):
            if b is not None:
                b.on_click = None
                b.disabled = True
                b.bgcolor = "#3a3a3a"
                if isinstance(b.content, ft.Text):
                    b.content.color = "#9a9a9a"

        # Move the card to the bottom of the list
        try:
            if card in self.content_column.controls:
                self.content_column.controls.remove(card)
                self.content_column.controls.append(card)
        finally:
            self.page.update()

    def on_attendance_change(self, e):
        # Handle attendance percentage change
        self.attend_val = int(e.control.value)
        self.attendance_label.value = f"Required Attendance: {self.attend_val}"
        self.page.update()

    def add_class_dialog(self, e):
        self.days = [ft.Checkbox(label=day, value=False) for day in self.weekdays]
        self.bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Text("Select the days for the class", weight="bold"),
                        ft.Column(self.days),
                        ft.ElevatedButton("Confirm", on_click=self.start_time),
                    ],
                    tight=True,
                ),
                padding=20,
            ),
        )
        self.page.overlay.append(self.bs)
        self.bs.open = True
        self.page.update()

    def start_time(self, e):
        self.bs.content.clean()
        self.selected_days = [cb.label for cb in self.days if cb.value]
        print(self.selected_days)
        # Store pickers mapped to each day
        self.day_time_pickers = {}

        # Create UI rows: Day + Pick Time button
        rows = []
        def save_time(e, day, current_time):
            time_str = current_time.value.strftime("%H:%M")
            print(self.course_name.value, day, time_str, self.attend_val)
            self.c.execute("INSERT INTO attendance (subject, req_attendance, day, timing, classes_held, classes_attended) VALUES (?, ?, ?, ?,?,?)", (self.course_name.value, self.attend_val,day,time_str, 0,0))
            self.conn.commit()

        for day in self.selected_days:
            tp = ft.TimePicker(
                confirm_text="Confirm",
                error_invalid_text="Time out of range",
                help_text=f"Pick time for {day}",
            )

            tp.on_change = lambda e, current_day=day, current_time=tp: save_time(e, current_day,current_time)

            self.day_time_pickers[day] = tp
            rows.append(
                ft.Row(
                    [
                        ft.Text(day),
                        ft.ElevatedButton(
                            "Pick time",
                            icon=ft.Icons.ACCESS_TIME,
                            on_click=lambda _, picker=tp: self.page.open(picker),
                        ),
                    ]
                )
            )

        # Add final confirm button
        rows.append(
            ft.ElevatedButton(
                "Confirm All",
                on_click=lambda e: (print({day: picker.value for day, picker in self.day_time_pickers.items()}),
                                setattr(self.bs, "open", False),
                                self.page.update()
                                )
            )
        )

        # Set new bottom sheet content
        self.bs.content = ft.Column(rows, tight=True)
        self.bs.update()

    def save_course(self, e):
        self.close_overlay_screen(e)
        self.show_homepage(None)

    def classes_held(self, start_date, end_date, subject):
        self.c.execute("SELECT * FROM attendance WHERE subject = ? COLLATE NOCASE", (subject,))
        items = self.c.fetchall()
        schedule = []
        for item in items:
            schedule.append(item[2])
        total = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.strftime("%A") in schedule:
                total = total +1
            current_date += datetime.timedelta(days=1)
        return total

    def get_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 18:
            return "Good afternoon"
        else:
            return "Good evening"

    def show_homepage(self,e):
        self.update_db()
        self.page.update()
        self.content_column.controls.clear()

        self.home_icon.bgcolor = "#404040"
        self.list_icon.bgcolor = None
        self.chart_icon.bgcolor = None

        greet_text = ft.Container(
            padding=ft.Padding(20,40,20,0),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=0,
                        alignment=ft.MainAxisAlignment.START,
                        controls=[
                            ft.Text(
                                self.get_greeting(),
                                size=20,
                                color="#e0e0e0",
                                font_family="Inter",
                                weight="w800",
                            ),
                            ft.Text(
                                "Rudra Agrawal",
                                size=28,
                                color="#ffb366",
                                font_family="Inter",
                                weight="w900",
                            ),
                        ]
                    ),
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        icon_color="#e0e0e0",
                        icon_size=24,
                        tooltip="More options",
                        items=[
                            ft.PopupMenuItem(
                                text="Mark Present",
                                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                                on_click=self.mark_all_present
                            ),
                            ft.PopupMenuItem(
                                text="Mark Absent",
                                icon=ft.Icons.CANCEL_OUTLINED,
                                on_click=self.mark_all_absent
                            )
                        ]
                    )
                ]
            )
        )

        self.content_column.controls.append(greet_text)

        # Simple date display with clickable calendar icon
        date_row = ft.Container(
            margin=ft.Margin(10, 15, 10, 15),
            padding=ft.Padding(20, 15, 20, 15),
            bgcolor="#2a2a2a",
            border_radius=15,
            border=ft.border.all(1, "#404040"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        f"{self.selected_date.strftime('%A, %B %d, %Y')}",
                        size=18,
                        color="#ffffff",
                        font_family="Inter",
                        weight="w600"
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
                        icon_color="#ff6b35",
                        icon_size=28,
                        on_click=self.show_date_picker,
                        style=ft.ButtonStyle(
                            bgcolor="#404040",
                            shape=ft.RoundedRectangleBorder(radius=12)
                        )
                    )
                ]
            )
        )

        self.content_column.controls.append(date_row)

        # Get classes for the selected date (only if after semester start)
        selected_day = self.selected_date.strftime("%A")
        self.c.execute("SELECT * FROM attendance WHERE day = ?", (selected_day,))
        items = self.c.fetchall()

        if items:
            for item in items:
                subject, req_attendance, day, timing, classes_held, classes_attended = item

                att_per = round((classes_attended/classes_held) * 100)

                # Buttons (handlers wired to shared logic)
                absent_btn = ft.Container(
                    padding=ft.Padding(20, 10, 20, 10),
                    border_radius=8,
                    bgcolor="#f5f5f5",
                    content=ft.Text(
                        "Absent",
                        size=14,
                        color="#2a2a2a",
                        font_family="Inter",
                        weight="w500",
                    ),
                    on_click=self.handle_attendance_click
                )

                present_btn = ft.Container(
                    padding=ft.Padding(20, 10, 20, 10),
                    border_radius=8,
                    bgcolor="#ff6b35",
                    content=ft.Text(
                        "Present",
                        size=14,
                        color="#ffffff",
                        font_family="Inter",
                        weight="w500"
                    ),
                    on_click=self.handle_attendance_click
                )

                sub_card = ft.Container(
                    margin=ft.Margin(10, 0, 10, 10),
                    border_radius=15,
                    expand=True,
                    padding=ft.Padding(20, 20, 20, 15),
                    bgcolor="#2a2a2a",
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        subject,
                                        size=18,
                                        color="#ffffff",
                                        font_family="Inter",
                                        weight="w600"
                                    ),
                                    ft.Text(
                                        timing,
                                        size=14,
                                        color="#b8b8b8",
                                        font_family="Inter",
                                        weight="w400"
                                    )
                                ]
                            ),
                            ft.Row(
                                spacing=8,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.ProgressBar(
                                        value=  att_per/100,
                                        bgcolor="#4a4a4a",
                                        color="#ff6b35",
                                        expand=True,
                                        height= 8,
                                        border_radius=15
                                    ),
                                    ft.Text(
                                        att_per,
                                        size=16,
                                        color="#ffffff",
                                        font_family="Inter",
                                        weight="w600"
                                    )
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    absent_btn,
                                    present_btn
                                ]
                            )
                        ]
                    )
                )

                # Pass references via each button's data for shared handler use
                absent_btn.data = {"card": sub_card, "present_btn": present_btn, "absent_btn": absent_btn, "status": "absent"}
                present_btn.data = {"card": sub_card, "present_btn": present_btn, "absent_btn": absent_btn, "status": "present"}
                self.content_column.controls.extend([sub_card])

        else:  # No classes for selected date
            date_display = "today" if self.selected_date == datetime.date.today() else f"on {self.selected_date.strftime('%A')}"
            self.content_column.controls.extend( [
                ft.Container(
                    padding=ft.Padding(20, 40, 20, 0),
                    content=ft.Text(
                        f"No classes {date_display} 🎉",
                        size=22,
                        color="#aaaaaa",
                        font_family="Inter",
                        weight="w600",
                    )
                )
            ]
            )

        self.page.update()

    def show_chart_screen(self, e):
        self.update_db()
        self.page.update()
        self.content_column.controls.clear()

        self.home_icon.bgcolor = None
        self.list_icon.bgcolor = None
        self.chart_icon.bgcolor = "#404040"

        self.c.execute("""SELECT * FROM attendance a WHERE rowid = (SELECT MIN(rowid) FROM attendance b WHERE b.subject = a.subject)""" )
        rows = self.c.fetchall()

        if rows:
            for item in rows:
                subject, req_attendance, day, timing, classes_held, classes_attended = item
                att_per = round((classes_attended/classes_held) * 100)

                sub_card = ft.Container(
                    margin=ft.Margin(10, 0, 10, 10),
                    border_radius=15,
                    expand=True,
                    padding=ft.Padding(20, 20, 20, 15),
                    bgcolor="#2a2a2a",
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        subject,
                                        size=18,
                                        color="#ffffff",
                                        font_family="Inter",
                                        weight="w600"
                                    ),
                                ]
                            ),
                            ft.Row(
                                spacing=8,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.ProgressBar(
                                        value=  att_per/100,
                                        bgcolor="#4a4a4a",
                                        color="#ff6b35",
                                        expand=True,
                                        height= 8,
                                        border_radius=15
                                    ),
                                    ft.Text(
                                        att_per,
                                        size=16,
                                        color="#ffffff",
                                        font_family="Inter",
                                        weight="w600"
                                    )
                                ]
                            )
                        ]
                    )
                )

                self.content_column.controls.extend([sub_card])

        else:  # No classes today
            self.content_column.controls.extend( [
                ft.Container(
                    padding=ft.Padding(20, 40, 20, 0),
                    content=ft.Text(
                        "No classes today 🎉",
                        size=22,
                        color="#aaaaaa",
                        font_family="Inter",
                        weight="w600",
                    )
                )
            ]
            )

        self.page.update()

    def show_date_picker(self, e):
        """Show date picker dialog to select a date"""
        def date_changed(e):
            if e.control.value:
                self.selected_date = e.control.value
                # Update the calendar display and refresh the homepage data
                self.show_homepage(e)
        
        date_picker = ft.DatePicker(
            on_change=date_changed,
            first_date=self.sem_date,  # Can't select dates before semester starts
            last_date=datetime.date(2030, 12, 31),
            current_date=self.selected_date,
        )
        
        self.page.overlay.append(date_picker)
        self.page.update()
        self.page.open(date_picker)

    def mark_all_present(self, e):
        """Dummy method to mark all classes as present"""
        # This is a placeholder for future functionality
        print("Mark all present clicked")
        # You can implement actual logic here later
        # For example: update all classes for the selected date to present

    def mark_all_absent(self, e):
        """Dummy method to mark all classes as absent"""
        # This is a placeholder for future functionality
        print("Mark all absent clicked")
        # You can implement actual logic here later
        # For example: update all classes for the selected date to absent

    def show_list_screen(self, e):
        self.update_db()
        self.page.update()
        self.content_column.controls.clear()

        self.home_icon.bgcolor = None
        self.list_icon.bgcolor = "#404040"
        self.chart_icon.bgcolor = None

        # List screen content - showing "nothing to show"
        list_content = ft.Container(
            padding=ft.Padding(20, 40, 20, 0),
            content=ft.Column(
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "nothing to show",
                        size=24,
                        color="#aaaaaa",
                        font_family="Inter",
                        weight="w600",
                    )
                ]
            )
        )

        self.content_column.controls.append(list_content)
        self.page.update()


def main(page: ft.Page):
    tracker(page)


ft.app(target=main)
