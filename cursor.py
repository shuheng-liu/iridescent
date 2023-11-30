class CursorManager:
    def __enter__(self):
        print("\x1B[5 q", end="", flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("\x1B[5 q", end="", flush=True)

