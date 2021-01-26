# This module manages .json files

import json

# This gets a key's chosen attribute by hook name
def get(hook,key='name'):
    for s in range(len(hooks)):
        if hooks[s]['name'] == hook:
            return hooks[s][key]
    return None

# This loads certain .json files
def load():
    global hooks, commands
    with open('json\webhooks.json') as f:
        hooks = json.load(f)
    with open('json\commands.json') as x:
        commands = json.load(x)

# This deletes a hook by its name
def delete(hook):
    for s in range(len(hooks)):
        if hooks[s]["name"] == hook:
            if currentHook == hook:
                currentHook = None
            hooks.pop(s)
            with open('json\webhooks.json', 'w') as f:
                json.dump(hooks, f,
                sort_keys=True, indent=2, separators=(',', ': '))
            return True
            break
    return False

# This adds a hook to webhooks.json
def amend(hook):
    hooks.append(hook.copy())
    with open('json\webhooks.json', 'w') as f:
        json.dump(hooks, f, sort_keys=True, indent=2, separators=(',', ': '))
