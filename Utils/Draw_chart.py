from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.ticker import FuncFormatter

def draw_bar_chart(frame, income_data: dict, expense_data: dict):
    income_data = {int(k): v for k, v in income_data.items()}
    expense_data = {int(k): v for k, v in expense_data.items()}

    months = list(range(1, 13))
    income = [income_data.get(m, 0) for m in months]
    expense = [expense_data.get(m, 0) for m in months]
    labels = [f"T{m}" for m in months]

    # Tạo Figure và Canvas
    fig = Figure(figsize=(6, 3))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    def millions_formatter(x, pos):
        return f'{x / 1e6:.0f}M'
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)
    x = np.arange(len(months))
    width = 0.40
    ax.bar(x - width / 2, income, width, label='Income', color='#4CAF50')
    ax.bar(x + width / 2, expense, width, label='Expense', color='#F44336')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Month", fontweight='bold')
    ax.set_ylabel("Amount", fontweight='bold')
    ax.set_title("Income and Expenses by Month", fontweight='bold', pad=30)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
    fig.tight_layout()
    # Xóa biểu đồ cũ (nếu có) và thêm mới
    layout = frame.layout()
    if layout is None:
        layout = QVBoxLayout(frame)
        frame.setLayout(layout)
    else:
        for i in reversed(range(layout.count())):
            old_widget = layout.itemAt(i).widget()
            if old_widget:
                old_widget.setParent(None)

    layout.addWidget(canvas)

def draw_pie_chart(frame, data: dict, title="Expense Breakdown", top_n=3):
    # Tạo Figure và Canvas
    fig = Figure(figsize=(4, 3))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    # Sắp xếp dữ liệu theo giá trị giảm dần
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)

    # Lấy top N mục lớn nhất
    top_items = sorted_items[:top_n]
    other_items = sorted_items[top_n:]

    new_labels = [label for label, _ in top_items]
    new_values = [value for _, value in top_items]

    # Gộp phần còn lại thành "Others"
    if other_items:
        other_value = sum(value for _, value in other_items)
        new_labels.append("Others")
        new_values.append(other_value)

    # Tạo biểu đồ tròn
    colors = plt.get_cmap("Set3")(np.linspace(0, 1, len(new_labels)))
    wedges, texts, autotexts = ax.pie(
        new_values, autopct='%1.1f%%', startangle=140, colors=colors
    )
    ax.set_title(title, fontweight='bold', pad=20)
    ax.legend(wedges, new_labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0.5))
    fig.tight_layout()

    # Xóa biểu đồ cũ (nếu có) và thêm mới
    layout = frame.layout()
    if layout is None:
        layout = QVBoxLayout(frame)
        frame.setLayout(layout)
    else:
        for i in reversed(range(layout.count())):
            old_widget = layout.itemAt(i).widget()
            if old_widget:
                old_widget.setParent(None)

    layout.addWidget(canvas)
