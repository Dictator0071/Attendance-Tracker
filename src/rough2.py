import flet as ft

def main(page: ft.Page):
    page.title = "Date Range Picker"

    start_picker = ft.DatePicker()
    end_picker = ft.DatePicker()

    page.overlay.append(start_picker)
    page.overlay.append(end_picker)

    start_field = ft.TextField(label="Start date", read_only=True)
    end_field = ft.TextField(label="End date", read_only=True)

    def open_start(e):
        page.open(start_picker)

    def open_end(e):
        page.open(end_picker)

    def on_start_change(e):
        start_field.value = str(start_picker.value)
        page.update()

    def on_end_change(e):
        end_field.value = str(end_picker.value)
        page.update()

    start_picker.on_change = on_start_change
    end_picker.on_change = on_end_change

    page.add(
        ft.Row([start_field, ft.ElevatedButton("Pick start", on_click=open_start)]),
        ft.Row([end_field, ft.ElevatedButton("Pick end", on_click=open_end)]),
    )

ft.app(target=main)
