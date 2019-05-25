print("//////////////// EXAMPLE NUMBER 1 ////////////////")
xs = [1,1,1,2,4,5,6,7]

my_dict = {}

for i in range(len(xs)):
    my_dict[xs[i]] = xs.count(xs[i])
print(my_dict)

print("//////////////// EXAMPLE NUMBER 2 ////////////////")

student = {"name":"john", "age":25, "courses": ["math", "compsci"]}

student["phone"] = '555-3535334'


print(student["name"])
print(student.get("age"))
print(student.get("sex", "Not Found"))
print(student.values())
print(student.items())

for key in student:
    print(key)

for key, value in student.items():
    print(key,value)