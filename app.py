import os
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import json
from tkinter import filedialog

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("UI Application")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Tool_1: Fixed size window
        self.root.resizable(False, False)

        # Tool_4: BMS Slave ID Combobox
        self.bms_slave_id = ttk.Combobox(root, values=["0x200", "0x201", "0x202", "0x203", "0x204", "0x205", "0x206", "0x207", "0x208", "0x209"])
        self.bms_slave_id.set("BMS Slave ID")
        self.bms_slave_id.pack()
        self.bms_slave_id.bind("<<ComboboxSelected>>", self.update_comboboxes)

        # Tool_5: Cell Temperature ID Combobox
        self.cell_temp_id = ttk.Combobox(root, values=["0x304", "0x314", "0x324", "0x334", "0x344", "0x354", "0x364", "0x374", "0x384", "0x394"])
        self.cell_temp_id.set("Cell Temperature ID")
        self.cell_temp_id.pack()
        self.cell_temp_id.bind("<<ComboboxSelected>>", self.update_other_comboboxes)

        # Tool_6: Cell Voltage ID Combobox
        self.cell_voltage_id = ttk.Combobox(root, values=["0x300", "0x310", "0x320", "0x330", "0x340", "0x350", "0x360", "0x370", "0x380", "0x390"])
        self.cell_voltage_id.set("Cell Voltage ID")
        self.cell_voltage_id.pack()
        self.cell_voltage_id.bind("<<ComboboxSelected>>", self.update_other_comboboxes)

        # Tool_3: Development session mode checkboxes
        self.mode_var = tk.StringVar()
        self.debug_check = ttk.Checkbutton(root, text="Debug", variable=self.mode_var, onvalue="Debug", offvalue="", command=self.toggle_mode)
        self.debug_check.pack()
        self.release_check = ttk.Checkbutton(root, text="Release", variable=self.mode_var, onvalue="Release", offvalue="", command=self.toggle_mode)
        self.release_check.pack()

        # Tool_8: Version ID
        self.version_label = ttk.Label(root, text="Version: 1.0.0", anchor="se")
        self.version_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Tool_10: Launch button
        self.launch_button = ttk.Button(root, text="Launch", command=self.launch)
        self.launch_button.pack()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def toggle_mode(self):
        if self.mode_var.get() == "Debug":
            self.release_check.state(['!selected'])
        else:
            self.debug_check.state(['!selected'])

    def update_comboboxes(self, event):
        index = self.bms_slave_id.current()
        self.cell_temp_id.current(index)
        self.cell_voltage_id.current(index)

    def update_other_comboboxes(self, event):
        index = self.cell_temp_id.current()
        self.bms_slave_id.current(index)
        self.cell_voltage_id.current(index)

    def update_config_file(self, file_path, bms_slave_id, cell_temp_id, cell_voltage_id):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                lines = f.readlines()
        else:
            lines = []

        new_lines = []
        for line in lines:
            if line.startswith("#define BMS_SLAVE_ID"):
                new_lines.append(f"#define BMS_SLAVE_ID {bms_slave_id}\n")
            elif line.startswith("#define CELL_TEMP_ID"):
                new_lines.append(f"#define CELL_TEMP_ID {cell_temp_id}\n")
            elif line.startswith("#define CELL_VOLTAGE_ID"):
                new_lines.append(f"#define CELL_VOLTAGE_ID {cell_voltage_id}\n")
            else:
                new_lines.append(line)

        if not any(line.startswith("#define BMS_SLAVE_ID") for line in new_lines):
            new_lines.append(f"#define BMS_SLAVE_ID {bms_slave_id}\n")
        if not any(line.startswith("#define CELL_TEMP_ID") for line in new_lines):
            new_lines.append(f"#define CELL_TEMP_ID {cell_temp_id}\n")
        if not any(line.startswith("#define CELL_VOLTAGE_ID") for line in new_lines):
            new_lines.append(f"#define CELL_VOLTAGE_ID {cell_voltage_id}\n")

        with open(file_path, "w") as f:
            f.writelines(new_lines)

        print(f"Configurația a fost actualizată în {file_path}")


    def launch(self):
        bms_slave_id = self.bms_slave_id.get()
        cell_temp_id = self.cell_temp_id.get()
        cell_voltage_id = self.cell_voltage_id.get()

        if sys.platform.startswith("win"):
            stm32_path = r"C:\ST\STM32CubeIDE_1.12.0\STM32CubeIDE.exe"
        elif sys.platform.startswith("darwin"):
            stm32_path = "/Applications/STM32CubeIDE.app/Contents/MacOS/STM32CubeIDE"
        else:
            messagebox.showerror("Eroare", "Sistemul de operare nu este suportat!")
            return
        
        selected_folder = filedialog.askdirectory(title="Selectează directorul proiectului")

        config_file = os.path.expanduser(selected_folder)
        os.makedirs(config_file, exist_ok=True)
        file_path = os.path.join(config_file, "config.h")

        self.update_config_file(file_path, bms_slave_id, cell_temp_id, cell_voltage_id)

        try:
            if sys.platform.startswith("win"):
                subprocess.Popen([stm32_path])
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", "-a", "STM32CubeIDE"])
            print("STM32CubeIDE a fost deschis.")
        except FileNotFoundError:
            messagebox.showerror("Eroare", f"STM32CubeIDE nu a fost găsit la {stm32_path}. Asigură-te că este instalat!")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()