from Cowmunity import Sets, Parameters, Variables, Equations, FixSBMLs, solve, extract_results, print_results, bug_huntin

# variable_choice can be set to 'biomass_outer' or 'ATP_outer'


variable_choice = 'biomass_outer'  # Default objective variable

file = open('cow.txt', 'r')
cow = file.read()
print(cow)
print()

print('Choose the treatment molecule to be used in the model:\n\n\
0. None\n\
1. Imidazole\n\
2. L-Carnitine\n\
3. Methyl Jasmonate\n\
4. Propylpyrazine')
print()
treatment_choice = input('Enter your choice (0-4): ')
print()

if treatment_choice == '0':
    treatment = 'no'
elif treatment_choice == '1':
    treatment = 'imidazole'
elif treatment_choice == '2':
    treatment = 'l-carnitine'
elif treatment_choice == '3':
    treatment = 'methyl jasmonate'
elif treatment_choice == '4':
    treatment = 'propylpyrazine'
else:
    print('Invalid choice. Defaulting to no treatment.')
    treatment = 'no'

print(f"Building the Cowmunity model with {treatment} treatment...")

FixSBMLs()
Sets()
Parameters()
Variables(variable_choice, treatment)
Equations()
solve()
extract_results()
print_results()
bug_huntin()