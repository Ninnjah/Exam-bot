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


def tickets_stat(data: list):
    data: DataFrame = DataFrame.from_records(
        data
    ).sort_values(
        by=["start_time"]
    )

    # Create date column
    data["start_date"] = data["start_time"].dt.date

    # Create variables for data
    all_count: int = 0
    all_tickets: dict = {}

    success_tickets: dict = {}
    success_count: int = 0

    failed_tickets: dict = {}
    failed_count: int = 0

    # Collect data
    for start_date, success in zip(data["start_date"], data["success"]):
        all_count += 1
        if success:
            success_count += 1
        else:
            failed_count += 1

        all_tickets.update({start_date: all_count})
        success_tickets.update({start_date: success_count})
        failed_tickets.update({start_date: failed_count})

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Add data to plot
    ax.plot(
        *zip(*sorted(all_tickets.items())), label="Все билеты",
        color=colors.yellow
    )
    ax.plot(
        *zip(*sorted(success_tickets.items())), label="Успешные билеты",
        color=colors.green
    )
    ax.plot(
        *zip(*sorted(failed_tickets.items())), label="Неуспешные билеты",
        color=colors.red
    )

    # Format plot
    ax.set_ylabel("Количество решенных билетов")
    ax.set_title("Все решенные билеты")
    ax.legend()

    # Save plot to bytesio
    plot_file: BytesIO = BytesIO()
    fig.savefig(plot_file)
    plot_file.seek(0)

    return plot_file


def user_top_plot(raw_data: list):
    data: DataFrame = DataFrame.from_records(raw_data)

    tickets_data: DataFrame = DataFrame()
    tickets_data["user_id"] = data["user_id"]
    tickets_data["success"] = data["success"]
    tickets_data["success_count"] = tickets_data.groupby(["user_id", "success"])["success"].transform("count")

    success_y = [
        x[0] for x in zip(
            tickets_data["success_count"],
            tickets_data["success"]
        ) if x[1]
    ]

    failed_y = [
        x[0] for x in zip(
            tickets_data["success_count"],
            tickets_data["success"]
        ) if not x[1]
    ]

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Add data to plot
    ax.bar(
        x=tickets_data["user_id"], height=success_y,
        label="Успешные билеты", color=colors.green
    )
    ax.bar(
        x=tickets_data["user_id"], height=failed_y,
        label="Проваленые билеты", color=colors.green,
        bottom=success_y
    )

    # Format plot
    ax.set_ylabel("Количество решенных билетов")
    ax.set_title("Топ пользователей")
    ax.legend()

    # Save plot to bytesio
    plot_file: BytesIO = BytesIO()
    fig.savefig(plot_file)
    plot_file.seek(0)

    return plot_file


def users_stat(data: list):
    data: DataFrame = DataFrame.from_records(
        data
    ).sort_values(
        by=["created_on"]
    )

    # Create date column
    data["created_date"] = data["created_on"].dt.date

    # Create variables for data
    users_count: int = 0
    users: dict = {}

    # Collect data
    for created_date in data["created_date"]:
        users_count += 1
        users.update({created_date: users_count})

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Add data to plot
    ax.plot(
        *zip(*sorted(users.items())), label="Все пользователи",
        color=colors.green
    )

    # Format plot
    ax.set_ylabel("Количество пользователей")
    ax.set_title("Динамика пользователей")
    ax.legend()

    # Save plot to bytesio
    plot_file: BytesIO = BytesIO()
    fig.savefig(plot_file)
    plot_file.seek(0)

    return plot_file
