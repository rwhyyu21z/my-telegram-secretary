import logging
import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS, TIMEZONE
from database_setup import init_db, SessionLocal, AcademicTask, DebtRecord

logging.basicConfig(level=logging.INFO)
tz = pytz.timezone(TIMEZONE)

def is_authorized(user_id: int) -> bool:
    return not ALLOWED_USER_IDS or user_id in ALLOWED_USER_IDS

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    text = (
        "🚀 *Personal Secretary (Tanpa AI - Super Cepat)*\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Gunakan format perintah berikut:\n\n"
        "📌 *1. Tambah Tugas Akademik:*\n"
        "`/tugas Nama Matkul | Nama Tugas | YYYY-MM-DD HH:MM`\n"
        " Contoh: `/tugas Pancasila | Kumpul UTS | 2026-11-07 11:00`\n\n"
        "💳 *2. Catat Utang / Piutang:*\n"
        "`/utang UTANG/PIUTANG | Nama Orang | Nominal`\n"
        " Contoh: `/utang UTANG | Meita | 120000`\n\n"
        "📋 *3. Cek Ringkasan Data:*\n"
        "`/cek` — Menampilkan daftar tugas & utang aktif"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def add_task_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    try:
        raw_text = " ".join(context.args)
        parts = [p.strip() for p in raw_text.split("|")]
        
        if len(parts) < 3:
            await update.message.reply_text("⚠️ Format salah! Gunakan:\n`/tugas Matkul | Deskripsi | YYYY-MM-DD HH:MM`", parse_mode="Markdown")
            return
            
        course, task, deadline_str = parts[0], parts[1], parts[2]
        dt = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        
        db = SessionLocal()
        db.add(AcademicTask(user_id=update.effective_user.id, course_name=course, task_name=task, deadline=dt))
        db.commit()
        db.close()
        
        await update.message.reply_text(f"✅ *Tugas Berhasil Disimpan!*\n📖 Matkul: {course}\n📝 Tugas: {task}\n⏰ Deadline: {deadline_str}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal format tanggal/waktu. Pastikan formatnya `YYYY-MM-DD HH:MM` (Contoh: `2026-11-07 11:00`)", parse_mode="Markdown")

async def add_debt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    try:
        raw_text = " ".join(context.args)
        parts = [p.strip() for p in raw_text.split("|")]
        
        if len(parts) < 3:
            await update.message.reply_text("⚠️ Format salah! Gunakan:\n`/utang UTANG/PIUTANG | Nama Orang | Nominal`", parse_mode="Markdown")
            return
            
        debt_type, person, amount_str = parts[0].upper(), parts[1], parts[2]
        amount = float(amount_str.replace(".", "").replace(",", ""))
        
        db = SessionLocal()
        db.add(DebtRecord(user_id=update.effective_user.id, type=debt_type, person_name=person, amount=amount))
        db.commit()
        db.close()
        
        await update.message.reply_text(f"✅ *Catatan Keuangan Disimpan!*\n💳 Tipe: {debt_type}\n👤 Pihak: {person}\n💵 Nominal: Rp {amount:,.0f}", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ Gagal menyimpan. Pastikan nominal berupa angka murni (Contoh: `120000`)")

async def check_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    db = SessionLocal()
    tasks = db.query(AcademicTask).filter_by(user_id=update.effective_user.id).all()
    debts = db.query(DebtRecord).filter_by(user_id=update.effective_user.id).all()
    db.close()
    
    res = "📋 *RINGKASAN DATA SECRETARY*\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📖 *TUGAS AKADEMIK:*\n"
    if not tasks:
        res += "_Tidak ada tugas_\n"
    for t in tasks:
        res += f"• [{t.course_name}] {t.task_name} (Deadline: {t.deadline.strftime('%d-%m-%Y %H:%M')})\n"
        
    res += "\n💳 *CATATAN UTANG/PIUTANG:*\n"
    if not debts:
        res += "_Tidak ada catatan keuangan_\n"
    for d in debts:
        res += f"• {d.type} - {d.person_name}: Rp {d.amount:,.0f}\n"
        
    await update.message.reply_text(res, parse_mode="Markdown")

def main():
    init_db()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("tugas", add_task_cmd))
    app.add_handler(CommandHandler("utang", add_debt_cmd))
    app.add_handler(CommandHandler("cek", check_cmd))
    print("🚀 Bot No-AI running...")
    app.run_polling()

if __name__ == "__main__":
    main()