import pandas as pd
import random
from fractions import Fraction
from copy import deepcopy
from flask import session
import operator
from datetime import datetime
import numpy as np

ops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

# 随机在24点库获得题目
def generate_numbers_inlibrary():
    # 读取 4nums
    library = pd.read_csv(".//4nums//4nums.csv")
    # 随机生成一个数字
    index_random = random.randint(0,len(library)-1)
    # 获得24点
    nums = library.at[index_random,"Puzzles "]
    nums = [int(num) for num in nums.split()]
    return nums

# Fraction和string的互换
def Fraction2string(F):
    if(F.denominator == 1): return str(F.numerator)
    else:return str(F.numerator) + '/' + str(F.denominator)

def string2Fraction(S):
    if(len(S.split('/'))== 1):return Fraction(int(S.split('/')[0]), int(1))   
    else:
        numerator, denominator = S.split('/')
        return Fraction(int(numerator), int(denominator))    
    
# 增加events
def modify_event_df( events, position = np.nan, value = None, nums = [], result_stack = [], expression_stack = []):
    # 读取trial_info
    trial_info_df =pd.read_pickle(session['filepath'])
    event_df = trial_info_df.at[len(trial_info_df) - 1,'events']
    # 判断事件
    if(events == 'selectedNumber' or events == 'selectedOperator'):
        position = session['button_index']
        value = session['button_value']
    else:
        value = events
    new_row = {'events':events , 'event_time': datetime.now(), 'position': position, 'value':value, 'nums':deepcopy(session['nums']), 'result_stack':deepcopy(session['result']), 'expression_stack':deepcopy(session['expression'])}
    # 使用 pandas.concat 进行行连接
    event_df = pd.concat([event_df, pd.DataFrame([new_row])], ignore_index=True)
    # 保存event_df
    trial_info_df.at[len(trial_info_df) - 1, 'events'] = event_df
    if(events == 'Mah'):
        trial_info_df.at[len(trial_info_df) - 1, 'mah'] = 1
    trial_info_df.to_pickle(session['filepath'])
    return event_df

# 初始化trial_info
def init_trial_info(input):
    # 修改input格式
    input = [string2Fraction(i) for i in input]
    # 读取文件
    trial_info_df = pd.read_pickle(session['filepath'])
    # 初始化当前trial的events_info
    events_columns = ["events", "event_time", "position", "value", "nums", "result_stack", "expression_stack"]
    events_df = pd.DataFrame([], columns=events_columns)
    # 初始化当前trial  ['block_index','trial_index', 'trial_index_in_block', 'input', 'mah','action','events','trial_start','trial_end']
    trial_info_df.loc[len(trial_info_df)] = [1,len(trial_info_df), 1, input, 0,[],events_df, datetime.now(), None ]
    # 保存文件
    trial_info_df.to_pickle(session['filepath'])
    # 添加trial_start event
    add_events('Trial_start')

# 根据结束情况，修改trial_info_df
def End_Trial_info():
    trial_info_df = pd.read_pickle(session['filepath'])
    trial_end = datetime.now()
    trial_info_df.at[len(trial_info_df) -1,'action'] =  session['action']
    trial_info_df.at[len(trial_info_df) -1,'trial_end'] = trial_end
    trial_info_df.to_pickle(session['filepath'])


# 添加各类事件
def add_events(events):
    if(events != 'Mah'): 
        modify_event_df(events)
    if events == 'Reset' or events == 'Pass' or events == 'Mah':
       
        # 添加一次结束事件
        modify_event_df('Trial_end')
        # 结束事件
        End_Trial_info()


from datetime import date
# 初始化session
def session_init( subject = None, nums = None, id = None, filepath = None ):
    '''trial info'''
    # 从题库中获得随机24点题目
    if(nums == None):
        nums = generate_numbers_inlibrary()
        nums_Fraction = [Fraction(n, 1) for n in nums] 
        session['nums'] = [Fraction2string(f) for f in nums_Fraction]
    else:
        session['nums'] = nums
    session['nums_target'] = deepcopy(session['nums']) # 原始题目
    session['id'] = id # session在当天的编号
    session['result'] = [] # 存放结果的栈
    session['selectedposition'] = [] # 已选操作位置
    session['button_index'] = None # 点击事件的位置
    session['button_value'] = None # 点击事件的值
    session['expression'] = deepcopy(session['nums_target']) # 记录表达式的栈
    session['action'] = [] # 记载有效动作
    session['signal'] = ['+','-','*','/','<-','->']  # 符号信息
    if(subject != None):
        session['subject'] = subject # 被试信息
    if(id != None):
        session['id'] = id
        session['filepath'] = filepath
    # 初始化当前trial的trial_info
    init_trial_info(session['nums_target'])

    return


# 判断是什么点击事件
def which_events(index):
    if(index<4): return "selectedNumber"
    elif(index>=4 and index<8):return "selectedOperator"
    elif(index==8): return "Reset"
    else: return "Next"



# 处理操作数和操作符
def resultDeal(index):

    session['button_index'] = index # 表示点击的button的index
    events_name = which_events(index)
    # 判断选择的是signal or num
    if(events_name == "selectedNumber"): selected_value = session["nums"][index]; 
    elif(events_name == "selectedOperator"):selected_value = session["signal"][index - 4]
    else:print('出错'); return 
    session["button_value"] = selected_value 
    # 判断是否能够添加
    if(index in session['selectedposition'] or selected_value == None):return 
    # 如果原result为空，则碰到数字直接添加
    elif(len(session["selectedposition"]) == 0):
        if(which_events(index) == "selectedNumber"):
            session["selectedposition"].append(index)
            session["result"].append(selected_value)
            session["action"].append(selected_value)
    # 原result不是空，则判断是否需要覆盖
    elif(which_events(session["selectedposition"][-1])=="selectedNumber" and which_events(index) == "selectedNumber" \
        or which_events(session["selectedposition"][-1]) == "selectedOperator" and which_events(index) == "selectedOperator"):
        session["selectedposition"][-1] = index
        session["result"][-1] = selected_value
        session["action"].pop()
        session["action"].append(selected_value)
    # 直接添加
    else:
        session["selectedposition"].append(index)
        session['result'].append(selected_value)
        session["action"].append(selected_value)
    
    # 添加点击事件
    add_events(events_name)

    return 

# 计算函数
def caculateResult(result):
    # result是string需要转换
    num1 = string2Fraction( result[0])
    num2 = string2Fraction( result[2])
    r = ops[result[1]](num1, num2)
    return Fraction2string(r)

# 处理result栈
def Evaluate_calculate():
    if(len(session['result']) == 3):
        # result
        r = caculateResult(session['result'])
        session['result'] = []
        old_nums = deepcopy(session['nums'])
        session['nums'][session['selectedposition'][0]] = None
        session['nums'][session['selectedposition'][2]] = r
        # expression
        op_index = session['selectedposition'][1] - 4
        num1_index = session['selectedposition'][0]
        num2_index = session['selectedposition'][2]
        session['expression'][num2_index] = "(" + session["expression"][num1_index] + session["signal"][op_index] + session['expression'][num2_index] + ")"
        session['expression'][num1_index] = None
        session['selectedposition'] = []

        # 添加计算事件
        add_events('calculate')

        # 判断是否mah
        if_solve()


# 处理鼠标点击事件
def deal_post(button_index):
    # 判断是哪种类型 [num1 num2 num3 num4 op1 op2 op3 op4 reset next]
    if(button_index == 8):  # RESET
        # 添加RESET事件
        add_events('Reset')
        # 初始化新的trial
        session_init(None, session['nums_target'])

    elif(button_index == 9) : # PASS
        # 添加
        add_events('Pass')
        # 初始化新的trial
        session_init()

    else:  
        # 操作数操作符处理
        resultDeal(button_index)
        # 判断是否可以calculate
        Evaluate_calculate()

    return


# 判断当前题目是否解答成功
def if_solve():
    effective_num = [num for num in session['nums'] if num != None]

    if(len(effective_num) == 1): 
        if(string2Fraction(effective_num[0]) == 24 ):
            # 添加mah事件
            add_events('Mah')
            # 初始化新的trial
            session_init()


from datetime import date
import os
# 创建被试的文件夹
def create_recording(subject):
    # 根据subject创建recording
    trail_info_columns = ['block_index','trial_index', 'trial_index_in_block', 'input', 'mah','action','events','trial_start','trial_end']
    data = pd.DataFrame([],columns = trail_info_columns)
    # 创建当前日期的文件夹
    today = date.today()
    filepath = './Recording/' + str(today) + '/'
    if(not os.path.exists(filepath)):
        os.mkdir(filepath)
    # 获取当前的数字
    folders = os.listdir(filepath) # 获取当前路径下的所有文件夹
    max_digit = -1  # 初始化最大数字为负数
    for folder in folders:
        split_label = folder.split("_")
        first_part = split_label[0]
    
        if(int(first_part) > max_digit):
            max_digit = int(first_part)
    
    filepath = filepath + str(max_digit + 1) + '_' + subject + '.pkl'
    data.to_pickle(filepath)

    return max_digit+1, filepath