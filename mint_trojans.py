import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from cadCAD.configuration import Configuration
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor

initial_conditions = {
  'BC_reserve': 0,
  'token_holders': np.array([1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]),
  'n': 8, # max number of token holders including guildbank and DAO pool
  'DAO_pool_index': 0,
  'guildbank_index': 1,
  'amount_to_mint': 100, # in eth
  'amount_to_burn': 0.2, # proportion of holdings
  'price': 1, # in eth/tok
  'total_tokens': 0,
  'action': 'mint',
  'update_index': 0,
  'DAO_tax_rate': 0.02,
  'redist_tax_rate': 0.01,
  'redist': 0,
}

def choose_holder(params, step, sL, s):
  index = np.random.randint(2, s['n'])
  print("Index to act on is %s" % (index))
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

#def update_BC_reserve_burn(params, step, sL, s, _input):
#    return (y, x)

def update_total_tokens_mint(params, step, sL, s, _input):
    y = 'total_tokens'
    amount_to_mint = s['amount_to_mint']
    x = s['total_tokens'] + amount_to_mint
    return (y, x)

def update_total_tokens_burn(params, step, sL, s, _input):
    y = 'total_tokens'
    token_holders = s['token_holders']
    update_index = _input['update_index']
    amount_to_burn = s['amount_to_burn'] * token_holders[update_index]
    x = s['total_tokens'] - amount_to_burn
    return (y, x)

def update_token_holders_mint(params, step, sL, s, _input):
  y = 'token_holders'
  x = s['token_holders']
  update_index = _input['update_index']
  amount_to_mint = s['amount_to_mint'] * (1 - s['DAO_tax_rate'] - s['redist_tax_rate'])
  x[update_index] = x[update_index] + amount_to_mint
  DAO_tax_amount = s['amount_to_mint'] * s['DAO_tax_rate']
  x[0] = x[0] + DAO_tax_amount
  print(x)
  return (y, x)

def update_token_holders_burn(params, step, sL, s, _input):
  y = 'token_holders'
  x = s['token_holders']
  update_index = _input['update_index']
  amount_to_burn = s['amount_to_burn'] * x[update_index]
  x[update_index] = x[update_index] - amount_to_burn
  print(x)
  return (y, x)

def update_redistribution_amount_mint(params, step, sL, s, _input):
  y = 'redist'
  update_index = _input['update_index']
  redist_tax_amount = 0
  if (update_index > 1):
    redist_tax_amount = s['amount_to_mint'] * s['redist_tax_rate']
  print(redist_tax_amount)
  return (y, redist_tax_amount)

def redistribute(params, step, sL, s, _input):
  y = 'token_holders'
  x = s['token_holders']
  n = s['n']
  redist = s['redist']
  total_tokens = s['total_tokens']
  print("Redistribute %s based on total %s" % (redist, total_tokens))
  for i in range(0, n):
      x[i] = x[i] + redist * x[i] / total_tokens
  print(x)
  return (y, x)

partial_state_update_blocks = [
    { 
        'policies': {
            'choose_holder': choose_holder, 
        },
        'variables': {
            # 'BC_reserve': update_BC_reserve_burn,
            'token_holders': update_token_holders_burn,
            # 'redist': update_redistribution_amount_burn,
            'total_tokens': update_total_tokens_burn,
        }
    }
]


simulation_parameters = {
    'T': range(100),
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
