import tkinter as tk
import os
import datetime
from tkinter import filedialog
from PIL import Image, ImageTk
from googletrans import Translator

def resize_image(image, width, height):
    return image.resize((width, height), Image.ANTIALIAS)

def show_image(image_path):
    if os.path.exists(image_path):
        original_image = Image.open(image_path)
        canvas_width = image_canvas.winfo_width()
        canvas_height = image_canvas.winfo_height()

        aspect_ratio = original_image.width / original_image.height

        if canvas_width / canvas_height < aspect_ratio:
            image_width = canvas_width
            image_height = int(canvas_width / aspect_ratio)
        else:
            image_height = canvas_height
            image_width = int(canvas_height * aspect_ratio)

        resized_image = resize_image(original_image, image_width, image_height)
        photo = ImageTk.PhotoImage(resized_image)
        image_canvas.delete('all')
        image_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        image_canvas.image = photo

def clear_text_and_image():
    text.delete(1.0, tk.END)
    image_canvas.delete('all')

def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()
        text.delete(1.0, tk.END)
        text.insert(tk.END, content)
def update_file_list():
    global files
    directory = directory_entry.get()

    if not directory:
        directory = filedialog.askdirectory()
        if not directory:
            directory = os.getcwd()
            directory_entry.insert(0, directory)

    png_files = [file_name for file_name in os.listdir(directory) if file_name.endswith(".png")]
    txt_files = [file_name for file_name in os.listdir(directory) if file_name.endswith(".txt")]

    # .png 파일만 있는 경우, .txt 파일 생성
    for png_file in png_files:
        txt_file = os.path.splitext(png_file)[0] + ".txt"
        if txt_file not in txt_files:
            create_info_txt(os.path.join(directory, png_file))

    # .png 파일이 없는 .txt 파일 삭제 및 버튼 삭제
    for txt_file in txt_files:
        png_file = os.path.splitext(txt_file)[0] + ".png"
        if png_file not in png_files:
            txt_file_path = os.path.join(directory, txt_file)
            os.remove(txt_file_path)
            continue

    for widget in file_button_frame.winfo_children():
        widget.destroy()

    row_index = 0
    col_index = 0
    buttons_per_row = 2

    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            file_path = os.path.join(directory, file_name)
            file_base_name = os.path.splitext(file_name)[0]
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

            # 해당 .txt 파일에 대응하는 .png 파일이 있을 때만 버튼 생성
            if f"{file_base_name}.png" in png_files:
                # .txt 확장자를 제거한 파일 이름
                korean_name = translate_to_korean(file_base_name)
                button_text = f"{korean_name} "#(입고일: {creation_time})
                #button_text = f"{korean_name} (입고일: {creation_time.strftime('%Y-%m-%d %H:%M')})"

                button = tk.Button(file_button_frame, text=button_text, command=lambda path=file_path: (load_file(path), show_image(f"{path[:-4]}.png")))

                button.config(width=32, height=1)
                button.grid(row=row_index, column=col_index, sticky="w", padx=5, pady=5)

                col_index += 1
                if col_index >= buttons_per_row:
                    col_index = 0
                    row_index += 1


def remove_png_extension(file_name):
    if file_name.lower().endswith(".png"):
        return file_name[:-4]
    return file_name

def translate_to_korean(english_name):
    translator = Translator()
    english_name_without_extension = remove_png_extension(english_name)
    translation = translator.translate(english_name_without_extension, src='en', dest='ko')
    return translation.text

def create_info_txt(png_file_path):
    file_name = os.path.basename(png_file_path)
    creation_time = datetime.datetime.fromtimestamp(os.path.getctime(png_file_path))
    end_date = creation_time + datetime.timedelta(days=30)
    korean_name = translate_to_korean(file_name)

    txt_file_path = os.path.splitext(png_file_path)[0] + ".txt"
    if not os.path.exists(txt_file_path):
        with open(txt_file_path, 'w') as txt_file:
            txt_file.write(f"식품이름: {korean_name}\n")
            txt_file.write(f"입고날짜: {creation_time.strftime('%Y-%m-%d %H:%M')}\n")
            txt_file.write(f"유통기한: {end_date.strftime('%Y-%m-%d %H:%M')}\n")
            txt_file.write("\nAdditional information goes here...\n")

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory)
        update_file_list()

def on_file_selected(event):
    selected_index = file_listbox.curselection()
    if selected_index:
        selected_file = file_listbox.get(selected_index)
        selected_file = selected_file.split()[0].strip()
        for file_path in files:
            if selected_file in file_path:
                load_file(file_path)
                show_image(f"{file_path[:-4]}.png")

def on_listbox_select(event):
    selected_index = file_listbox.curselection()
    if selected_index:
        selected_file = file_listbox.get(selected_index)
        selected_file = selected_file.split()[0].strip()
        for file_path in files:
            if selected_file in file_path:
                show_image(f"{file_path[:-4]}.png")

def change_font_size():
    new_font_size = 20
    text.tag_configure("font", font=("Helvetica", new_font_size))
    text.tag_add("font", "1.0", "end")

root = tk.Tk()
root.title("smart")

window_width = 600
window_height = 800

root.geometry(f"{window_width}x{window_height}")

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.BOTH, expand=False)

top_frame.columnconfigure(0, weight=1)
top_frame.columnconfigure(1, weight=1)
top_frame.columnconfigure(2, weight=1)

top_left_frame = tk.Frame(top_frame)
top_left_frame.grid(row=0, column=0, sticky="nsew")

image_canvas = tk.Canvas(top_left_frame, width=window_width/2, height=280)
image_canvas.pack(fill=tk.BOTH, expand=True)

top_center_frame = tk.Frame(top_frame)
top_center_frame.grid(row=0, column=1, sticky="nsew")

top_right_frame = tk.Frame(top_frame)
top_right_frame.grid(row=0, column=2, sticky="nsew")

top_right_frame = tk.Frame(top_frame)
top_right_frame.grid(row=0, column=1, sticky="nsew")

bottom_frame = tk.Frame(root, borderwidth=4, relief="ridge")
bottom_frame.pack(fill=tk.BOTH, expand=True)

directory_label = tk.Label(bottom_frame, text="디렉터리 경로:")
directory_label.grid(row=0, column=0, sticky="w", padx=0, pady=0)

directory_entry = tk.Entry(bottom_frame)
directory_entry.grid(row=0, column=1, sticky="ew", padx=0, pady=0)

select_directory_button = tk.Button(bottom_frame, text="파일선택", command=select_directory)
select_directory_button.grid(row=0, column=2, sticky="e", padx=10, pady=5)

update_button = tk.Button(bottom_frame, text="업데이트", command=update_file_list)
update_button.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)

file_button_frame = tk.Frame(bottom_frame)
file_button_frame.grid(row=1, column=0,columnspan=6,  sticky="nsew")

clear_button = tk.Button(bottom_frame, text="메인화면", command=clear_text_and_image)
clear_button.grid(row=0, column=4, sticky="e", padx=0, pady=0)

file_listbox = tk.Listbox(file_button_frame, selectmode=tk.SINGLE)
file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
file_listbox.bind("<ButtonRelease-1>", on_file_selected)
file_listbox.bind("<<ListboxSelect>>", on_listbox_select)

files = []
update_file_list()

text = tk.Text(top_right_frame, wrap=tk.WORD, height=1, width=40, state="normal")
text.configure(font=("Helvetica", 11))
text.pack(fill=tk.BOTH, expand=True)

root.mainloop()

