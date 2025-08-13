import flet as ft
from datetime import datetime, time, date, timedelta
from enum import Enum
from typing import List, Optional, Tuple, Dict
import sqlite3
import json
from dataclasses import dataclass, asdict
from pathlib import Path


# Data Models
class CourseClassStatus(Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    CANCELLED = "Cancelled"
    UNSET = "Unset"


@dataclass
class ClassDetail:
    day_of_week: int  # 0-6 (Monday=0)
    start_time: time
    end_time: time
    schedule_id: Optional[int] = None
    included_in_schedule: bool = True


@dataclass
class AttendanceCounts:
    percent: float
    present: int
    absents: int
    cancels: int
    unsets: int
    required_percentage: float


@dataclass
class AttendanceRecordHybrid:
    course_name: str
    course_id: int
    start_time: time
    end_time: time
    class_status: CourseClassStatus
    date: date


class ScheduledClass(AttendanceRecordHybrid):
    def __init__(self, attendance_id: Optional[int], schedule_id: Optional[int],
                 course_id: int, course_name: str, start_time: time, end_time: time,
                 class_status: CourseClassStatus, record_date: date):
        super().__init__(course_name, course_id, start_time, end_time, class_status, record_date)
        self.attendance_id = attendance_id
        self.schedule_id = schedule_id


class ExtraClass(AttendanceRecordHybrid):
    def __init__(self, extra_class_id: int, course_id: int, course_name: str,
                 start_time: time, end_time: time, class_status: CourseClassStatus, record_date: date):
        super().__init__(course_name, course_id, start_time, end_time, class_status, record_date)
        self.extra_class_id = extra_class_id


@dataclass
class CourseDetailsOverallItem:
    course_id: int
    course_name: str
    required_attendance: float
    current_attendance_percentage: float
    presents: int
    absents: int
    cancels: int
    unsets: int


# Database Operations
class DBOps:
    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                required_attendance_percentage REAL NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                weekday INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                included_in_schedule INTEGER DEFAULT 1,
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER,
                extra_class_id INTEGER,
                date TEXT NOT NULL,
                class_status TEXT NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (schedule_id) REFERENCES schedule (id),
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extra_classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                class_status TEXT NOT NULL,
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        ''')

        conn.commit()
        conn.close()

    def create_course(self, name: str, required_attendance_percentage: float,
                      schedule: List[ClassDetail]) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO courses (name, required_attendance_percentage) VALUES (?, ?)",
            (name, required_attendance_percentage)
        )
        course_id = cursor.lastrowid

        for class_detail in schedule:
            cursor.execute(
                "INSERT INTO schedule (course_id, weekday, start_time, end_time, included_in_schedule) VALUES (?, ?, ?, ?, ?)",
                (course_id, class_detail.day_of_week,
                 class_detail.start_time.strftime("%H:%M"),
                 class_detail.end_time.strftime("%H:%M"),
                 1 if class_detail.included_in_schedule else 0)
            )

        conn.commit()
        conn.close()
        return course_id

    def get_schedule_and_extra_classes_for_today(self) -> List[Tuple[AttendanceRecordHybrid, AttendanceCounts]]:
        today = date.today()
        weekday = today.weekday()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get scheduled classes for today
        cursor.execute('''
            SELECT a.id, s.id, c.id, c.name, s.start_time, s.end_time, a.class_status, a.date
            FROM courses c
            JOIN schedule s ON c.id = s.course_id
            LEFT JOIN attendance a ON s.id = a.schedule_id AND a.date = ?
            WHERE s.weekday = ?
        ''', (today.isoformat(), weekday))

        scheduled_classes = []
        for row in cursor.fetchall():
            attendance_id, schedule_id, course_id, course_name, start_time_str, end_time_str, class_status_str, date_str = row

            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            class_status = CourseClassStatus(class_status_str) if class_status_str else CourseClassStatus.UNSET
            record_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else today

            scheduled_class = ScheduledClass(
                attendance_id, schedule_id, course_id, course_name,
                start_time, end_time, class_status, record_date
            )

            # Get attendance counts
            counts = self._get_course_attendance_percentage(course_id)
            scheduled_classes.append((scheduled_class, counts))

        # Get extra classes for today
        cursor.execute('''
            SELECT ec.id, c.id, c.name, ec.start_time, ec.end_time, ec.class_status, ec.date
            FROM courses c
            JOIN extra_classes ec ON c.id = ec.course_id
            WHERE ec.date = ?
        ''', (today.isoformat(),))

        extra_classes = []
        for row in cursor.fetchall():
            extra_class_id, course_id, course_name, start_time_str, end_time_str, class_status_str, date_str = row

            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            class_status = CourseClassStatus(class_status_str)
            record_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            extra_class = ExtraClass(
                extra_class_id, course_id, course_name,
                start_time, end_time, class_status, record_date
            )

            counts = self._get_course_attendance_percentage(course_id)
            extra_classes.append((extra_class, counts))

        conn.close()

        # Combine and sort by start time
        all_classes = scheduled_classes + extra_classes
        all_classes.sort(key=lambda x: x[0].start_time, reverse=True)
        return all_classes

    def _get_course_attendance_percentage(self, course_id: int) -> AttendanceCounts:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                SUM(CASE WHEN class_status = 'Present' THEN 1 ELSE 0 END) as presents,
                SUM(CASE WHEN class_status = 'Absent' THEN 1 ELSE 0 END) as absents,
                SUM(CASE WHEN class_status = 'Cancelled' THEN 1 ELSE 0 END) as cancels,
                SUM(CASE WHEN class_status = 'Unset' THEN 1 ELSE 0 END) as unsets,
                required_attendance_percentage
            FROM courses c
            LEFT JOIN (
                SELECT schedule_id, class_status, course_id FROM attendance WHERE schedule_id IS NOT NULL
                UNION ALL
                SELECT extra_class_id, class_status, course_id FROM attendance WHERE extra_class_id IS NOT NULL
            ) a ON c.id = a.course_id
            WHERE c.id = ?
            GROUP BY c.id
        ''', (course_id,))

        row = cursor.fetchone()
        conn.close()

        if row and row[0] is not None:
            presents, absents, cancels, unsets, required_percentage = row
            total = presents + absents
            percent = 100.0 if total == 0 else (presents / total) * 100
            return AttendanceCounts(percent, presents, absents, cancels, unsets, required_percentage)
        else:
            return AttendanceCounts(100.0, 0, 0, 0, 0, 75.0)

    def mark_attendance_for_schedule_class(self, attendance_id: Optional[int],
                                           class_status: CourseClassStatus,
                                           schedule_id: Optional[int],
                                           record_date: date, course_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if attendance_id:
            cursor.execute(
                "UPDATE attendance SET class_status = ? WHERE id = ?",
                (class_status.value, attendance_id)
            )
        else:
            cursor.execute(
                "INSERT INTO attendance (schedule_id, date, class_status, course_id) VALUES (?, ?, ?, ?)",
                (schedule_id, record_date.isoformat(), class_status.value, course_id)
            )

        conn.commit()
        conn.close()

    def mark_attendance_for_extra_class(self, extra_class_id: int, status: CourseClassStatus):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE extra_classes SET class_status = ? WHERE id = ?",
            (status.value, extra_class_id)
        )

        conn.commit()
        conn.close()


# Main Application
class AttendanceTrackerApp:
    def __init__(self):
        self.db_ops = DBOps()
        self.current_tab = 0
        self.today_items = []
        self.user_name = "Rudra Agrawal"
        self.page = None

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Self Attendance Tracker"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0
        page.spacing = 0

        # Initialize with some sample data
        self._add_sample_data()
        self.today_items = self.db_ops.get_schedule_and_extra_classes_for_today()

        # Create main content
        self.content_area = ft.Container(
            content=self._build_today_tab(),
            expand=True
        )

        # Bottom navigation
        bottom_nav = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.CALENDAR_TODAY,
                    label="Today"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.TABLE_CHART,
                    label="Attendance"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.TABLE_CHART,
                    label="Grades"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.PERSON,
                    label="Profile"
                )
            ],
            on_change=self._on_tab_change,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE_VARIANT),
            indicator_color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE_VARIANT)
        )

        # Floating Action Button
        self.fab = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=self._on_fab_click,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE_VARIANT),
            visible=self.current_tab == 0
        )

        # Main layout
        page.add(
            ft.Column([
                self.content_area,
                bottom_nav
            ], expand=True),
            self.fab
        )

        page.update()

    def _build_today_tab(self):
        # Greeting section
        greeting = ft.Column([
            ft.Text(
                "Hi",
                size=24,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.ON_SURFACE
            ),
            ft.Text(
                self.user_name,
                size=32,
                weight=ft.FontWeight.W_800,
                color=ft.Colors.ON_SURFACE
            ),
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT)
        ], spacing=12)

        # Today's classes list
        classes_list = ft.Column(
            spacing=12,
            expand=True
        )

        for item, counts in self.today_items:
            card = self._create_class_card(item, counts)
            classes_list.controls.append(card)

        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=greeting,
                    padding=ft.padding.only(left=16, right=16, top=36, bottom=12)
                ),
                ft.Container(
                    content= classes_list,
                    padding=ft.padding.only(left=16, right=16),
                    expand=True
                )
            ]),
            expand=True
        )

    def _create_class_card(self, item: AttendanceRecordHybrid, counts: AttendanceCounts):
        is_marked = item.class_status != CourseClassStatus.UNSET

        # Card content
        card_content = ft.Container(
            content=ft.Column([
                # Header row
                ft.Row([
                    ft.Text(
                        item.course_name,
                        size=20,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.ON_SURFACE_VARIANT if is_marked else ft.Colors.ON_SURFACE,
                        expand=True
                    ),
                    ft.Text(
                        f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}",
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                # Progress bar
                ft.ProgressBar(
                    value=counts.percent / 100.0,
                    color=ft.Colors.PRIMARY,
                    bgcolor=ft.Colors.SURFACE
                ),

                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                # Footer row
                ft.Row([
                    ft.Text(
                        f"{int(counts.percent)}% attendance",
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Container() if not is_marked else ft.Container(
                        content=ft.Text(
                            item.class_status.value,
                            size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.W_500
                        ),
                        bgcolor=self._get_status_color(item.class_status),
                        padding=ft.padding.all(8),
                        border_radius=ft.border_radius.all(20)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            padding=ft.padding.all(16)
        )

        # Create swipeable card
        return ft.GestureDetector(
            content=ft.Card(
                content=card_content,
                color=self._get_card_color(item.class_status),
                elevation=2,
                margin=ft.margin.only(bottom=12)
            ),
            on_pan_end=self._on_swipe_end(item, counts)
        )

    def _get_status_color(self, status: CourseClassStatus):
        if status == CourseClassStatus.PRESENT:
            return ft.Colors.GREEN
        elif status == CourseClassStatus.ABSENT:
            return ft.Colors.RED
        elif status == CourseClassStatus.CANCELLED:
            return ft.Colors.ORANGE
        else:
            return ft.Colors.PRIMARY

    def _get_card_color(self, status: CourseClassStatus):
        base_color = ft.Colors.ON_SURFACE_VARIANT
        if status == CourseClassStatus.PRESENT:
            return ft.Colors.with_opacity(0.12, ft.Colors.GREEN)
        elif status == CourseClassStatus.ABSENT:
            return ft.Colors.with_opacity(0.12, ft.Colors.RED)
        else:
            return base_color

    def _on_swipe_end(self, item: AttendanceRecordHybrid, counts: AttendanceCounts):
        def handle_swipe(e: ft.DragEndEvent):
            if e.primary_velocity and abs(e.primary_velocity) > 500:
                if e.primary_velocity > 0:  # Swipe right - Present
                    self._mark_attendance(item, CourseClassStatus.PRESENT)
                else:  # Swipe left - Absent
                    self._mark_attendance(item, CourseClassStatus.ABSENT)

        return handle_swipe

    def _mark_attendance(self, item: AttendanceRecordHybrid, status: CourseClassStatus):
        if isinstance(item, ScheduledClass):
            self.db_ops.mark_attendance_for_schedule_class(
                item.attendance_id, status, item.schedule_id, item.date, item.course_id
            )
        elif isinstance(item, ExtraClass):
            self.db_ops.mark_attendance_for_extra_class(item.extra_class_id, status)

        # Update the item status
        item.class_status = status

        # Move to bottom of list
        self.today_items.remove((item, self._get_updated_counts(item)))
        self.today_items.append((item, self._get_updated_counts(item)))

        # Refresh the UI
        self._refresh_ui()

    def _get_updated_counts(self, item: AttendanceRecordHybrid) -> AttendanceCounts:
        return self.db_ops._get_course_attendance_percentage(item.course_id)

    def _refresh_ui(self):
        if self.page:
            # Rebuild the content area
            self.content_area.content = self._build_today_tab()
            self.page.update()

    def _on_tab_change(self, e):
        self.current_tab = e.control.selected_index
        # Update FAB visibility
        self.fab.visible = self.current_tab == 0
        self.page.update()

    def _on_fab_click(self, e):
        # Show create course dialog
        self._show_create_course_dialog()

    def _show_create_course_dialog(self):
        course_name_field = ft.TextField(
            label="Course Name",
            border=ft.InputBorder.UNDERLINE,
            expand=True
        )

        attendance_field = ft.TextField(
            label="Required Attendance %",
            border=ft.InputBorder.UNDERLINE,
            value="75",
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True
        )

        def create_course(e):
            try:
                name = course_name_field.value
                attendance = float(attendance_field.value)

                if name and attendance > 0:
                    # Create a simple schedule (Monday-Friday, 9 AM - 10 AM)
                    schedule = []
                    for day in range(5):  # Monday to Friday
                        schedule.append(ClassDetail(
                            day_of_week=day,
                            start_time=time(9, 0),
                            end_time=time(10, 0)
                        ))

                    self.db_ops.create_course(name, attendance, schedule)

                    # Refresh today's items
                    self.today_items = self.db_ops.get_schedule_and_extra_classes_for_today()
                    self.page.dialog.open = False
                    # Refresh the UI
                    self._refresh_ui()

                    # Show success message
                    self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Course '{name}' created successfully!")))

            except ValueError:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Please enter valid values")))

        dialog = ft.AlertDialog(
            title=ft.Text("Create New Course"),
            content=ft.Column([
                course_name_field,
                ft.Divider(height=16),
                attendance_field
            ], spacing=16),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(self.page.dialog, 'open', False)),
                ft.ElevatedButton("Create", on_click=create_course)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()

    def _add_sample_data(self):
        # Add a sample course if none exists
        conn = sqlite3.connect(self.db_ops.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM courses")
        if cursor.fetchone()[0] == 0:
            # Add sample course
            schedule = [
                ClassDetail(0, time(9, 0), time(10, 0)),  # Monday
                ClassDetail(1, time(10, 0), time(11, 0)),  # Tuesday
                ClassDetail(2, time(11, 0), time(12, 0)),  # Wednesday
            ]
            self.db_ops.create_course("Sample Course", 75.0, schedule)
        conn.close()


def main():
    app = AttendanceTrackerApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
