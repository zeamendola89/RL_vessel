from sklearn.svm import SVR
from sklearn import tree
from sklearn.ensemble import RandomForestRegressor
from sklearn import neighbors
import numpy as np
import actions
import pickle
import datetime
import reward
import datetime


class Learner(object):

    exploring = None

    def __init__(self, file_to_save='default_agent', load_saved_regression=False,
                 action_space_name='simple_action_space',
                 r_m_=None):
        self.rw_mp = r_m_
        self.batch_list = list()
        if load_saved_regression:
            self.learner = load_saved_regression
        else:
            self.learner = neighbors.KNeighborsRegressor(2, weights='distance')
            # self.learner = SVR(kernel='rbf', C=0.2, gamma=1)
            # self.learner = RandomForestRegressor()
            # self.learner = tree.DecisionTreeRegressor()
        self.end_states = dict()
        self.file = file_to_save
        self.discount_factor = 1.0
        self.mode = 'angle_only'
        self.action_space = actions.BaseAction(action_space_name)
        self.states = list()
        self.act = list()
        self.rewards = list()
        self.states_p = list()
        self.q_target = list()
        self.debug_file = open('debug_fqi'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'.txt','w')

    def replace_reward(self, transition_list):
        new_list = list()
        for transition in transition_list:
            resulting_state = transition[2]
            self.rw_mp.update_ship(resulting_state[0],
                                   resulting_state[1],
                                   resulting_state[2],
                                   resulting_state[3],
                                   resulting_state[4],
                                   resulting_state[5])
            new_reward = self.rw_mp.get_reward()
            tmp = list(transition)
            tmp[3] = new_reward
            transition = tuple(tmp)
            new_list.append(transition)
        print(new_list[-1])
        return new_list

    def add_to_batch(self, transition_list, final_flag):
        if self.rw_mp is not None:
            transition_list = self.replace_reward(transition_list)
        if final_flag == 1:
            self.batch_list = self.batch_list + transition_list
            if final_flag != 0:
                self.end_states[len(self.batch_list)-1] = final_flag

    def set_up_agent(self):
        self.states = [list(k[0]) for k in self.batch_list]
        if self.mode == 'angle_only':
            self.act = [(x[1][0]) for x in self.batch_list]
        self.rewards = np.asarray([x[3] for x in self.batch_list], dtype=np.float64)
        self.states_p = [list(k[2]) for k in self.batch_list]
        self.q_target = self.rewards
        self.states = np.array(self.states)
        self.act = np.array(self.act)
        self.samples = np.column_stack((self.states, self.act))

    def fit_batch(self, max_iterations, debug=False):
        for it in range(max_iterations):
            print("FQI_iteration: ", it)
            self.learner.fit(self.samples, self.q_target)
            maxq_prediction = np.asarray([self.find_max_q(i, state_p) for i,state_p in enumerate(self.states_p)])
            self.q_target = self.rewards + self.discount_factor*maxq_prediction
            if debug:
                print(self.q_target,file=self.debug_file)
                print('\n\n', file=self.debug_file)



    def find_max_q(self, i, state_p):
        qmax = -float('Inf')
        final = self.end_states.get(i)
        if final != None:
            qmax = 0
        else:
            for action in self.action_space.action_combinations:
                if self.mode == 'angle_only':
                    state_action = np.append(state_p, action[0])
                state_action = np.reshape(state_action, (1, -1))
                qpred = self.learner.predict(state_action)
                if qpred > qmax:
                    qmax = qpred
        return qmax

    def select_action(self, state):
        selected_action = None
        qmax = -float('Inf')
        print('Select action')
        for action in self.action_space.action_combinations:
            if self.mode == 'angle_only':
                state_action = np.append(state, action[0])
            state_action = np.reshape(state_action, (1, -1))
            qpred = self.learner.predict(state_action)
            print(self.learner.kneighbors(state_action))
            print(self.learner.get_params(deep=True))
            print(qpred)
            print(action[0])
            if qpred > qmax:
                qmax = qpred
                selected_action = action
                #TODO Implement random choice for equal q value cases
        return selected_action

    def __del__(self):
        self.debug_file.close()
        with open(self.file, 'wb') as outfile:
            pickle.dump(self.learner, outfile)

if __name__ == '__main__':
    with open('agent20180408200244', 'rb') as infile:
        agent_obj = pickle.load(infile)
        agent = Learner(load_saved_regression=agent_obj, action_space_name='only_rudder_action_space')
        action = agent.select_action((7977.5731952, 4594.6156251, -103.49968, -2.909885, -0.6988991, 0.0005474))

        print(action)