import codecs
import os
import sys
import threading
import subprocess
import customtkinter as ctk
from tkinter import Tk, filedialog, messagebox
import tkinter as tk 
# import time
import json
# import tempfile

# Customizing the appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Basic paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JIRA_UPDATER_DIR = os.path.join(BASE_DIR, "jira_updater")
REPORT_CREATOR_DIR = os.path.join(BASE_DIR, "report_creater")
GEO_TRANSLATOR_DIR = os.path.join(BASE_DIR, "geo_translator")

class OfferApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Offer Manager Pro")
        self.geometry("700x700+0+0")
        self.minsize(500, 500)
        
        # icon
        try:
            self.iconbitmap(os.path.join(BASE_DIR, "logo_.ico"))
        except:
            pass
        
        # container for pages
        self.container = ctk.CTkFrame(self, corner_radius=0)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Creating pages
        self.pages = {}
        for Page in (MainMenuPage, 
                     SettingsPage, 
                     OffersInputPage,
                     ReportPage, 
                     GeoTranslatorPage,
                    ):
            page = Page(self.container, self)
            self.pages[Page.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Showing main page
        self.show_page("MainMenuPage")
    
    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()
        page.on_show()

class BasePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        pass
    
    def on_show(self):
        pass

class MainMenuPage(BasePage):
    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # title
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_frame.pack(pady=(50, 30))
        
        self.title = ctk.CTkLabel(self.title_frame, 
                                text="App Manager Pro",
                                font=ctk.CTkFont(size=36, weight="bold"))
        self.title.pack()
        
        self.subtitle = ctk.CTkLabel(self.title_frame,
                                   text="Управление рутинными процессами",
                                   font=ctk.CTkFont(size=16))
        self.subtitle.pack(pady=10)
        
        # start button
        self.start_btn = ctk.CTkButton(self.main_frame,
                                     text="Начать работу",
                                     command=lambda: self.controller.show_page("SettingsPage"),
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     height=50,
                                     width=350)
        self.start_btn.pack(pady=40)
        
        # footer
        self.footer = ctk.CTkLabel(self.main_frame,
                                 text="© 2025 App Manager Pro | Версия 2.0 | 20.04.2025",
                                 font=ctk.CTkFont(size=12))
        self.footer.pack(side="bottom", pady=20)

class SettingsPage(BasePage):
    def setup_ui(self):
        # main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # title
        self.title = ctk.CTkLabel(self.main_frame,
                                text="Меню настроек",
                                font=ctk.CTkFont(size=28, weight="bold"))
        self.title.pack(pady=(0, 30))
        
        # action buttons
        button_options = {
            "font": ctk.CTkFont(size=16),
            "height": 50,
            "corner_radius": 8
        }
        
        self.update_btn = ctk.CTkButton(self.main_frame,
                                      text="Актуализировать настройки в Jira",
                                      command=lambda: self.controller.show_page("OffersInputPage"),
                                      **button_options)
        self.update_btn.pack(fill="x", pady=10)
        
        self.report_btn = ctk.CTkButton(self.main_frame,
                                      text="Еженедельные отчеты",
                                      command=lambda: self.controller.show_page("ReportPage"),
                                      **button_options)
        self.report_btn.pack(fill="x", pady=10)
        
        self.geo_btn = ctk.CTkButton(self.main_frame,
                                   text="Гео переводчик",
                                   command=lambda: self.controller.show_page("GeoTranslatorPage"),
                                   **button_options)
        self.geo_btn.pack(fill="x", pady=10)
        
        self.back_btn = ctk.CTkButton(self.main_frame,
                                    text="Назад",
                                    command=lambda: self.controller.show_page("MainMenuPage"),
                                    fg_color="transparent",
                                    border_width=2,
                                    text_color=("gray10", "#DCE4EE"),
                                    **button_options)
        self.back_btn.pack(fill="x", pady=(30, 10))

class OffersInputPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.task_offer_pairs = []
        self.task_var = ctk.StringVar()
        self.offers_var = ctk.StringVar()
        self.is_processing = False
        self.process = None
        self.stop_processing = False
        self.setup_ui()

    def on_show(self):
        self.task_var.set("")
        self.offers_var.set("")
        self.task_entry.focus()
        self.update_pairs_display()

    def setup_ui(self):
        self.pack_propagate(False)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="Ввод офферов для Jira",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(0, 20), anchor="w")

        # Link to the task in Jira
        ctk.CTkLabel(
            main_frame,
            text="Ссылка на задачу в Jira:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.task_entry = ctk.CTkEntry(
            main_frame,
            font=ctk.CTkFont(size=14),
            height=35,
            placeholder_text="xxxx",
            textvariable=self.task_var,
            border_width=1,
            corner_radius=5
        )
        self.task_entry.pack(fill="x", pady=(0, 15))
        self.task_entry.bind("<Button-3>", self.show_context_menu)
        self.task_entry.focus_set()

        # Field for entering offers
        ctk.CTkLabel(
            main_frame,
            text="Оффер/Оффера:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.offers_entry = ctk.CTkEntry(
            main_frame,
            font=ctk.CTkFont(size=14),
            height=35,
            placeholder_text="1234, 5678, 91011",
            textvariable=self.offers_var,
            border_width=1,
            corner_radius=5
        )
        self.offers_entry.pack(fill="x", pady=(0, 15))
        self.offers_entry.bind("<Button-3>", self.show_context_menu)

        # add button
        ctk.CTkButton(
            main_frame,
            text="+ Добавить",
            command=self.add_task_offer_pair,
            font=ctk.CTkFont(size=14),
            height=35,
            width=100,
            corner_radius=5
        ).pack(pady=(5, 5), anchor="w")

        # Main Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 10))

        center_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        center_frame.pack(expand=True)

        # Start Button
        ctk.CTkButton(
            center_frame,
            text="Запустить",
            command=self.run_processing,
            font=ctk.CTkFont(size=14),
            height=35,
            width=120,
            corner_radius=5,
            fg_color="#4CAF50"
        ).pack(side="left", padx=10)

        # Back Button
        ctk.CTkButton(
            center_frame,
            text="Назад",
            command=lambda: self.controller.show_page("SettingsPage"),
            font=ctk.CTkFont(size=14),
            height=35,
            width=120,
            corner_radius=5,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE")
        ).pack(side="left", padx=10)

        # Logging
        self.log_frame = ctk.CTkFrame(main_frame)
        self.log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=12),
            height=65
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")

        # Progress_bar and status
        self.progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(10, 0))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, mode="determinate")
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame, 
            text="Готов к работе", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack()
        
        self.loading_indicator = ctk.CTkProgressBar(
            self.progress_frame, 
            mode="indeterminate"
        )
        
        # Cancel Button
        self.cancel_btn = ctk.CTkButton(
            self.progress_frame,
            text="Отменить",
            command=self.cancel_processing,
            fg_color="#e74a3b",
            hover_color="#c23d31",
            font=ctk.CTkFont(size=12)
        )

        # Added task Blog
        ctk.CTkLabel(
            main_frame,
            text="Добавленные задачи:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.pairs_container = ctk.CTkScrollableFrame(
            main_frame,
            height=150,
            fg_color="transparent"
        )
        self.pairs_container.pack(fill="both", expand=True, pady=(0, 10))
        self.update_pairs_display()
        


    def show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Вставить", command=lambda: self.paste_text(event.widget))
        menu.tk_popup(event.x_root, event.y_root)

    def paste_text(self, widget):
        try:
            widget.delete(0, tk.END)
            widget.insert(0, self.clipboard_get())
        except tk.TclError:
            pass

    def update_pairs_display(self):
        for widget in self.pairs_container.winfo_children():
            widget.destroy()
        
        if not self.task_offer_pairs:
            empty_label = ctk.CTkLabel(
                self.pairs_container,
                text="Пока здесь пусто, нужно ввести нужные значения в полях выше и нажать \"+ Добавить\"",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color="gray70"
            )
            empty_label.pack(pady=20)
            return
        
        for idx, (task_url, offers) in enumerate(self.task_offer_pairs, 1):
            pair_frame = ctk.CTkFrame(self.pairs_container, fg_color="transparent")
            pair_frame.pack(fill="x", pady=2)
            
            left_frame = ctk.CTkFrame(pair_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                left_frame,
                text=f"{idx}.",
                font=ctk.CTkFont(size=12),
                width=30
            ).pack(side="left", padx=(0, 5))
            
            # ID task
            ctk.CTkLabel(
                left_frame,
                text=task_url,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100
            ).pack(side="left", padx=(0, 10))
            
            # offers
            ctk.CTkLabel(
                left_frame,
                text=offers,
                font=ctk.CTkFont(size=12)
            ).pack(side="left", fill="x", expand=True)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                pair_frame,
                text="×",
                command=lambda i=idx-1: self.remove_pair(i),
                font=ctk.CTkFont(size=14, weight="bold"),
                width=28,
                height=28,
                fg_color="transparent",
                hover_color="#ff6b6b",
                text_color="#ff6b6b",
                corner_radius=15#,
                #border_width=1,
                #border_color="#ff6b6b"
            )
            delete_btn.pack(side="right")
            
            # Hover effects
            delete_btn.bind("<Enter>", lambda e, btn=delete_btn: (
                btn.configure(text_color="white", fg_color="#ff6b6b", border_color="#ff6b6b")
            ))
            delete_btn.bind("<Leave>", lambda e, btn=delete_btn: (
                btn.configure(text_color="#ff6b6b", fg_color="transparent", border_color="#ff6b6b")
            ))

    def remove_pair(self, index):
        if 0 <= index < len(self.task_offer_pairs):
            self.task_offer_pairs.pop(index)
            self.update_pairs_display()

    def add_task_offer_pair(self):
        task_url = self.task_var.get().strip()
        offers = self.offers_var.get().strip()
        
        if not task_url or not offers:
            messagebox.showwarning("Ошибка", "Заполните оба поля!")
            return
            
        self.task_offer_pairs.append((task_url, offers))
        
        self.task_var.set("")
        self.offers_var.set("")
        self.task_entry.focus()
        self.update_pairs_display()

    def run_processing(self):
        if not self.task_offer_pairs:
            messagebox.showwarning("Ошибка", "Нет данных для обработки")
            return
        
        if self.is_processing:
            return
            
        self.clear_log()
        self.is_processing = True
        self.stop_processing = False
        self.update_ui_for_processing(True)

        # Creating a JSON structure
        data = {f"pair{idx}": {"link": link.strip(), "offer": offer.strip()} 
               for idx, (link, offer) in enumerate(self.task_offer_pairs, 1)}

        # starting processing in a separate thread
        threading.Thread(
            target=self.process_data, 
            args=(data,),
            daemon=True
        ).start()

    def process_data(self, data):
        temp_file = None
        try:
            # Creating temporary file
            temp_file = os.path.join(JIRA_UPDATER_DIR, "temp_jira_input.json")
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.update_status(0.1, "Подготовка данных...")
            self.log_message("Подготовка данных...\n")
            
            # The command to run
            cmd = [
                sys.executable,
                os.path.join(JIRA_UPDATER_DIR, "test.py"),
                temp_file
            ]
            
            # Starting the process with output buffering
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=JIRA_UPDATER_DIR,
                encoding='utf-8',
                errors='replace'
            )
            
            self.update_status(0.3, "Обработка задач...")
            self.log_message("Начало обработки задач...\n")
            
            # Reading the output in real time
            for line in iter(self.process.stdout.readline, ''):
                if self.stop_processing:
                    break
                    
                line = line.strip()
                if line:
                    self.log_message(line + "\n")
                    if "Задача" in line and "успешно обновлена" in line:
                        current = len([p for p in self.task_offer_pairs if p[0] in line])
                        progress = 0.3 + 0.7 * (current / len(self.task_offer_pairs))
                        self.update_status(progress, f"Обработано {current} из {len(self.task_offer_pairs)}")
            
            if not self.stop_processing:
                self.update_status(1.0, "Обработка завершена!")
                self.log_message("\nОбработка успешно завершена!\n")
                self.after(100, lambda: messagebox.showinfo(
                    "Успех", 
                    f"Обработано {len(self.task_offer_pairs)} задач"
                ))
            
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}\n"
            self.update_status(0.0, error_msg.strip(), error=True)
            self.log_message(error_msg, error=True)
            self.after(100, lambda: messagebox.showerror(
                "Ошибка", 
                f"Не удалось запустить обработку: {str(e)}"
            ))
            
        finally:
            self.cleanup_processing(temp_file)

    # Output of the message to the log
    def log_message(self, message, error=False):
        self.after(0, lambda: [
            self.log_text.configure(state="normal"),
            self.log_text.insert("end", message, "error" if error else "normal"),
            self.log_text.see("end"),
            self.log_text.configure(state="disabled")
        ])

    # Clearing the log
    def clear_log(self):
        self.after(0, lambda: [
            self.log_text.configure(state="normal"),
            self.log_text.delete("1.0", "end"),
            self.log_text.configure(state="disabled")
        ])

    # Post-treatment cleaning
    def cleanup_processing(self, temp_file):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
                
        self.is_processing = False
        self.process = None
        self.update_ui_for_processing(False)

    # Cancellation of processing
    def cancel_processing(self):
        if self.is_processing:
            self.stop_processing = True
            if self.process:
                self.process.terminate()
            self.update_status(0.0, "Обработка отменена", error=True)

    def update_ui_for_processing(self, processing):
        """Обновление UI в зависимости от состояния"""
        self.after(0, lambda: [
            self.loading_indicator.pack(fill="x", pady=(5, 0)) if processing 
            else self.loading_indicator.pack_forget(),
            self.loading_indicator.start() if processing 
            else self.loading_indicator.stop(),
            self.progress_bar.pack_forget() if processing 
            else self.progress_bar.pack(fill="x"),
            self.cancel_btn.pack(pady=(5, 0)) if processing 
            else self.cancel_btn.pack_forget(),
            [w.configure(state="disabled" if processing else "normal") 
             for w in [self.task_entry, self.offers_entry]]
        ])

    # Progress and status update
    def update_status(self, value, message, error=False):
        self.after(0, lambda: [
            self.progress_bar.set(value),
            self.status_label.configure(
                text=message,
                text_color="#e74a3b" if error else ("gray10", "#DCE4EE")
            )
        ])

    def update_progress(self, value, message, error=False):
        self.after(0, lambda: [
            self.progress_bar.set(value),
            self.status_label.configure(
                text=message,
                text_color="#e74a3b" if error else ("gray10", "#DCE4EE")
            )
        ])

    # Reading the process output
    def read_process_output(self, process):
        total_pairs = len(self.task_offer_pairs)
        current_pair = 0
        
        def reader():
            nonlocal current_pair
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    if "Задача" in output and "успешно обновлена" in output:
                        current_pair += 1
                        progress = 0.3 + 0.7 * (current_pair / total_pairs)
                        self.update_progress(progress, 
                                          f"Обработка {current_pair} из {total_pairs} задач")
            
            return_code = process.poll()
            if return_code == 0:
                print("Обработка завершена успешно!")
            else:
                print(f"Ошибка выполнения (код {return_code})")

        threading.Thread(target=reader, daemon=True).start()

class ReportPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.is_running = False
        self.process = None
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=50, pady=30)
        
        self.title = ctk.CTkLabel(self.main_frame,
                                text="Генерация отчетов",
                                font=ctk.CTkFont(size=28, weight="bold"))
        self.title.pack(pady=(0, 10))
        
        self.progress_label = ctk.CTkLabel(self.main_frame,
                                         text="Нажмите на Запуск Генерации",
                                         font=ctk.CTkFont(size=14))
        self.progress_label.pack(pady=(0, 10))
        
        self.log_area = ctk.CTkTextbox(self.main_frame,
                                     font=ctk.CTkFont(size=12, family="Consolas"),
                                     height=300,
                                     border_width=2,
                                     corner_radius=8)
        self.log_area.pack(fill="both",  pady=(0, 20))
        self.log_area.configure(state="disabled")
        
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", pady=(10, 0))
        
        self.run_btn = ctk.CTkButton(self.btn_frame,
                                   text="Запустить генерацию",
                                   command=self.start_report_generation,
                                   font=ctk.CTkFont(size=16),
                                   height=50,
                                   fg_color="#21ae3f",
                                   hover_color="#156e28")
        self.run_btn.pack(side="left", padx=5, expand=True)
        
        self.stop_btn = ctk.CTkButton(self.btn_frame,
                                    text="Остановить",
                                    command=self.stop_report_generation,
                                    font=ctk.CTkFont(size=16),
                                    height=50,
                                    #state="disabled",
                                    fg_color="#e74a3b",
                                    hover_color="#c23d31",
                                    text_color="#fcf0ed")
        self.stop_btn.pack(side="left", padx=5, expand=True)
        
        self.back_btn = ctk.CTkButton(self.btn_frame,
                                    text="Назад",
                                    command=self.go_back,
                                    font=ctk.CTkFont(size=16),
                                    height=50,
                                    fg_color="transparent",
                                    border_width=2,
                                    text_color=("gray10", "#DCE4EE"))
        self.back_btn.pack(side="left", padx=5, expand=True)
    
    def start_report_generation(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.insert("end", "Запуск генерации отчетов...\n")
        self.log_area.configure(state="disabled")
        self.progress_label.configure(text="Выполняется...")
        
        threading.Thread(target=self.run_converter_script, daemon=True).start()
    
    def run_converter_script(self):
        try:
            script_path = os.path.join(REPORT_CREATOR_DIR, 'converter.py')
            
            if not os.path.exists(script_path):
                self.update_log(f"Ошибка: файл скрипта не найден: {script_path}")
                return
            
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=REPORT_CREATOR_DIR#,
                # env=os.environ
            )
            
            while True:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self.update_log(output.strip())
            
            return_code = self.process.poll()
            if return_code == 0:
                self.update_log("\nГенерация отчетов успешно завершена!")
                self.progress_label.configure(text="Готово!")
            else:
                error_msg = f"\nОшибка выполнения (код {return_code})"
                self.update_log(error_msg)
                self.progress_label.configure(text="Ошибка выполнения")
        
        except Exception as e:
            error_msg = f"\nКритическая ошибка: {str(e)}"
            self.update_log(error_msg)
            self.progress_label.configure(text="Ошибка выполнения")
        finally:
            self.is_running = False
            self.run_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.process = None
    
    def stop_report_generation(self):
        if self.process and self.is_running:
            self.process.terminate()
            self.update_log("\nПроцесс остановлен пользователем")
            self.progress_label.configure(text="Остановлено")
            self.is_running = False
            self.run_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
    
    def update_log(self, message):
        self.log_area.configure(state="normal")
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")
    
    def go_back(self):
        if self.is_running:
            if messagebox.askyesno("Подтверждение", 
                                 "Процесс еще выполняется. Вы уверены, что хотите прервать и выйти?"):
                self.stop_report_generation()
                self.controller.show_page("SettingsPage")
        else:
            self.controller.show_page("SettingsPage")

class GeoTranslatorPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.is_running = False
        self.current_mode = None
        self.process = None
        self.file_path = None
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=50, pady=30)
        
        self.title = ctk.CTkLabel(self.main_frame,
                                text="Гео переводчик KLADR",
                                font=ctk.CTkFont(size=28, weight="bold"))
        self.title.pack(pady=(0, 20))
        
        # The frame for selecting the mode
        self.mode_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.mode_frame.pack(fill="x", pady=(0, 20))
        
        self.mode_label = ctk.CTkLabel(self.mode_frame,
                                     text="Режим работы:",
                                     font=ctk.CTkFont(size=16))
        self.mode_label.pack(side="left", padx=(0, 10))
        
        self.mode_var = ctk.StringVar(value="Выберите режим...")
        self.mode_menu = ctk.CTkOptionMenu(self.mode_frame,
                                         values=[
                                             "КЛАДР -> Адрес",
                                             "Адрес -> КЛАДР"
                                         ],
                                         variable=self.mode_var,
                                         font=ctk.CTkFont(size=14),
                                         width=250)
        self.mode_menu.pack(side="left")

        # The frame for selecting the data entry method
        self.mode_input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.mode_input_frame.pack(fill="x", pady=(0, 20))
        
        self.mode_input_label = ctk.CTkLabel(self.mode_input_frame,
                                     text="Способ ввода данных:",
                                     font=ctk.CTkFont(size=16))
        self.mode_input_label.pack(side="left", padx=(0, 10))
        
        self.mode_input_var = ctk.StringVar(value="Выберите способ...")
        self.mode_input_menu = ctk.CTkOptionMenu(self.mode_input_frame,
                                         values=[
                                             "Загрузить из файла",
                                             "Ввести вручную"
                                         ],
                                         variable=self.mode_input_var,
                                         font=ctk.CTkFont(size=14),
                                         width=250,
                                         command=self.update_input_method)
        self.mode_input_menu.pack(side="left")
        
        # The frame for the line with the name and the input field
        self.output_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.output_frame.pack(fill="x", pady=(0, 15))

        self.output_name_label = ctk.CTkLabel(
            self.output_frame,
            text="Имя нового файла, куда будет сохранён результат:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w", 
            width=180 
        )
        self.output_name_label.pack(side="left", padx=(0, 10))

        self.output_entry = ctk.CTkEntry( 
            self.output_frame,
            font=ctk.CTkFont(size=13),
            height=32, 
            fg_color="#f5f5f5",
            border_color="#4e8cff", 
            border_width=1,
            text_color="#333333", 
            corner_radius=6 
        )
        self.output_entry.pack(side="left", fill="x", expand=True, pady=2)



        self.dynamic_input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dynamic_input_frame.pack(fill="x", pady=(0, 20))
        
        self.setup_file_input()
        self.setup_manual_input()
        
        self.action_frame = ctk.CTkFrame(self.main_frame,
                                        fg_color="transparent")
        self.action_frame.pack(fill="x", pady=10)
        
        self.run_btn = ctk.CTkButton(
                                self.action_frame,
                                text="Перевести",
                                command=self.start_processing,
                                font=ctk.CTkFont(size=16),
                                height=40,
                                fg_color="#1f6aa5",
                                hover_color="#144870"
        )
        self.run_btn.pack(side="left")

        self.back_btn = ctk.CTkButton(self.action_frame,
                                    text="Назад",
                                    command=self.go_back,
                                    font=ctk.CTkFont(size=16),
                                    height=40,
                                    fg_color="transparent",
                                    border_width=2,
                                    text_color=("gray10", "#DCE4EE"))
        self.back_btn.pack(side="right", padx=5)

        self.clear_btn = ctk.CTkButton(self.action_frame,
                                     text="Очистить",
                                     command=self.clear_data,
                                     font=ctk.CTkFont(size=16),
                                     height=40,
                                     fg_color="transparent",
                                     border_width=2,
                                     text_color=("gray10", "#DCE4EE"))
        self.clear_btn.pack(side="right", padx=30)
        
        # Progress and status
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.status_frame.pack(fill="x", pady=(20, 0))
        
        self.progress = ctk.CTkProgressBar(self.status_frame, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 10))
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(self.status_frame,
                                       text="Готов к работе",
                                       font=ctk.CTkFont(size=14))
        self.status_label.pack()

        self.hide_all_input_methods()


        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.pack(fill="both", pady=(10, 0))
        
        self.log_area = ctk.CTkTextbox(self.log_frame, 
                                    font=ctk.CTkFont(size=12, family="Consolas"),
                                    wrap="word", height=90,)
        self.log_area.pack(fill="both", padx=5, pady=5)
        self.log_area.configure(state="disabled")
        
        self.log_area.tag_config("error", foreground="#FF5555")
        self.log_area.tag_config("success", foreground="#55FF55")

        self.loading_indicator = ctk.CTkProgressBar(self.status_frame, mode='indeterminate')

        # When starting the process
        self.loading_indicator.start()
        self.loading_indicator.pack(fill="x", pady=5)

        # Upon completion
        self.loading_indicator.stop()
        self.loading_indicator.pack_forget()

    # Configuring the interface for uploading a file
    def setup_file_input(self):
        self.file_input_frame = ctk.CTkFrame(self.dynamic_input_frame,
                                            fg_color="transparent")
        
        self.file_selection_frame = ctk.CTkFrame(self.file_input_frame, 
                                            fg_color="transparent")
        self.file_selection_frame.pack(side="top", anchor="w", fill="x", pady=(0, 5))

        
        self.file_btn = ctk.CTkButton(self.file_selection_frame,
                                    text="Выбрать файл*",
                                    command=self.select_file,
                                    font=ctk.CTkFont(size=14),
                                    width=150)
        self.file_btn.pack(side="left", padx=(0, 10))
        
        self.file_path_label = ctk.CTkLabel(self.file_selection_frame,
                                          text="Файл не выбран",
                                          font=ctk.CTkFont(size=12),
                                          wraplength=400,
                                          justify="left")
        self.file_path_label.pack(side="left", fill="x")
        
        self.file_hint = ctk.CTkLabel(self.file_input_frame,
                                    text="Поддерживаемые форматы: Excel (.xlsx, .xls), CSV (.csv) ",
                                    font=ctk.CTkFont(size=12,
                                                     slant="italic"),
                                    text_color="gray")
        self.file_hint.pack(side="top", anchor="w", padx=(10, 0), pady=(0, 5))
    
    # Configuring the interface for manual input
    def setup_manual_input(self):
        self.manual_input_frame = ctk.CTkFrame(self.dynamic_input_frame)
        
        self.manual_input_label = ctk.CTkLabel(self.manual_input_frame,
                                             text="Введите данные (по одному значению на строку):",
                                             font=ctk.CTkFont(size=14, weight="bold"))
        self.manual_input_label.pack(anchor="w", pady=(0, 5))
        
        self.manual_input_text = ctk.CTkTextbox(self.manual_input_frame,
                                              font=ctk.CTkFont(size=12, family="Consolas"),
                                              height=90,
                                              wrap="none")
        self.manual_input_text.pack(fill="both", expand=True)
    
    # Updating the interface depending on the selected input method"
    def update_input_method(self, choice):
        self.hide_all_input_methods()
        
        if choice == "Загрузить из файла":
            self.file_input_frame.pack(fill="x", pady=(0, 10))
        elif choice == "Ввести вручную":
            self.manual_input_frame.pack(fill="both", expand=True)
    
    # Hides all data entry options
    def hide_all_input_methods(self):
        for widget in self.dynamic_input_frame.winfo_children():
            widget.pack_forget()
    
    def select_file(self):
        filetypes = (
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv")
        )
        
        file_path = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=filetypes
        )
        
        if file_path:
            self.file_path = file_path
            self.file_path_label.configure(text=file_path)

    def run_kladr_script(self, params_dict):
            try:
                self.is_running = True
                self.clear_log()
                self.log_message("Запуск обработки...\n")
                
                kladr_script_path = os.path.join(GEO_TRANSLATOR_DIR, "kladr.py")
                command = [
                    sys.executable,
                    kladr_script_path,
                    params_dict["mode"],
                    params_dict["input_method"],
                    params_dict["output_filename"]
                ]
                
                if params_dict["input_method"] == "1":  # File input
                    command.extend([
                        "--file_type", params_dict["file_type"],
                        "--input_filename", params_dict["input_filename"]
                    ])
                else:  # Manual input
                    command.extend(params_dict["values"])
                
                self.log_message(f"Выполняемая команда: {' '.join(command)}\n")
                
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    encoding='utf-8',
                    cwd=GEO_TRANSLATOR_DIR
                )
                
                # Reading the output in real time
                threading.Thread(
                    target=self.read_output_stream,
                    args=(self.process.stdout, False),
                    daemon=True
                ).start()
                threading.Thread(
                    target=self.read_output_stream,
                    args=(self.process.stderr, True),
                    daemon=True
                ).start()
                
            except Exception as e:
                self.log_message(f"Ошибка запуска: {str(e)}\n", error=True)
                self.is_running = False
                self.toggle_run_button(False)

    def read_stream(self, stream, is_error):
        decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
        while True:
            out = stream.read(1)
            if not out and self.process.poll() is not None:
                break
            if out:
                try:
                    text = decoder.decode(out)
                    if text:
                        self.after(0, self.log_message, text, is_error)
                except Exception as e:
                    self.after(0, self.log_message, f"Ошибка декодирования: {str(e)}", True)

        self.after(0, self.on_script_finished)

    def log_message(self, text, error=False):
        try:
            self.log_area.configure(state="normal")
            self.log_area.insert("end", text)
            if error:
                self.log_area.tag_add("error", "end-%dc" % (len(text)+1), "end")
            self.log_area.see("end")
            self.log_area.configure(state="disabled")
        except Exception as e:
            print(f"Ошибка вывода в лог: {e}")

    def clear_log(self):
        if hasattr(self, 'log_area'):
            self.log_area.configure(state="normal")
            self.log_area.delete("1.0", "end")
            self.log_area.configure(state="disabled")

    def on_script_finished(self):
            if not hasattr(self, 'process_finished'):
                self.process_finished = True
                return_code = self.process.poll()
                
                if return_code == 0:
                    self.status_label.configure(text="Готово!", text_color="#1cc88a")
                    self.log_message("Обработка завершена успешно!\n")
                else:
                    self.status_label.configure(text="Ошибка выполнения", text_color="#d9534f")
                
                self.is_running = False
                self.toggle_run_button(False)
                self.progress.stop()
                del self.process_finished

    def start_processing(self):
        if self.is_running:
            return
        
        self.toggle_run_button(True)

        params = {
            "mode": "1" if self.mode_var.get() == "КЛАДР -> Адрес" else "2",
            "input_method": "1" if self.mode_input_var.get() == "Загрузить из файла" else "2",
            "output_filename": os.path.splitext(self.output_entry.get().strip())[0]
        }
        
        if params["input_method"] == "1":  # File input
            if not self.file_path:
                messagebox.showwarning("Ошибка", "Выберите файл для загрузки")
                return
            
            file_ext = os.path.splitext(self.file_path)[1].lower()
            params.update({
                "file_type": "1" if file_ext == '.csv' else "2",
                "input_filename": os.path.splitext(os.path.basename(self.file_path))[0]
            })
        else:  # Manual input
            input_text = self.manual_input_text.get("1.0", "end-1c").strip()
            if not input_text:
                messagebox.showwarning("Ошибка", "Введите данные для преобразования")
                return
            
            params["values"] = [line.strip() for line in input_text.split('\n') if line.strip()]
        
        self.run_kladr_script(params)

    def clear_data(self):
        if hasattr(self, 'manual_input_text'):
            self.manual_input_text.delete("1.0", "end")
        
        self.file_path = None
        if hasattr(self, 'file_path_label'):
            self.file_path_label.configure(text="Файл не выбран")
        
        self.status_label.configure(text="Готов к работе", text_color=("gray10", "#DCE4EE"))
        self.progress.set(0)
    
    def go_back(self):
        if self.is_running:
            if messagebox.askyesno("Подтверждение", 
                                 "Процесс еще выполняется. Вы уверены, что хотите прервать и выйти?"):
                self.is_running = False
                self.progress.stop()
                self.progress.set(0)
                self.controller.show_page("SettingsPage")
        else:
            self.controller.show_page("SettingsPage")
    
    def read_output_stream(self, stream, is_error):
        while True:
            output = stream.readline()
            if not output and self.process.poll() is not None:
                break
            if output:
                self.after(0, self.log_message, output, is_error)
        
        self.after(0, self.on_script_finished)

    # Switches the button state between 'Translate' and 'Stop'
    def toggle_run_button(self, running):
        if running:
            self.run_btn.configure(
                text="Остановить",
                command=self.stop_processing,
                fg_color="#d9534f",
                hover_color="#a94442"
            )
        else:
            self.run_btn.configure(
                text="Перевести",
                command=self.start_processing,
                fg_color="#1f6aa5",
                hover_color="#144870"
            )
        self.update_idletasks()

    # Stopping the process execution
    def stop_processing(self):
        if hasattr(self, 'process') and self.process:
            try:
                self.process.terminate()
                self.log_message("\nПроцесс остановлен пользователем\n", error=True)
                self.status_label.configure(text="Остановлено", text_color="#d9534f")
            except Exception as e:
                self.log_message(f"\nОшибка при остановке: {str(e)}\n", error=True)
            finally:
                self.cleanup_after_process()

    # Cleaning after completion of the process
    def cleanup_after_process(self):
        self.is_running = False
        self.toggle_run_button(False)
        self.progress.stop()
        
        # Secure deletion of a temporary file
        if hasattr(self, 'temp_json_path') and self.temp_json_path:
            try:
                if os.path.exists(self.temp_json_path):
                    os.unlink(self.temp_json_path)
            except Exception as e:
                pass

if __name__ == "__main__":
    app = OfferApp()
    app.mainloop()