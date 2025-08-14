def __init__(self, page: ft.Page):
    # ... existing initialization code ...

    # Create the main stack that will hold both home and overlay screens
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

    # Add the stack instead of the column
    self.page.add(self.main_stack)

    # Add FAB to overlay
    self.page.overlay.append(self.fab)

    # Show homepage by default
    self.show_homepage(None)


def create_sub_screen(self, e):
    # Create the overlay screen
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
                                        ft.Text(
                                            "Required Attendance: 75%",
                                            size=18,
                                            color="#ffffff",
                                            font_family="Inter",
                                            weight="w600",
                                        ),

                                        # Custom slider
                                        ft.Container(
                                            padding=ft.Padding(0, 10, 0, 0),
                                            content=ft.Slider(
                                                min=0,
                                                max=100,
                                                divisions=100,
                                                value=75,
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
    attendance_value = int(e.control.value)
    print(f"Attendance changed to: {attendance_value}%")


def add_class_dialog(self, e):
    # Handle add class functionality
    print("Add class dialog")


def save_course(self, e):
    # Handle save course functionality
    print("Save course")
    # Close overlay after saving
    self.close_overlay_screen(None)