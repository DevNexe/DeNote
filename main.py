import flet as ft
import os
from datetime import datetime
from flet import FilePickerResultEvent

def main(page: ft.Page):
    # Настройка страницы
    page.title = "DeNote"
    page.window_width = 750
    page.window_height = 350
    page.padding = 0
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    # Переменные для управления вкладками
    current_tab_index = 0
    tabs = []
    tab_contents = []
    
    # Функция для добавления новой вкладки
    def add_new_tab(e=None, content="", filename=""):
        nonlocal current_tab_index
        
        # Имя файла по умолчанию для новой вкладки
        if not filename:
            filename = f"Untitled-{len(tabs) + 1}.txt"
        
        # Создание текстового поля для содержимого вкладки
        text_field = ft.TextField(
            value=content,
            multiline=True,
            min_lines=30,
            max_lines=99,
            expand=True,
            border="none",
            on_change=update_tab_status
        )
        
        # Function to close this specific tab
        def close_this_tab(e):
            tab_idx = tabs.index(tab)
            # Check if file has unsaved changes
            if tab_contents[tab_idx]["modified"]:
                # Set current tab to this one before showing dialog
                tabs_view.selected_index = tab_idx
                nonlocal current_tab_index
                current_tab_index = tab_idx
                page.update()
                
                # Update dialog content with specific filename
                confirmation_dialog.title = ft.Text(f"Сохранить изменения в {tab_contents[tab_idx]['filename']}?")
                confirmation_dialog.content = ft.Text("Файл был изменен. Хотите сохранить изменения перед закрытием?")
                confirmation_dialog.open = True
                page.update()
            else:
                # Close tab directly if not modified
                tabs.pop(tab_idx)
                tab_contents.pop(tab_idx)
                if len(tabs) > 0:
                    # Adjust current tab index
                    current_tab_index = min(current_tab_index, len(tabs) - 1)
                    tabs_view.selected_index = current_tab_index
                    tabs_view.tabs = tabs
                    update_status_bar()
                else:
                    # If no tabs left, add a new tab
                    page.window.close()
        
        # Create tab with text and close button
        tab = ft.Tab(
            tab_content=ft.Row(
                [
                    ft.Text(filename),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        icon_size=16,
                        tooltip="Закрыть",
                        on_click=close_this_tab,
                    ),
                ],
                spacing=5,
                tight=True,
            ),
            content=ft.Container(
                content=text_field,
                expand=True,
                padding=10
            )
        )
        
        # Создание и добавление информации о состоянии вкладки
        tab_info = {
            "text_field": text_field,
            "filename": filename,
            "saved": True,
            "last_saved": None,
            "modified": False
        }
        
        # Добавляем вкладку и её содержимое
        tabs.append(tab)
        tab_contents.append(tab_info)
        
        # Обновляем интерфейс
        tabs_view.tabs = tabs
        tabs_view.selected_index = len(tabs) - 1
        current_tab_index = len(tabs) - 1
        update_status_bar()
        page.update()
    
    # Обновление статуса вкладки при изменении текста
    def update_tab_status(e):
        if 0 <= current_tab_index < len(tab_contents):
            tab_contents[current_tab_index]["modified"] = True
            
            # Get the filename text element from the tab
            tab_text = tabs[current_tab_index].tab_content.controls[0]
            tab_text.value = f"● {tab_contents[current_tab_index]['filename']}"
            
            update_status_bar()
            page.update()
    
    # Обновление статусной строки
    def update_status_bar():
        if 0 <= current_tab_index < len(tab_contents):
            content = tab_contents[current_tab_index]["text_field"].value or ""
            char_count.value = f"Символов: {len(content)}"
            line_count.value = f"Строк: {content.count(os.linesep) + 1 if content else 1}"
            if tab_contents[current_tab_index]["last_saved"]:
                last_saved.value = f"Последнее сохранение: {tab_contents[current_tab_index]['last_saved'].strftime('%H:%M:%S')}"
            else:
                last_saved.value = "Не сохранено"
            page.update()
    
    # Функция для сохранения текущей вкладки
    def save_current_tab(e=None):
        if 0 <= current_tab_index < len(tab_contents):
            try:
                filename = tab_contents[current_tab_index]["filename"]
                content = tab_contents[current_tab_index]["text_field"].value
                
                def save_file_result(e: FilePickerResultEvent):
                    if e.path:
                        # Сохраняем содержимое в выбранный файл
                        try:
                            with open(e.path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            # Обновляем имя файла в данных вкладки
                            tab_contents[current_tab_index]["filename"] = os.path.basename(e.path)
                            tab_contents[current_tab_index]["saved"] = True
                            tab_contents[current_tab_index]["modified"] = False
                            tab_contents[current_tab_index]["last_saved"] = datetime.now()
                            
                            # Обновляем текст вкладки
                            tab_text = tabs[current_tab_index].tab_content.controls[0]
                            tab_text.value = os.path.basename(e.path)
                            
                            show_snackbar(f"Файл '{os.path.basename(e.path)}' успешно сохранен")
                            update_status_bar()
                        except Exception as ex:
                            show_snackbar(f"Ошибка при сохранении: {str(ex)}", "error")
                
                # Устанавливаем обработчик результата
                file_picker.on_result = save_file_result
                
                # Открываем диалог сохранения
                file_picker.save_file(
                    file_name=filename if filename != "Untitled.txt" else "Untitled.txt",
                    allowed_extensions=["txt", "md", "py", "js", "html", "css", "json"],
                    initial_directory=os.getcwd(),
                )
                
            except Exception as ex:
                show_snackbar(f"Ошибка при сохранении: {str(ex)}", "error")
            
    # Функция обработки результата выбора файлов - определяем перед использованием!
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            try:
                file_path = e.files[0].path
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                add_new_tab(content=content, filename=filename)
                show_snackbar(f"Файл '{filename}' успешно загружен")
            except Exception as ex:
                show_snackbar(f"Ошибка при чтении файла: {str(ex)}", "error")
    
    # Функция для загрузки файла
    def load_file(e=None):
        file_picker.pick_files(
            allowed_extensions=["txt", "md", "py", "js", "html", "css", "json"],
            initial_directory=os.getcwd(),
        )
    
    # Функция для переключения между вкладками
    def change_tab(e):
        nonlocal current_tab_index
        current_tab_index = e.control.selected_index
        update_status_bar()
    
    # Функция для закрытия текущей вкладки (используется для диалога)
    def close_current_tab(e=None):
        nonlocal current_tab_index
        if len(tabs) > 0:
            # Если вкладка изменена, показать диалог подтверждения
            if tab_contents[current_tab_index]["modified"]:
                # Update dialog content with specific filename
                confirmation_dialog.title = ft.Text(f"Сохранить изменения в {tab_contents[current_tab_index]['filename']}?")
                confirmation_dialog.content = ft.Text("Файл был изменен. Хотите сохранить изменения перед закрытием?")
                confirmation_dialog.open = True
                page.update()
                return
            
            # Иначе закрыть вкладку
            _close_tab_without_confirmation()
    
    # Функция для закрытия вкладки без подтверждения
    def _close_tab_without_confirmation():
        nonlocal current_tab_index
        if len(tabs) > 0:
            tabs.pop(current_tab_index)
            tab_contents.pop(current_tab_index)
            
            # Если после закрытия остались вкладки
            if len(tabs) > 0:
                current_tab_index = min(current_tab_index, len(tabs) - 1)
                tabs_view.selected_index = current_tab_index
                tabs_view.tabs = tabs
                update_status_bar()
                page.update()
            else:
                # Если вкладок не осталось, добавить новую
                add_new_tab()
    
    # Функции для диалога подтверждения
    def close_dialog(e):
        confirmation_dialog.open = False
        page.update()
    
    def confirm_close_without_saving(e):
        confirmation_dialog.open = False
        _close_tab_without_confirmation()
    
    def save_and_close(e):
        confirmation_dialog.open = False
        save_current_tab()
        _close_tab_without_confirmation()
    
    # Handle application close event
    def on_window_event(e):
        if e.data == "close":
            # Check if any tabs have unsaved changes
            unsaved_tabs = [tab_contents[i]["filename"] for i in range(len(tab_contents)) if tab_contents[i]["modified"]]
            
            if unsaved_tabs:
                # Show dialog for unsaved changes
                if len(unsaved_tabs) == 1:
                    confirmation_dialog.title = ft.Text(f"Сохранить изменения в {unsaved_tabs[0]}?")
                    confirmation_dialog.content = ft.Text("Файл был изменен. Хотите сохранить изменения перед выходом?")
                else:
                    confirmation_dialog.title = ft.Text("Сохранить изменения?")
                    confirmation_dialog.content = ft.Text(f"У вас есть несохраненные изменения в {len(unsaved_tabs)} файлах. Хотите сохранить изменения перед выходом?")
                
                confirmation_dialog.open = True
                page.update()
                e.prevent_default = True
    
    # Register window event handler
    page.on_window_event = on_window_event
    
    # Функция для отображения уведомлений
    def show_snackbar(message, severity="success"):
        color = "#0067c0" if severity == "success" else "#c42b1c"
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=color,
            action="OK",
        )
        page.snack_bar = snack_bar
        snack_bar.open = True
        page.update()
    
    # Создание компонентов интерфейса
    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)
    
    # Верхняя панель с кнопками (без кнопки закрытия)
    top_app_bar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(icon=ft.icons.ADD,tooltip="Новый файл",on_click=add_new_tab), 
                ft.IconButton(
                    icon=ft.icons.FOLDER_OPEN,
                    tooltip="Открыть файл",
                    on_click=load_file
                ),
                ft.IconButton(
                    icon=ft.icons.SAVE,
                    tooltip="Сохранить файл",
                    on_click=save_current_tab
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=10,
        border=ft.border.only(bottom=ft.border.BorderSide(1)),
    )
    
    # Виджет вкладок
    tabs_view = ft.Tabs(
        selected_index=0,
        on_change=change_tab,
        tabs=[],
        expand=True
    )
    
    # Создаем контейнер для вкладок с кнопкой добавления справа
    tabs_container = ft.Container(
        content=ft.Row(
            [
                # The tab bar will expand to fill available space
                ft.Container(
                    content=tabs_view,
                    expand=True,
                ),
            ],
            spacing=0,
        ),
        expand=True,
    )
    
    # Статусная строка
    char_count = ft.Text("Символов: 0")
    line_count = ft.Text("Строк: 1", size=12)
    last_saved = ft.Text("Не сохранено", size=12)
    
    status_bar = ft.Container(
        content=ft.Row(
            [
                char_count,
                ft.VerticalDivider(width=1),
                line_count,
                ft.VerticalDivider(width=1),
                last_saved,
                ft.Container(expand=True),
                ft.Text("UTF-8", size=12),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border=ft.border.only(top=ft.border.BorderSide(1)),
        height=30,
    )
    
    # Диалог подтверждения закрытия
    confirmation_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Сохранить изменения?"),
        content=ft.Text("Вы хотите сохранить изменения в файле перед закрытием?"),
        actions=[
            ft.TextButton("Отмена", on_click=close_dialog),
            ft.TextButton("Не сохранять", on_click=confirm_close_without_saving),
            ft.TextButton("Сохранить", on_click=save_and_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Добавляем все компоненты на страницу
    page.add(
        top_app_bar,
        tabs_container,  # Use the container with tabs and add button
        status_bar
    )
    
    # Создаем первую вкладку автоматически
    add_new_tab()

if __name__ == "__main__":
    ft.app(target=main, view=ft.FLET_APP)