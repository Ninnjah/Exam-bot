from aiogram.utils.callback_data import CallbackData

cat_select_cb = CallbackData("cat_select", "category")
show_ticket_cb = CallbackData("show_ticket", "category", "ticket")
exam_start_cb = CallbackData("exam_start", "category", "ticket")
menu_explorer_cb = CallbackData("menu_explorer", "menu")
ticket_cancel_cb = CallbackData("ticket_cancel")
