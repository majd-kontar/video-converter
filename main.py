from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
import tkinter as tk
import os
import subprocess

videos_path = "D:/user/Videos"
desktop_path = "D:/user/Desktop"

title = 'FFmpeg'
button_color = 'sky blue'
button_size = {'height': 5, 'width': 20}
button_font = ('Arial', 16)
base = tk.Tk()
filetypes = (('Video files', ['*.webm', '*.mpg', '*.mp2', '*.mpeg', '*.mpe', '*.mpv', '*.ogg', '*.mp4', '*.m4p', '*.m4v', '*.avi', '*.wmv', '*.mov',
                              '*.qt', '*.flv', '*.swf', '*.mkv']),
             ('Audio files', ['*.mp3', '*.weba', '*.flp', '*.wav', '*.aac', '*.flac', '*.wma']),
             ('All files', '*.*'))
valid_types = ['webm', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'ogg', 'mp4', 'm4p', 'm4v', 'avi', 'wmv', 'mov', 'qt', 'flv', 'swf', 'mkv', 'mp3', 'weba',
               'flp', 'wav', 'aac', 'flac', 'wma']
subtitle_types = (('Subtitle files', '*.srt'), ('All files', '*.*'))


def get_file():
    return filedialog.askopenfilenames(filetypes=filetypes, initialdir=videos_path)


def get_dir(file):
    pick_dir = messagebox.askyesno(message='Would you like to select an output directory?', title=title)
    if pick_dir:
        directory = ''
        while len(directory) == 0:
            directory = filedialog.askdirectory(initialdir=desktop_path)
            if len(directory) == 0:
                messagebox.showwarning(title=title, message="No directory chosen!\nPlease choose a directory")
    else:
        x = file[0]
        directory = x[0:x.rfind('/', x.rfind('/') - 1)]
    return directory


def get_ext():
    ext = None
    while ext is None or ext not in valid_types:
        ext = simpledialog.askstring(title, 'Enter an output file format (mp4, mp3, mkv, wmv, avi...):', )
        if ext is None:
            messagebox.showwarning(title, 'Please enter a file format.')
        elif ext not in valid_types:
            messagebox.showwarning(title, 'Please enter a valid file format.')
    return ext


def get_name():
    name = None
    while name is None:
        name = simpledialog.askstring(title, 'Enter the output file name:', )
        if name is None:
            messagebox.showwarning(title, 'Please enter a file name.')
    return name


def get_feedback(command):
    for cmd in command:
        out, err = cmd.communicate()
        if err is not None:
            return messagebox.showinfo(title, err)
    return messagebox.showinfo(title, 'Operation Successful')


def escape(s):
    s = s.replace('\\', '/').replace('\'', '\\\\\\\'').replace('\"', '\\\\\\\"').replace(':', '\\\\:')
    print(s)
    return s


def option1():
    input_file = get_file()
    if len(input_file) == 0:
        return
    ext = get_ext()
    directory = get_dir(input_file)
    convert(input_file, ext, directory)


def option2():
    input_file = get_file()
    if len(input_file) == 0:
        return
    messagebox.showinfo(title, 'Please select subtitle file(s).')
    sub_file = []
    while len(sub_file) != len(input_file):
        sub_file = filedialog.askopenfilenames(initialdir="D:/user/Videos", filetypes=subtitle_types)
        if len(sub_file) == 0:
            messagebox.showerror(title=title, message="No subtitles chosen!\nPlease choose subtitles")
        elif len(sub_file) != len(input_file):
            messagebox.showerror(title=title, message="Please choose " + str(len(input_file)) + " subtitle file(s)")
    ext = get_ext()
    font = None
    while font is None:
        font = simpledialog.askinteger(title, 'Please choose a font size (default = 24):', initialvalue=24, minvalue=8, maxvalue=50)
        if font is None:
            messagebox.showerror(title=title, message="Please choose a font size")
    directory = get_dir(input_file)
    burn_subs(input_file, sub_file, font, ext, directory)


def option3():
    input_file = get_file()
    if len(input_file) == 0:
        return
    frames_per_second = None
    while frames_per_second is None:
        frames_per_second = simpledialog.askinteger(title, 'Please choose a sampling rate (frames per second):', initialvalue=60, maxvalue=99999,
                                                    minvalue=0)
        if frames_per_second is None:
            messagebox.showerror(title=title, message="Please choose a sampling rate")
    directory = get_dir(input_file)
    sample(input_file, frames_per_second, "jpg", directory)


def option4():
    input_file = get_file()
    if len(input_file) == 0:
        return
    directory = get_dir(input_file)
    name = get_name()
    combine(input_file, name, directory)


def convert(inputs, ext, directory):
    commands = []
    outputs = [directory + inp[inp.rfind('/'):inp.rfind('.')] + '.' + ext for inp in inputs]
    for i, video in enumerate(inputs):
        cmd = subprocess.Popen(["ffmpeg", "-hwaccel", "cuda", "-i", video, outputs[i]])
        commands.append(cmd)
    get_feedback(commands)


def combine(inputs, name, directory):
    output = directory + '/' + name + inputs[0][inputs[0].rfind('.'):]
    # print(output)
    files = []
    f = open('mylist.txt', 'w')
    for video in inputs:
        files.append('file \'' + video + '\'')
    mylist = '\n'.join(map(str, files))
    f.write(mylist)
    f.close()
    # print(mylist)
    cmd = subprocess.Popen(["ffmpeg", "-hwaccel", "cuda", "-f", "concat", "-safe", "0", "-i", "mylist.txt", "-c", "copy", output])
    get_feedback(cmd)


def burn_subs(inputs, sub_file, font, ext, directory):
    commands = []
    outputs = [directory + inp[inp.rfind('/'):inp.rfind('.')] + '.' + ext for inp in inputs]
    for i, video in enumerate(inputs):
        cmd = subprocess.Popen(
            ["ffmpeg", "-hwaccel", "cuda", "-i", video, "-vf", "subtitles=" + escape(sub_file[i]) + ":force_style=Fontsize=" + str(font), outputs[i]])
        commands.append(cmd)
    get_feedback(commands)


def sample(inputs, frames_per_second, ext, directory=None):
    commands = []
    outputs = [directory + inp[inp.rfind('/'):inp.rfind('.')] + '/' for inp in inputs]
    for i, video in enumerate(inputs):
        try:
            os.mkdir(outputs[i])
        except FileExistsError:
            pass
        cmd = subprocess.Popen(["ffmpeg", "-hwaccel", "cuda", "-i", video, "-r", str(frames_per_second), outputs[i] + "out%d." + ext])
        commands.append(cmd)
    get_feedback(commands)


def main():
    base.resizable(False, False)
    base.title('FFmpeg')
    tk.Label(base, text='Please select one of the options', font=("Arial", 25, 'bold')).pack()
    options = tk.Frame(base, width=500, height=120).pack()
    op1 = tk.Button(options, text='Convert Video Type', width=button_size['width'], height=button_size['height'], font=button_font, bg=button_color,
                    command=option1).pack(side=tk.LEFT)
    op2 = tk.Button(options, text='Burn Subtitles', width=button_size['width'], height=button_size['height'], font=button_font, bg=button_color,
                    command=option2).pack(side=tk.LEFT)
    op3 = tk.Button(options, text='Sample Video', width=button_size['width'], height=button_size['height'], font=button_font, bg=button_color,
                    command=option3).pack(side=tk.RIGHT)
    op4 = tk.Button(options, text='Combine Videos', width=button_size['width'], height=button_size['height'], font=button_font, bg=button_color,
                    command=option4).pack(side=tk.RIGHT)
    base.wait_window()
    base.mainloop()


if __name__ == '__main__':
    main()
