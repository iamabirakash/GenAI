from typing import TypedDict, List

class Student(TypedDict):
    name: str
    rollno: int
    marks: List[int]

student : Student = {
    "name": "Abir",
    "rollno": 23,
    "marks": [90, 80, 70]
}

#PRINT THE VALUES
print(student["name"])
print(student["rollno"])
print(student["marks"])