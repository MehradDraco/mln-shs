from math_solver import CuteMathProfessor
import os

if __name__ == "__main__":
    professor = CuteMathProfessor()

    print(professor._get_random_response('greetings'))
    print("می‌تونی بپرسی: 'معادله x^2 - 4 = 0 رو حل کن', 'مشتق x**3 + 2*x رو بگیر', 'انتگرال x*sin(x) رو حساب کن'")
    print("همچنین می‌تونی عبارات رو ساده کنی: 'ساده کن: (x+y)^2' یا 'مقدار cos(pi)'")
    print("برای خروج بنویس 'خداحافظ' یا 'بای'.")

    while True:
        user_input = input("\nشما: ")
        user_input_lower = user_input.lower()

        if user_input_lower in ["خداحافظ", "بای", "exit"]:
            print(professor._get_random_response('farewells'))
            break
        
        response = professor.get_math_response(user_input)
        print(f"پروفسور بامزه: {response}")
