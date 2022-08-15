def tmux_rewrite(op, left, right):
    diff = []
    left_arr = str(left).split("\n")
    right_arr = str(right).split("\n")
    if op == "==":
        diff.append("failed")
        diff.append("> Common line")
        diff.append("- Left")
        diff.append("+ Right")
        diff.append("-------------")
        for i in range(len(max([left_arr, right_arr], key=len))):
            try:
                left = left_arr[i]
            except IndexError:
                left = None

            try:
                right = right_arr[i]
            except IndexError:
                right = None

            if op == "==":
                if left != right:
                    if left is not None:
                        diff.append(f"- {left}")
                    if right is not None:
                        diff.append(f"+ {right}")
                else:
                    diff.append(f"> {left}")
        diff.append("-------------")
    elif op == "!=":
        diff.append("failed")
        diff.append("left and right are equal")
        diff.append("-------------")
        diff.extend(left_arr)
        diff.append("-------------")
    elif op == "in":
        diff.append("failed")
        diff.append("-------------")
        diff.extend(left_arr)
        diff.append("-------------")
        diff.append("was not found in")
        diff.append("-------------")
        diff.extend(right_arr)
        diff.append("-------------")
    return diff
