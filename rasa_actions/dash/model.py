from __future__ import division

import numpy as np
import copy

import datetime, time

from pymongo import MongoClient

class Dash():

    def __init__(self, **kwargs):

        self.__load_model()

        self.sample_delay = self.__sample_const_delay(kwargs.get('sample_delay', 5))

        self.now = 0

        self.reward_func = kwargs.get('reward_func', 'likelihood')

        # Tham số khả năng của học viên
        self.student_ability   = kwargs.get('student_ability', 0)

        # Tham số khả năng bổ sung của học viên
        self.student_decay_exp = kwargs.get('student_decay_exp', [])

        # Số câu hỏi, tham số độ khó và độ khó bổ sung của câu hỏi
        self.questions   = kwargs.get('questions', [])
        self.n_questions = kwargs.get('n_questions', 0)

        self.question_difficulties = kwargs.get('question_difficulties', [])
        self.question_decay_exps   = kwargs.get('question_decay_exps', [])

        self.answers = kwargs.get('answers', {})

        self.n_steps     = kwargs.get('n_steps', 100)
        self.n_windows   = kwargs.get('n_windows', 5)
        self.window_size = self.n_steps // self.n_windows

        if self.n_steps % self.n_windows != 0: raise ValueError

        self.n_corrects, self.n_attempts = None, None

        window_cw = kwargs.get('window_cw', self.__sample_window_cw(self.n_windows))
        window_nw = kwargs.get('window_nw', self.__sample_window_nw(self.n_windows))

        if len(window_cw) != self.n_windows or len(window_nw) != self.n_windows:
            raise ValueError

        self.window_cw = np.tile(window_cw, self.n_questions).reshape((self.n_questions, self.n_windows))
        self.window_nw = np.tile(window_nw, self.n_questions).reshape((self.n_questions, self.n_windows))

        self.__init_params()

    def __create_db_connect(self):
        from app.bots.bot_manager import bot_manager

        self.db_tho_trang = bot_manager.mongo_client["tho_trang"]

    def __load_model(self):

        self.__create_db_connect()

        model_collection = self.db_tho_trang["dash_model"]

        self.saved_model = model_collection.find_one()

        # Hằng số phân rã
        self.decay_constant = self.saved_model.get('decay_constant', 2)

    def __transform_date(self, date_array):

        retention_intervals = []

        for date in date_array:

            if date != False:
                day_interval = (datetime.datetime.now() - date).total_seconds() / 86400

                retention_intervals.append(day_interval)
            else:

                retention_intervals.append(0.0)

        retention_intervals = np.asarray(retention_intervals)

        print(retention_intervals)

        retention_intervals = np.exp((retention_intervals - np.min(retention_intervals)) / (np.max(retention_intervals) - np.min(retention_intervals)))

        normed = np.exp((retention_intervals - retention_intervals.mean()) / retention_intervals.std())
        # print('**************************', normed)
        return retention_intervals

    def __sample_window_cw(self, n_windows):
        x = 1 / np.sqrt(np.arange(1, n_windows + 1, 1))
        return x[::-1]

    def __sample_window_nw(self, n_windows):
        x = 1 / np.sqrt(np.arange(1, n_windows + 1, 1))
        return x[::-1]

    def __sample_const_delay(self, d):
        return (lambda: d)

    def recall_log_likelihoods(self, eps=1e-9):
        return np.log(eps + self.recall_likelihoods())

    def __init_params(self):

        self.n_corrects = np.zeros((self.n_questions, self.n_windows))
        self.n_attempts = np.zeros((self.n_questions, self.n_windows))

        self.tlasts = [False for i in range(self.n_questions)]


        for step in range(self.n_steps):

            if step + 1 <= len(self.answers):

                anw = self.answers[step]

                for q_i, q in enumerate(self.questions):

                    if q['hoclieu_q_id'] == anw['hoclieu_q_id']:

                        self.tlasts[q_i] = anw.get('tlast')

                        c_window = self.n_windows - (step + 1) // self.window_size

                        if anw['result'] == 1:
                            self.n_corrects[q_i][c_window - 1] += 1

                        self.n_attempts[q_i][c_window - 1] += 1

        self.tlasts = np.asarray(self.__transform_date(self.tlasts))

    def __sample_const_delay(self, d):

        return (lambda: d)

    def recall_likelihoods(self):

        study_histories = np.zeros((1, self.n_questions))[0]

        for curr_window in range(self.n_windows):
            study_histories += (
                self.window_cw[:, :curr_window] * np.log(1 + self.n_corrects[:, :curr_window]) +
                self.window_nw[:, :curr_window] * np.log(1 + self.n_attempts[:, :curr_window])).sum(axis=1)

        m = 1 / (1 + np.exp(-(self.student_ability - self.question_difficulties + study_histories)))
        f = np.exp(self.student_decay_exp - self.question_decay_exps)

        delays = np.abs(self.now - self.tlasts)

        return m / (1 + self.decay_constant * delays)**f
