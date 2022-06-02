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
