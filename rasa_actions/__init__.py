from typing import Dict, Text, Any, List, Union, Optional

from rasa_sdk import Tracker, Action
from rasa_sdk.events import SlotSet, BotUttered
from app.rasa_action.events import ReminderScheduled
from app.rasa_action.bots.tho_trang.templates import Quick_Replies_Answers, Attachment_Link

import logging
import random

import json
from dateutil.parser import parse
import traceback
import datetime, pymongo

from mongoengine.context_managers import switch_db
import numpy as np
from bson import ObjectId

from rasa_sdk import Tracker, Action
from rasa_sdk.events import SlotSet, BotUttered, ActionReverted

from app.rasa_action.events import ReminderScheduled
from app.commons import is_json
from app.commons.constants import (
    ID_FACEBOOK_PREFIX,
    RASA_BOT_DB_NAME,
)

logger = logging.getLogger(__name__)

class CustomAppActionBot:

    def __init__(self, called_action, db_name):

        from app.bots.bot_manager import bot_manager

        self.called_action = called_action

        self.db_name = db_name

        self.__bot_db = bot_manager.mongo_client[self.db_name]

        self.__bot_user_collection = self.__bot_db["bot_users"]

        self.__study_history_collection = self.__bot_db["study_histories"]

        self.__connect_question_db_name()

    def __connect_question_db_name(self):

        from app.bots.bot_manager import bot_manager

        self.__question_db_name = "hoclieu_cauhoi"

        self.__question_db = bot_manager.mongo_client[self.__question_db_name]

        self.__question_collection = self.__question_db["questions"]

    def __get_needed_data(
        self,
        user_id,
        current_subject,
        current_skill,
        q_difficulty_label
    ):

        current_user = self.__bot_user_collection.find_one({
            'user_id': user_id
        })

        questions_filter = {
            'subject' : current_subject
        }

        answers_filter = {
            'user_id' : user_id,
            'subject' : current_subject
        }

        if current_subject == "english" and current_skill != "general":
            questions_filter["skills"] = current_skill
            answers_filter["skills"] = current_skill

        if q_difficulty_label in ['easy', 'medium', 'hard']:
            questions_filter['difficulity_label'] = q_difficulty_label
            answers_filter['difficulity_label']   = q_difficulty_label

        questions = np.asarray(list(self.__question_collection.find(questions_filter)))

        answers   = np.asarray(list(self.__study_history_collection.find().sort('test_time', pymongo.DESCENDING)))

        n_questions, \
        question_difficulties, \
        question_decay_exps = self.__extract_question_properties(questions)

        answers = self.__extract_answer_properties(answers)

        return {
            'student_ability'       : current_user.get('ability', 0),
            'student_decay_exp'     : current_user.get('decay_exp', 0),
            'questions'             : np.asarray(questions),
            'n_questions'           : n_questions,
            'question_difficulties' : question_difficulties,
            'question_decay_exps'   : question_decay_exps,
            'answers'           : answers
        }

    def __extract_question_properties(self, questions):

        difficulties = np.asarray(list(map(lambda question: question['difficulty_val'], questions)))

        decay_exps   = np.asarray(list(map(lambda question: question['decay_exps'], questions)))

        n_questions  = len(questions)

        return n_questions, difficulties, decay_exps

    def __extract_answer_properties(self, answers):

        tmp_answers = []

        for anw in answers:

            if anw['result'] == 'correct': result = 1
            else: result = 0

            tmp_answers.append({
                'hoclieu_q_id': anw['hoclieu_q_id'],
                'tlast' : anw['test_time'],
                'result': result
            })

        return tmp_answers

    def app_custom_get_question(self, dispatcher, tracker, domain):

        from .tutor.threshold import threshold_tutor

        print('slots: ', tracker.slots)

        # user infos
        user_id = tracker.current_state().get('sender_id', '')

        # toán/tiếng anh
        user_current_subject = tracker.get_slot('user_current_subject')
        user_current_skill   = tracker.get_slot('user_english_skill')
        user_q_difficulty_label = tracker.get_slot('user_q_difficulty_label') or 'default'

        user_question_id = tracker.get_slot('user_question_id')

        evaluated_data = self.__get_needed_data(
            user_id,
            user_current_subject,
            user_current_skill,
            user_q_difficulty_label)

        if user_question_id:
            # get a new question depends on the user's level
            probs = threshold_tutor.next_question(**evaluated_data)

            q_index = np.random.choice(np.argsort(probs)[0 : 5])

            next_question = evaluated_data.get('questions')[q_index]

            while user_question_id == str(next_question.get('hoclieu_q_id')):

                q_index = np.random.choice(np.argsort(probs)[0 : 5])

                next_question = evaluated_data.get('questions')[q_index]

            user_question_id = str(next_question.get('hoclieu_q_id'))

        else:
            # get a new question depends on the user's level and differs from user_question_id
            # next_question    = threshold_tutor.next_question(**evaluated_data)
            probs = threshold_tutor.next_question(**evaluated_data)

            q_index = np.random.choice(np.argsort(probs)[0 : 5])

            next_question = evaluated_data.get('questions')[q_index]

            user_question_id = str(next_question.get('hoclieu_q_id'))

        events = []

        text = next_question.get('text')
        answers = next_question.get('answers')
        image = next_question.get('image')
        audio = next_question.get('attachment')
        difficulty_label = next_question.get('difficulty_label', 'easy')

        level2stars = {
            'easy': '⭐',
            'medium': '⭐⭐',
            'hard': '⭐⭐⭐',
        }
        events.append(BotUttered(text="Question's difficulty: {}".format(
            level2stars[difficulty_label]
        )))

        data = { "custom": [] }
        if image:
            data["custom"].append(Attachment_Link("image", image))

        if audio:
            data["custom"].append(Attachment_Link("audio", audio))

        if answers:
            data["custom"].append(Quick_Replies_Answers(answers))

        events.append(BotUttered(text=text, data=data))

        events.append(SlotSet('user_question_id', user_question_id))

        return events

    def __evaluated_user_answer(self, current_question, user_answer):

        print('correct answer: ', current_question.get('correct_answer'))

        correct_answer = current_question.get('correct_answer', "").strip().lower()
        user_answer = user_answer.strip().lower()

        if correct_answer == user_answer:
            return 'correct'
        else:
            if len(user_answer) > 1:
                return 'wrong'

            answers = current_question.get("answers", [])
            answer_index = ord(user_answer) - 97

            if answer_index < 0 or answer_index >= len(answers):
                return 'wrong'

            user_answer = answers[answer_index].strip().lower()

            if correct_answer == user_answer:
                return 'correct'
            else:
                return 'wrong'


    def app_custom_check_answer(self, dispatcher, tracker, domain):

        print ('inside _app_custom_check_answer')

        user_id = tracker.current_state().get('sender_id', '')

        # toán/tiếng anh
        user_current_subject = tracker.get_slot('user_current_subject')
        user_current_skill   = tracker.get_slot('user_english_skill')

        # user_question_id is empty (first time) or the previous question id
        user_question_id = tracker.get_slot('user_question_id')

        # the current answer empty/correct/wrong
        user_answer = tracker.get_slot('user_answer')

        current_question = self.__question_collection.find_one({
            'hoclieu_q_id': user_question_id
        })

        user_answer_result = self.__evaluated_user_answer(current_question, user_answer)

        self.__save_study_history(**{
            'hoclieu_q_id': user_question_id,
            'user_id'     : user_id,
            'result'      : user_answer_result,
            'user_answer' : user_answer,
            'subject'     : current_question['subject'],
            'skills'      : current_question['skills']
        })

        print('slots: ', tracker.slots)

        return [SlotSet('user_answer_result', user_answer_result)]

    def __save_study_history(self, **kwargs):

        from datetime import datetime

        self.__study_history_collection.insert_one({
            'hoclieu_q_id': kwargs.get('hoclieu_q_id'),
            'user_id'     : kwargs.get('user_id'),
            'test_time'   : datetime.today(),
            'result'      : kwargs.get('result'),
            'subject'     : kwargs.get('subject'),
            'skills'      : kwargs.get('skills'),
            'user_answer' : kwargs.get('user_answer'),
        })

    def app_custom_show_correct_answer(self, dispatcher, tracker, domain):

        user_question_id = tracker.get_slot('user_question_id')

        current_question = self.__question_collection.find_one({
            'hoclieu_q_id': user_question_id
        })

        return [BotUttered(text='"{}"'.format(current_question.get('correct_answer')))]

    def app_custom_show_hint(self, dispatcher, tracker, domain):
        user_question_id = tracker.get_slot('user_question_id')

        current_question = self.__question_collection.find_one({
            'hoclieu_q_id': user_question_id
        })

        return [BotUttered(text='Đáp án là: {}'.format(current_question.get('correct_answer')))]

    def app_custom_check_user_existed(self, dispatcher, tracker, domain):
        from app.bots.bot_users.models import BotUser

        events = []
        sender_id = tracker.current_state().get('sender_id', '')

        with switch_db(BotUser, self.db_name) as BotUser:
            is_existed, user = BotUser.check_if_existed(sender_id)

            if is_existed:
                event = SlotSet('user_is_existed', is_existed)
                events.extend([
                    SlotSet('user_name', user.extra_info.get('user_name', 'bạn')),
                    SlotSet('user_age', user.extra_info.get('user_age', 10)),
                ])
                events.append(event)

        return events

    def app_custom_save_user_info(self, dispatcher, tracker, domain):
        events = []

        self._save_user_info(tracker)

        return events

    def __sample_student_ability(self):

        return 0

    def __sample_student_decay_exp(self):

        return 0

    def _save_user_info(self, tracker):
        from app.bots.bot_users.models import BotUser

        sender_id = tracker.current_state().get('sender_id', '')

        data = {
            'user_name': tracker.get_slot('user_name'),
            'user_age' : tracker.get_slot('user_age'),
            'ability'  : self.__sample_student_ability(),
            'decay_exp': self.__sample_student_decay_exp(),
            'q_difficulty_label': 'default'
        }

        with switch_db(BotUser, self.db_name) as BotUser:
            is_existed = BotUser.save_user_info(sender_id, data)

        logger.info('Saved info for sender_id {}'.format(sender_id))

    # Remider related actions
    def app_custom_set_remider(self, dispatcher, tracker, domain):
        sender_id = tracker.current_state().get('sender_id', '')
        user_reminder_time_str = tracker.get_slot('user_reminder_time')

        if user_reminder_time_str:
            # now = datetime.datetime.now()
            # trigger_time = now + datetime.timedelta(seconds=10)
            try:
                if type(user_reminder_time_str) is dict:
                    user_reminder_time_str = user_reminder_time_str.get('to', '')

                trigger_time = parse(user_reminder_time_str)

                logger.info('app_custom_set_remider with trigger_time {}'.format(trigger_time))

                event = ReminderScheduled(
                    action_name = 'app_app_custom_run_remider',
                    trigger_date_time = trigger_time,
                    name='app_custom_run_remider_{}'.format(sender_id),
                    kill_on_user_message=False,
                    kill_on_restarted=False,
                )

                return [event]
            except:
                traceback.print_exc()
                logger.error('Error while running app_custom_set_remider')
                return []
        else:
            logger.error('Can not find user_reminder_time_str in app_custom_set_remider')
            return []

    def app_custom_run_remider(self, dispatcher, tracker, domain):
        from app.bots.models import Bot
        from app.bots.channels.facebook.facebook_api import call_send_api

        sender_id = tracker.current_state().get('sender_id', '')
        events = [ActionReverted()]

        # TODO: Sinh will move code to a better place later :D

        reminder_messenger = "🔔🔔🔔 ĐẾN GIỜ HỌC RỒI BẠN ƠI!!! 🔔🔔🔔"

        if sender_id.startswith(ID_FACEBOOK_PREFIX):
            bots = Bot.objects(database_name=self.db_name)

            if bots:
                try:
                    id_parts = sender_id.split(':')
                    page_id = id_parts[1]
                    sender_psid = id_parts[2]

                    bot = bots[0]
                    call_send_api(page_id,
                                  sender_psid,
                                  response={'text': reminder_messenger},
                                  bot=bot,
                                  send_type='message')
                except Exception as e:
                    traceback.print_exc()
                    logger.error('Error while running app_custom_run_remider for bot database_name {} sender_id {}'.format(
                        self.db_name, sender_id
                    ))
            else:
                logger.error('Error while running app_custom_run_remider empty bots')
        else:
            logger.warning('sender_id does not start with ID_FACEBOOK_PREFIX')

        return events

        # TODO: Sinh will move code to a better place later :D

    def app_custom_cancel_remider(self, dispatcher, tracker, domain):
        logger.info("inside app_custom_cancel_remider")

        return []
