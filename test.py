import subprocess

text = """A vector is an ordered list of scalar values, called attributes. We denote a vector as a bold
character, for example, x or w. Vectors can be visualized as arrows that point to some
directions as well as points in a multi-dimensional space. Illustrations of three two-dimensional
vectors, a = [2, 3], b = [≠2, 5], and c = [1, 0] is given in fig. 1. We denote an attribute of a
vector as an italic value with an index, like this: w(j) or x(j). The index j denotes a specific
dimension of the vector, the position of an attribute in the list. For instance, in the vector a
shown in red in fig. 1, a(1) = 2 and a(2) = 3.
The notation x(j) should not be confused with the power operator, like this x2 (squared) or
x3 (cubed). If we want to apply a power operator, say square, to an indexed attribute of a
vector, we write like this: (x(j))2
.
A variable can have two or more indices, like this: x(j)
i or like this x(k)
i,j . For example, in
neural networks, we denote as x(j)
l,u the input feature j of unit u in layer l."""

one_line = " ".join(text.splitlines())

voice = 'en_US-ryan-high'
print("Working on the task...\n")
subprocess.run([
    "python3", "-m", "piper",
    "-m", voice,
    "-f", "test.wav",
    "--", one_line
])
print("Task Completed\n")