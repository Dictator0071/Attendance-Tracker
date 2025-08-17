import flet as ft


class ClassDialogTest:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Class Dialog Test"
        self.page.bgcolor = "#0a0a0a"
        self.page.padding = 20
        self.page.fonts = {
            "Inter": "https://rsms.me/inter/font-files/Inter-Regular.woff2",
            "Inter Bold": "https://rsms.me/inter/font-files/Inter-Bold.woff2"
        }

        # State variables for the dialog
        self.selected_weekday = "Thursday"
        self.selected_start_time = "12:00"
        self.selected_end_time = "13:00"
        self.current_tab = 0

        # Create main UI
        self.create_main_ui()

    def create_main_ui(self):
        # Test button to open dialog
        test_button = ft.ElevatedButton(
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

        # Display current selections
        self.result_display = ft.Container(
            padding=ft.Padding(20, 20, 20, 20),
            bgcolor="#2a2a2a",
            border_radius=15,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        "Current Selection:",
                        size=18,
                        color="#ffffff",
                        font_family="Inter",
                        weight="w600"
                    ),
                    ft.Text(
                        f"Weekday: {self.selected_weekday}",
                        size=14,
                        color="#e0e0e0",
                        font_family="Inter"
                    ),
                    ft.Text(
                        f"Start Time: {self.selected_start_time}",
                        size=14,
                        color="#e0e0e0",
                        font_family="Inter"
                    ),
                    ft.Text(
                        f"End Time: {self.selected_end_time}",
                        size=14,
                        color="#e0e0e0",
                        font_family="Inter"
                    )
                ]
            )
        )

        # Main layout
        main_content = ft.Column(
            spacing=30,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Class Dialog Test App",
                    size=32,
                    color="#ffffff",
                    font_family="Inter",
                    weight="w800"
                ),
                ft.Text(
                    "Click the button below to test the class dialog",
                    size=16,
                    color="#b8b8b8",
                    font_family="Inter"
                ),
                test_button,
                self.result_display
            ]
        )

        self.page.add(main_content)

    def add_class_dialog(self, e):
        # Time picker for start time
        self.start_time_picker = ft.TimePicker(
            confirm_text="Confirm",
            error_invalid_text="Time out of range",
            help_text="Select start time",
            on_change=self.on_start_time_change,
            on_dismiss=lambda e: print("Start TimePicker dismissed"),
        )

        # Time picker for end time
        self.end_time_picker = ft.TimePicker(
            confirm_text="Confirm",
            error_invalid_text="Time out of range",
            help_text="Select end time",
            on_change=self.on_end_time_change,
            on_dismiss=lambda e: print("End TimePicker dismissed"),
        )

        # Add time pickers to page overlay
        self.page.overlay.extend([self.start_time_picker, self.end_time_picker])

        # Create weekday selection content
        def create_weekday_tab():
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            return ft.Container(
                padding=ft.Padding(20, 20, 20, 20),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.RadioGroup(
                            content=ft.Column(
                                spacing=15,
                                controls=[
                                    ft.Radio(
                                        value=day,
                                        label=day,
                                        label_style=ft.TextStyle(
                                            color="#ffffff",
                                            size=18,
                                            font_family="Inter"
                                        ),
                                        active_color="#ff6b35",
                                    )
                                    for day in weekdays
                                ]
                            ),
                            value=self.selected_weekday,
                            on_change=lambda e: setattr(self, 'selected_weekday', e.control.value)
                        )
                    ]
                )
            )

        # Create start time tab
        def create_start_time_tab():
            return ft.Container(
                padding=ft.Padding(20, 40, 20, 20),
                content=ft.Column(
                    spacing=30,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Start Time",
                            size=24,
                            color="#ffffff",
                            font_family="Inter",
                            weight="w600"
                        ),

                        # Display current selected time
                        ft.Container(
                            padding=ft.Padding(30, 20, 30, 20),
                            bgcolor="#404040",
                            border_radius=15,
                            content=ft.Text(
                                self.selected_start_time,
                                size=36,
                                color="#ff6b35",
                                font_family="Inter",
                                weight="w700"
                            )
                        ),

                        # Button to open time picker
                        ft.ElevatedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.ACCESS_TIME, color="#ffffff"),
                                    ft.Text("Select Time", color="#ffffff", font_family="Inter")
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=8,
                                tight=True
                            ),
                            bgcolor="#ff6b35",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding(20, 15, 20, 15),
                            ),
                            on_click=lambda e: self.start_time_picker.pick_time()
                        )
                    ]
                )
            )

        # Create end time tab
        def create_end_time_tab():
            return ft.Container(
                padding=ft.Padding(20, 40, 20, 20),
                content=ft.Column(
                    spacing=30,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "End Time",
                            size=24,
                            color="#ffffff",
                            font_family="Inter",
                            weight="w600"
                        ),

                        # Display current selected time
                        ft.Container(
                            padding=ft.Padding(30, 20, 30, 20),
                            bgcolor="#404040",
                            border_radius=15,
                            content=ft.Text(
                                self.selected_end_time,
                                size=36,
                                color="#ff6b35",
                                font_family="Inter",
                                weight="w700"
                            )
                        ),

                        # Button to open time picker
                        ft.ElevatedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.ACCESS_TIME, color="#ffffff"),
                                    ft.Text("Select Time", color="#ffffff", font_family="Inter")
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=8,
                                tight=True
                            ),
                            bgcolor="#ff6b35",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding(20, 15, 20, 15),
                            ),
                            on_click=lambda e: self.end_time_picker.pick_time()
                        )
                    ]
                )
            )

        # Create the main tabs
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tab_alignment=ft.TabAlignment.CENTER,
            indicator_color="#ff6b35",
            label_color="#ff6b35",
            unselected_label_color="#ffffff",
            tabs=[
                ft.Tab(
                    text="Weekday",
                    content=create_weekday_tab()
                ),
                ft.Tab(
                    text="Start Time",
                    content=create_start_time_tab()
                ),
                ft.Tab(
                    text="End Time",
                    content=create_end_time_tab()
                )
            ],
            on_change=self.on_tab_change
        )

        # Create the dialog
        self.class_dialog = ft.AlertDialog(
            modal=True,
            bgcolor="#2a2a2a",
            content_padding=ft.Padding(0, 20, 0, 0),
            title=ft.Text(
                "Select weekday, start time and end time for the new class",
                size=16,
                color="#ffffff",
                font_family="Inter",
                weight="w400"
            ),
            content=ft.Container(
                width=400,
                height=400,
                content=tabs
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    style=ft.ButtonStyle(color="#ffffff"),
                    on_click=self.close_class_dialog
                ),
                ft.TextButton(
                    "OK",
                    style=ft.ButtonStyle(color="#ff6b35"),
                    on_click=self.save_class
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = self.class_dialog
        self.class_dialog.open = True
        self.page.update()

    def on_tab_change(self, e):
        self.current_tab = e.control.selected_index

    def on_start_time_change(self, e):
        if e.control.value:
            # Format time to HH:MM
            time_obj = e.control.value
            self.selected_start_time = f"{time_obj.hour:02d}:{time_obj.minute:02d}"

            # Update the dialog display
            if hasattr(self, 'class_dialog') and self.class_dialog.open:
                # Find and update the start time display
                start_tab = self.class_dialog.content.content.tabs[1].content
                time_display = start_tab.content.controls[1].content
                time_display.value = self.selected_start_time
                self.page.update()

    def on_end_time_change(self, e):
        if e.control.value:
            # Format time to HH:MM
            time_obj = e.control.value
            self.selected_end_time = f"{time_obj.hour:02d}:{time_obj.minute:02d}"

            # Update the dialog display
            if hasattr(self, 'class_dialog') and self.class_dialog.open:
                # Find and update the end time display
                end_tab = self.class_dialog.content.content.tabs[2].content
                time_display = end_tab.content.controls[1].content
                time_display.value = self.selected_end_time
                self.page.update()

    def close_class_dialog(self, e):
        if hasattr(self, 'class_dialog'):
            self.class_dialog.open = False

            # Clean up time pickers from overlay
            if hasattr(self, 'start_time_picker') and self.start_time_picker in self.page.overlay:
                self.page.overlay.remove(self.start_time_picker)
            if hasattr(self, 'end_time_picker') and self.end_time_picker in self.page.overlay:
                self.page.overlay.remove(self.end_time_picker)

            self.page.update()

    def save_class(self, e):
        # Handle saving the class with selected values
        print(f"Saved class: {self.selected_weekday} from {self.selected_start_time} to {self.selected_end_time}")

        # Update the result display
        self.result_display.content.controls[1].value = f"Weekday: {self.selected_weekday}"
        self.result_display.content.controls[2].value = f"Start Time: {self.selected_start_time}"
        self.result_display.content.controls[3].value = f"End Time: {self.selected_end_time}"

        # Close dialog
        self.close_class_dialog(e)


def main(page: ft.Page):
    ClassDialogTest(page)


# Run the app
if __name__ == "__main__":
    ft.app(target=main)