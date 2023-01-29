from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional


def tmux_rewrite(op: str, left: object, right: object) -> Optional[List[str]]:
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
                left_v = left_arr[i]
            except IndexError:
                left_v = None

            try:
                right_v = right_arr[i]
            except IndexError:
                right_v = None

            if op == "==":
                if left_v != right_v:
                    if left_v is not None:
                        diff.append(f"- {left_v}")
                    if right_v is not None:
                        diff.append(f"+ {right_v}")
                else:
                    diff.append(f"> {left_v}")
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
