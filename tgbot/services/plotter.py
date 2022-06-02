from collections import namedtuple
from io import BytesIO

import numpy as np
from pandas import DataFrame

import matplotlib.pyplot as plt

plt.style.use("bmh")
Colors = namedtuple(
    "colors",
    ("red", "yellow", "green")
)
colors = Colors._make({
    "#BB5555": "red",
    "#EE9944": "yellow",
    "#99BB55": "green"
})


def tickets_plot(data: list):
    data: DataFrame = DataFrame.from_records(data)
    # Create start_date column
    data["start_date"] = data["start_time"].dt.round("6H")

    # Get all tickets count
    all_tickets = data.value_counts("start_date").to_dict()

    # Count of success and failed tickets
    tickets_data: dict = data.groupby("start_date")["success"].value_counts().to_dict()
    success_data: dict = {k[0]: i for k, i in tickets_data.items() if k[1] == True}
    failed_data: dict = {k[0]: i for k, i in tickets_data.items() if k[1] == False}

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.fill_between(
        *zip(*sorted(all_tickets.items())), y2=0, label="Все билеты",
        alpha=0.5, color=colors.yellow, linewidth=2
    )
    ax.fill_between(
        *zip(*sorted(failed_data.items())), y2=0, label="Проваленые билеты",
        alpha=0.5, color=colors.red, linewidth=2
    )
    ax.fill_between(
        *zip(*sorted(success_data.items())), y2=0, label="Успешные билеты",
        alpha=0.5, color=colors.green, linewidth=2
    )
    fig.legend()

    # Save plot to bytesio
    plot_file: BytesIO = BytesIO()
    fig.savefig(plot_file)
    plot_file.seek(0)

    return plot_file


def user_top_plot(data: list):
    data: DataFrame = DataFrame.from_records(data)

    # Count of success and failed tickets
    tickets_data: dict = data.groupby("user_id")["success"].value_counts().to_dict()
    success_data: dict = {str(k[0]): i for k, i in tickets_data.items() if k[1] == True}
    failed_data: dict = {str(k[0]): i for k, i in tickets_data.items() if k[1] == False}

    success_data.update({k: 0 for k, v in failed_data.items() if k not in success_data.keys()})
    failed_data.update({k: 0 for k, v in success_data.items() if k not in failed_data.keys()})

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    x_axis = np.arange(len(success_data))

    # Add data to plot
    ax.bar(
        *zip(*sorted(success_data.items())), label="Успешные билеты",
        color=colors.green
    )
    ax.bar(
        *zip(*sorted(failed_data.items())), label="Проваленые билеты",
        color=colors.red, bottom=[x[1] for x in sorted(success_data.items())]
    )

    # Format plot
    ax.set_ylabel("Количество решенных билетов")
    ax.set_title("Топ пользователей")
    ax.set_xticks(x_axis, success_data.keys())
    ax.legend()

    # Save plot to bytesio
    plot_file: BytesIO = BytesIO()
    fig.savefig(plot_file)
    plot_file.seek(0)

    return plot_file
