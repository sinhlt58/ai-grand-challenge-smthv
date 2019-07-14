from __future__ import division

import copy
import numpy as np

from ..dash.model import Dash

class ThresholdTutor():
    '''review question with recall likelihood closest to some threshold'''

    ENV = {
        'dash_model': Dash
    }

    def __init__(self, env_name='dash_model'):

        self.threshold = 0.01

        self.env_name  = env_name

        # self.env._reset()

    def next_question(self, **kwargs):

        self.env = self.ENV[self.env_name](**{
            'question_difficulties': kwargs.get('question_difficulties', []),
            'question_decay_exps'  : kwargs.get('question_decay_exps', []),
            'student_ability'      : kwargs.get('student_ability', 0),
            'student_decay_exp'    : kwargs.get('student_decay_exp', 0),
            'n_questions'          : kwargs.get('n_questions', 0),
            'questions'            : kwargs.get('questions', []),
            'answers'              : kwargs.get('answers', []),
            'n_windows'            : kwargs.get('n_windows', 5),
        })

        # q_index = np.argmin()

        # print('**********************', np.abs(self.env.recall_likelihoods()))


        # print('**********************', np.min(np.abs(self.env.recall_likelihoods() - self.threshold)) )

        return np.abs(self.env.recall_likelihoods() - self.threshold)

    def reset(self):
        self.env._reset()


threshold_tutor = ThresholdTutor('dash_model')
