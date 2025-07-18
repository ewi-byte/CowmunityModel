from Cowmunity import Sets, Parameters, Variables, Equations, FixSBMLs, solve, extract_results, print_results, bug_huntin

# variable_choice can be set to 'biomass_outer' or 'ATP_outer'

variable_choice = 'biomass_outer'  # Default objective variable

file = open('cow.txt', 'r')
cow = file.read()
print(cow)
print()
print("Building the Cowmunity model...")

FixSBMLs()
Sets()
Parameters()
Variables(variable_choice)
Equations()
solve()
extract_results()
print_results()
bug_huntin()