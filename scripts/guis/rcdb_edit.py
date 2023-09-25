# RCDB edit tool for Hall C
# 09.07.2023 Sanghwa Park <sanghwa@jlab.org>
#
# Conditions that can be updated from this gui
# : run_type, run_flag, user_comment
# 
# To-Dos: (add to-do items here for improvement..
#  Elecments are currently packed at fixed positions
#  Make it adjustable in the future

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import traceback

import rcdb
from rcdb.provider import RCDBProvider

class RCDB_EDIT(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="RCDB Edit")

        self.set_size_request(350,600)
        self.timeout_id = None
        self.set_border_width(10)

        self.run_flag_selected = None
        self.run_type_selected = ""
        self.user_comment_selected = ""
        self.myDBTool = None

        ### First, run number ###
        fixed = Gtk.Fixed()
        lbl = Gtk.Label("Run Number:")
        fixed.put(lbl, 25, 35)
        self.entry1 = Gtk.Entry()
        fixed.put(self.entry1, 125, 30)
        button1 = Gtk.Button("Connect")
        button1.connect("clicked", self.on_connect, self.entry1)
        fixed.put(button1, 300, 30)

        ### Run Type ###
        lbl2 = Gtk.Label("Run Type:")
        fixed.put(lbl2, 25, 80)

        self.text2 = Gtk.Entry()
        fixed.put(self.text2, 125, 80)

        type_store = Gtk.ListStore(str)
        run_types = ["Production", 
                     "Commission", 
                     "Cosmics", 
                     "Spot++", 
                     "LED",
                     "Elastic",
                     "Optics", 
                     "Junk",
                     "Other"]

        for run_type in run_types:
            type_store.append([run_type])

        treeView = Gtk.TreeView()
        treeView.set_model(type_store)
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Select New Run Types", rendererText, text=0)
        treeView.append_column(column)

        fixed.put(treeView, 127, 120)

        self.selection = treeView.get_selection()
        self.selection.connect("changed", self.on_changed)

        #### USER COMMENT ####
        lbl3 = Gtk.Label("User Comment:")
        fixed.put(lbl3, 25, 400)
        hbox = Gtk.HBox()
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_size_request(350, 30)

        comment_text = Gtk.TextView()
        self.textbuffer = comment_text.get_buffer()
        self.textbuffer.set_text("")
        scrolledwindow.add(comment_text)
        hbox.pack_start(scrolledwindow, True, True, 1)
        fixed.put(hbox, 25, 420)

        #### RUN FLAG ###
        lbl4 = Gtk.Label("Run Flag:")
        fixed.put(lbl4, 25, 480)

        #hidden for the inital value
        self.rbutton0 = Gtk.RadioButton.new_with_label_from_widget(None, "None")
        self.rbutton0.connect("toggled", self.on_rbutton_toggled, "None")

        self.rbutton1 = Gtk.RadioButton.new_from_widget(self.rbutton0)
        self.rbutton1.set_label("Good")
        self.rbutton1.connect("toggled", self.on_rbutton_toggled, "Good")

        self.rbutton2 = Gtk.RadioButton.new_from_widget(self.rbutton0)
        self.rbutton2.set_label("NeedCut")
        self.rbutton2.connect("toggled", self.on_rbutton_toggled, "NeedCut")

        self.rbutton3 = Gtk.RadioButton.new_from_widget(self.rbutton0)
        self.rbutton3.set_label("Bad")
        self.rbutton3.connect("toggled", self.on_rbutton_toggled, "Bad")

        self.rbutton4 = Gtk.RadioButton.new_from_widget(self.rbutton0)
        self.rbutton4.set_label("Suspicous")
        self.rbutton4.connect("toggled", self.on_rbutton_toggled, "Suspicious")

        fixed.put(self.rbutton1, 110, 480)
        fixed.put(self.rbutton2, 180, 480)
        fixed.put(self.rbutton3, 270, 480)
        fixed.put(self.rbutton4, 330, 480)

        # Save and exit
        ok_button = Gtk.Button("SAVE")
        ok_button.connect("clicked", self.on_ok_clicked, self.entry1)
        ok_button.set_size_request(160, 10)

        cancel_button = Gtk.Button("CANCEL")
        cancel_button.connect("clicked", self.on_cancel_clicked)
        cancel_button.set_size_request(160, 10)

        fixed.put(ok_button, 50, 520)
        fixed.put(cancel_button, 220, 520)

        self.add(fixed)

    def on_ok_clicked(self, widget, value):
        runnum = value.get_text()
        if self.myDBTool is not None:
            if self.run_type_selected is not None:
                print ("New run type:", self.run_type_selected)
                self.myDBTool.save_new_condition(runnum, "run_type", self.run_type_selected)
            if self.run_flag_selected is not None:
                print ("New run flag:", self.run_flag_selected)
                self.myDBTool.save_new_condition(runnum, "run_flag", self.run_flag_selected)
            if self.user_comment_selected is not None:
                buf = self.textbuffer
                comment = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)
                print ("New user comment:", comment)
                self.myDBTool.save_new_condition(runnum, "user_comment", comment)
        else:
            print ("DB connection failed?")
        #Gtk.main_quit()

    def on_cancel_clicked(self, widget):
        Gtk.main_quit()

    def on_rbutton_toggled(self, button, name):
        if button.get_active():
            state = "on"
        else:
            state = "off"
        self.run_flag_selected = name

    def on_connect(self, widget, value):
        con_str = "mysql://rcdb@cdaqdb1.jlab.org:3306/c-rcdb"
        self.myDBTool = DBTool(con_str)

        if not self.myDBTool.is_connected:
            print ("ERROR: Failed to connect to DB")
        else:
            read_ok = self.myDBTool.read_conditions(value.get_text())
            if read_ok:
                # Run type
                if self.myDBTool.run_type is not None:
                    self.run_type_selected = self.myDBTool.run_type
                    self.text2.set_text(self.run_type_selected)
                # Run flag
                if self.myDBTool.run_flag is not None:
                    self.run_flag_selected = self.myDBTool.run_flag
                    if self.run_flag_selected == "Good":
                        self.rbutton1.set_active(True)
                    if self.run_flag_selected == "NeedCut":
                        self.rbutton2.set_active(True)
                    elif self.run_flag_selected == "Bad":
                        self.rbutton3.set_active(True)
                    elif self.run_flag_selected == "Suspicious":
                        self.rbutton4.set_active(True)
                    else:
                        print ("Warning: Invalid run flag from DB: %s" % self.run_flag_selected)
                # User comment
                if self.myDBTool.user_comment is not None:
                    self.user_comment_selected = self.myDBTool.user_comment
                    self.textbuffer.set_text(self.user_comment_selected)

    def on_changed(self, selection):
        (model, iter) = selection.get_selected()
        if iter is not None:
            print ("Run type:",  model[iter][0], "selected")
        else:
            print ("MOOOOOOOOOOOOOO")
        self.run_type_selected = model[iter][0]

class DBTool(object):
    def __init__(self, con_str=None):
        self.connection_string = ""
        self.run_type = None
        self.user_comment = None
        self.run_flag = None
        self.is_connected = None
        self.run_number = None
        self.run = None

        if con_str and self.is_connected is not True:
            print ("connect to DB")
            self.db = rcdb.RCDBProvider(con_str)            
            self.is_connected = True
            
    def read_conditions(self, run_num):
        read_ok = False

        self.run_number = run_num
        self.run = self.db.get_run(run_num)
        if not self.run:
            print ("ERROR: Run %s is not found in DB" % run_num)
            return False
        else:        
            try:
                self.run_type = self.db.get_condition(self.run, "run_type").value
                read_ok = True
            except Exception as ex:
                print ("Info: no initial run_type condition available in DB")
            try:
                self.run_flag = self.db.get_condition(self.run, "run_flag").value
                read_ok = True
            except Exception as ex:
                print ("Info: no initial run_flag condition available in DB")
            try:
                self.user_comment = self.db.get_condition(self.run, "user_comment").value
                read_ok = True
            except Exception as ex:
                print ("Info: no initial user_comment available in DB")
        return read_ok

    def save_new_condition(self, runnum, key, val):
        if not self.is_connected:
            print ("ERROR: No DB connection?????")
            return

        if runnum != self.run_number:
            print ("ERROR: Run Number mismatch! Check run number again!")
            return
        try:
            self.db.add_condition(self.run, key, val, True)
            print("Saved to DB: %s %s" % (key, str(val)))
        except Exception as ex:
            print("ERROR: fail to update the DB, %s" % key)
        return


#--------------------
# Main program
#--------------------
win = RCDB_EDIT()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
