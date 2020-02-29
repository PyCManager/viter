#!/bin/python3

import sys
import os
import gi
import enum

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")

# We import more than we actually use so that more things are exposed to user configs.
from gi.repository import Gtk, Vte, GLib, Pango, Gdk  # noqa E402

Mode = enum.Enum("Mode", ["NORMAL", "DETACHED"])


class Terminal(Vte.Terminal):
    def __init__(self, argv):
        Vte.Terminal.__init__(self)
        self.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,
            argv,
            None,
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
        )


class Window(Gtk.Window):
    def handle_detached_key_press(self, event):
        if event.keyval == Gdk.KEY_colon:
            if not self.command_line.has_focus():
                self.command_line.grab_focus()
                Gtk.Entry.do_insert_at_cursor(self.command_line, ":")
                return True
        if event.keyval == Gdk.KEY_slash:
            if not self.command_line.has_focus():
                self.command_line.grab_focus()
                Gtk.Entry.do_insert_at_cursor(self.command_line, "/")
                return True

    def key_press_handler(self, widget, event):
        if (
            event.keyval == Gdk.KEY_space
            and event.state & Gdk.ModifierType.CONTROL_MASK > 0
        ):
            if self.command_line.is_visible():
                self.command_line.hide()
                self.mode = Mode.NORMAL
            else:
                self.command_line.show()
                self.mode = Mode.DETACHED
            return True

        if self.mode == Mode.DETACHED:
            return self.handle_detached_key_press(event)

    def command_handler(self, command_line):
        command = command_line.get_text()
        if command[0] == ":":
            try:
                eval(command[1:])
            except Exception as err:
                command_line.set_text(str(err))
        elif command[0] == "/":
            # TODO search.
            pass

    def movement_handler(self, terminal):
        x, y = terminal.get_cursor_position()
        self.command_line.set_placeholder_text(str((x, y)))

    def derive_command_line_appearance(self):
        # `override_font` is deprecated.
        # Nothing like it is exposed instead though.
        self.command_line.override_font(self.terminal.get_font())

    def __init__(self, terminal_shell_argv):
        Gtk.Window.__init__(self, title="viter")
        self.connect("delete_event", Gtk.main_quit)
        self.connect("key_press_event", self.key_press_handler)

        self.terminal = Terminal(terminal_shell_argv)
        self.terminal.connect("cursor_moved", self.movement_handler)

        self.box = Gtk.VBox()
        self.add(self.box)
        self.box.pack_start(self.terminal, True, True, 0)

        self.command_line = Gtk.Entry(placeholder_text="sample text")
        self.command_line.connect("activate", self.command_handler)
        self.box.pack_start(self.command_line, False, True, 0)

        self.derive_command_line_appearance()

        self.show_all()

        self.command_line.hide()
        self.mode = Mode.NORMAL


def read_config():
    if "XDG_CONFIG_HOME" in os.environ:
        config_dir = os.environ["XDG_CONFIG_HOME"]
    else:
        config_dir = os.environ["HOME"] + "/.config"

    path = config_dir + "/viter/viterrc.py"
    if os.path.isfile(path):
        config_file = open(path, "r")
        exec(config_file.read())


if __name__ == "__main__":
    child_argv = sys.argv[1:]
    if child_argv == []:
        child_argv = [os.environ["SHELL"]]
    window = Window(child_argv)
    read_config()
    Gtk.main()
