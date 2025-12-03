import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

# Fixed offsets
WATER_HEIGHT_OFFSET = 0xB0
WATER_PATH_OFFSET = 0xB9
WATER_PATH_MAX_OFFSET = 0x1BF
FIX_BYTES = bytes.fromhex("C0E440FFFFFF")
FIX_OFFSET_START = 0x21

# Template copy range (inclusive start, exclusive end for python slicing)
TEMPLATE_START = 0x00
TEMPLATE_END = 0xF0  # 0x00..0xEF inclusive -> slice up to 0xF0

# Embedded template data (240 bytes)
EMBEDDED_TEMPLATE = bytes.fromhex(
    "52 10 00 E9 09 00 00 00 64 5C 00 00 50 5C 00 00 00 00 00 00 21 00 00 00 00 00 00 00 00 00 00 00 00 C0 E4 40 FF FF FF 00 5C 59 00 00 04 00 00 00 01 00 00 00 00 61 6D 65 72 65 34 00 60 BC A9 0A 00 00 02 01 1D 64 E0 4F 15 00 00 00 60 A0 CE 34 60 A0 CE 34 00 00 00 00 E3 7B C2 94 2C FB 3F 0F 60 A0 CE 34 3C FB 3F 0F 00 00 00 00 00 00 00 00 D4 F9 3F 0F 10 EA E0 4F 40 00 00 00 00 00 00 00 20 60 CE 34 00 00 00 00 E8 30 CF 34 08 8D A9 0A 01 00 00 00 B8 21 0F 40 8C FB 3F 0F 00 00 00 00 00 00 48 43 00 00 80 C0 01 00 00 00 00 00 00 00 00 00 00 3F 00 00 00 00 00 67 72 61 70 68 69 63 73 5C 5F 6D 61 74 65 72 69 61 6C 73 5C 65 64 69 74 6F 72 5C 77 61 74 65 72 5F 61 76 5F 72 61 69 6E 66 6F 72 65 73 74 2E 6D 6C 6D 00 00 00 00 00"
)

# Water file paths (displayed strings; bytes are written with single backslashes)
WATER_PATHS_BYTES = [
    b"graphics\\_materials\\editor\\df_water_default_top.mlm",
    b"graphics\\_materials\\editor\\water_av_openfield.mlm",
    b"graphics\\_materials\\editor\\water_av_rainforest.mlm",
    b"graphics\\_materials\\editor\\water_av_rainforest_prolemuris_noreflection.mlm",
    b"graphics\\_materials\\editor\\water_av_riverbank.mlm",
    b"graphics\\_materials\\editor\\water_av_swamp.mlm",
]

WATER_PATHS_STR = [p.decode('ascii') for p in WATER_PATHS_BYTES]

class ModernWaterEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("AVATAR: The Game Water Editor | Version 1.0 | Made By: Jasper Zebra")
        self.root.geometry("1200x720")
        # UI colors
        self.colors = {
            'bg': '#1e1e2e',
            'bg_secondary': '#2a2a3e',
            'bg_tertiary': '#363649',
            'accent': '#4a9eff',
            'accent_hover': '#5eb0ff',
            'text': '#e0e0e0',
            'text_secondary': '#a0a0a0',
            'success': '#50fa7b',
            'warning': '#ffb86c',
            'grid_bg': '#2a2a3e',
            'sector_water': '#1e88e5',
            'sector_selected': '#ff6b6b',
            'grid_line': '#404050'
        }

        self.root.configure(bg=self.colors['bg'])
        self.setup_styles()

        self.sdat_folder = None
        self.current_sector = None

        self.create_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', background=self.colors['bg_secondary'], relief='flat')
        style.configure('TLabel', background=self.colors['bg_secondary'], foreground=self.colors['text'], font=('Segoe UI', 10))
        style.configure('Header.TLabel', background=self.colors['bg'], foreground=self.colors['text'], font=('Segoe UI', 16, 'bold'))
        style.configure('TButton', background=self.colors['accent'], foreground='white', borderwidth=0, font=('Segoe UI', 10))
        style.map('TButton', background=[('active', self.colors['accent_hover'])])
        style.configure('Accent.TButton', background=self.colors['accent'], foreground='white', padding=8, font=('Segoe UI', 11, 'bold'))
        style.configure('Warning.TButton', background=self.colors['warning'], foreground='white', padding=8, font=('Segoe UI', 11, 'bold'))
        style.configure('TCombobox', fieldbackground=self.colors['bg_tertiary'], background=self.colors['bg_tertiary'], foreground='black', arrowcolor=self.colors['text'])
        style.configure('TScale', background=self.colors['bg_secondary'], troughcolor=self.colors['bg_tertiary'])

    def create_ui(self):
        main_container = ttk.Frame(self.root, padding=16)
        main_container.pack(fill='both', expand=True)
        header = ttk.Label(main_container, text="🌊 AVATAR: The Game Water Editor", style='Header.TLabel')
        header.pack(pady=(0, 12))

        content = ttk.Frame(main_container)
        content.pack(fill='both', expand=True)

        left_panel = ttk.Frame(content, style='Card.TFrame', padding=12)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0,10))
        right_panel = ttk.Frame(content, style='Card.TFrame', padding=12)
        right_panel.pack(side='right', fill='both', padx=(10,0))

        # Controls (left)
        self.load_btn = ttk.Button(left_panel, text="📁 Load SDAT Folder", command=self.load_sdat_folder, style='Accent.TButton')
        self.load_btn.pack(fill='x', pady=(0,8))
        self.status_label = ttk.Label(left_panel, text="No folder loaded", foreground=self.colors['text_secondary'])
        self.status_label.pack(pady=(6,8))

        sep = ttk.Separator(left_panel, orient='horizontal')
        sep.pack(fill='x', pady=8)

        # Add Water Block button (first step)
        self.add_water_btn = ttk.Button(left_panel, text="➕ Add Water Block", command=self.add_water_block, style='Accent.TButton')
        self.add_water_btn.pack(fill='x', pady=(0,12))

        # Height control
        ttk.Label(left_panel, text="💧 Water Height", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(6,6))
        slider_frame = ttk.Frame(left_panel)
        slider_frame.pack(fill='x', pady=(0,8))
        self.height_var = tk.DoubleVar(value=0.0)
        self.height_slider = ttk.Scale(slider_frame, from_=0.0, to=50.0, variable=self.height_var, orient='horizontal')
        self.height_slider.pack(side='left', fill='x', expand=True, padx=(0,8))
        self.height_entry_var = tk.StringVar(value="0.00")
        self.height_entry = tk.Entry(slider_frame, textvariable=self.height_entry_var, width=8, bg=self.colors['bg_tertiary'], fg=self.colors['text'], relief='flat', insertbackground=self.colors['text'])
        self.height_entry.pack(side='right')
        self.height_var.trace_add('write', self.update_height_display)
        self.height_entry_var.trace_add('write', self.sync_height_from_entry)

        # Water material/path
        ttk.Label(left_panel, text="🎨 Water Material", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(8,6))
        self.path_var = tk.StringVar(value="00")
        self.path_dropdown = ttk.Combobox(left_panel, textvariable=self.path_var, values=WATER_PATHS_STR, state='readonly')
        self.path_dropdown.pack(fill='x', pady=(0,8))

        # Save and reset buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill='x', pady=(10,8))
        
        self.save_btn = ttk.Button(button_frame, text="💾 Save Sector", command=self.save_current_sector, style='Accent.TButton')
        self.save_btn.pack(fill='x', pady=(0,6))
        
        self.reset_btn = ttk.Button(button_frame, text="🔄 Reset Sector (clear water)", command=self.reset_current_sector, style='Warning.TButton')
        self.reset_btn.pack(fill='x')

        self.sector_info = ttk.Label(left_panel, text="Select a sector to edit", foreground=self.colors['text_secondary'])
        self.sector_info.pack(pady=(12,0))

        # Grid (right)
        ttk.Label(right_panel, text="🗺️ Sector Map", font=('Segoe UI', 11, 'bold')).pack()
        self.grid_canvas = tk.Canvas(right_panel, width=480, height=480, bg=self.colors['grid_bg'], highlightthickness=0)
        self.grid_canvas.pack(pady=(12,0))
        self.grid_canvas.bind('<Button-1>', self.select_sector)

        legend_frame = ttk.Frame(right_panel)
        legend_frame.pack(pady=(10,0))
        self.create_legend_item(legend_frame, self.colors['grid_bg'], "Empty")
        self.create_legend_item(legend_frame, self.colors['sector_water'], "Water")
        self.create_legend_item(legend_frame, self.colors['sector_selected'], "Selected")

        self.draw_sector_grid()

    def create_legend_item(self, parent, color, text):
        item = ttk.Frame(parent)
        item.pack(side='left', padx=8)
        canvas = tk.Canvas(item, width=20, height=20, bg=self.colors['bg_secondary'], highlightthickness=0)
        canvas.pack(side='left', padx=(0,6))
        canvas.create_rectangle(2,2,18,18, fill=color, outline=self.colors['grid_line'])
        ttk.Label(item, text=text).pack(side='left')

    def draw_sector_grid(self):
        self.grid_canvas.delete('all')
        cell_size = 30
        for y in range(16):
            for x in range(16):
                sector_index = y * 16 + x
                display_x = x * cell_size
                display_y = (15 - y) * cell_size
                has_water = self.sector_has_water(sector_index)
                is_selected = (sector_index == self.current_sector)
                fill_color = self.colors['grid_bg']
                if has_water: fill_color = self.colors['sector_water']
                if is_selected: fill_color = self.colors['sector_selected']
                outline_color = self.colors['grid_line']
                outline_width = 3 if is_selected else 1
                self.grid_canvas.create_rectangle(display_x, display_y, display_x + cell_size, display_y + cell_size, outline=outline_color, fill=fill_color, width=outline_width)
                text_color = 'white' if (has_water or is_selected) else self.colors['text_secondary']
                self.grid_canvas.create_text(display_x + cell_size/2, display_y + cell_size/2, text=str(sector_index), fill=text_color, font=('Segoe UI', 8))

    def sector_has_water(self, sector_index):
        if self.sdat_folder is None: return False
        file_path = os.path.join(self.sdat_folder, f'sd{sector_index}.csdat')
        if not os.path.isfile(file_path): return False
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            if len(data) < WATER_HEIGHT_OFFSET + 4:
                return False
            height = struct.unpack('<f', data[WATER_HEIGHT_OFFSET:WATER_HEIGHT_OFFSET+4])[0]
            path_bytes = data[WATER_PATH_OFFSET:WATER_PATH_MAX_OFFSET+1] if len(data) > WATER_PATH_OFFSET else b''
            path_str = path_bytes.split(b'\x00')[0].decode('ascii', errors='ignore').strip() if path_bytes else ''
            return (abs(height) > 1e-6) or (path_str != '' and path_str != '00')
        except:
            return False

    def update_height_display(self, *args):
        self.height_entry_var.set(f"{self.height_var.get():.2f}")

    def sync_height_from_entry(self, *args):
        try:
            v = float(self.height_entry_var.get())
            if 0.0 <= v <= 50.0:
                self.height_var.set(v)
        except:
            pass

    def load_sdat_folder(self):
        folder = filedialog.askdirectory(title='Select SDAT Folder')
        if not folder:
            return
        self.sdat_folder = folder
        self.current_sector = None
        self.status_label.config(text="✓ SDAT folder loaded", foreground=self.colors['success'])
        self.draw_sector_grid()
        self.update_sector_info()

    def load_sector_into_ui(self, sector_index):
        if self.sdat_folder is None:
            return
        file_path = os.path.join(self.sdat_folder, f'sd{sector_index}.csdat')
        if not os.path.isfile(file_path):
            self.current_sector = None
            self.update_sector_info()
            return
        self.current_sector = sector_index
        with open(file_path, 'rb') as f:
            data = f.read()
        height = struct.unpack('<f', data[WATER_HEIGHT_OFFSET:WATER_HEIGHT_OFFSET+4])[0] if len(data) >= WATER_HEIGHT_OFFSET + 4 else 0.0
        if len(data) >= WATER_PATH_OFFSET:
            path_bytes = data[WATER_PATH_OFFSET:WATER_PATH_MAX_OFFSET+1]
            path_str_raw = path_bytes.split(b'\x00')[0].decode('ascii', errors='ignore').strip()
            path_str = path_str_raw if path_str_raw != '' else '00'
        else:
            path_str = '00'
        self.height_var.set(height)
        self.height_entry_var.set(f"{height:.2f}")
        if path_str in WATER_PATHS_STR:
            self.path_var.set(path_str)
        else:
            self.path_var.set(path_str)
        self.update_sector_info()

    def add_water_block(self):
        if self.current_sector is None or self.sdat_folder is None:
            messagebox.showwarning('No Sector', 'Select a sector first.')
            return
        target_path = os.path.join(self.sdat_folder, f'sd{self.current_sector}.csdat')
        if not os.path.isfile(target_path):
            messagebox.showerror('Missing file', f'{os.path.basename(target_path)} not found.')
            return

        try:
            with open(target_path, 'rb') as f:
                target_data = bytearray(f.read())

            # Save original sector byte at 0x14
            if len(target_data) > 0x14:
                original_sector_byte = target_data[0x14]
            else:
                original_sector_byte = self.current_sector & 0xFF
                if len(target_data) < 0x15:
                    target_data.extend(b'\x00' * (0x15 - len(target_data)))

            # Copy embedded template into target
            if len(target_data) < TEMPLATE_END:
                target_data.extend(b'\x00' * (TEMPLATE_END - len(target_data)))
            target_data[TEMPLATE_START:TEMPLATE_END] = EMBEDDED_TEMPLATE
            
            # Restore the original sector byte at 0x14
            target_data[0x14] = original_sector_byte

            with open(target_path, 'wb') as f:
                f.write(target_data)
                f.flush()
                os.fsync(f.fileno())

            # Reload the sector to show the template's default values
            self.load_sector_into_ui(self.current_sector)
            self.draw_sector_grid()
            messagebox.showinfo('Added', f'Water block added to sector {self.current_sector}! Now adjust settings and Save.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to add water block: {e}')

    def save_current_sector(self):
        if self.current_sector is None or self.sdat_folder is None:
            messagebox.showwarning('No Sector', 'Select a sector first.')
            return
        target_path = os.path.join(self.sdat_folder, f'sd{self.current_sector}.csdat')
        if not os.path.isfile(target_path):
            messagebox.showerror('Missing file', f'{os.path.basename(target_path)} not found.')
            return

        try:
            with open(target_path, 'rb') as f:
                target_data = bytearray(f.read())

            # Write water height
            if len(target_data) < WATER_HEIGHT_OFFSET + 4:
                target_data.extend(b'\x00' * ((WATER_HEIGHT_OFFSET + 4) - len(target_data)))
            height = float(self.height_entry_var.get())
            target_data[WATER_HEIGHT_OFFSET:WATER_HEIGHT_OFFSET+4] = struct.pack('<f', height)

            # Write water path
            max_len = WATER_PATH_MAX_OFFSET - WATER_PATH_OFFSET + 1
            path = self.path_var.get()
            if path in ('00', ''):
                path_bytes = b'\x00' * max_len
            else:
                try:
                    if path in WATER_PATHS_STR:
                        idx = WATER_PATHS_STR.index(path)
                        encoded = WATER_PATHS_BYTES[idx]
                    else:
                        encoded = path.encode('ascii', errors='ignore')
                except:
                    encoded = path.encode('ascii', errors='ignore')

                if len(encoded) >= max_len:
                    path_bytes = encoded[:max_len-1] + b'\x00'
                else:
                    path_bytes = encoded + b'\x00' + b'\x00' * (max_len - len(encoded) - 1)

            if len(target_data) < WATER_PATH_MAX_OFFSET + 1:
                target_data.extend(b'\x00' * ((WATER_PATH_MAX_OFFSET + 1) - len(target_data)))
            target_data[WATER_PATH_OFFSET:WATER_PATH_MAX_OFFSET+1] = path_bytes

            # Write FIX_BYTES at FIX_OFFSET_START
            fix_end = FIX_OFFSET_START + len(FIX_BYTES)
            if len(target_data) < fix_end:
                target_data.extend(b'\x00' * (fix_end - len(target_data)))
            target_data[FIX_OFFSET_START:fix_end] = FIX_BYTES

            with open(target_path, 'wb') as f:
                f.write(target_data)
                f.flush()
                os.fsync(f.fileno())

            self.draw_sector_grid()
            self.update_sector_info()
            messagebox.showinfo('Saved', f'Sector {self.current_sector} saved successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save: {e}')

    def reset_current_sector(self):
        if self.current_sector is None or self.sdat_folder is None:
            messagebox.showwarning('No Sector', 'Select a sector first.')
            return
        target_path = os.path.join(self.sdat_folder, f'sd{self.current_sector}.csdat')
        if not os.path.isfile(target_path):
            messagebox.showerror('Missing file', f'{os.path.basename(target_path)} not found.')
            return
        try:
            with open(target_path, 'rb') as f:
                data = bytearray(f.read())

            # Reset height
            if len(data) < WATER_HEIGHT_OFFSET + 4:
                data.extend(b'\x00' * ((WATER_HEIGHT_OFFSET + 4) - len(data)))
            data[WATER_HEIGHT_OFFSET:WATER_HEIGHT_OFFSET+4] = struct.pack('<f', 0.0)

            # Reset path region
            max_len = WATER_PATH_MAX_OFFSET - WATER_PATH_OFFSET + 1
            if len(data) < WATER_PATH_MAX_OFFSET + 1:
                data.extend(b'\x00' * ((WATER_PATH_MAX_OFFSET + 1) - len(data)))
            data[WATER_PATH_OFFSET:WATER_PATH_MAX_OFFSET+1] = b'\x00' * max_len

            # Write fix bytes
            fix_end = FIX_OFFSET_START + len(FIX_BYTES)
            if len(data) < fix_end:
                data.extend(b'\x00' * (fix_end - len(data)))
            data[FIX_OFFSET_START:fix_end] = FIX_BYTES

            with open(target_path, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())

            self.load_sector_into_ui(self.current_sector)
            self.draw_sector_grid()
            messagebox.showinfo('Reset', f'Sector {self.current_sector} reset successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to reset: {e}')

    def select_sector(self, event):
        if self.sdat_folder is None:
            return
        cell_size = 30
        col = event.x // cell_size
        row = event.y // cell_size
        row = 15 - row
        if col < 0 or col > 15 or row < 0 or row > 15:
            return
        sector_index = row * 16 + col
        file_path = os.path.join(self.sdat_folder, f'sd{sector_index}.csdat')
        if os.path.isfile(file_path):
            self.load_sector_into_ui(sector_index)
        else:
            self.current_sector = None
            self.update_sector_info()
        self.draw_sector_grid()

    def update_sector_info(self):
        if self.current_sector is None:
            self.sector_info.config(text='Select a sector to edit')
        else:
            has_water = self.sector_has_water(self.current_sector)
            status = '💧 Has water' if has_water else '⚪ No water'
            self.sector_info.config(text=f'Sector {self.current_sector} | {status}')

if __name__ == '__main__':
    root = tk.Tk()
    app = ModernWaterEditor(root)
    root.mainloop()