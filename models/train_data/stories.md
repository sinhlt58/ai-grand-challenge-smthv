## 0
* get_started OR greetings
	- app_app_custom_check_user_existed
	- utter_utter_greets_first_time
	- app_form_get_user_info
	- form{"name": "app_form_get_user_info"}
	- form{"name": null}
	- utter_utter_show_function_first_time
	- app_set_slot_after_got_info
	- app_app_custom_save_user_info
	- app_restart_custom_user_existed

## 1
* choose_subject
	- app_form_choose_subject
	- form{"name": "app_form_choose_subject"}
	- form{"name": null}
	- app_set_slot_after_choose_subject
	- slot{"user_current_subject": "math"}
	- utter_utter_after_choose_subject_math
	- app_restart_custom_go_play

## 2
* choose_subject
	- app_form_choose_subject
	- form{"name": "app_form_choose_subject"}
	- form{"name": null}
	- app_set_slot_after_choose_subject
	- slot{"user_current_subject": "english"}
	- app_form_choose_english_skill
	- form{"name": "app_form_choose_english_skill"}
	- form{"name": null}
	- app_set_slot_after_choose_english_skill
	- app_restart_custom_go_play

## 3
* play
	- slot{"user_current_subject": "english"}
	- app_app_custom_get_question
	- app_form_get_answer
	- form{"name": "app_form_get_answer"}
	- form{"name": null}
	- app_set_slot_after_get_answer
	- app_app_custom_check_answer
	- slot{"user_answer_result": "correct"}
	- utter_utter_answer_result_correct
	- app_set_slot_after_answer_result_correct
	- slot{"user_answer_result": null}
	- app_app_custom_show_correct_answer
	- utter_utter_show_next_question
* next_question
	- app_restart_custom_after_answer_result_correct

## 4
* play
	- slot{"user_current_subject": "english"}
	- app_app_custom_get_question
	- app_form_get_answer
	- form{"name": "app_form_get_answer"}
	- form{"name": null}
	- app_set_slot_after_get_answer
	- app_app_custom_check_answer
	- slot{"user_answer_result": "wrong"}
	- utter_utter_answer_result_wrong
	- app_set_slot_after_answer_result_wrong
	- slot{"user_answer_result": null}
	- app_restart_custom_after_answer_result_wrong

## 5
* play
	- slot{"user_current_subject": "english"}
	- app_app_custom_get_question
	- app_form_get_answer
	- form{"name": "app_form_get_answer"}
* give_up
	- utter_utter_give_up_boost
	- action_deactivate_form
	- form{"name": null}
* next_question
	- app_restart_custom_go_play

## 6
* play
	- slot{"user_current_subject": "english"}
	- app_app_custom_get_question
	- app_form_get_answer
	- form{"name": "app_form_get_answer"}
* show_hint
	- app_app_custom_show_hint
	- app_restart_custom_after_show_hint

## 7
* get_started OR greetings
	- app_app_custom_check_user_existed
	- slot{"user_is_existed": "yes"}
	- utter_utter_greets_user_existed
	- app_restart_custom_user_existed

## 8
* exit_play_with_response
	- utter_utter_exit_play_response
	- action_deactivate_form
	- app_restart_custom_user_existed

## 9
* play
	- slot{"user_current_subject": "math"}
	- app_app_custom_get_question
	- app_form_get_answer
	- form{"name": "app_form_get_answer"}
	- form{"name": null}
	- app_set_slot_after_get_answer
	- app_app_custom_check_answer
	- slot{"user_answer_result": "correct"}
	- utter_utter_answer_result_correct
	- app_set_slot_after_answer_result_correct
	- slot{"user_answer_result": null}
	- app_app_custom_show_correct_answer
	- utter_utter_show_next_question
* next_question
	- app_restart_custom_after_answer_result_correct

## 10
* play
	- slot{"user_current_subject": "math"}
	- app_app_custom_get_question
	- app_form_get_answer
	- form{"name": "app_form_get_answer"}
	- form{"name": null}
	- app_set_slot_after_get_answer
	- app_app_custom_check_answer
	- slot{"user_answer_result": "wrong"}
	- utter_utter_answer_result_wrong
	- app_set_slot_after_answer_result_wrong
	- slot{"user_answer_result": null}
	- app_restart_custom_after_answer_result_wrong

## 11
* play
	- slot{"user_current_subject": "math"}
	- app_app_custom_get_question
	- app_form_get_answer
	- form{"name": "app_form_get_answer"}
* give_up
	- utter_utter_give_up_boost
	- action_deactivate_form
	- form{"name": null}
* next_question
	- app_restart_custom_go_play

## 12
* play
	- slot{"user_current_subject": "math"}
	- app_app_custom_get_question
	- app_form_get_answer
	- form{"name": "app_form_get_answer"}
* show_hint
	- app_app_custom_show_hint
	- app_restart_custom_after_show_hint

## 13
* set_reminder
	- app_form_set_reminder
	- form{"name": "app_form_set_reminder"}
	- form{"name": null}
	- app_set_slot_after_set_reminder
	- app_app_custom_set_remider
	- app_restart_custom_after_set_reminder

