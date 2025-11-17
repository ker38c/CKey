from queue import Queue, Empty
import weakref


class UiDispatcher:
    """Central UI dispatcher to schedule callbacks on the tkinter main thread."""
    def __init__(self, root, poll_ms: int = 10):
        self._root = root
        self._queue = Queue()
        self._poll_ms = int(poll_ms)
        self._running = False
        # optional registry of named widgets (store weakrefs)
        self._registry = {}

    def _poll(self):
        try:
            while True:
                func, args, kwargs = self._queue.get_nowait()
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    # Do not crash the poll loop; print for debugging.
                    print("UiDispatcher callback error:", e)
        except Empty:
            pass

        if self._running:
            try:
                self._root.after(self._poll_ms, self._poll)
            except Exception:
                # If scheduling fails, stop polling to avoid noisy errors
                self._running = False

    def start(self):
        if not self._running:
            self._running = True
            try:
                self._root.after(self._poll_ms, self._poll)
            except Exception:
                self._running = False

    def stop(self):
        self._running = False

    # Registry helpers
    def register(self, name: str, widget):
        """Register a widget under `name`. Stored as a weak reference."""
        try:
            self._registry[name] = weakref.ref(widget)
        except Exception:
            pass

    def unregister(self, name: str):
        self._registry.pop(name, None)

    def post_to(self, name: str, method_name: str, *args, **kwargs):
        """Post a call to `widget.method_name(*args, **kwargs)` using the registered widget name.

        This is safe from background threads. If the widget no longer exists, the call is ignored.
        """
        ref = self._registry.get(name)
        if ref is None:
            return
        widget = None
        try:
            widget = ref()
        except Exception:
            widget = None

        if widget is None:
            # Remove dead reference
            self._registry.pop(name, None)
            return

        func = getattr(widget, method_name, None)
        if func is None:
            return

        self._queue.put((func, args, kwargs))
