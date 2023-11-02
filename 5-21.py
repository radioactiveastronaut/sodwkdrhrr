import tkinter as tk
import os
from datetime import timedelta, datetime
from PIL import Image, ImageTk
from information import information_name, information_food, day
# 전역 변수
text = None
image_canvas = None
button_number = 1
# 사용자 지정 .txt 파일 디렉터리 경로
directory = "/home/username/final_test_gui"
# 사용자 지정 .png 파일 디렉터리 경로
png_directory = "/home/username/final_test_gui/png"
# 이미지 표시 함수
def show_image(txt_file_path):
    global image_canvas , png_directory
    translated_name = remove_png_extension(os.path.basename(txt_file_path))
    image_path = os.path.join(png_directory, f"{translated_name}")
    if os.path.exists(image_path):
        photo = ImageTk.PhotoImage(file=image_path)
        image_canvas.delete('all')
        image_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        image_canvas.image = photo
    else:
        pass

# 텍스트 및 이미지 초기화 함수
def clear_text_and_image():
    global text, image_canvas
    if text:
        text.delete(1.0, tk.END)
    if image_canvas:
        image_canvas.delete('all')
# .txt 파일의 확장자를 제거하는 함수
def remove_png_extension(file_name):
    file_name_without_numbers = ''.join([char for char in file_name if not (char.isdigit() or char == '_')])
    if file_name.lower().endswith(".txt"):
        return file_name_without_numbers[:-4]
    return file_name_without_numbers
# DB에 파일명과 같은 정보를 찾아 나타내는 함수
def find_info_in_database(translated_name):
    # 대문자로 변환
    translated_name_upper = translated_name.capitalize()
    # 대문자로 변환한 이름으로 정보를 찾기
    if translated_name_upper in information:
        info_dict = information[translated_name_upper]
        info_str = '\n'.join([f'{key}: {value}' for key, value in info_dict.items()])
        return info_str
    else:
        return None
#  db에 시간정보를 받아 식품에 맞게 계산하여 나타낸다   
def calculate_expiration_date(file_creation_time, expiration_days):
    # 파일 생성 시간을 datetime 형식으로 변환
    creation_datetime = datetime.fromtimestamp(file_creation_time)
    # 유통기한 계산
    expiration_date = creation_datetime + timedelta(days=expiration_days)
    # 유통기한을 포맷팅
    formatted_expiration_date = expiration_date.strftime('%Y-%m-%d %H:%M')
    return formatted_expiration_date
# 파일 목록을 업데이트하는 함수
def update_file_list():
    global button_number, text, image_canvas, png_directory
    existing_button_names = set()   
     
    button_number = 1
    txt_files = sorted([file_name for file_name in os.listdir(directory) if file_name.endswith(".txt")],
                       key=lambda x: os.path.getctime(os.path.join(directory, x)),
                       reverse=False)
    row_index = 0
    col_index = 0
    buttons_per_row = 2
    # 기존 버튼 목록을 저장할 리스트
    existing_buttons = []

    # 기존 버튼을 복제하여 동기화 유지
    for button in file_button_frame.winfo_children():
        existing_buttons.append(button)

    for txt_file_name in txt_files:
        txt_base_name = remove_png_extension(txt_file_name)
        png_file_name = f"{txt_base_name}.png"
        
        if png_file_name in os.listdir(png_directory):
            button_text = f"{button_number}.{txt_base_name}"
            
            while button_text in existing_button_names:
                button_number += 1
                button_text = f"{button_number}.{txt_base_name}"
            existing_button_names.add(button_text)
            # 데이터베이스에서 정보 가져오기
            name_info = information_name.get(txt_base_name)
            if name_info and "식품이름" in name_info:
                button_text = f"{button_number}.{name_info['식품이름']}"

            # 이미 있는 버튼을 재사용
            if existing_buttons:
                button = existing_buttons.pop(0)
                button.config(text=button_text, command=lambda path=os.path.join(directory, txt_file_name): on_button_click(path))
            else:
                button = tk.Button(
                    file_button_frame,
                    text=button_text,
                    command=lambda path=os.path.join(directory, txt_file_name): on_button_click(path)
                )
            button.config(width=43, height=2)
            button.grid(row=row_index, column=col_index, sticky="w", padx=12, pady=5)
            
            col_index += 1
            if col_index >= buttons_per_row:
                col_index = 0
                row_index += 1

            txt_file_path = os.path.join(directory, txt_file_name)
            button_number += 1
            
    # 기존 버튼이 남아있는 경우 삭제
    for button in existing_buttons:
        button.destroy()
        clear_text_and_image()
        
    root.after(1000, update_file_list)
    
def on_button_click(txt_file_path):
    show_image(f"{txt_file_path[:-4]}.png")
    if text:
        translated_name = remove_png_extension(os.path.basename(txt_file_path))
        file_creation_time = os.path.getctime(txt_file_path)
        formatted_creation_time = datetime.fromtimestamp(file_creation_time).strftime('%Y-%m-%d %H:%M')
        name_info = information_name.get(translated_name)
        food_info = information_food.get(translated_name)
        expiration_info = day.get(translated_name)
        listbox_text = ""
        if name_info:
            listbox_text += f"식품이름: {name_info['식품이름']}\n"
        else:
            listbox_text += f"식품이름: {translated_name} (파일 정보 없음)\n"
        listbox_text += f"생성시간: {formatted_creation_time}\n"
        if expiration_info and 'expiration_time' in expiration_info:
            expiration_days = expiration_info['expiration_time']
            formatted_expiration_date = calculate_expiration_date(file_creation_time, expiration_days)
            listbox_text += f"유통기한: {formatted_expiration_date}\n"
        if food_info:
            listbox_text += ""
            for key, value in food_info.items():
                listbox_text += f"{key}: {value}\n"
        text.delete(1.0, tk.END)
        text.insert(tk.END, listbox_text)

    
root = tk.Tk()
root.title("smart")

window_width = 800
window_height = 1280

root.geometry(f"{window_width}x{window_height}")

top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, sticky="nsew")

top_frame.columnconfigure(0, weight=1)
top_frame.columnconfigure(1, weight=1)
top_frame.columnconfigure(2, weight=1)

top_left_frame = tk.Frame(top_frame)
top_left_frame.grid(row=0, column=0, sticky="nsew")

image_canvas = tk.Canvas(top_left_frame, width=400, height=400)
image_canvas.pack(fill=tk.BOTH, expand=False)

top_center_frame = tk.Frame(top_frame)
top_center_frame.grid(row=0, column=1, sticky="nsew")

top_right_frame = tk.Frame(top_frame)
top_right_frame.grid(row=0, column=2, sticky="nsew")

bottom_frame = tk.Frame(root)
bottom_frame.grid(row=1, column=0, sticky="nsew")

update_button = tk.Button(bottom_frame, text="업데이트", command=update_file_list)
update_button.grid(row=0, column=0, sticky="w", padx=12, pady=4)

file_button_frame = tk.Frame(bottom_frame)
file_button_frame.grid(row=1, column=0, columnspan=10,  sticky="nsew")

files = []
update_file_list()

text = tk.Text(top_right_frame, wrap=tk.WORD, height=1, width=24, state="normal")
text.configure(font=("Helvetica", 22))
text.pack(fill=tk.BOTH, expand=True)

root.mainloop()

