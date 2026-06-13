# Code Generator Design

## ⚙️ Nguyên tắc xử lý

| 🔸 Loại Node | 🔽 Input  | 🔼 Output          | 📌 Đặc điểm                              |
| ------------ | --------- | ------------------ | ---------------------------------------- |
| **Stmt**     | `SubBody` | `SubBody`          | Emit code trực tiếp, không trả về string |
| **Expr**     | `Access`  | `(str_code, type)` | Sinh code + suy luận kiểu                |

### ✅ Statement

```python
def visit_if_stmt(self, node: IfStmt, o: SubBody):
    cond_code, _ = self.visit(node.condition, Access(o.frame, o.sym))
    self.emit.print_out(cond_code)
    ...
    return o
```

✔ Đặc điểm:

* Gọi `emit.print_out`
* Không return code

---

### ✅ Expression

```python
def visit_binary_op(self, node: BinaryOp, o: Access):
    left_code, left_type = self.visit(node.left, o)
    right_code, right_type = self.visit(node.right, o)

    code = left_code + right_code + self.emit.emit_add_op(...)
    return code, result_type
```

✔ Đặc điểm:

* Trả về `(code, type)`
* Không emit ngay

## For Statement Flow

```
        ┌───────────────┐
        │     init      │
        └──────┬────────┘
               ↓
        ┌───────────────┐
        │   L_start     │
        └──────┬────────┘
               ↓
        ┌───────────────┐
        │  condition    │
        └──────┬────────┘
         false ↓      ↓ true
        ┌────────┐   ┌───────────────┐
        │ L_break│   │     body      │
        └────────┘   └──────┬────────┘
                            ↓
                    ┌───────────────┐
                    │  L_continue   │
                    └──────┬────────┘
                            ↓
                    ┌───────────────┐
                    │    update     │
                    └──────┬────────┘
                            ↓
                         goto L_start
```

## Switch Statement Flow

```
if (expr == case1) → goto L_case1
if (expr == case2) → goto L_case2
...
goto L_default

L_case1:
    stmt1

L_case2:
    stmt2

...

L_default:
    stmt_default

L_break:
```

