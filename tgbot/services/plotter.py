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
    success_data: list = [i for k, i in tickets_data.items() if k[1] == True]
    failed_data: list = [i for k, i in tickets_data.items() if k[1] == False]

    # Load all users and all tickets
    user_data = data.value_counts("user_id").to_dict()
    all_users: list = list(user_data.keys())
    all_tickets: list = list(user_data.values())

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    x_axis = np.arange(len(all_users))

    # Add data to plot
    ax.bar(
        x_axis - 0.15, failed_data, label="Проваленые билеты",
        width=0.15, color=colors.red
    )
    ax.bar(
        x_axis + 0.00, all_tickets, label="Все билеты",
        width=0.15, color=colors.yellow
    )
    ax.bar(
        x_axis + 0.15, success_data, label="Успешные билеты",
        width=0.15, color=colors.green
    )

    # Format plot
    ax.set_ylabel("Количество решенных билетов")
    ax.set_title("Топ пользователей")
    ax.set_xticks(x_axis, all_users)
    ax.legend()

    # Save plot to bytesio
    plot_file: BytesIO = BytesIO()
    fig.savefig(plot_file)
    plot_file.seek(0)

    return plot_file
