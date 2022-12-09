import tkinter as tk
import os

from phantom_US_toolbox.phantom_US_toolbox import load_US_data

class US_GUI:
    def __init__(self):
        # Initialize values
        self.passed_values = {}
        self.btn = []
        self.btn_2 = []
        self.file_loc = ""
        self.plot_specs = {}
        self.params = {}
        
        # Run
        self._build_GUI()
        return
    
    def _parse_file_name(self, file_name):

        fid = os.path.basename(file_name.replace('\\',os.sep))

        params = {}
        try:
            params["len_x"] = int(float(fid.split("x")[0].split("_")[-1]) + 1)
        except:
            params["len_x"] = 0
        
        try:
            params["len_y"] = int(float(fid.split("y")[0].split("_")[-1]) + 1)
        except:
            params["len_y"] = 0
        
        try:
            params["len_z"] = int(float(fid.split("z")[0].split("_")[-1]) + 1)
        except:
            params["len_z"] = 0
            
        try:
            params["f0"] = float(fid.split("UFF")[1].split("_")[0]) * 1e3
        except:
            params["f0"] = 0
        
        try:
            params["CPP"] = float(fid.split("CPP")[1].split("_")[0])
        except:
            params["CPP"] = 0
            
        try:
            params["pulse_number"] = float(fid.split("PN")[1].split("_")[0])
        except:
            params["pulse_number"] = 0
        
        try:
            params["sample_rate"] = float(fid.split("SR")[1].split("_")[0])
        except:
            params["sample_rate"] = 0
        
        try:
            params["PRF"] = float(fid.split("UPRF")[1].split("_")[0])
        except:
            params["PRF"] = 0
        
        try:
            params["input_mv"] = float(fid.split("mv")[0].split("_")[-1])
        except:
            params["input_mv"] = 0
        
        try:
            params["series_len"] = int(float(fid.split("DL")[1].split("_")[0]))
        except:
            params["series_len"] = 0 
        
        try:
            params["title"] = "_".join(fid.strip(".tdms").split("_")[-2:])
        except:
            params["title"] = 0
        
        self.params = params
        self._pack_params()
        
        return
   
    def _pack_params(self):
        
        param_frame = tk.Frame()
        
        for key in self.params.keys():
            key_label = tk.Label(text = key, master = param_frame)
            key_entry = tk.Entry(master = param_frame)
            key_entry.insert(-1, self.params[key])
            
            key_label.pack(fill=tk.BOTH)
            key_entry.pack(fill=tk.BOTH)
        
        param_frame.pack(fill=tk.BOTH)
                
        new_frame = tk.Frame()
        run_button = tk.Button(
            master=new_frame, text="Analyze Data", height=5, width=20,
            fg="black", bg="red", highlightbackground="red",
            command = lambda : self._update_vals_and_run(param_frame, fr"{self.path_entry.get()}")
        )
        
        restart_button = tk.Button(
                    master=new_frame, text="Restart Program", height=2, width=10,
                    fg="red", bg="black", highlightbackground="black",
                    command = lambda : self._restart())
        
        run_button.pack(fill=tk.BOTH)
        restart_button.pack()
        new_frame.pack()
        
        return
    
    def _run_program(self, file_path):
        # Run the program
        for tab in self.window.winfo_children():
            tab.destroy()
        
        new_frame = tk.Frame()
        l = tk.Label(text = f"Data loaded for {self.params['title']}", master = new_frame)
        l.pack(fill = tk.BOTH)
        
        self.data = load_US_data(file_path, passed_params = self.params)
        
        df = self.data.return_dataframe()
        df_frame = tk.Frame()
        
        for i in range(df.shape[0]):
            name = tk.Label(text=df.iloc[i].name, master = df_frame)
            try:
                val = tk.Label(text=round(df.iloc[i].values[0],3), master = df_frame)
            except:
                val = tk.Label(text=df.iloc[i].values[0], master = df_frame)
            name.grid(row=i, column=0)
            val.grid(row=i, column=1)
        
        
        plot_frame = self._plotting_frame()
        plot_locs = self._plotting_slices()
        plot_buttom_frame = tk.Frame()
        
        plot_button = tk.Button(
                    master=plot_buttom_frame, text="Plot", height=5, width=20,
                    fg="black", bg="red", highlightbackground="red",
                    command = lambda : self._make_plot())
        
        
        
        restart_button = tk.Button(
                    master=plot_buttom_frame, text="Restart Program", height=2, width=10,
                    fg="red", bg="black", highlightbackground="black",
                    command = lambda : self._restart())
        
        new_frame.pack()
        df_frame.pack()
        plot_frame.pack(fill=tk.BOTH)
        plot_locs.pack(fill=tk.BOTH)
        plot_button.pack()
        restart_button.pack()
        plot_buttom_frame.pack()
        
        return
    
    def _restart(self):
        self.window.destroy()
        self._build_GUI()
        return
    
    def _make_plot(self):
        
        if self.plot_specs["XY"] == True:
            if self.plot_specs["Focal Point"] == True:
                _slice = "max_slice"
            elif self.plot_specs["All"] == True:
                _slice = "all"
            else:
                _slice = int(self.plotting_idx.get())
                
            if self.plot_specs["Pressure"] == True:
                self.data.plot_XY(param = "Pressure", slice_idx = _slice)
            if self.plot_specs["Intensity"] == True:
                self.data.plot_XY(param = "Intensity", slice_idx = _slice)
                       
                
        if self.plot_specs["XZ"] == True:
            if self.plot_specs["Focal Point"] == True:
                _slice = "max_slice"
            elif self.plot_specs["All"] == True:
                _slice = "all"
            else:
                _slice = int(self.plotting_idx.get())
                
            if self.plot_specs["Pressure"] == True:
                self.data.plot_XZ(param = "Pressure", slice_idx = _slice)
            if self.plot_specs["Intensity"] == True:
                self.data.plot_XZ(param = "Intensity", slice_idx = _slice)
        return
        
    def _update_vals_and_run(self, parent_widget, file_path):
        
        # Update Values
        children_widgets = parent_widget.winfo_children()
        for child_widget in children_widgets:
            # This follows the building logic of the GUI >> 
            # Label 1
            # Value 1
            # Label 2
            # Value 2
            # ... etc ...
            if child_widget.winfo_class() == 'Entry':
                val = child_widget.get()
                self.params[key] == val
                
            else:
                key = child_widget.cget("text")
                
        
        # Run
        self._run_program(file_path)
        
        return

    def _build_GUI(self):
        self.window = tk.Tk()

        # Frame 1: r/path/to/file
        frame_1 = tk.Frame()
        path_label = tk.Label(text="Path to tdms file", master = frame_1)
        self.path_entry = tk.Entry(master = frame_1)
        self.path_entry.insert(-1, "/path/to/file.tdms")
        path_label.pack(fill=tk.BOTH)
        self.path_entry.pack(fill=tk.BOTH)
        
        
        # Frame 6: Parse File Button
        frame_2 = tk.Frame()
        run_button = tk.Button(
            master=frame_2, text="Parse File", height=5, width=20,
            fg="black", bg="red", highlightbackground="red",
            command = lambda : self._parse_file_name(fr"{self.path_entry.get()}")
        )
        
        run_button.pack(fill=tk.BOTH)

        frame_1.pack()
        frame_2.pack()

        self.window.mainloop()
        
        return
    
    
    def _plotting_frame(self):
        
        frame = tk.Frame()
        
        _specs = ["Pressure", "Intensity", "XY", "XZ"]
                
        for i in _specs:
            self.plot_specs[i] = False

        frame.rowconfigure(0, minsize=50, weight=1)
        frame.columnconfigure([0, 1, 2, 3, 4], minsize=50, weight=1)

        b = tk.Label(
            master=frame,
            text="Select Plotting Option(s)"
        )
        b.grid(row=0, column=0)
        for i in range(len(_specs)):
            b = tk.Button(
                master=frame, text=_specs[i], fg="grey", bg="white",
                command=lambda i=i: self._button_press(self.btn, _specs[i], i)
            )

            b.grid(row=0, column=i + 1)
            self.btn.append(b)
        
        return(frame)
    
    
    def _plotting_slices(self):
        
        frame = tk.Frame()
        
        _specs = ["Focal Point", "All"]
                
        for i in _specs:
            self.plot_specs[i] = False

        frame.rowconfigure(0, minsize=50, weight=1)
        frame.columnconfigure([0, 1, 2, 3, 4], minsize=50, weight=1)

        b = tk.Label(
            master=frame,
            text="Select Plotting Location (only one):"
        )
        b.grid(row=0, column=0)
        for i in range(len(_specs)):
            b = tk.Button(
                master=frame, text=_specs[i], fg="grey", bg="white",
                command=lambda i=i: self._button_press(self.btn_2, _specs[i], i)
            )
            
            b.grid(row=0, column=i + 1)
            self.btn_2.append(b)
        b = tk.Label(text="Other (integer loc):", master = frame)
        b.grid(row=0, column = len(_specs) + 2)
        self.plotting_idx = tk.Entry(master = frame)
        self.plotting_idx.grid(row=0, column = len(_specs) + 3)
        
        return(frame)
    
    
    def _button_press(self, btn_array, file_type, i):
        if btn_array[i]["fg"] == 'grey':
            btn_array[i]["fg"] = 'Red'
            self.plot_specs[f"{file_type}"] = True
        else:
            btn_array[i]["fg"] = 'grey'
            self.plot_specs[f"{file_type}"] = False

        return