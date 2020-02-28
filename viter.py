#!/bin/python3

import sys
import os
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")

from gi.repository import Gtk, Vte, GLib, Pango  # noqa E402


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
        self.set_font(Pango.FontDescription("Monospace 12.5"))


class Window(Gtk.Window):
    def __init__(self, terminal):
        Gtk.Window.__init__(self, title="viter")
        self.connect("delete_event", Gtk.main_quit)

        box = Gtk.VBox()
        self.add(box)
        box.pack_start(terminal, True, True, 0)

        command_line = Gtk.Entry(placeholder_text="sample text")
        # `override_font` is deprecated.
        # Nothing like this is exposed instead though.
        command_line.override_font(Pango.FontDescription("Monospace 12.5"))
        box.pack_start(command_line, False, True, 0)

        self.show_all()


if __name__ == "__main__":
    child_argv = sys.argv[1:]
    if child_argv == []:
        child_argv = [os.environ["SHELL"]]
    term = Terminal(child_argv)
    wind = Window(term)
    Gtk.main()
