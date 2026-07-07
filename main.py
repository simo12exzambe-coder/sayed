from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.clock import Clock
import sqlite3
from datetime import datetime
import threading

class UniversityApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        self.init_db()
        
        # الشاشة الرئيسية
        screen = MDScreen()
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # عنوان البرنامج
        from kivymd.uix.label import MDLabel
        layout.add_widget(MDLabel(
            text="S-9 ZINAR | منظم المواد الجامعية",
            font_style="H5",
            halign="center",
            theme_text_color="Primary"
        ))
        
        # حقل إدخال اسم المادة
        self.subject_input = MDTextField(
            hint_text="اسم المادة الدراسية",
            halign="right",
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5}
        )
        layout.add_widget(self.subject_input)
        
        # أزرار القوائم المنسدلة الاختيارية
        menu_layout = MDBoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(50))
        
        self.btn_year = MDRaisedButton(text="السنة", on_release=self.open_year_menu)
        self.btn_month = MDRaisedButton(text="الشهر", on_release=self.open_month_menu)
        self.btn_day = MDRaisedButton(text="اليوم", on_release=self.open_day_menu)
        self.btn_hour = MDRaisedButton(text="الساعة", on_release=self.open_hour_menu)
        self.btn_min = MDRaisedButton(text="الدقيقة", on_release=self.open_min_menu)
        
        menu_layout.add_widget(self.btn_year)
        menu_layout.add_widget(self.btn_month)
        menu_layout.add_widget(self.btn_day)
        menu_layout.add_widget(self.btn_hour)
        menu_layout.add_widget(self.btn_min)
        layout.add_widget(menu_layout)
        
        # زر الحفظ
        save_btn = MDRaisedButton(
            text="حفظ المادة وتفعيل التنبيه",
            pos_hint={"center_x": 0.5},
            on_release=self.save_data
        )
        layout.add_widget(save_btn)
        
        # جدول عرض البيانات المرتب
        self.data_table = MDDataTable(
            size_hint=(0.9, 0.5),
            pos_hint={"center_x": 0.5},
            use_pagination=True,
            column_data=[
                ("المادة", dp(30)),
                ("التاريخ والوقت", dp(40)),
            ],
            row_data=[]
        )
        layout.add_widget(self.data_table)
        
        screen.add_widget(layout)
        
        # تحديث الجدول عند فتح التطبيق
        self.update_table()
        
        # بدء فحص المنبه في الخلفية
        Clock.schedule_interval(self.check_alarm, 10)
        
        return screen

    def init_db(self):
        self.conn = sqlite3.connect("university_app.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS schedule 
                              (id INTEGER PRIMARY KEY, subject TEXT, datetime_full TEXT)''')
        self.conn.commit()

    # إنشاء وإدارة القوائم المنسدلة الاختيارية
    def open_year_menu(self, button):
        items = [{"text": str(y), "viewclass": "OneLineListItem", "on_release": lambda x=str(y): self.set_menu_val(button, x)} for y in range(2026, 2031)]
        MDDropdownMenu(caller=button, items=items, width_mult=3).open()

    def open_month_menu(self, button):
        items = [{"text": f"{m:02d}", "viewclass": "OneLineListItem", "on_release": lambda x=f"{m:02d}": self.set_menu_val(button, x)} for m in range(1, 13)]
        MDDropdownMenu(caller=button, items=items, width_mult=2).open()

    def open_day_menu(self, button):
        items = [{"text": f"{d:02d}", "viewclass": "OneLineListItem", "on_release": lambda x=f"{d:02d}": self.set_menu_val(button, x)} for d in range(1, 32)]
        MDDropdownMenu(caller=button, items=items, width_mult=2).open()

    def open_hour_menu(self, button):
        items = [{"text": f"{h:02d}", "viewclass": "OneLineListItem", "on_release": lambda x=f"{h:02d}": self.set_menu_val(button, x)} for h in range(0, 24)]
        MDDropdownMenu(caller=button, items=items, width_mult=2).open()

    def open_min_menu(self, button):
        items = [{"text": f"{m:02d}", "viewclass": "OneLineListItem", "on_release": lambda x=f"{m:02d}": self.set_menu_val(button, x)} for m in range(0, 60)]
        MDDropdownMenu(caller=button, items=items, width_mult=2).open()

    def set_menu_val(self, button, val):
        button.text = val

    def save_data(self, instance):
        subject = self.subject_input.text.strip()
        if not subject or self.btn_year.text == "السنة":
            return
        
        dt_full = f"{self.btn_year.text}-{self.btn_month.text}-{self.btn_day.text} {self.btn_hour.text}:{self.btn_min.text}"
        
        self.cursor.execute("INSERT INTO schedule (subject, datetime_full) VALUES (?, ?)", (subject, dt_full))
        self.conn.commit()
        
        self.subject_input.text = ""
        self.update_table()

    def update_table(self):
        self.cursor.execute("SELECT subject, datetime_full FROM schedule")
        rows = self.cursor.fetchall()
        self.data_table.row_data = rows

    def check_alarm(self, dt):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute("SELECT id, subject, datetime_full FROM schedule")
        rows = self.cursor.fetchall()
        for row in rows:
            if row[2] == now:
                # تفعيل التنبيه (طباعة وإشعار أندرويد داخلي)
                print(f"🔔 تنبيه S-9 ZINAR: موعد مادة {row[1]}")
                self.cursor.execute("DELETE FROM schedule WHERE id = ?", (row[0],))
                self.conn.commit()
                self.update_table()

if __name__ == "__main__":
    UniversityApp().run()