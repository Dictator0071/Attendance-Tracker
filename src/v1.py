import flet as ft
import datetime


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

        self.attend_val = 75
        self.class_duration = 55

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
        self.list_icon = ft.IconButton(
            icon=ft.Icons.LIST_ALT_ROUNDED,
            icon_color="#e0e0e0"
        )
        self.chart_icon = ft.IconButton(
            icon=ft.Icons.INSERT_CHART_ROUNDED,
            icon_color="#e0e0e0"
        )

        # Navigation Bar
        self.nav_bar = ft.Container(
            padding=ft.padding.symmetric(vertical=0, horizontal=0),
            expand=True,  # Expand to fill available space
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    self.home_icon,
                    self.list_icon,
                    self.chart_icon
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

        self.page.add(self.main_stack)
        # Add FAB to overlay
        self.page.overlay.append(self.fab)
        # Show homepage by default
        self.show_homepage(None)

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

        overlay_screen = ft.Container(
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
                                    content=ft.TextField(
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
                            # on_click=self.save_course
                        )
                    )
                ]
            )
        )

        # Add the overlay screen to the stack
        self.main_stack.controls.append(overlay_screen)

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

    def on_attendance_change(self, e):
        # Handle attendance percentage change
        self.attend_val = int(e.control.value)
        self.attendance_label.value = f"Required Attendance: {self.attend_val}"
        self.page.update()

    def add_class_dialog(self, e):
        print("Add class dialog")

    def get_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 18:
            return "Good afternoon"
        else:
            return "Good evening"

    def show_homepage(self,e):
        self.content_column.controls.clear()

        self.home_icon.bgcolor = "#404040"
        self.list_icon.bgcolor = None
        self.chart_icon.bgcolor = None

        greet_text = ft.Container(
            padding=ft.Padding(20,40,20,0),
            content=ft.Column(
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
            )
        )

        sub_card = ft.Container(
            margin=ft.Margin(10, 0, 10, 10),
            border_radius=15,
            expand=True,
            padding=ft.Padding(20, 20, 20, 15),
            bgcolor="#2a2a2a",  # Dark background like in the image
            content=ft.Column(
                spacing=15,
                controls=[
                    # Top section with subject and time
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Mathematics",
                                size=18,
                                color="#ffffff",
                                font_family="Inter",
                                weight="w600"
                            ),
                            ft.Text(
                                "10:00 - 11:00 AM",
                                size=14,
                                color="#b8b8b8",
                                font_family="Inter",
                                weight="w400"
                            )
                        ]
                    ),

                    # Progress section
                    ft.Row(
                        spacing=8,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            # Progress bar
                            ft.Container(
                                height=8,
                                border_radius=4,
                                bgcolor="#4a4a4a",  # Background of progress bar
                                expand=True,  # Takes available space
                                content=ft.Container(
                                    width=None,  # This will be calculated based on percentage
                                    height=8,
                                    border_radius=4,
                                    bgcolor="#ff6b35",  # Orange progress color
                                    # For 85% progress, you might want to set width dynamically
                                )
                            ),
                            # Percentage text
                            ft.Text(
                                "85%",
                                size=16,
                                color="#ffffff",
                                font_family="Inter",
                                weight="w600"
                            )
                        ]
                    ),

                    # Bottom buttons section
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                padding=ft.Padding(20, 10, 20, 10),
                                border_radius=8,
                                bgcolor="#f5f5f5",  # Light background for Present
                                content=ft.Text(
                                    "Present",
                                    size=14,
                                    color="#2a2a2a",  # Dark text
                                    font_family="Inter",
                                    weight="w500"
                                )
                            ),
                            ft.Container(
                                padding=ft.Padding(20, 10, 20, 10),
                                border_radius=8,
                                bgcolor="#ff6b35",  # Orange background for Absent
                                content=ft.Text(
                                    "Absent",
                                    size=14,
                                    color="#ffffff",  # White text
                                    font_family="Inter",
                                    weight="w500"
                                )
                            )
                        ]
                    )
                ]
            )
        )
        # Add all components to the content column
        self.content_column.controls.extend([
            greet_text,
            sub_card
        ])

        self.page.update()


def main(page: ft.Page):
    tracker(page)


ft.app(target=main)
