import json
import random
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import os

def simple_normalize_fa(text):
    text = text.replace('ی', 'ی')
    text = text.replace('ك', 'ک')
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ة', 'ه')
    
    text = re.sub(r'[^\u0600-\u06FF\s]', '', text)
    text = re.sub(r'\d+', '', text) 
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def simple_tokenize_fa(text):
    return text.split()

def load_intents(file_path="intents.json"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"خطا: فایل '{file_path}' پیدا نشد. لطفاً مطمئن شوید فایل در کنار 'main.py' قرار دارد.")
        exit()
    except json.JSONDecodeError:
        print(f"خطا: فایل '{file_path}' یک JSON معتبر نیست. لطفاً ساختار فایل را بررسی کنید.")
        exit()

intents_data = load_intents()

patterns = []
tags = []
responses_dict = {}

for intent in intents_data['intents']:
    tag = intent['tag']
    responses_dict[tag] = intent['responses']

    for pattern in intent['patterns']:
        normalized_pattern = simple_normalize_fa(pattern)
        patterns.append(normalized_pattern)
        tags.append(tag)

model_pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(tokenizer=simple_tokenize_fa, preprocessor=None)),
    ('classifier', LogisticRegression(solver='liblinear', max_iter=1000)) 
])

print("در حال آموزش مدل Scikit-learn (بدون Hazm) با داده‌های جدید...")
model_pipeline.fit(patterns, tags)
print("مدل با موفقیت آموزش دید.")

global_user_name = None 

def get_response(user_input):
    global global_user_name

    normalized_input = simple_normalize_fa(user_input)
    
    predicted_tag = model_pipeline.predict([normalized_input])[0]
    
    if predicted_tag == "معرفی_خود":
        name_match = re.search(r'(اسم من|من اسمم|من|اسمم رو میگم)\s*(.+)', normalized_input)
        
        if name_match:
            user_name = name_match.group(2).strip()
            user_name = user_name.replace("هستم", "").replace("گفتم", "").strip()
            
            if user_name:
                global_user_name = user_name
                response = random.choice(responses_dict[predicted_tag])
                return response.replace("[نام_کاربر]", global_user_name)
            else:
                return "خوشبختم! متاسفانه اسمت رو کامل متوجه نشدم، می‌تونی دقیق‌تر بگی؟"
        else:
            return "خوشبختم! متاسفانه اسمت رو کامل متوجه نشدم، می‌تونی دقیق‌تر بگی؟"
    
    elif predicted_tag in responses_dict:
        response = random.choice(responses_dict[predicted_tag])
        
        if global_user_name:
            response = response.replace("[نام_کاربر]", global_user_name)
        
        return response
    else:
        return "اوه، ببخشید! متوجه منظورت نشدم. می‌تونی یه جور دیگه بگی؟ 🤔"

def main():
    print("\n--- چت‌بات هوش مصنوعی دوستانه (نسخه متنی) ---")
    print("من یه هوش مصنوعی کوچک و دوستانه هستم. چطور می‌تونم کمکت کنم؟ 😊")
    print("برای خروج از چت، 'خروج' یا 'exit' را تایپ کنید.")

    while True:
        user_input = input("شما: ")
        
        if user_input.lower() in ["خروج", "exit", "پایان", "بای", "ختم کلام"]:
            print("چت‌بات: خداحافظ! امیدوارم روز خوبی داشته باشی. 👋")
            break
        
        ai_response = get_response(user_input)
        print(f"چت‌بات: {ai_response}")

if __name__ == "__main__":
    main()
