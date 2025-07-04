import random
import re
import json
import os
from sympy import * # ایمپورت کردن همه توابع SymPy

# مسیر فایل responses.json
RESPONSES_FILE = os.path.join(os.path.dirname(__file__), 'responses.json')

class CuteMathProfessor:
    def __init__(self):
        self.responses = self._load_json_responses()
        # تعریف متغیرهای نمادین پیش‌فرض (SymPy Symbols)
        # این‌ها کلماتی هستند که SymPy آن‌ها را به عنوان متغیر می‌شناسد.
        self.symbols = symbols('x y z t a b c d k m n p q r s u v w')
        
        # الگوهای تشخیص نوع درخواست ریاضی
        self.math_patterns = {
            'solve': r'(حل کن|جواب بده|پیدا کن|معادله)\s*(.*)',
            'derivative': r'(مشتق)\s*(.*)',
            'integral': r'(انتگرال)\s*(.*)',
            'simplify': r'(ساده کن|ساده سازی)\s*(.*)',
            'evaluate': r'(مقدار|چی میشه)\s*(.*)' # برای ارزیابی عبارات
        }

    def _load_json_responses(self):
        """بارگذاری جملات بامزه از فایل JSON."""
        try:
            with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {RESPONSES_FILE} not found. Using default responses.")
            return {
                "greetings": ["Hello!"], "farewells": ["Goodbye!"],
                "positive_feedback": ["Amazing!"], "error_messages": ["Oops, I didn't get that."],
                "result_prefixes": ["The answer is: "], "intro_commands": ["solve"]
            }

    def _get_random_response(self, category):
        """یک پاسخ تصادفی از دسته مورد نظر را برمی‌گرداند."""
        return random.choice(self.responses.get(category, ["I'm not sure how to respond to that."]))

    def _parse_and_solve(self, user_input):
        """
        ورودی کاربر را تجزیه و تحلیل کرده و با SymPy حل می‌کند.
        اینجا "هوش" اصلی و تشخیص الگوهای پیچیده‌تر ورودی اتفاق می‌افتد.
        """
        input_lower = user_input.lower()
        
        # ابتدا بررسی می‌کنیم که آیا کلمه کلیدی عملیات ریاضی وجود دارد
        detected_command = None
        expression_str = None

        for cmd, pattern in self.math_patterns.items():
            match = re.search(pattern, input_lower)
            if match:
                detected_command = cmd
                expression_str = match.group(2).strip()
                break
        
        if not detected_command:
            # اگر هیچ دستور صریحی پیدا نشد، فرض می‌کنیم کاربر می‌خواهد عبارتی را ارزیابی کند
            # یا معادله‌ای که نیازی به کلمه "حل کن" ندارد.
            detected_command = 'evaluate'
            expression_str = input_lower # کل ورودی را به عنوان عبارت در نظر می‌گیریم
            
        if not expression_str:
            return "empty_expression", None

        try:
            # مهم: SymPy به شما اجازه می‌دهد که عبارات متنی را parse کنید.
            # برای ایمنی، فقط از SymPy's `sympify` استفاده کنید.
            # Eval (eval()) پایتون خطرناک است.
            expr = sympify(expression_str, evaluate=False, locals={str(s):s for s in self.symbols})
            
            # eval=False در sympify از ارزیابی فوری جلوگیری می‌کند.
            # حالا بر اساس دستور، عملیات را انجام می‌دهیم.
            result = None
            if detected_command == 'solve':
                # سعی می‌کنیم متغیر اصلی را پیدا کنیم. اگر مشخص نشده بود، SymPy سعی می‌کند حدس بزند.
                # مثال: "solve x^2 - 4 = 0"
                # SymPy معادلات را به فرم "expr = 0" ترجیح می‌دهد.
                # اگر کاربر "x^2 = 4" گفت، باید تبدیل شود به "x^2 - 4".
                eq_parts = str(expr).split('=')
                if len(eq_parts) == 2:
                    eq = sympify(eq_parts[0].strip()) - sympify(eq_parts[1].strip())
                else:
                    eq = expr # فرض می‌کنیم اگر مساوی نبود، برابر صفر است

                # اگر متغیرهای نامشخص وجود داشته باشند، سعی می‌کنیم حل کنیم.
                # `solve` می‌تواند یک یا چند متغیر را حل کند.
                result = solve(eq, *[s for s in eq.free_symbols if s in self.symbols])
                if not result: # اگر SymPy نتوانست حل کند
                    result = "نتوانستم این معادله را حل کنم. شاید خیلی پیچیده بود یا فرمت صحیحی نداشت."
                
            elif detected_command == 'derivative':
                # مشتق نسبت به کدام متغیر؟ معمولاً x.
                # می‌توانیم سعی کنیم اولین متغیر موجود در عبارت را پیدا کنیم.
                diff_var = None
                for s in self.symbols:
                    if s in expr.free_symbols:
                        diff_var = s
                        break
                if diff_var:
                    result = diff(expr, diff_var)
                else:
                    result = "برای مشتق‌گیری نیاز به یک متغیر دارم (مثل x)."
            
            elif detected_command == 'integral':
                # انتگرال نسبت به کدام متغیر؟ معمولاً x.
                int_var = None
                for s in self.symbols:
                    if s in expr.free_symbols:
                        int_var = s
                        break
                if int_var:
                    result = integrate(expr, int_var)
                else:
                    result = "برای انتگرال‌گیری نیاز به یک متغیر دارم (مثل x)."
            
            elif detected_command == 'simplify':
                result = simplify(expr)

            elif detected_command == 'evaluate':
                # برای ارزیابی عبارات عددی یا عباراتی که به صورت پیش‌فرض ساده‌سازی می‌شوند
                result = expr.evalf() if expr.is_Float or expr.is_Rational or expr.is_Pow else expr # ارزیابی عددی برای اعداد
                if result is None:
                    result = simplify(expr) # سعی در ساده‌سازی اگر ارزیابی مستقیم نشد

            return "success", result

        except Exception as e:
            print(f"SymPy error: {e}")
            return "error", None

    def get_math_response(self, user_input):
        """یک پاسخ بامزه به همراه نتیجه ریاضی برمی‌گرداند."""
        status, result = self._parse_and_solve(user_input)

        if status == "success":
            response_prefix = self._get_random_response('result_prefixes')
            positive_feedback = self._get_random_response('positive_feedback')
            return f"{response_prefix}{result}! {positive_feedback}"
        elif status == "empty_expression":
            return self._get_random_response('error_messages') + " (لطفاً سوالتو واضح بگو!)"
        else: # status == "error"
            return self._get_random_response('error_messages')
