# Battle Royal
A kick-ass player for an imaginary battle-royal game


FIRST TIME:
1) create a directory wherever you want on your computer
2) In same directory run 'git clone https://github.com/mcconvillec/battle_royal.git'

When you clone the repository, navigate to where it is stored on your computer and run:
1) python3 -m venv battle_royal
2) source battle_royal/bin/activate
3) pip install -r requirements.txt
4) deavtivate battle_royal  #exits venv

REPEAT STEPS 2 and 3 each time you work on the project


CONTRIBUTING:
Make a branch with your commits (be sure to branch from a fresh copy of master, not another branch!) eg:

1) git checkout master && git pull
2) git checkout -b feature/my_new_branch_name
3) git add file.py && git commit -m "my new commit".    #Provides a message about what code you've added with the commit
5) git push #pushes all your commits up to the git repository 'git push --set-upstream origin feature/my_new_branch_name'
6) make a Pull Request on the github interface 
7) get someone to review!



# Project description:

Inputs: Each turn
- String name of current location
- Market inventory (if researched): {product: (price, amount), product2: (price,amount)}
- Market inventory (if no research): {}
- Player information: {market1: {product: price, product2: price}, market2: {product1: price, product2:price}}
- Black: [“market1”, “market2”, “market3”]
- Grey: [“market1”, “market2”, “market3”]


Function: take_turn

- Output: each turn
(Command.attribute, x)
       o If Command.attribute = MOVE_TO or RESEARCH or PASS: x = None
       o If Command.attribute = BUY, SELL: x = (product name, amount)


