from flask import Flask, render_template, request, redirect, url_for,flash
from pymongo import MongoClient
from bson.objectid import ObjectId
app = Flask(__name__)
app.secret_key = "your_secret_key"

client = MongoClient("mongodb://localhost:27017/")
db = client["student_database"]
students_collection = db["students"]
credentials = {
    "admin": "adminpassword",
    "user": "password"
}
students_data = []
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in credentials and credentials[username] == password:
            if username == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("student"))
        else:
           flash("Invalid credentials. Please try again.", "error")

    return render_template("login.html")

@app.route("/admin")
def admin():
    students = list(students_collection.find())
    return render_template("admin_students.html", students=students)
@app.route("/student", methods=["GET", "POST"])
def student():
    if request.method == "POST":
        student_name = request.form.get("student_name")
        student_age = request.form.get("student_age")
        gender=request.form.get("gender")
        mail=request.form.get("mail")
        phone_number=request.form.get("phone_number")
        student_course = request.form.get("student_course")
        student ={
            "name": student_name,
            "age": student_age,
            "gender": gender,
            "mail": mail,
            "phone_number": phone_number,
            "course": student_course,
            "avatar_filename": "male_avatar.png" if gender == "male" else "female_avatar.png"
        }
        students_collection.insert_one(student)
        return redirect(url_for("student_details"))
    return render_template("student.html",)
@app.route("/student_details")
def student_details():
    student = students_collection.find_one(sort=[("_id", -1)])
    avatar_filename = "male_avatar.png" if student.get("gender", "") == "male" else "female_avatar.png"
    return render_template("student_details.html", student=student, avatar_filename=avatar_filename)


@app.route("/edit_student/<string:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if request.method == "POST":
        students_collection.update_one({"_id": ObjectId(student_id)}, {"$set": {
            "name": request.form.get("edited_name"),
            "age": request.form.get("edited_age"),
            "gender": request.form.get("edited_gender"),
            "mail": request.form.get("edited_mail"),
            "phone_number": request.form.get("edited_phone_number"),
            "course": request.form.get("edited_course"),
        }})
        return redirect(url_for("admin"))

    student = students_collection.find_one({"_id": ObjectId(student_id)})
    return render_template("edit_student.html", student=student)

@app.route("/delete_student/<string:student_id>", methods=["POST"])
def delete_student(student_id):
    students_collection.delete_one({"_id": ObjectId(student_id)}) 
    return redirect(url_for("admin"))

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        username = request.form.get("username")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        if username == "admin" and credentials.get(username) == old_password:
            credentials[username] = new_password
            flash("Password changed successfully.", "success")
            return redirect(url_for("login"))
        else:
            flash("Invalid username or old password.", "error")
    return render_template("change_password.html")

if __name__ == "__main__":
    app.run(debug=True)
