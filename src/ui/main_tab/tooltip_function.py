"""
Module containing tooltip functionality for widgets.
"""
import tkinter as tk
from tkinter import ttk

def add_tooltip(widget, text):
    """
    Add a tooltip to a widget.
    
    Args:
        widget: The widget to add tooltip to
        text: The tooltip text
    """
    tooltip = None
    
    def enter(event):
        nonlocal tooltip
        x = y = 0
        try:
            x, y, _, _ = widget.bbox("insert") if hasattr(widget, "bbox") else (0, 0, 0, 0)
        except:
            # If bbox not available, use widget position
            x, y = 0, 0
            
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Create a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        # Add a little padding
        frame = ttk.Frame(tooltip, borderwidth=1, relief="solid")
        frame.pack(fill="both", expand=True)
        
        label = ttk.Label(frame, text=text, background="#ffffe0", padding=(5, 3))
        label.pack()
        
        # Auto destroy after 3 seconds
        widget.after(3000, lambda: tooltip.destroy() if tooltip else None)
        
    def leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
            
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)