import tkinter as tk

parent = tk.Tk()
parent.title("股票")
parent.geometry("800x500")

# ====

main = tk.Frame(parent, width=800, height=300)
main.pack(side=tk.TOP, padx=5)

switch = tk.LabelFrame(main, text='功能', width=200, height=300)
input = tk.LabelFrame(main, text='參數', width=600, height=300)

switch.pack(side=tk.LEFT)
input.pack(side=tk.RIGHT)

# ====

result = tk.LabelFrame(parent, text='結果', width=200, height=200)
result.pack(side=tk.LEFT, padx=5, pady=2)

# ====

scrollbar = tk.Scrollbar(parent)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=2)

listbox = tk.Listbox(parent, yscrollcommand=scrollbar.set, width=64)

for i in range(100):
    listbox.insert(tk.END, str(i))

listbox.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=2)

scrollbar.config(command=listbox.yview)

parent.mainloop()
