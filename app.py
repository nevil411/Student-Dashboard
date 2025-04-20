import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

DB_FILE = 'school.db'

# ----------------------------------------
# 📦 DB FUNCTIONS
# ----------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student (
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS course (
        course_id INTEGER PRIMARY KEY,
        course_name TEXT NOT NULL,
        student_id INTEGER,
        FOREIGN KEY(student_id) REFERENCES student(student_id)
    )
    ''')

    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect(DB_FILE)
    students_df = pd.read_sql_query("SELECT * FROM student", conn)
    courses_df = pd.read_sql_query("SELECT * FROM course", conn)
    merged_df = pd.merge(courses_df, students_df, on='student_id', how='left')
    merged_df['is_adult'] = np.where(merged_df['age'] >= 21, 'Yes', 'No')
    conn.close()
    return students_df, courses_df, merged_df

def insert_student(name, age, gender):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO student (name, age, gender) VALUES (?, ?, ?)", (name, age, gender))
    conn.commit()
    conn.close()

def insert_course(course_name, student_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO course (course_name, student_id) VALUES (?, ?)", (course_name, student_id))
    conn.commit()
    conn.close()

# ----------------------------------------
# 📊 PLOT FUNCTIONS
# ----------------------------------------
def plot_gender_distribution(df):
    gender_counts = df['gender'].value_counts()
    fig, ax = plt.subplots(figsize=(4, 3))
    gender_counts.plot(kind='bar', ax=ax, color=['skyblue', 'lightgreen'])
    ax.set_title("Gender Distribution")
    ax.set_ylabel("Count")
    return fig

def plot_course_enrollment(df):
    course_counts = df['course_name'].value_counts()
    fig, ax = plt.subplots(figsize=(4, 3))
    course_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    ax.set_title("Course Enrollment")
    return fig

# ----------------------------------------
# 🚀 STREAMLIT DASHBOARD
# ----------------------------------------
st.set_page_config(page_title="Student Dashboard", layout="centered")
st.title("🎓 Student Dashboard")

# Initialize DB
init_db()

# Form to Add Student
st.sidebar.header("➕ Add New Student")
with st.sidebar.form(key="student_form"):
    new_name = st.text_input("Student Name")
    new_age = st.number_input("Age", min_value=1, max_value=100, step=1)
    new_gender = st.selectbox("Gender", ["M", "F"])
    submit_student = st.form_submit_button("Add Student")

if submit_student and new_name:
    insert_student(new_name, new_age, new_gender)
    st.success(f"Student {new_name} added!")

# Reload data after insert
students_df, courses_df, merged_df = get_data()

# Form to Add Course
st.sidebar.header("➕ Add Course Enrollment")
with st.sidebar.form(key="course_form"):
    course_name = st.text_input("Course Name")
    student_selected = st.selectbox("Select Student", students_df['name'].tolist())
    submit_course = st.form_submit_button("Add Course")

if submit_course and course_name:
    student_id = students_df[students_df['name'] == student_selected]['student_id'].values[0]
    insert_course(course_name, int(student_id))
    st.success(f"Course '{course_name}' assigned to {student_selected}")
    # Refresh data again
    students_df, courses_df, merged_df = get_data()

# Display Tables
st.header("📋 Students Table")
st.dataframe(students_df)

st.header("📋 Courses Table")
st.dataframe(courses_df)

st.header("📌 Merged View + Derived Columns")
st.dataframe(merged_df)

# Interactive Selection
st.subheader("🔍 Get Data for a Student")
student_name = st.selectbox("Select a student", students_df['name'].tolist())
if student_name:
    student_info = merged_df[merged_df['name'] == student_name]
    st.write(f"### 📄 Data for {student_name}")
    st.dataframe(student_info)

st.subheader("🔍 Get Students Enrolled in a Course")
course_name = st.selectbox("Select a course", merged_df['course_name'].unique().tolist())
if course_name:
    course_info = merged_df[merged_df['course_name'] == course_name]
    st.write(f"### 📄 Students enrolled in {course_name}")
    st.dataframe(course_info[['name', 'age', 'gender', 'is_adult']])

# Plots
st.subheader("📊 Gender Distribution")
st.pyplot(plot_gender_distribution(merged_df))

st.subheader("📊 Course Enrollment")
st.pyplot(plot_course_enrollment(merged_df))
