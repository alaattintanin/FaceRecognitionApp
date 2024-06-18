import os
import json
import sqlite3
import numpy as np
import cv2
import face_recognition
import tkinter as tk
from tkinter import messagebox, ttk
import itertools


class CNNFaceRecognition:
    def __init__(self, master, title):
        # Arayüz kodları--------------------------------------------------------------------------------------------------------
        self.master = master
        self.master.title(title)
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        self.tabCheck = ttk.Notebook(master)
        self.tabCheck.pack(expand=1, fill="both")

        self.tab_check = ttk.Frame(self.tabCheck)
        self.tabCheck.add(self.tab_check, text="Kontrol")

        self.tab_register = tk.Frame(self.tabCheck)
        self.tabCheck.add(self.tab_register, text='Kayıt')

        self.tab_list = tk.Frame(self.tabCheck)
        self.tabCheck.add(self.tab_list, text='Liste')

        self.tab_delete = ttk.Frame(self.tabCheck)
        self.tabCheck.add(self.tab_delete, text="Sil")

        self.canvas = tk.Canvas(self.tab_check, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH),
                                height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()
        self.label = tk.Label(self.tab_check, text="")
        self.label.pack()

        self.btn_check = tk.Button(self.tab_check, text="Yüzü Tara", command=self.check_person)
        self.btn_check.pack()

        # Listeleme

        frame_list = tk.Frame(self.tab_list)
        frame_list.pack(pady=10)

        self.listbox = tk.Listbox(frame_list, width=40, height=10)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(frame_list, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        refresh_button = tk.Button(self.tab_list, text="Kayıtları Yenile", command=self.show_registered_people)
        refresh_button.pack(pady=10)

        # Kayıt

        self.entry_register_label = tk.Label(self.tab_register, text="KAYIT YAPILIRKEN LÜTFEN KAMERAYA BAKIN")
        self.entry_register_label.pack(pady=(10, 0))
        self.entry_name_label = tk.Label(self.tab_register, text="Ad")
        self.entry_name_label.pack()
        self.entry_name = tk.Entry(self.tab_register)
        self.entry_name.pack()

        self.entry_surname_label = tk.Label(self.tab_register, text="Soyad")
        self.entry_surname_label.pack()
        self.entry_surname = tk.Entry(self.tab_register)
        self.entry_surname.pack()

        self.entry_identify_no_label = tk.Label(self.tab_register, text="Kimlik No (UNIQ)")
        self.entry_identify_no_label.pack()
        self.entry_identify_no = tk.Entry(self.tab_register)
        self.entry_identify_no.pack()

        self.btn_register = tk.Button(self.tab_register, text="Kişiyi Kaydet", command=self.register_person)
        self.btn_register.pack()

        # Silme
        self.entry_delete_label = tk.Label(self.tab_delete, text="KAYIT SİLERKEN LÜTFEN KAMERAYA BAKIN")
        self.entry_delete_label.pack(pady=(10, 0))
        self.entry_delete_label = tk.Label(self.tab_delete, text="Kimlik no")
        self.entry_delete_label.pack()

        self.entry_delete_identify_no = tk.Entry(self.tab_delete)
        self.entry_delete_identify_no.pack()

        self.btn_delete = tk.Button(self.tab_delete, text="Kişiyi Sil", command=self.delete_person)
        self.btn_delete.pack()

        self.message_label_delete = tk.Label(self.tab_delete, text="")
        self.message_label_delete.pack()
        # -------------------------------------------------------------------------------------------------------------
        self.known_faces = {}
        self.photo = None
        self.face_encoding = None
        self.update()
        self.db_filename = "people.db"
        self.conn = sqlite3.connect(self.db_filename)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.known_faces = self.load_database()
        self.show_registered_people()

    # Tablo oluşturma
    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS known_faces (
                                identify_no INT,
                                stored_vectors BLOB,
                                name TEXT,
                                surname TEXT
                            )''')
        self.conn.commit()

    def load_database(self):
        self.cursor.execute("SELECT identify_no, name, surname, stored_vectors FROM known_faces")
        rows = self.cursor.fetchall()
        known_faces = {}
        for row in rows:
            face_id, name, surname, stored_vectors_json = row
            stored_vectors = json.loads(stored_vectors_json)
            known_faces[face_id] = {"name": name, "surname": surname, "stored_vectors": stored_vectors}
        return known_faces

    def save_database(self):
        for face_id, person in self.known_faces.items():
            stored_vectors_json = json.dumps(person["stored_vectors"])
            self.cursor.execute(
                "INSERT OR REPLACE INTO known_faces (identify_no, name, surname, stored_vectors) VALUES (?, ?, ?, ?)",
                (face_id, person["name"], person["surname"], stored_vectors_json))
        self.conn.commit()

    def search_in_database(self, query_face_encoding):
        for identify_no, known_face in self.known_faces.items():
            stored_vectors = known_face["stored_vectors"]
            matches = [face_recognition.compare_faces([np.array(vector)], query_face_encoding, tolerance=0.6)[0] for
                       vector in stored_vectors]
            if True in matches:
                index = matches.index(True)
                return True, known_face["name"], known_face["surname"], identify_no
        return False, "", "", ""

    def show_registered_people(self):
        self.listbox.delete(0, tk.END)

        for identify_no, person in self.known_faces.items():
            person_info = f"{person['name']} {person['surname']} ({identify_no})"
            self.listbox.insert(tk.END, person_info)
    def register_person(self):
        ret, frame = self.vid.read()

        if not ret:
            messagebox.showwarning("Warning!", "Kamera bağlantısı başarısız. Lütfen tekrar deneyin.")
            return

        face_encoding = self.extract_face_encoding(frame)
        if face_encoding is None:
            messagebox.showwarning("Warning!", "Yüz tanıma başarısız. Lütfen doğrudan kameraya bakın.")
            return

        name = self.entry_name.get()
        surname = self.entry_surname.get()
        identify_no = self.entry_identify_no.get()

        if not (name and surname and identify_no):
            messagebox.showwarning("Warning!", "Ad, soyad ve kimlik no bilgileri boş bırakılamaz.")
            return

        self.cursor.execute("SELECT COUNT(*) FROM known_faces WHERE identify_no=?", (identify_no,))
        count = self.cursor.fetchone()[0]
        if count > 0:
            messagebox.showwarning("Warning!", "Bu kimlik numarası zaten kayıtlı.")
            return

        if self.is_duplicate_person(identify_no, face_encoding):
            messagebox.showwarning("Warning!", "Bu yüz zaten veri tabanında kayıtlı.")
            return

        if face_encoding.size == 0:
            messagebox.showwarning("Warning!", "Yüz vektörü bulunamadı. Lütfen doğrudan kameraya bakın.")
            return

        self.known_faces[identify_no] = {"name": name, "surname": surname, "stored_vectors": [face_encoding.tolist()]}
        messagebox.showinfo("Success", "Kişi kaydedildi.")

        stored_vectors_json = json.dumps(self.known_faces[identify_no]["stored_vectors"])
        self.cursor.execute(
            "INSERT INTO known_faces (identify_no, name, surname, stored_vectors) VALUES (?, ?, ?, ?)",
            (identify_no, name, surname, stored_vectors_json))
        self.conn.commit()

        self.show_registered_people()
    def delete_person(self):
        identify_no = self.entry_delete_identify_no.get()

        if identify_no not in self.known_faces:
            messagebox.showwarning("Warning!", "Bu kimlik numarası veri tabanında kayıtlı değil.")
            return

        ret, frame = self.vid.read()
        if not ret:
            messagebox.showwarning("Warning!", "Kamera bağlantısı başarısız. Lütfen tekrar deneyin.")
            return

        entered_face_encoding = self.extract_face_encoding(frame)
        if entered_face_encoding is None:
            messagebox.showwarning("Warning!", "Lütfen doğrudan kameraya bakın.")
            return

        match_found = False
        for stored_vector in self.known_faces[identify_no]["stored_vectors"]:
            if face_recognition.compare_faces([np.array(stored_vector)], entered_face_encoding, tolerance=0.6)[0]:
                match_found = True
                break

        if match_found:

            self.cursor.execute("DELETE FROM known_faces WHERE identify_no=?", (identify_no,))
            self.conn.commit()
            del self.known_faces[identify_no]
            self.show_registered_people()
            messagebox.showinfo("Success", "Kişi veritabanından başarıyla silindi.")
        else:
            messagebox.showwarning("Warning!", "Kameradaki kişi bu kimlik numarasına sahip değil.")


    def update(self):
        ret, frame = self.vid.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = self.convert_frame_to_photo(frame_rgb)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.master.after(10, self.update)

    def convert_frame_to_photo(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        photo = tk.PhotoImage(data=self.convert_frame_to_base64(frame_rgb))
        return photo

    def convert_frame_to_base64(self, frame):
        _, img_encoded = cv2.imencode('.png', frame)
        return img_encoded.tobytes()


    def check_person(self):
        ret, frame = self.vid.read()

        if ret:
            face_encoding = self.extract_face_encoding(frame)

            if face_encoding is not None:
                match, name, surname, identify_no = self.search_in_database(face_encoding)

                if match:
                    messagebox.showinfo("Info", f"\nAd: {name}\nSoyad: {surname}\nKimlik No: {identify_no}")
                else:
                    messagebox.showinfo("Info", "Veri tabanı kaydı bulunmamaktadır!")


    def is_vector_duplicate(self, new_vector, current_identify_no):
        for identify_no, known_face in self.known_faces.items():
            if identify_no == current_identify_no:
                continue
            for stored_vector in known_face["stored_vectors"]:
                if np.array_equal(new_vector, np.array(stored_vector)):
                    return True
        return False

    def merge_similar_vectors(self, tolerance=0.6):
        merged_known_faces = {}

        for identify_no, known_face in self.known_faces.items():
            merged_vector_found = False
            for merged_identify_no, merged_face in merged_known_faces.items():
                for stored_vector in known_face["stored_vectors"]:
                    if any(face_recognition.compare_faces([np.array(stored_vector)],
                                                          np.array(merged_face["stored_vectors"][0]),
                                                          tolerance=tolerance)):
                        merged_face["stored_vectors"].extend(known_face["stored_vectors"])
                        merged_vector_found = True
                        break

            if not merged_vector_found:
                merged_known_faces[identify_no] = {"name": known_face["name"], "surname": known_face["surname"],
                                                   "stored_vectors": [np.array(v).tolist() for v in
                                                                      known_face["stored_vectors"]]}

        self.known_faces = merged_known_faces
        self.save_database()


    def is_duplicate_person(self, current_identify_no, new_face_encoding, tolerance=0.6):
        new_encoding_array = np.array(new_face_encoding)
        all_stored_vectors = itertools.chain.from_iterable(known_face["stored_vectors"]
                                                           for known_face in self.known_faces.values())
        for stored_vector in all_stored_vectors:
            stored_array = np.array(stored_vector)
            if any(face_recognition.compare_faces([new_encoding_array], stored_array, tolerance=tolerance)):
                return True
        return False


    def extract_face_encoding(self, frame):
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        if face_encodings:
            return face_encodings[0]
        else:
            messagebox.showwarning("Error", "Lütfen kameraya bakın.")
            return None


root = tk.Tk()
main = CNNFaceRecognition(root, "Kimlik Kontrol Uygulaması")
root.mainloop()
