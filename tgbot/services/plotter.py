from io import BytesIO

from pandas import DataFrame

import matplotlib.pyplot as plt

plt.style.use("bmh")


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
        alpha=0.5, color="b", linewidth=2
    )
    ax.fill_between(
        *zip(*sorted(failed_data.items())), y2=0, label="Проваленые билеты",
        alpha=0.5, color="r", linewidth=2
    )
    ax.fill_between(
        *zip(*sorted(success_data.items())), y2=0, label="Успешные билеты",
        alpha=0.5, color="g", linewidth=2
    )
    fig.legend()

    # Save plot to bytesio
    plot_file: BytesIO = BytesIO()
    fig.savefig(plot_file)
    plot_file.seek(0)

    return plot_file


def user_top_plot(data: list):
    data: DataFrame = DataFrame.from_records(data)
    all_tickets = data.value_counts("user_id").to_dict()

    # Count of success and failed tickets
    user_data: dict = data.groupby("user_id")["success"].value_counts().to_dict()
    success_data: dict = {k[0]: i for k, i in user_data.items() if k[1] == True}
    failed_data: dict = {k[0]: i for k, i in user_data.items() if k[1] == False}

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    x = [str(x) for x in (all_tickets.keys())]
    y = list(all_tickets.values())
    ax.bar(
        x, y, label="Все билеты",
        width=0.15, color="b"
    )
    x = [str(x) for x in (failed_data.keys())]
    y = list(failed_data.values())
    ax.bar(
        x, y, label="Проваленые билеты",
        width=0.15, color="r"
    )
    x = [str(x) for x in (success_data.keys())]
    y = list(success_data.values())
    ax.bar(
        x, y, label="Успешные билеты",
        width=0.15, color="g"
    )
    fig.legend()

    # Save plot to bytesio
    plot_file: BytesIO = BytesIO()
    fig.savefig(plot_file)
    plot_file.seek(0)

    return plot_file
