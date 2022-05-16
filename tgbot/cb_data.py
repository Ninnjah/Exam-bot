from aiogram.utils.callback_data import CallbackData

cat_select_cb = CallbackData("cat_select", "category")
show_ticket_cb = CallbackData("show_ticket", "category", "ticket")
exam_start_cb = CallbackData("exam_start", "category", "ticket")
menu_explorer_cb = CallbackData("menu_explorer", "menu")
ticket_cancel_cb = CallbackData("ticket_cancel")
exam_answer_cb = CallbackData("exam_answer", "score")
get_tip_cb = CallbackData("get_tip")
exam_result_cb = CallbackData("exam_result")
delete_cb = CallbackData("delete_cb")
