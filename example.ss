# this is a comment

# single-line function
func oopify(prefix) -> prefix + "oop"

# multi-line function
func join(elements, sep)

    # variable assignment
    var result = ""
    var length = len(elements)
    
    for i = 0 to length do

        # string and list operations
        var result = result + elements/i

        # if statement
        if i != length - 1 then var result = result + sep
    
    end

    return result
end

# built-in function
print("hello world")

# for loop
for i = 0 to 5 do
    print(join([oopify("sp"), oopify("lp")], ", "))
end