from typing import TypedDict

class Student(TypedDict):
    name: str
    rollno: int

student : Student = {
    "name": "Abir",
    "rollno": 23
}

#PRINT THE VALUES
print(student["name"])
print(student["rollno"])