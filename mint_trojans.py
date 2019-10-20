import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from cadCAD.configuration import Configuration
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor

initial_conditions = {
  'BC_reserve': 0,
  'token_holders': np.zeros(5),
  'n': 5, # max number of token holders including guildbank and DAO pool
  'DAO_pool_index': 0,
  'guildbank_index': 1,
  'amount_to_mint': 100, # in eth
  'amount_to_burn': 0.2, # proportion of holdings
  'price': 1, # in eth/tok
  'total_tokens': 0,
  'action': 'mint',
  'update_index': 0,
  'DAO_tax_rate': 0.02,
}

def choose_holder_to_update(params, step, sL, s):
  index = np.random.randint(0, s['n']-1)
  print("Index to update is %s" % (index))
  return ({'update_index': index})

def choose_action(params, step, sL, s):
  p = np.random.randint(0, 100)
  return ({'action': 'mint'})

def update_BC_reserve_mint(params, step, sL, s, _input):
    y = 'BC_reserve'
    amount_to_mint = 0
    if (_input['update_index'] > 1):
        amount_to_mint = s['amount_to_mint']
    x = s['BC_reserve'] + amount_to_mint # newly minted amount
    print("New BC reserve is %s" % (x))
    return (y, x)

def update_token_holders_mint(params, step, sL, s, _input):
  y = 'token_holders'
  x = s['token_holders']
  update_index = _input['update_index']
  amount_to_mint = 0
  DAO_tax_amount = 0
  if (update_index > 1):
    amount_to_mint = s['amount_to_mint'] * (1 - s['DAO_tax_rate'])
    x[update_index] = x[update_index] + amount_to_mint
    DAO_tax_amount = s['amount_to_mint'] * s['DAO_tax_rate']
    x[0] = x[0] + DAO_tax_amount
  print(x)
  return (y, x)

partial_state_update_blocks = [
    { 
        'policies': {
            'choose_holder_to_update': choose_holder_to_update, 
        },
        'variables': {
            'BC_reserve': update_BC_reserve_mint,
            'token_holders': update_token_holders_mint
        }
    },
]


simulation_parameters = {
    'T': range(10),
    'N': 1,
    'M': {}
}


config = Configuration(initial_state=initial_conditions,
                       partial_state_update_blocks=partial_state_update_blocks,
                       sim_config=simulation_parameters
                      )


exec_mode = ExecutionMode()
exec_context = ExecutionContext(exec_mode.single_proc)
executor = Executor(exec_context, [config])
raw_result, tensor = executor.execute()

plt.show()
