import customtkinter as ctk
from services.inventory_service import InventoryService
from datetime import datetime, timedelta
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

class AnalyticsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Results area
        
        # --- Top: Filters ---
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.filter_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=10)
        self.start_date_var = ctk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.start_date_entry = ctk.CTkEntry(self.filter_frame, textvariable=self.start_date_var, width=120)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=10)
        
        ctk.CTkLabel(self.filter_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=10)
        self.end_date_var = ctk.StringVar(value=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.end_date_entry = ctk.CTkEntry(self.filter_frame, textvariable=self.end_date_var, width=120)
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=10)
        
        self.refresh_btn = ctk.CTkButton(self.filter_frame, text="Update Analytics", command=self.refresh)
        self.refresh_btn.grid(row=0, column=4, padx=20, pady=10)

        # --- Middle: Results ---
        self.results_scroll = ctk.CTkScrollableFrame(self)
        self.results_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Summary Area
        self.summary_frame = ctk.CTkFrame(self.results_scroll)
        self.summary_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_sales_lbl = ctk.CTkLabel(self.summary_frame, text="Total Sales: 0", font=ctk.CTkFont(size=14, weight="bold"))
        self.total_sales_lbl.grid(row=0, column=0, padx=20, pady=10)
        
        self.gross_rev_lbl = ctk.CTkLabel(self.summary_frame, text="Gross Revenue: $0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.gross_rev_lbl.grid(row=0, column=1, padx=20, pady=10)
        
        self.net_profit_lbl = ctk.CTkLabel(self.summary_frame, text="Net Profit: $0.00", font=ctk.CTkFont(size=14, weight="bold"), text_color="green")
        self.net_profit_lbl.grid(row=0, column=2, padx=20, pady=10)
        
        # Chart Area
        self.chart_frame = ctk.CTkFrame(self.results_scroll)
        self.chart_frame.pack(fill="x", padx=10, pady=10)
        self.canvas = None

        # Product Breakdown Area
        self.prod_lbl = ctk.CTkLabel(self.results_scroll, text="Product Breakdown", font=ctk.CTkFont(size=16, weight="bold"))
        self.prod_lbl.pack(pady=(20, 10))
        self.prod_container = ctk.CTkFrame(self.results_scroll)
        self.prod_container.pack(fill="x", padx=10, pady=5)
        
        # Filament Usage Area
        self.fil_lbl = ctk.CTkLabel(self.results_scroll, text="Filament Usage", font=ctk.CTkFont(size=16, weight="bold"))
        self.fil_lbl.pack(pady=(20, 10))
        self.fil_container = ctk.CTkFrame(self.results_scroll)
        self.fil_container.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=2, column=0, pady=5)

    def refresh(self):
        """Fetches and displays analytics data."""
        try:
            start = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
            
            data = InventoryService.get_analytics_data(start, end)
            
            # Update Summary
            self.total_sales_lbl.configure(text=f"Total Sales: {data['total_sales_count']}")
            self.gross_rev_lbl.configure(text=f"Gross Revenue: ${data['gross_revenue']:.2f}")
            self.net_profit_lbl.configure(text=f"Net Profit: ${data['net_profit']:.2f}")
            
            # Update Chart
            self.update_chart(data['daily_stats'], start, end)

            # Update Product Breakdown
            for widget in self.prod_container.winfo_children():
                widget.destroy()
            
            header = ctk.CTkFrame(self.prod_container, fg_color="transparent")
            header.pack(fill="x", padx=5)
            ctk.CTkLabel(header, text="Product", width=250, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0)
            ctk.CTkLabel(header, text="Qty", width=50, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
            ctk.CTkLabel(header, text="Revenue", width=100, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2)
            ctk.CTkLabel(header, text="Profit", width=100, font=ctk.CTkFont(weight="bold")).grid(row=0, column=3)
            
            for name, stats in data['product_breakdown'].items():
                row = ctk.CTkFrame(self.prod_container, fg_color="transparent")
                row.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(row, text=name, width=250, anchor="w").grid(row=0, column=0)
                ctk.CTkLabel(row, text=str(stats['count']), width=50).grid(row=0, column=1)
                ctk.CTkLabel(row, text=f"${stats['revenue']:.2f}", width=100).grid(row=0, column=2)
                ctk.CTkLabel(row, text=f"${stats['revenue'] - stats['cost']:.2f}", width=100).grid(row=0, column=3)
            
            # Update Filament Usage
            for widget in self.fil_container.winfo_children():
                widget.destroy()
                
            header_f = ctk.CTkFrame(self.fil_container, fg_color="transparent")
            header_f.pack(fill="x", padx=5)
            ctk.CTkLabel(header_f, text="Filament", width=300, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0)
            ctk.CTkLabel(header_f, text="Usage (g)", width=100, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
            ctk.CTkLabel(header_f, text="Cost", width=100, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2)
            
            for name, stats in data['filament_usage'].items():
                row = ctk.CTkFrame(self.fil_container, fg_color="transparent")
                row.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(row, text=name, width=300, anchor="w").grid(row=0, column=0)
                ctk.CTkLabel(row, text=f"{stats['grams']:.2f}g", width=100).grid(row=0, column=1)
                ctk.CTkLabel(row, text=f"${stats['cost']:.2f}", width=100).grid(row=0, column=2)
            
            self.status_label.configure(text="Analytics updated.", text_color="green")
            
        except ValueError:
            self.status_label.configure(text="Error: Invalid date format. Use YYYY-MM-DD", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def update_chart(self, daily_stats, start, end):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Prepare data
        dates = []
        revenues = []
        profits = []
        
        curr = start
        while curr <= end:
            date_str = curr.strftime("%Y-%m-%d")
            dates.append(curr)
            stats = daily_stats.get(date_str, {'revenue': 0, 'profit': 0})
            revenues.append(float(stats['revenue']))
            profits.append(float(stats['profit']))
            curr += timedelta(days=1)

        # Matplotlib Styling for dark/light mode
        appearance_mode = ctk.get_appearance_mode()
        if appearance_mode == "Dark":
            bg_color = "#2b2b2b"  # CTK default dark
            text_color = "white"
            grid_color = "#4a4a4a"
        else:
            bg_color = "#ebebeb"  # CTK default light
            text_color = "black"
            grid_color = "#d1d1d1"

        # Create plot
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        # Plot with smoother lines and nicer colors
        ax.plot(dates, revenues, label='Revenue', color='#1f77b4', marker='o', linewidth=2, markersize=4)
        ax.plot(dates, profits, label='Profit', color='#2ca02c', marker='s', linewidth=2, markersize=4)
        
        ax.set_title("Sales Over Time", color=text_color, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel("Date", color=text_color, fontsize=10)
        ax.set_ylabel("USD ($)", color=text_color, fontsize=10)
        
        # Legend styling
        legend = ax.legend(facecolor=bg_color, edgecolor=grid_color)
        plt.setp(legend.get_texts(), color=text_color)
        
        # Grid styling
        ax.grid(True, linestyle='--', alpha=0.6, color=grid_color)
        
        # Spines
        for spine in ax.spines.values():
            spine.set_color(grid_color)
            
        # Ticks
        ax.tick_params(colors=text_color, labelsize=9)
        
        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        fig.autofmt_xdate()
        plt.tight_layout()

        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
