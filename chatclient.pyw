#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import ttk
import tkinter
import socket
import threading
import pickle


host = socket.gethostbyname(socket.gethostname())
port = 50000
encoding = "utf-8"


class ScrollableCanvas(tkinter.Canvas):

    """Class for creating scrollable canvas."""

    def __init__(self, *args, **kwargs):
        tkinter.Canvas.__init__(self, *args, **kwargs)
        self.master = args[0]
        self.create_scrollbar()
        self.scroll_down()

    def create_scrollbar(self, position="right"):
        """Create a scrollbar widget for the canvas.
        The scrollbar will have the same master widget as the canvas."""

        self.scrollbar = ttk.Scrollbar(self.master)
        self.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.yview)
        self.scrollbar.pack(side=position, fill="y")

    def set_scrollregion(self, y):
        """Set vertical scrollregion."""

        self.configure(scrollregion=(0, 0, 0, y))

    def adjust(self, event=None):
        """Read the new canvas size."""

        self.width = self.winfo_width()
        self.height = self.winfo_height()

    def scroll_down(self):
        """Scrolls to the bottom."""

        self.yview_moveto(1)


class MenuBar(ttk.Frame):

    def __init__(self, master, appobj):
        ttk.Frame.__init__(self, master, padding=2, relief="groove")

        self.app = appobj

        filebutton = ttk.Menubutton(self, text="File")
        filebutton.pack(side="left")
        filemenu = tkinter.Menu(filebutton, tearoff=0)
        filemenu.add_command(label="Connect", command=self.connectpopup)
        filemenu.add_command(label="Exit", command=appobj.exit)
        filebutton.configure(menu=filemenu)

        optionsbutton = ttk.Menubutton(self, text="Options")
        optionsbutton.pack(side="left")
        optionsmenu = tkinter.Menu(optionsbutton, tearoff=0)
        optionsmenu.add_command(label="Set name", command=self.namepopup)
        optionsmenu.add_command(label="Background", command=self.bgpopup)
        optionsbutton.configure(menu=optionsmenu)

    def connectpopup(self):
        """Popup window to help connecting to the server."""

        self.popup = tkinter.Toplevel()
        self.popup.title("Connect")
        addlbl = ttk.Label(self.popup, text="Address: ")
        addlbl.grid(row=1, column=1, padx=5, pady=5)
        self.ipent = ttk.Entry(self.popup)
        self.ipent.insert(0, "{}:{}".format(host, port))
        self.ipent.grid(row=1, column=2, padx=5, pady=5)
        okbutton = ttk.Button(self.popup, text="OK", command=self.connect)
        okbutton.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

    def namepopup(self):
        """Popup window to change username."""

        self.namepopup = tkinter.Toplevel()
        self.namepopup.title("Set name")
        namelbl = ttk.Label(self.namepopup, text="Name: ")
        namelbl.grid(row=1, column=1, padx=5, pady=5)
        self.nameent = ttk.Entry(self.namepopup)
        self.nameent.insert(0, self.app.clientdata["name"])
        self.nameent.bind("<Return>", self.changename)
        self.nameent.grid(row=1, column=2, padx=5, pady=5)
        okbutton = ttk.Button(
            self.namepopup, text="OK", command=self.changename)
        okbutton.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

    def bgpopup(self):
        """Popup window that allows to user to set their background color."""

        bg = self.app.clientdata["background"]
        self.rgb = self.get_rgb(bg)
        self.bgpopup = tkinter.Toplevel()
        self.bgpopup.title("Choose background color")

        self.canvas = tkinter.Canvas(
            self.bgpopup, width=300, height=200, bg=bg)
        self.canvas.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        color_r_label = ttk.Label(self.bgpopup, text="Red: ")
        color_r_label.grid(row=1, column=0, sticky="e")
        self.color_r_entry = ttk.Entry(self.bgpopup, width=5)
        self.color_r_entry.insert(0, self.rgb[0])
        self.color_r_entry.bind("<KeyRelease>", self.adjust_palette)
        self.color_r_entry.grid(row=1, column=1, sticky="w")

        color_g_label = ttk.Label(self.bgpopup, text="Green: ")
        color_g_label.grid(row=2, column=0, sticky="e")
        self.color_g_entry = ttk.Entry(self.bgpopup, width=5)
        self.color_g_entry.insert(0, self.rgb[1])
        self.color_g_entry.bind("<KeyRelease>", self.adjust_palette)
        self.color_g_entry.grid(row=2, column=1, sticky="w")

        color_b_label = ttk.Label(self.bgpopup, text="Blue: ")
        color_b_label.grid(row=3, column=0, sticky="e")
        self.color_b_entry = ttk.Entry(self.bgpopup, width=5)
        self.color_b_entry.insert(0, self.rgb[2])
        self.color_b_entry.bind("<KeyRelease>", self.adjust_palette)
        self.color_b_entry.grid(row=3, column=1, sticky="w")

        okbutton = ttk.Button(self.bgpopup, text="OK", command=self.change_bg)
        okbutton.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def adjust_palette(self, event):
        """Change the color of the sample canvas
        according to the RGB values."""

        r = self.color_r_entry.get()
        g = self.color_g_entry.get()
        b = self.color_b_entry.get()

        # there is no guarantee at all that r, g, b values are acceptable
        try:
            r, g, b = int(r), int(g), int(b)
            if r < 0: r = 0
            if r > 255: r = 255
            if g < 0: g = 0
            if g > 255: g = 255
            if b < 0: b = 0
            if b > 255: b = 255
            bg = "#{:02x}{:02x}{:02x}".format(r, g, b)
            self.canvas.configure(bg=bg)
            self.rgb = (r, g, b)
        except ValueError:
            pass

    def get_rgb(self, string):
        """Return a tuple, (R, G, B) from a hex string."""

        r = int(string[1:3], 16)
        g = int(string[3:5], 16)
        b = int(string[5:7], 16)
        return r, g, b

    def connect(self):
        host = self.ipent.get().split(":")[0]
        port = int(self.ipent.get().split(":")[1])
        self.popup.destroy()
        app.connect(host, port)

    def changename(self, event=None):
        app.clientdata["name"] = self.nameent.get()
        f = open("client.data", "wb")
        pickle.dump(app.clientdata, f)
        f.close()
        self.namepopup.destroy()

    def change_bg(self):
        """Change the color of the background."""

        r, g, b = self.rgb
        bg = "#{:02x}{:02x}{:02x}".format(r, g, b)
        self.app.msgwin.set_background(bg)
        f = open("client.data", "wb")
        pickle.dump(app.clientdata, f)
        f.close()
        self.bgpopup.destroy()


class MessageWindow(ttk.Frame):

    """Widget for displaying messages. Contains scrolled canvas widget."""

    leftmargin = 10
    spacing = 20

    def __init__(self, master, chat):
        ttk.Frame.__init__(self, master)
        self.messages = []
        self.chat = chat
        self.canvas = ScrollableCanvas(
            self, width=100, height=100, bg=self.chat.clientdata["background"])
        self.canvas.bind("<Configure>", self.canvas.adjust)
        self.canvas.pack(fill="both", expand="yes", side="left")
        self.bottom = 0

    def drawmessage(self, string, color="white"):
        """Draw text on the canvas."""

        x = MessageWindow.leftmargin
        y = (len(self.messages) + 0.5) * MessageWindow.spacing
        self.canvas.create_text(
            x, y, text=string, anchor="nw", fill=color, font="arial 10 bold")
        self.canvas.set_scrollregion(y + MessageWindow.spacing)
        self.canvas.scroll_down()
        self.messages.append(string)

    def set_background(self, color):
        """Change the background to color, where color is a hex string."""

        self.chat.clientdata["background"] = color
        self.canvas.configure(bg=self.chat.clientdata["background"])


class Chat:

    """Main window of the application."""

    def __init__(self, master):
        self.master = master
        self.connected = False
        self.load_data()

        self.master.title("Chat (Alpha version)")
        self.master.wm_minsize(300, 400)
        self.master.protocol("WM_DELETE_WINDOW", self.exit)

        # Widgets are packed on the main window
        # MenuBar passes the application object to its constructor
        # to be able to associate menu elements with application-level methods
        menubar = MenuBar(master, self)
        menubar.pack(fill="x")

        self.msgwin = MessageWindow(master, self)
        self.msgwin.pack(fill="both", expand="yes")
        sendframe = ttk.Frame(self.master)
        sendframe.pack(fill="x")
        self.messagebox = ttk.Entry(sendframe)
        self.messagebox.bind("<Return>", self.sendmessage)
        self.messagebox.pack(fill="x", expand="yes", side="left")
        ttk.Button(sendframe, text="Send", command=self.sendmessage).pack()
        self.connection = socket.socket()

        # this update is required for the popup window to show up at the top
        self.master.update()

        if self.clientdata["name"] == "clientname":
            menubar.namepopup()

    def load_data(self):
        """Load the client's data from an external file."""

        try:
            f = open("client.data", "rb")
            self.clientdata = pickle.load(f)
        except FileNotFoundError:
            f = open("client.data", "wb")
            self.clientdata = {"name": "clientname", "background": "#5050C8"}
            pickle.dump(self.clientdata, f)
        finally:
            f.close()

    def connect(self, host, port):
        """Connect to the server."""

        if self.connected:
            return
        try:
            self.connection.connect((host, port))
            self.connected = True
        except socket.error:
            self.msgwin.drawmessage("Connection to server failed.")
        if self.connected:
            self.msgthread = RecieveThread()
            self.msgthread.start()

    def sendmessage(self, event=None):

        if not self.connected:
            return
        message = "{}: {}".format(
            self.clientdata["name"], self.messagebox.get())
        self.connection.send(bytes(message, encoding))
        self.msgwin.drawmessage(message)
        self.messagebox.delete(0, "end")
        self.messagebox.focus_set()

    def exit(self):
        """Exit method for the app."""

        # let the server know we're quiting
        if self.connected:
            self.connection.send(
                bytes("{}:CLIENT_EXIT_MESSAGE".format(self.clientdata["name"]), encoding))
        self.master.quit()


class RecieveThread(threading.Thread):

    """Thread that keeps checking for messages from the server."""

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            msg = app.connection.recv(1024).decode(encoding)
            # the way I close this thread is I send the message to the server
            # that the client wants to close the connection,
            # then I stop the recieving thread based on the server's response
            if msg == "REMOTECLOSE_THREAD":
                break
            app.msgwin.drawmessage(msg)

if __name__ == "__main__":
    root = tkinter.Tk()
    app = Chat(root)
    root.mainloop()
