from flask import Flask, request, render_template, url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import os

# ตั้งค่า Flask
app = Flask(__name__)

# ตั้งค่าฐานข้อมูล SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# สร้างโมเดล Word
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), unique=True, nullable=False)
    image_filename = db.Column(db.String(200))
    video_filename = db.Column(db.String(200))

# ---------- ส่วนเพิ่มข้อมูล seed ----------

@app.before_request
def seed_data():
    if not hasattr(app, 'already_seeded'):
        db.create_all()
        if not Word.query.first():
            db.session.add_all([
                Word(text='สวัสดี', video_filename='vdo/สวัสดี.mp4'),
                Word(text='ขอบคุณ', video_filename='vdo/ขอบคุณ.mp4')
            ])
            db.session.commit()
        app.already_seeded = True

# ---------- หน้าแรก ----------
@app.route('/')
def index():
    return render_template('front2.html')

# ---------- หน้าผลลัพธ์ ----------
@app.route('/translate', methods=['POST'])
def translate():
    word_text = request.form.get('word')
    word = Word.query.filter_by(text=word_text).first()

    return render_template(
        'front2-2.html',
        word=word_text,
        image=word.image_filename if word else None,
        video=word.video_filename if word else None
    )


# หน้าเพิ่มคำใหม่
@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    if request.method == 'POST':
        word_text = request.form['word']
        video_file = request.files['video']
        
        # ตรวจสอบว่าไฟล์วิดีโอถูกเลือก
        if video_file:
            video_filename = f"vdo/{video_file.filename}"
            save_path = os.path.join('static', video_filename)
            video_file.save(save_path)

            

            # เพิ่มคำใหม่ในฐานข้อมูล
            new_word = Word(text=word_text, video_filename=video_filename)
            db.session.add(new_word)
            db.session.commit()

            return redirect(url_for('index'))  # กลับไปที่หน้าแรกหลังจากเพิ่มคำ

    return render_template('add_word.html')


# ---------- รันแอป ----------
if __name__ == '__main__':
    # ตรวจสอบโฟลเดอร์ static/vdo ถ้าไม่มีให้สร้าง
    os.makedirs('static/vdo', exist_ok=True)
    # แจ้งเตือนเรื่องไฟล์วิดีโอ
    print("📂 วางไฟล์วิดีโอในโฟลเดอร์ static/vdo เช่น 'สวัสดี.mp4' และ 'ขอบคุณ.mp4'")
    app.run(debug=True)
