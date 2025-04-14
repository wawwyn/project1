import re
import random
import string
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# 인접 키 조합들
adjacent_keys = [
    "qwerty", "asdfgh", "zxcvbn", "12345", "qwertyuiop", "asdfghjkl", "jkl;", "123",
    "qaws", "wsxedc", "erfvtg", "rfvgb", "yhnujm", "ujmki", "ikmlo", "plm", "asdf", "sdfg", "fghj"
]

def check_adjacent_keys(password):
    for keys in adjacent_keys:
        for i in range(len(keys) - 2):
            if keys[i:i+3] in password.lower():
                return True
    return False

def password_predictability(password):
    common_patterns = [
        '123', 'password', 'qwerty', 'letmein', '12345', 'qwerty123', 
        'admin123', 'abc123', 'welcome', '123456', 'qwertyuiop', '111111', 
        '123123', 'letmein123', 'monkey', 'dragon', 'iloveyou', 'sunshine'
    ]
    return any(pattern in password.lower() for pattern in common_patterns)

def generate_similar_password(password):
    password_list = list(password)
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[\W_]', password))

    for _ in range(10):
        new_password = []
        for char in password_list:
            if char.islower():
                new_char = random.choice(string.ascii_lowercase.replace(char, ''))
                new_password.append(new_char.upper() if has_upper else new_char)
            elif char.isupper():
                new_char = random.choice(string.ascii_uppercase.replace(char, ''))
                new_password.append(new_char.lower() if has_lower else new_char)
            elif char.isdigit():
                new_password.append(random.choice(string.digits.replace(char, '')))
            elif char in string.punctuation:
                new_password.append(random.choice(string.punctuation.replace(char, '')))
            else:
                new_password.append(char)
        new_pw = ''.join(new_password)
        if not check_adjacent_keys(new_pw):
            return new_pw
    return generate_random_string(len(password))

def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        result = ''.join(random.choice(characters) for _ in range(length))
        if not check_adjacent_keys(result):
            return result

def evaluate_password(password):
    if len(password) < 8:
        return "매우 약함", 0, ["비밀번호는 최소 8자리 이상이어야 합니다."], []

    score = 0
    suggestions = []

    if re.search(r'[a-z]', password): score += 15
    else: suggestions.append("소문자를 추가해주세요.")
    if re.search(r'[A-Z]', password): score += 15
    else: suggestions.append("대문자를 추가해주세요.")
    if re.search(r'\d', password): score += 15
    else: suggestions.append("숫자를 추가해주세요.")
    if re.search(r'[\W_]', password): score += 15
    else: suggestions.append("특수 문자를 추가해주세요.")
    if len(password) >= 12: score += 10
    else: suggestions.append("비밀번호 길이를 12자 이상으로 늘려주세요.")
    if not password_predictability(password): score += 15
    else: suggestions.append("예측 가능한 패턴을 피해주세요.")
    if re.search(r'(.)\1{2,}', password):
        suggestions.append("반복되는 문자를 피해주세요.")
    if check_adjacent_keys(password):
        suggestions.append("인접한 키를 피해주세요.")

    # 0 ~ 100 점으로 변환
    score = min(score, 100)  # 최대 점수는 100점
    rating = ["매우 약함", "약함", "보통", "강함", "매우 강함"]
    strength = rating[min(score // 20, 4)]  # 점수에 맞는 강도 표시

    recommendations = list({generate_similar_password(password) for _ in range(3)})

    return strength, score, suggestions, recommendations

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("복사됨", f"추천 비밀번호가 복사되었습니다:\n{text}")

# 애니메이션 효과 (부드럽게 색 바꾸기)
def animate_strength_bar(level):
    colors = ["#ff4d4d", "#ff944d", "#ffd11a", "#aaff80", "#00cc66"]
    target_width = (level + 1) * 60
    current_width = strength_bar.winfo_width()

    def grow():
        nonlocal current_width
        if abs(current_width - target_width) < 4:
            strength_bar.config(width=target_width)
            return
        step = (target_width - current_width) // 5 or 1
        current_width += step
        strength_bar.config(width=current_width)
        strength_bar.after(15, grow)

    strength_bar.config(bg=colors[level])
    grow()

# 실시간 평가
def update_evaluation(*args):
    password = password_var.get()
    if not password:
        strength_label.config(text="", fg="#333")
        strength_bar.config(width=0)
        suggestion_text.config(text="")
        for w in recommend_frame.winfo_children():
            w.destroy()
        return

    strength, score, suggestions, recommendations = evaluate_password(password)

    rating_levels = ["매우 약함", "약함", "보통", "강함", "매우 강함"]
    animate_strength_bar(rating_levels.index(strength))
    strength_label.config(text=f"강도: {strength} ({score}/100점)")  # 점수 표시

    suggestion_text.config(text="\n".join(suggestions))

    for w in recommend_frame.winfo_children():
        w.destroy()
    if recommendations:
        for r in recommendations:
            subframe = tk.Frame(recommend_frame, bg="#f0f0f0")
            subframe.pack(pady=2, fill="x", padx=10)
            label = tk.Label(subframe, text=r, font=("맑은 고딕", 10), bg="#f0f0f0", anchor="w")
            label.pack(side="left", fill="x", expand=True)
            btn = ttk.Button(subframe, text="복사", width=6, command=lambda text=r: copy_to_clipboard(text))
            btn.pack(side="right", padx=4)

# GUI 구성
root = tk.Tk()
root.title("비밀번호 강도 평가기")
root.geometry("500x580")
root.configure(bg="#f9f9f9")

password_var = tk.StringVar()
password_var.trace_add("write", update_evaluation)

style = ttk.Style()
style.configure("TButton", font=("맑은 고딕", 11), padding=6)

frame = tk.Frame(root, bg="#ffffff", bd=2, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center", width=440, height=540)

tk.Label(frame, text="🔐 비밀번호 강도 평가기", font=("맑은 고딕", 16, "bold"), bg="#ffffff", fg="#333").pack(pady=20)

tk.Label(frame, text="비밀번호를 입력하세요:", font=("맑은 고딕", 11), bg="#ffffff").pack()
password_entry = ttk.Entry(frame, textvariable=password_var, show="*", font=("맑은 고딕", 11), width=30)
password_entry.pack(pady=8)

def toggle_password():
    if password_entry.cget("show") == "*":
        password_entry.config(show="")
        toggle_btn.config(text="비밀번호 숨기기")
    else:
        password_entry.config(show="*")
        toggle_btn.config(text="비밀번호 보기")

toggle_btn = ttk.Button(frame, text="비밀번호 보기", command=toggle_password)
toggle_btn.pack(pady=5)

strength_label = tk.Label(frame, text="", font=("맑은 고딕", 12, "bold"), bg="#ffffff", fg="#333")
strength_label.pack(pady=(10, 5))

strength_bar = tk.Frame(frame, bg="#ddd", height=8, width=0)
strength_bar.pack(pady=(0, 15))

tk.Label(frame, text="개선 사항:", font=("맑은 고딕", 11, "bold"), bg="#ffffff").pack()
suggestion_text = tk.Label(frame, text="", font=("맑은 고딕", 10), bg="#ffffff", fg="red", justify="left")
suggestion_text.pack(pady=(5, 15))

tk.Label(frame, text="추천 비밀번호:", font=("맑은 고딕", 11, "bold"), bg="#ffffff").pack()
recommend_frame = tk.Frame(frame, bg="#ffffff")
recommend_frame.pack(pady=5, fill="x")

root.mainloop()
