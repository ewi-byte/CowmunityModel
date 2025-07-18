import pandas as pd
import libsbml
from gamspy import Container, Set, Parameter, Variable, Equation, Model, Sum, Sense, Options, SpecialValues, SolveStatus
from gamspy.math import abs
import sys

def Sets():
    print("Creating sets...")
    global cowmunity

    cowmunity = Container()

    global j_mgk, j_prm, j_rfl, i_mgk, i_prm, i_rfl

    j_mgk = Set(container=cowmunity, name="j_mgk", description="M. Gottschalkii reactions")
    j_prm = Set(container=cowmunity, name="j_prm", description="P. ruminicola reactions")
    j_rfl = Set(container=cowmunity, name="j_rfl", description="R. flavefaciens reactions")

    i_mgk = Set(container=cowmunity, name="i_mgk", description="M. Gottschalkii metabolites")
    i_prm = Set(container=cowmunity, name="i_prm", description="P. ruminicola metabolites")
    i_rfl = Set(container=cowmunity, name="i_rfl", description="R. flavefaciens metabolites")

    def extract_metabolites(xml_file_path, GAMSpy_set):
        # Parse the XML file
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{xml_file_path}')
        model = document.getModel()
        if model is None:
            raise ValueError("The SBML model could not be parsed or is empty.")
        
        # Extract names and store them in a list
        met_name = {}
        for i in range(model.getNumSpecies()):
            species = model.getSpecies(i)
            new_entry = {species.id : species.getName()[0:63]}
            met_name.update(new_entry)
        df = pd.DataFrame.from_dict(met_name, orient='index', columns=['name'])
        
        # add the names to the GAMSpy Set
        GAMSpy_set.setRecords(df.reset_index())


    def extract_reactions(xml_file_path, GAMSpy_set):
        # Parse the XML file
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{xml_file_path}')
        model = document.getModel()
        if model is None:
            raise ValueError("The SBML model could not be parsed or is empty.")
        
        # Extract names and store them in a list
        rxn_name = {}
        for i in range(model.getNumReactions()):
            reaction = model.getReaction(i)
            new_entry = {reaction.id : reaction.getName()[0:63]}
            rxn_name.update(new_entry)
        df = pd.DataFrame.from_dict(rxn_name, orient='index', columns=['name'])
        
        # add the names to the GAMSpy Set
        GAMSpy_set.setRecords(df.reset_index())

    
    extract_reactions('M. gottschalkii.xml', j_mgk)
    extract_reactions('P. ruminicola.xml', j_prm)
    extract_reactions('R. flavefaciens.xml', j_rfl)

    extract_metabolites('M. gottschalkii.xml', i_mgk)
    extract_metabolites('P. ruminicola.xml', i_prm)
    extract_metabolites('R. flavefaciens.xml', i_rfl)

def Parameters():
    print("Adding model parameters...")
    global ub_mgk, ub_prm, ub_rfl, lb_mgk, lb_prm, lb_rfl

    ub_mgk = Parameter(container=cowmunity, name="ub_mgk", domain=j_mgk, description="Upper bound for M. Gottschalkii reactions")
    lb_mgk = Parameter(container=cowmunity, name="lb_mgk", domain=j_mgk, description="Lower bound for M. Gottschalkii reactions")

    ub_prm = Parameter(container=cowmunity, name="ub_prm", domain=j_prm, description="Upper bound for P. ruminicola reactions")
    lb_prm = Parameter(container=cowmunity, name="lb_prm", domain=j_prm, description="Lower bound for P. ruminicola reactions")

    ub_rfl = Parameter(container=cowmunity, name="ub_rfl", domain=j_rfl, description="Upper bound for R. flavefaciens reactions")
    lb_rfl = Parameter(container=cowmunity, name="lb_rfl", domain=j_rfl, description="Lower bound for R. flavefaciens reactions")

    # define the reaction types for each reaction, whether they are reversible (1) or irreversible (0)

    rxntype_mgk = Parameter(container=cowmunity, name="rxntype_mgk", domain=j_mgk, description="Reaction type for M. Gottschalkii reactions")
    rxntype_prm = Parameter(container=cowmunity, name="rxntype_prm", domain=j_prm, description="Reaction type for P. ruminicola reactions")
    rxntype_rfl = Parameter(container=cowmunity, name="rxntype_rfl", domain=j_rfl, description="Reaction type for R. flavefaciens reactions")

    # define the stoichiometric matrix for each species, which describes the relationship between reactions and metabolites
    # gives the coefficients for each reaction

    global S_mgk, S_prm, S_rfl

    S_mgk = Parameter(container=cowmunity, name="S_mgk", domain=[j_mgk, i_mgk], description="Stoichiometric matrix for M. Gottschalkii")
    S_prm = Parameter(container=cowmunity, name="S_prm", domain=[j_prm, i_prm], description="Stoichiometric matrix for P. ruminicola")
    S_rfl = Parameter(container=cowmunity, name="S_rfl", domain=[j_rfl, i_rfl], description="Stoichiometric matrix for R. flavefaciens")

    # define whether each reaction is an exchange reaction

    ex_mgk = Parameter(container=cowmunity, name="ex_mgk", domain=j_mgk, description="Exchange for M. Gottschalkii reactions")
    ex_prm = Parameter(container=cowmunity, name="ex_prm", domain=j_prm, description="Exchange for P. ruminicola reactions")
    ex_rfl = Parameter(container=cowmunity, name="ex_rfl", domain=j_rfl, description="Exchange for R. flavefaciens reactions")

    def extract_rxn_type(xml_file_path, GAMSpy_parameter):
        # Parse the XML file
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{xml_file_path}')
        model = document.getModel()
        if model is None:
            raise ValueError("The SBML model could not be parsed or is empty.")
        # Extract names and store them in a list
        type_dict = {}
        for i in range(model.getNumReactions()):
            reaction = model.getReaction(i)
            rxn_type = reaction.getReversible()
            if rxn_type:
                rxn_type = 1
            else:
                rxn_type = 0
            new_entry = {reaction.id : rxn_type}
            type_dict.update(new_entry)
        
        df = pd.DataFrame.from_dict(type_dict, orient='index', columns=['name'])
        
        # add the names to the GAMSpy Set
        GAMSpy_parameter.setRecords(df.reset_index())


    def extract_matrix(xml_file_path, GAMSpy_parameter):
        # Parse the XML file
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{xml_file_path}')
        model = document.getModel()
        if model is None:
            raise ValueError("The SBML model could not be parsed or is empty.")
        # Extract reactions, metabolites, and their stoichiometry
        df = pd.DataFrame()
        for i in range(model.getNumReactions()):
            reaction = model.getReaction(i)
            for i in range(reaction.getNumReactants()):
                reactant = reaction.getReactant(i)
                metabolite_id = reactant.species
                stoich = reactant.stoichiometry
                new_row_df = pd.DataFrame({'reaction': [reaction.id], 'metabolite': [metabolite_id], 'stoichiometry': [-stoich]})
                df = pd.concat([df, new_row_df], ignore_index=True)
            for i in range(reaction.getNumProducts()):
                product = reaction.getProduct(i)
                metabolite_id = product.species
                stoich = product.stoichiometry
                new_row_df = pd.DataFrame({'reaction': [reaction.id], 'metabolite': [metabolite_id], 'stoichiometry': [stoich]})
                df = pd.concat([df, new_row_df], ignore_index=True)

        df = df.set_index(['reaction', 'metabolite'])

        
        # add the names to the GAMSpy Set
        GAMSpy_parameter.setRecords(df.reset_index())


    def extract_exchange_type(xml_file_path, GAMSpy_parameter):
        # Parse the XML file
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{xml_file_path}')
        model = document.getModel()
        if model is None:
            raise ValueError("The SBML model could not be parsed or is empty.")
        # Extract names and store them in a list
        type_dict = {}
        ex_count = 0
        for i in range(model.getNumReactions()):
            reaction = model.getReaction(i)
            if 'EX_' in reaction.id:
                ex_type = 1
                ex_count += 1
            else:
                ex_type = 0
            new_entry = {reaction.id : ex_type}
            type_dict.update(new_entry)
        
        df = pd.DataFrame.from_dict(type_dict, orient='index', columns=['name'])
        
        # add the names to the GAMSpy Set
        GAMSpy_parameter.setRecords(df.reset_index())


    extract_rxn_type('M. gottschalkii.xml', rxntype_mgk)
    extract_rxn_type('P. ruminicola.xml', rxntype_prm)
    extract_rxn_type('R. flavefaciens.xml', rxntype_rfl)

    extract_matrix('M. gottschalkii.xml', S_mgk)
    extract_matrix('P. ruminicola.xml', S_prm)
    extract_matrix('R. flavefaciens.xml', S_rfl)

    extract_exchange_type('M. gottschalkii.xml', ex_mgk)
    extract_exchange_type('P. ruminicola.xml', ex_prm)
    extract_exchange_type('R. flavefaciens.xml', ex_rfl)

    # using a scalar parameter to define the maximum flux for each reaction, this is a constant that will be used in the model

    Vmax = Parameter(container=cowmunity, name='Vmax', records=1000)

    # set the reaction bounds for the irreversible reactions, reaction type 0

    ub_mgk[j_mgk].where[rxntype_mgk[j_mgk] == 0] = Vmax
    lb_mgk[j_mgk].where[rxntype_mgk[j_mgk] == 0] = SpecialValues.EPS # using SpecialValues.EPS to avoid zero lower bounds, which can cause issues in some solvers

    ub_prm[j_prm].where[rxntype_prm[j_prm] == 0] = Vmax
    lb_prm[j_prm].where[rxntype_prm[j_prm] == 0] = SpecialValues.EPS

    ub_rfl[j_rfl].where[rxntype_rfl[j_rfl] == 0] = Vmax
    lb_rfl[j_rfl].where[rxntype_rfl[j_rfl] == 0] = SpecialValues.EPS

    # set the reaction bounds for the reversible reactions, reaction type 1

    ub_mgk[j_mgk].where[rxntype_mgk[j_mgk] == 1] = Vmax
    lb_mgk[j_mgk].where[rxntype_mgk[j_mgk] == 1] = -Vmax

    ub_prm[j_prm].where[rxntype_prm[j_prm] == 1] = Vmax
    lb_prm[j_prm].where[rxntype_prm[j_prm] == 1] = -Vmax

    ub_rfl[j_rfl].where[rxntype_rfl[j_rfl] == 1] = Vmax
    lb_rfl[j_rfl].where[rxntype_rfl[j_rfl] == 1] = -Vmax

def Variables(variable_choice):
    global v_mgk, v_prm, v_rfl, biomass_outer, ATP_outer, objective_variable

    biomass_outer = Variable(container=cowmunity, name="biomass_outer", description="Outer problem Biomass objective function")
    ATP_outer = Variable(container=cowmunity, name="ATP_outer", description="Outer problem ATP objective function")

    if variable_choice == 'biomass_outer':
        objective_variable = biomass_outer
    if variable_choice == 'ATP_outer':
        objective_variable = ATP_outer


    v_mgk = Variable(container=cowmunity, name="v_mgk", domain=j_mgk, description="Fluxes for M. Gottschalkii reactions")
    v_prm = Variable(container=cowmunity, name="v_prm", domain=j_prm, description="Fluxes for P. ruminicola reactions")
    v_rfl = Variable(container=cowmunity, name="v_rfl", domain=j_rfl, description="Fluxes for R. flavefaciens reactions")

    global lambda_mgk, lambda_prm, lambda_rfl

    # Dual variables for the mass balance
    lambda_mgk = Variable(container=cowmunity, name="lambda_mgk", domain=i_mgk, description="Dual variables for M. Gottschalkii metabolites")
    lambda_prm = Variable(container=cowmunity, name="lambda_prm", domain=i_prm, description="Dual variables for P. ruminicola metabolites")
    lambda_rfl = Variable(container=cowmunity, name="lambda_rfl", domain=i_rfl, description="Dual variables for R. flavefaciens metabolites")

    # defining the flux bounds for each reaction as the upper and lower bounds defined above
    v_mgk.lo[j_mgk] = lb_mgk[j_mgk]
    v_mgk.up[j_mgk] = ub_mgk[j_mgk]
    v_prm.lo[j_prm] = lb_prm[j_prm]
    v_prm.up[j_prm] = ub_prm[j_prm]
    v_rfl.lo[j_rfl] = lb_rfl[j_rfl]
    v_rfl.up[j_rfl] = ub_rfl[j_rfl]

    # medium composition, is there anything else in the medium that i should include
    # fixing some of the flux variables to known values, these are the uptakes rates from supplemental data #8
    # should I set the O2 intake to zero?
    # how do I make sure that they are going to pull from a shared pool? Should these just upper bounds?
    # look to figure 1 in the islam paper for more information of where each metabolite goes
    v_prm.lo['EX_cpd11657_e0'] = -0.965423023 # uptake rate for Starch
    v_prm.lo['EX_cpd00076_e0'] = -0.834726132 # uptake rate for Sucrose
    v_rfl.lo['EX_cpd00076_e0'] = -0.834726132 
    v_prm.lo['EX_cpd00053_e0'] = -1.597816364 # uptake rate for L-Glutamine
    v_rfl.lo['EX_cpd00053_e0'] = -1.597816364
    # v_prm.lo['EX_cpd00027_e0'] = -0.794397609 # uptake rate for D-glucose *****
    v_rfl.lo['EX_cpd00027_e0'] = -0.794397609
    v_rfl.lo['EX_cpd00107_e0'] = -1.148366562 # uptake rate for L-Leucine
    v_prm.lo['EX_cpd00107_e0'] = -1.148366562 
    # v_prm.lo['EX_cpd00224_e0'] = -0.666427627 # uptake rate for L-arabinose *****
    v_rfl.lo['EX_cpd00224_e0'] = -0.666427627
    # v_prm.lo['EX_cpd00035_e0'] = -0.938846598 # uptake rate for L-Alanine ****
    # v_rfl.lo['EX_cpd00035_e0'] = -0.938846598
    v_prm.lo['EX_cpd00132_e0'] = -0.400330802 # uptake rate for L-Asparagine
    v_rfl.lo['EX_cpd00066_e0'] = -0.310015056 # uptake rate for L-Phenylalanine
    v_rfl.lo['EX_cpd00156_e0'] = -0.385856944 # uptake rate for L-Valine
    v_rfl.lo['EX_cpd00069_e0'] = -0.218417727 # uptake rate for L-Tyrosine
    v_prm.lo['EX_cpd00060_e0'] = -0.233929798 # uptake rate for L-Methionine
    v_prm.lo['EX_cpd00161_e0'] = -0.261179221 # uptake rate for L-Threonine
    v_rfl.lo['EX_cpd00161_e0'] = -0.261179221
    v_rfl.lo['EX_cpd00322_e0'] = -0.211165444 # uptake rate for L-Isoleucine
    v_prm.lo['EX_cpd00051_e0'] = -0.133660701 # uptake rate for L-Arginine
    v_rfl.lo['EX_cpd00051_e0'] = -0.133660701
    # v_prm.lo['EX_cpd00033_e0'] = -0.268595078 # uptake rate for Glycine ******
    # v_rfl.lo['EX_cpd00033_e0'] = -0.268595078
    v_prm.lo['EX_cpd00348_e0'] = -0.075513967 # uptake rate for D-Galactose 
    v_rfl.lo['EX_cpd00348_e0'] = -0.075513967
    v_rfl.lo['EX_cpd00119_e0'] = -0.124559013 # uptake rate for L-Histidine
    v_prm.lo['EX_cpd00039_e0'] = -0.098373937 # uptake rate for L-Lysine
    v_rfl.lo['EX_cpd00039_e0'] = -0.098373937
    v_prm.lo['EX_cpd00084_e0'] = -0.114920408 # uptake rate for L-Cysteine
    v_rfl.lo['EX_cpd00084_e0'] = -0.114920408
    v_prm.lo['EX_cpd00053_e0'] = -0.080568485 # uptake rate for L-Glutamine
    v_rfl.lo['EX_cpd00053_e0'] = -0.080568485
    v_rfl.lo['EX_cpd00038_e0'] = -0.007734655 # uptake rate for GTP
    v_rfl.lo['EX_cpd00138_e0'] = -0.021731242 # uptake rate for D-Mannose
    v_prm.lo['EX_cpd00052_e0'] = -0.00730785 # uptake rate for CTP
    v_rfl.lo['EX_cpd00052_e0'] = -0.00730785
    v_prm.lo['EX_cpd00002_e0'] = -0.006289719 # uptake rate for ATP
    v_rfl.lo['EX_cpd00002_e0'] = -0.006289719
    v_prm.lo['EX_cpd00062_e0'] = -0.005932755 # uptake rate for UTP
    v_rfl.lo['EX_cpd00062_e0'] = -0.005932755
    v_rfl.lo['EX_cpd00115_e0'] = -0.001147315 # uptake rate for dATP
    v_rfl.lo['EX_cpd00357_e0'] = -0.001147552 # uptake rate for dTTP
    v_rfl.lo['EX_cpd00241_e0'] = -0.001012678 # uptake rate for dGTP
    v_prm.lo['EX_cpd00356_e0'] = -0.001016235 # uptake rate for dCTP
    v_rfl.lo['EX_cpd00356_e0'] = -0.001016235
    # v_prm.lo['EX_cpd11746_e0'] = -0.320930655 # uptake rate for Cellulose ****
    v_rfl.lo['EX_cpd11746_e0'] = -0.320930655
    v_rfl.lo['EX_cpd29869_e0'] = -0.002499522 # uptake rate for hemicellulose
    v_prm.lo['EX_cpd00009_e0'] = -0.005244478 # uptake rate for Phosphate
    v_rfl.lo['EX_cpd00009_e0'] = -0.005244478
    v_rfl.lo['EX_cpd00065_e0'] = 0 # uptake rate for Tryptophan
    v_prm.lo['EX_cpd00073_e0'] = -0.629166662 # uptake rate for Urea
    v_rfl.lo['EX_cpd00073_e0'] = -0.629166662
    v_prm.lo['EX_cpd00048_e0'] = -0.004273279 # uptake rate for Sulfate
    v_rfl.lo['EX_cpd00048_e0'] = -0.004273279


    # Dual variables for bounds
    global muLB_mgk, muUB_mgk, muLB_prm, muUB_prm, muLB_rfl, muUB_rfl

    muLB_mgk = Variable(container=cowmunity, name="muLB_mgk", domain=j_mgk, description="Dual variables for MGK LB")
    muUB_mgk = Variable(container=cowmunity, name="muUB_mgk", domain=j_mgk, description="Dual variables for MGK UB")
    muLB_prm = Variable(container=cowmunity, name="muLB_prm", domain=j_prm, description="Dual variables for PRM LB")
    muUB_prm = Variable(container=cowmunity, name="muUB_prm", domain=j_prm, description="Dual variables for PRM UB")
    muLB_rfl = Variable(container=cowmunity, name="muLB_rfl", domain=j_rfl, description="Dual variables for RFL LB")
    muUB_rfl = Variable(container=cowmunity, name="muUB_rfl", domain=j_rfl, description="Dual variables for RFL UB")

    # Set dual variables to positive
    muLB_mgk.lo[j_mgk] = 0
    muUB_mgk.lo[j_mgk] = 0
    muLB_prm.lo[j_prm] = 0
    muUB_prm.lo[j_prm] = 0
    muLB_rfl.lo[j_rfl] = 0
    muUB_rfl.lo[j_rfl] = 0

    # transfer uptake positive variables for the shared metabolites

    global trans_CO2_mgk, trans_H2_mgk, trans_formate_mgk, trans_acetate_mgk, trans_d_mannose_mgk, trans_d_fructose_mgk, trans_tetrathionate_mgk, trans_thiosulfate_mgk
    global trans_cellulose_prm, trans_d_glucose_prm, trans_acetate_prm, trans_l_arabinose_prm, trans_biotin_prm, trans_thiamin_prm, trans_octadecenoate_prm, trans_maltoheptaose_prm
    global trans_nitrite_prm, trans_n_acetyl_d_glucosamine_prm, trans_aminoethanol_prm, trans_cobinamide_prm, trans_alanine_prm, trans_leucine_prm, trans_glycine_prm, trans_proline_prm
    global trans_d_galacturonate_rfl, trans_deoxyadenosine_rfl, trans_dephospho_coa_rfl, trans_cobinamide_rfl, trans_alanine_rfl, trans_leucine_rfl, trans_glycine_rfl, trans_proline_rfl, trans_aminoethanol_rfl

    trans_CO2_mgk = Variable(container=cowmunity, name="trans_CO2_mgk", description="maximum transfer of CO2 to M. Gottschalkii")
    trans_H2_mgk = Variable(container=cowmunity, name="trans_H2_mgk", description="maximum transfer of H2 to M. Gottschalkii")
    trans_formate_mgk = Variable(container=cowmunity, name='trans_formate_mgk', description="maximum transfer of formate to M. Gottschalkii")
    trans_acetate_mgk = Variable(container=cowmunity, name="trans_acetate_mgk", description="maximum transfer of acetate to M. Gottschalkii")
    trans_d_mannose_mgk = Variable(container=cowmunity, name="trans_dmannose_mgk", description="maximum transfer of D-mannose to M. Gottschalkii")
    trans_d_fructose_mgk = Variable(container=cowmunity, name="trans_dfructose_mgk", description="maximum transfer of D-fructose to M. Gottschalkii")
    trans_tetrathionate_mgk = Variable(container=cowmunity, name="trans_tetrathionate_mgk", description="maximum transfer of tetrathionate to M. Gottschalkii")
    trans_thiosulfate_mgk = Variable(container=cowmunity, name="trans_thiosulfate_mgk", description="maximum transfer of thiosulfate to M. Gottschalkii")

    trans_cellulose_prm = Variable(container=cowmunity, name='trans_cellulose_prm', description="maximum transfer of cellulose to P. ruminicola")
    trans_d_glucose_prm = Variable(container=cowmunity, name='trans_d_glucose_prm', description="maximum transfer of D-Glucose to P. ruminicola")
    trans_acetate_prm = Variable(container=cowmunity, name='trans_acetate_prm', description="maximum transfer of Acetate to P. ruminicola")
    trans_l_arabinose_prm = Variable(container=cowmunity, name='trans_l_arabinose_prm', description="maximum transfer of L-Arabinose to P. ruminicola")
    trans_biotin_prm = Variable(container=cowmunity, name='trans_biotin_prm', description="maximum transfer of Biotin to P. ruminicola")
    trans_thiamin_prm = Variable(container=cowmunity, name='trans_thiamin_prm', description="maximum transfer of Thiamin to P. ruminicola")
    trans_octadecenoate_prm = Variable(container=cowmunity, name='trans_octadecenoate_prm', description="maximum transfer of octadecenoate to P. ruminicola")
    trans_maltoheptaose_prm = Variable(container=cowmunity, name='trans_maltoheptaose_prm', description="maximum transfer of Maltoheptaose to P. ruminicola")
    trans_nitrite_prm = Variable(container=cowmunity, name='trans_nitrite_prm', description="maximum transfer of Nitrite to P. ruminicola")
    trans_n_acetyl_d_glucosamine_prm = Variable(container=cowmunity, name='trans_n_acetyl_d_glucosamine_prm', description="maximum transfer of N-Acetyl-D-glucosamine to P. ruminicola")
    trans_aminoethanol_prm = Variable(container=cowmunity, name='trans_aminoethanol_prm', description="maximum transfer of Aminoethanol to P. ruminicola")
    trans_cobinamide_prm = Variable(container=cowmunity, name='trans_cobinamide_prm', description="maximum transfer of Cobinamide to P. ruminicola")
    trans_alanine_prm = Variable(container=cowmunity, name='trans_alanine_prm', description="maximum transfer of Alanine to P. ruminicola")
    trans_leucine_prm = Variable(container=cowmunity, name='trans_leucine_prm', description="maximum transfer of Leucine to P. ruminicola")
    trans_glycine_prm = Variable(container=cowmunity, name='trans_glycine_prm', description="maximum transfer of Glycine to P. ruminicola")
    trans_proline_prm = Variable(container=cowmunity, name='trans_proline_prm', description="maximum transfer of Proline to P. ruminicola")

    trans_d_galacturonate_rfl = Variable(container=cowmunity, name='trans_d_galacturonate_rfl', description="maximum transfer of D-Galacturonate to R. flavefaciens")
    trans_deoxyadenosine_rfl = Variable(container=cowmunity, name='trans_deoxyadenosine_rfl', description="maximum transfer of Deoxyadenosine to R. flavefaciens")
    trans_dephospho_coa_rfl = Variable(container=cowmunity, name='trans_dephospho_coa_rfl', description="maximum transfer of Dephospho-CoA to R. flavefaciens")
    trans_cobinamide_rfl = Variable(container=cowmunity, name='trans_cobinamide_rfl', description="maximum transfer of Cobinamide to R. flavefaciens")
    trans_alanine_rfl = Variable(container=cowmunity, name='trans_alanine_rfl', description="maximum transfer of Alanine to R. flavefaciens")
    trans_leucine_rfl = Variable(container=cowmunity, name='trans_leucine_rfl', description="maximum transfer of Leucine to R. flavefaciens")
    trans_glycine_rfl = Variable(container=cowmunity, name='trans_glycine_rfl', description="maximum transfer of Glycine to R. flavefaciens")
    trans_proline_rfl = Variable(container=cowmunity, name='trans_proline_rfl', description="maximum transfer of Proline to R. flavefaciens")
    trans_aminoethanol_rfl = Variable(container=cowmunity, name='trans_aminoethanol_rfl', description="maximum transfer of Aminoethanol to R. flavefaciens")

    # set the transfer variables to positive, these are the maximum transfer rates for each metabolite

    trans_CO2_mgk.lo = 0
    trans_H2_mgk.lo = 0
    trans_formate_mgk.lo = 0
    trans_acetate_mgk.lo = 0
    trans_d_mannose_mgk.lo = 0
    trans_d_fructose_mgk.lo = 0
    trans_tetrathionate_mgk.lo = 0
    trans_thiosulfate_mgk.lo = 0

    trans_cellulose_prm.lo = 0
    trans_d_glucose_prm.lo = 0
    trans_acetate_prm.lo = 0
    trans_l_arabinose_prm.lo = 0
    trans_biotin_prm.lo = 0
    trans_thiamin_prm.lo = 0
    trans_octadecenoate_prm.lo = 0
    trans_maltoheptaose_prm.lo = 0
    trans_nitrite_prm.lo = 0
    trans_n_acetyl_d_glucosamine_prm.lo = 0
    trans_aminoethanol_prm.lo = 0
    trans_cobinamide_prm.lo = 0
    trans_alanine_prm.lo = 0
    trans_leucine_prm.lo = 0
    trans_glycine_prm.lo = 0
    trans_proline_prm.lo = 0

    trans_d_galacturonate_rfl.lo = 0
    trans_deoxyadenosine_rfl.lo = 0
    trans_dephospho_coa_rfl.lo = 0
    trans_cobinamide_rfl.lo = 0
    trans_alanine_rfl.lo = 0
    trans_leucine_rfl.lo = 0
    trans_glycine_rfl.lo = 0
    trans_proline_rfl.lo = 0
    trans_aminoethanol_rfl.lo = 0

def Equations():
    print("Adding equations...")


    # Objective Functions (Outer Objective)
    biomass_objective = Equation(container=cowmunity, name="biomass_objective", description="Objective function for total biomass accumulation")
    biomass_objective[...] = biomass_outer == v_mgk['R_biomass0'] + v_prm['R_biomass0'] + v_rfl['R_biomass0']

    ATP_objective = Equation(container=cowmunity, name="ATP_objective", description="Objective function for total ATP Production")
    ATP_objective[...] = ATP_outer == v_mgk['R_rxn02831_c0'] + v_mgk['R_rxn03535_c0'] + v_mgk['R_rxn06874_c0'] + v_mgk['R_rxn10476_c0'] + v_mgk['R_rxn11544_c0'] \
                                    + v_prm['R_rxn00986_c0'] + v_prm['R_rxn01987_c0'] + v_prm['R_rxn10042_c0'] \
                                    + v_rfl['R_rxn05840_c0'] + v_rfl['R_rxn06428_c0'] + v_rfl['R_rxn06874_c0'] + v_rfl['R_rxn10042_c0']


    # Constraints
    # these are the things that are going to make the model into a true community model rather than three separate models

    trans_CO2_mgk_balance = Equation(container=cowmunity, name='trans_CO2_balance', description="Balance for CO2 transfer to M. Gottschalkii")
    trans_CO2_mgk_balance[...] = trans_CO2_mgk <= v_prm['EX_cpd00011_e0'] + v_rfl['EX_cpd00011_e0']

    trans_H2_mgk_balance = Equation(container=cowmunity, name= 'trans_H2_mgk_balance', description="Balance for H2 transfer to M. Gottschalkii")
    trans_H2_mgk_balance[...] = trans_H2_mgk <= v_prm['EX_cpd11640_e0'] + v_rfl['EX_cpd11640_e0']

    trans_formate_mgk_balance = Equation(container=cowmunity, name='trans_formate_mgk_balance', description="Balance for formate transfer to M. Gottschalkii")
    trans_formate_mgk_balance[...] = trans_formate_mgk <= v_prm['EX_cpd00047_e0'] + v_rfl['EX_cpd00047_e0']

    trans_acetate_mgk_balance = Equation(container=cowmunity, name='trans_acetate_mgk_balance', description="Balance for acetate transfer to M. Gottschalkii")
    trans_acetate_mgk_balance[...] = trans_acetate_mgk <= v_rfl['EX_cpd00029_e0']

    trans_d_mannose_mgk_balance = Equation(container=cowmunity, name='trans_d_mannose_mgk_balance', description="Balance for D-mannose transfer to M. Gottschalkii")
    trans_d_mannose_mgk_balance[...] = trans_d_mannose_mgk <= v_rfl['EX_cpd00138_e0']

    trans_d_fructose_mgk_balance = Equation(container=cowmunity, name='trans_d_fructose_mgk_balance', description="Balance for D-fructose transfer to M. Gottschalkii")
    trans_d_fructose_mgk_balance[...] = trans_d_fructose_mgk <= v_rfl['EX_cpd00082_e0']

    trans_tetrathionate_mgk_balance = Equation(container=cowmunity, name='trans_tetrathionate_mgk_balance', description="Balance for tetrathionate transfer to M. Gottschalkii")
    trans_tetrathionate_mgk_balance[...] = trans_tetrathionate_mgk <= v_rfl['EX_cpd01414_e0']

    trans_thiosulfate_mgk_balance = Equation(container=cowmunity, name='trans_thiosulfate_mgk_balance', description="Balance for thiosulfate transfer to M. Gottschalkii")
    trans_thiosulfate_mgk_balance[...] = trans_thiosulfate_mgk <= v_prm['EX_cpd00268_e0']

    trans_cellulose_prm_balance = Equation(container=cowmunity, name='trans_cellulose_prm_balance', description="Balance for cellulose transfer to P. ruminicola")
    trans_cellulose_prm_balance[...] = trans_cellulose_prm <= v_rfl['EX_cpd11746_e0']

    trans_d_glucose_prm_balance = Equation(container=cowmunity, name='trans_d_glucose_prm_balance', description="Balance for D-glucose transfer to P. ruminicola")
    trans_d_glucose_prm_balance[...] = trans_d_glucose_prm <= v_rfl['EX_cpd00027_e0']

    trans_acetate_prm_balance = Equation(container=cowmunity, name='trans_acetate_prm_balance', description="Balance for acetate transfer to P. ruminicola")
    trans_acetate_prm_balance[...] = trans_acetate_prm <= v_rfl['EX_cpd00029_e0']

    trans_l_arabinose_prm_balance = Equation(container=cowmunity, name='trans_l_arabinose_prm_balance', description="Balance for L-arabinose transfer to P. ruminicola")
    trans_l_arabinose_prm_balance[...] = trans_l_arabinose_prm <= v_rfl['EX_cpd00224_e0']

    trans_biotin_prm_balance = Equation(container=cowmunity, name='trans_biotin_prm_balance', description="Balance for biotin transfer to P. ruminicola")
    trans_biotin_prm_balance[...] = trans_biotin_prm <= v_rfl['EX_cpd00104_e0']

    trans_thiamin_prm_balance = Equation(container=cowmunity, name='trans_thiamin_prm_balance', description="Balance for thiamin transfer to P. ruminicola")
    trans_thiamin_prm_balance[...] = trans_thiamin_prm <= v_rfl['EX_cpd00305_e0']

    trans_octadecenoate_prm_balance = Equation(container=cowmunity, name='trans_octadecenoate_prm_balance', description="Balance for octadecenoate transfer to P. ruminicola")
    trans_octadecenoate_prm_balance[...] = trans_octadecenoate_prm <= v_rfl['EX_cpd15269_e0'] + v_mgk['EX_cpd15269_e0']

    trans_maltoheptaose_prm_balance = Equation(container=cowmunity, name='trans_maltoheptaose_prm_balance', description="Balance for maltoheptaose transfer to P. ruminicola")
    trans_maltoheptaose_prm_balance[...] = trans_maltoheptaose_prm <= v_rfl['EX_cpd15494_e0']

    trans_nitrite_prm_balance = Equation(container=cowmunity, name='trans_nitrite_prm_balance', description="Balance for nitrite transfer to P. ruminicola")
    trans_nitrite_prm_balance[...] = trans_nitrite_prm <= v_mgk['EX_cpd00075_e0']

    trans_n_acetyl_d_glucosamine_prm_balance = Equation(container=cowmunity, name='trans_n_acetyl_d_glucosamine_prm_balance', description="Balance for N-acetyl-D-glucosamine transfer to P. ruminicola")
    trans_n_acetyl_d_glucosamine_prm_balance[...] = trans_n_acetyl_d_glucosamine_prm <= v_mgk['EX_cpd00122_e0']

    trans_aminoethanol_prm_balance = Equation(container=cowmunity, name='trans_aminoethanol_prm_balance', description="Balance for aminoethanol transfer to P. ruminicola")
    trans_aminoethanol_prm_balance[...] = trans_aminoethanol_prm <= v_mgk['EX_cpd00162_e0']

    trans_cobinamide_prm_balance = Equation(container=cowmunity, name='trans_cobinamide_prm_balance', description="Balance for cobinamide transfer to P. ruminicola")
    trans_cobinamide_prm_balance[...] = trans_cobinamide_prm <= v_mgk['EX_cpd03422_e0']

    trans_alanine_prm_balance = Equation(container=cowmunity, name='trans_alanine_prm_balance', description="Balance for alanine transfer to P. ruminicola")
    trans_alanine_prm_balance[...] = trans_alanine_prm <= v_mgk['EX_cpd00035_e0']

    trans_leucine_prm_balance = Equation(container=cowmunity, name='trans_leucine_prm_balance', description="Balance for leucine transfer to P. ruminicola")
    trans_leucine_prm_balance[...] = trans_leucine_prm <= v_mgk['EX_cpd00107_e0']

    trans_glycine_prm_balance = Equation(container=cowmunity, name='trans_glycine_prm_balance', description="Balance for glycine transfer to P. ruminicola")
    trans_glycine_prm_balance[...] = trans_glycine_prm <= v_mgk['EX_cpd00033_e0']

    trans_proline_prm_balance = Equation(container=cowmunity, name='trans_proline_prm_balance', description="Balance for proline transfer to P. ruminicola")
    trans_proline_prm_balance[...] = trans_proline_prm <= v_mgk['EX_cpd00129_e0']

    trans_d_galacturonate_rfl_balance = Equation(container=cowmunity, name='trans_d_galacturonate_rfl_balance', description="Balance for D-galacturonate transfer to R. flavefaciens")
    trans_d_galacturonate_rfl_balance[...] = trans_d_galacturonate_rfl <= v_prm['EX_cpd00280_e0']

    trans_deoxyadenosine_rfl_balance = Equation(container=cowmunity, name='trans_deoxyadenosine_rfl_balance', description="Balance for deoxyadenosine transfer to R. flavefaciens")
    trans_deoxyadenosine_rfl_balance[...] = trans_deoxyadenosine_rfl <= v_prm['EX_cpd00438_e0']

    trans_dephospho_coa_rfl_balance = Equation(container=cowmunity, name='trans_dephospho_coa_rfl_balance', description="Balance for dephospho-CoA transfer to R. flavefaciens")
    trans_dephospho_coa_rfl_balance[...] = trans_dephospho_coa_rfl <= v_mgk['EX_cpd00655_e0']

    trans_cobinamide_rfl_balance = Equation(container=cowmunity, name='trans_cobinamide_rfl_balance', description="Balance for cobinamide transfer to R. flavefaciens")
    trans_cobinamide_rfl_balance[...] = trans_cobinamide_rfl <= v_mgk['EX_cpd03422_e0']

    trans_alanine_rfl_balance = Equation(container=cowmunity, name='trans_alanine_rfl_balance', description="Balance for alanine transfer to R. flavefaciens")
    trans_alanine_rfl_balance[...] = trans_alanine_rfl <= v_mgk['EX_cpd00035_e0']

    trans_leucine_rfl_balance = Equation(container=cowmunity, name='trans_leucine_rfl_balance', description="Balance for leucine transfer to R. flavefaciens")
    trans_leucine_rfl_balance[...] = trans_leucine_rfl <= v_mgk['EX_cpd00107_e0']

    trans_glycine_rfl_balance = Equation(container=cowmunity, name='trans_glycine_rfl_balance', description="Balance for glycine transfer to R. flavefaciens")
    trans_glycine_rfl_balance[...] = trans_glycine_rfl <= v_mgk['EX_cpd00033_e0']

    trans_proline_rfl_balance = Equation(container=cowmunity, name='trans_proline_rfl_balance', description="Balance for proline transfer to R. flavefaciens")
    trans_proline_rfl_balance[...] = trans_proline_rfl <= v_mgk['EX_cpd00129_e0']

    trans_aminoethanol_rfl_balance = Equation(container=cowmunity, name='trans_aminoethanol_rfl_balance', description="Balance for aminoethanol transfer to R. flavefaciens")
    trans_aminoethanol_rfl_balance[...] = trans_aminoethanol_rfl <= v_mgk['EX_cpd00162_e0']

    overall_cobinamide_balance = Equation(container=cowmunity, name='overall_cobinamide_balance', description='Balance for cobinamide transfer for both prm and rfl')
    overall_cobinamide_balance[...] = trans_cobinamide_prm + trans_cobinamide_rfl <= v_mgk['EX_cpd03422_e0']

    overall_alanine_balance = Equation(container=cowmunity, name='overall_alanine_balance', description='Balance for alanine transfer for both prm and rfl')
    overall_alanine_balance[...] = trans_alanine_prm + trans_alanine_rfl <= v_mgk['EX_cpd00035_e0']

    overall_leucine_balance = Equation(container=cowmunity, name='overall_leucine_balance', description='Balance for leucine transfer for both prm and rfl')
    overall_leucine_balance[...] = trans_leucine_prm + trans_leucine_rfl <= v_mgk['EX_cpd00107_e0']

    overall_glycine_balance = Equation(container=cowmunity, name='overall_glycine_balance', description='Balance for glycine transfer for both prm and rfl')
    overall_glycine_balance[...] = trans_glycine_prm + trans_glycine_rfl <= v_mgk['EX_cpd00033_e0']

    overall_proline_balance = Equation(container=cowmunity, name='overall_proline_balance', description='Balance for proline transfer for both prm and rfl')
    overall_proline_balance[...] = trans_proline_prm + trans_proline_rfl <= v_mgk['EX_cpd00129_e0']

    overall_aminoethanol_balance = Equation(container=cowmunity, name='overall_aminoethanol_balance', description='Balance for aminoethanol transfer for both prm and rfl')
    overall_aminoethanol_balance[...] = trans_aminoethanol_prm + trans_aminoethanol_rfl <= v_mgk['EX_cpd00162_e0']

    # adding the constraints to each model

    constraint_CO2_mgk = Equation(container=cowmunity, name="constraint_CO2_mgk", description="constraint for the uptake of CO2 to M. Gottschalkii")
    constraint_CO2_mgk[...] = trans_CO2_mgk == v_mgk['EX_cpd00011_e0']

    constraint_H2_mgk = Equation(container=cowmunity, name="constraint_H2_mgk", description="constraint for the uptake of H2 to M. Gottschalkii")
    constraint_H2_mgk[...] = trans_H2_mgk == v_mgk['EX_cpd11640_e0']

    constraint_formate_mgk = Equation(container=cowmunity, name='constraint_formate_mgk', description="constraint for the uptake of formate to M. Gottschalkii")
    constraint_formate_mgk[...] = trans_formate_mgk == v_mgk['EX_cpd00047_e0']

    constraint_acetate_mgk = Equation(container=cowmunity, name="constraint_acetate_mgk", description="constraint for the uptake of acetate to M. Gottschalkii")
    constraint_acetate_mgk[...] = trans_acetate_mgk == v_mgk['EX_cpd00029_e0']

    constraint_d_mannose_mgk = Equation(container=cowmunity, name="constraint_dmannose_mgk", description="constraint for the uptake of D-mannose to M. Gottschalkii")
    constraint_d_mannose_mgk[...] = trans_d_mannose_mgk == v_mgk['EX_cpd00138_e0']

    constraint_d_fructose_mgk = Equation(container=cowmunity, name="constraint_dfructose_mgk", description="constraint for the uptake of D-fructose to M. Gottschalkii")
    constraint_d_fructose_mgk[...] = trans_d_fructose_mgk == v_mgk['EX_cpd00082_e0']

    constraint_tetrathionate_mgk = Equation(container=cowmunity, name="constraint_tetrathionate_mgk", description="constraint for the uptake of tetrathionate to M. Gottschalkii")
    constraint_tetrathionate_mgk[...] = trans_tetrathionate_mgk == v_mgk['EX_cpd01414_e0']

    constraint_thiosulfate_mgk = Equation(container=cowmunity, name="constraint_thiosulfate_mgk", description="constraint for the uptake of thiosulfate to M. Gottschalkii")
    constraint_thiosulfate_mgk[...] = trans_thiosulfate_mgk == v_mgk['EX_cpd00268_e0']

    constraint_cellulose_prm = Equation(container=cowmunity, name='constraint_cellulose_prm', description="constraint for the uptake of cellulose to P. ruminicola")
    constraint_cellulose_prm[...] = trans_cellulose_prm == v_prm['EX_cpd11746_e0']

    constraint_d_glucose_prm = Equation(container=cowmunity, name='constraint_d_glucose_prm', description="constraint for the uptake of D-Glucose to P. ruminicola")
    constraint_d_glucose_prm[...] = trans_d_glucose_prm == v_prm['EX_cpd00027_e0']

    constraint_acetate_prm = Equation(container=cowmunity, name='constraint_acetate_prm', description="constraint for the uptake of Acetate to P. ruminicola")
    constraint_acetate_prm[...] = trans_acetate_prm == v_prm['EX_cpd00029_e0']

    constraint_l_arabinose_prm = Equation(container=cowmunity, name='constraint_l_arabinose_prm', description="constraint for the uptake of L-Arabinose to P. ruminicola")
    constraint_l_arabinose_prm[...] = trans_l_arabinose_prm == v_prm['EX_cpd00224_e0']

    constraint_biotin_prm = Equation(container=cowmunity, name='constraint_biotin_prm', description="constraint for the uptake of Biotin to P. ruminicola")
    constraint_biotin_prm[...] = trans_biotin_prm == v_prm['EX_cpd00104_e0']

    constraint_thiamin_prm = Equation(container=cowmunity, name='constraint_thiamin_prm', description="constraint for the uptake of Thiamin to P. ruminicola")
    constraint_thiamin_prm[...] = trans_thiamin_prm == v_prm['EX_cpd00305_e0']

    constraint_octadecenoate_prm = Equation(container=cowmunity, name='constraint_octadecenoate_prm', description="constraint for the uptake of octadecenoate to P. ruminicola")
    constraint_octadecenoate_prm[...] = trans_octadecenoate_prm == v_prm['EX_cpd15269_e0']

    constraint_maltoheptaose_prm = Equation(container=cowmunity, name='constraint_maltoheptaose_prm', description="constraint for the uptake of Maltoheptaose to P. ruminicola")
    constraint_maltoheptaose_prm[...] = trans_maltoheptaose_prm == v_prm['EX_cpd15494_e0']

    constraint_nitrite_prm = Equation(container=cowmunity, name='constraint_nitrite_prm', description="constraint for the uptake of Nitrite to P. ruminicola")
    constraint_nitrite_prm[...] = trans_nitrite_prm == v_prm['EX_cpd00075_e0']

    constraint_n_acetyl_d_glucosamine_prm = Equation(container=cowmunity, name='constraint_n_acetyl_d_glucosamine_prm', description="constraint for the uptake of N-Acetyl-D-glucosamine to P. ruminicola")
    constraint_n_acetyl_d_glucosamine_prm[...] = trans_n_acetyl_d_glucosamine_prm == v_prm['EX_cpd00122_e0']

    constraint_aminoethanol_prm = Equation(container=cowmunity, name='constraint_aminoethanol_prm', description="constraint for the uptake of Aminoethanol to P. ruminicola")
    constraint_aminoethanol_prm[...] = trans_aminoethanol_prm == v_prm['EX_cpd00162_e0']

    constraint_cobinamide_prm = Equation(container=cowmunity, name='constraint_cobinamide_prm', description="constraint for the uptake of Cobinamide to P. ruminicola")
    constraint_cobinamide_prm[...] = trans_cobinamide_prm == v_prm['EX_cpd03422_e0']

    constraint_alanine_prm = Equation(container=cowmunity, name='constraint_alanine_prm', description="constraint for the uptake of Alanine to P. ruminicola")
    constraint_alanine_prm[...] = trans_alanine_prm == v_prm['EX_cpd00035_e0']

    constraint_leucine_prm = Equation(container=cowmunity, name='constraint_leucine_prm', description="constraint for the uptake of Leucine to P. ruminicola")
    constraint_leucine_prm[...] = trans_leucine_prm == v_prm['EX_cpd00107_e0']

    constraint_glycine_prm = Equation(container=cowmunity, name='constraint_glycine_prm', description="constraint for the uptake of Glycine to P. ruminicola")
    constraint_glycine_prm[...] = trans_glycine_prm == v_prm['EX_cpd00033_e0']

    constraint_proline_prm = Equation(container=cowmunity, name='constraint_proline_prm', description="constraint for the uptake of Proline to P. ruminicola")
    constraint_proline_prm[...] = trans_proline_prm == v_prm['EX_cpd00129_e0']

    constraint_d_galacturonate_rfl = Equation(container=cowmunity, name='constraint_d_galacturonate_rfl', description="constraint for the uptake of D-Galacturonate to R. flavefaciens")
    constraint_d_galacturonate_rfl[...] = trans_d_galacturonate_rfl == v_rfl['EX_cpd00280_e0']

    constraint_deoxyadenosine_rfl = Equation(container=cowmunity, name='constraint_deoxyadenosine_rfl', description="constraint for the uptake of Deoxyadenosine to R. flavefaciens")
    constraint_deoxyadenosine_rfl[...] = trans_deoxyadenosine_rfl == v_rfl['EX_cpd00438_e0']

    constraint_dephospho_coa_rfl = Equation(container=cowmunity, name='constraint_dephospho_coa_rfl', description="constraint for the uptake of Dephospho-CoA to R. flavefaciens")
    constraint_dephospho_coa_rfl[...] = trans_dephospho_coa_rfl == v_rfl['EX_cpd00655_e0']

    constraint_cobinamide_rfl = Equation(container=cowmunity, name='constraint_cobinamide_rfl', description="constraint for the uptake of Cobinamide to R. flavefaciens")
    constraint_cobinamide_rfl[...] = trans_cobinamide_rfl == v_rfl['EX_cpd03422_e0']

    constraint_alanine_rfl = Equation(container=cowmunity, name='constraint_alanine_rfl', description="constraint for the uptake of Alanine to R. flavefaciens")
    constraint_alanine_rfl[...] = trans_alanine_rfl == v_rfl['EX_cpd00035_e0']

    constraint_leucine_rfl = Equation(container=cowmunity, name='constraint_leucine_rfl', description="constraint for the uptake of Leucine to R. flavefaciens")
    constraint_leucine_rfl[...] = trans_leucine_rfl == v_rfl['EX_cpd00107_e0']

    constraint_glycine_rfl = Equation(container=cowmunity, name='constraint_glycine_rfl', description="constraint for the uptake of Glycine to R. flavefaciens")
    constraint_glycine_rfl[...] = trans_glycine_rfl == v_rfl['EX_cpd00033_e0']

    constraint_proline_rfl = Equation(container=cowmunity, name='constraint_proline_rfl', description="constraint for the uptake of Proline to R. flavefaciens")
    constraint_proline_rfl[...] = trans_proline_rfl == v_rfl['EX_cpd00129_e0']

    constraint_aminoethanol_rfl = Equation(container=cowmunity, name='constraint_aminoethanol_rfl', description="constraint for the uptake of Aminoethanol to R. flavefaciens")
    constraint_aminoethanol_rfl[...] = trans_aminoethanol_rfl == v_rfl['EX_cpd00162_e0']

    # mass balance equations

    mgk_mass_balance = Equation(container=cowmunity, name='mgk_mass_balance', domain=i_mgk, description='overall mass balance for mgk')
    mgk_mass_balance[i_mgk] = Sum(j_mgk, S_mgk[j_mgk, i_mgk] * v_mgk[j_mgk]) == 0

    prm_mass_balance = Equation(container=cowmunity, name='prm_mass_balance', domain=i_prm, description='overall mass balance for prm')
    prm_mass_balance[i_prm] = Sum(j_prm, S_prm[j_prm, i_prm] * v_prm[j_prm]) == 0

    rfl_mass_balance = Equation(container=cowmunity, name='rfl_mass_balance', domain=i_rfl, description='overall mass balance for rfl')
    rfl_mass_balance[i_rfl] = Sum(j_rfl, S_rfl[j_rfl, i_rfl] * v_rfl[j_rfl]) == 0

    # dual problem constraint equations

    mgk_dual_constraint = Equation(container=cowmunity, name="mgk_dual_constraint", domain=j_mgk, description="Dual constraint for MGK")
    mgk_dual_constraint[j_mgk] = Sum(i_mgk, lambda_mgk[i_mgk] * S_mgk[j_mgk, i_mgk]) + \
                                muUB_mgk[j_mgk] - muLB_mgk[j_mgk] == 0

    prm_dual_constraint = Equation(container=cowmunity, name="prm_dual_constraint", domain=j_prm, description="Dual constraint for PRM")
    prm_dual_constraint[j_prm] = Sum(i_prm, lambda_prm[i_prm] * S_prm[j_prm, i_prm]) + \
                                muUB_prm[j_prm] - muLB_prm[j_prm] == 0

    rfl_dual_constraint = Equation(container=cowmunity, name="rfl_dual_constraint", domain=j_rfl, description="Dual constraint for RFL")
    rfl_dual_constraint[j_rfl] = Sum(i_rfl, lambda_rfl[i_rfl] * S_rfl[j_rfl, i_rfl]) + \
                                muUB_rfl[j_rfl] - muLB_rfl[j_rfl] == 0

def FixSBMLs():
    print("Fixing SBML files...")

    def add_reaction(file_name, metabolite_code, metabolite_name, charge=0):
        # Define the SBML document and model
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{file_name}')
        model = document.getModel()

        # Check if the cytosol species already exists
        species_id = f'M_{metabolite_code}_c0'
        if model.getSpecies(species_id) is None:
            species = model.createSpecies()
            species.setId(species_id)
            species.setCompartment('c0')
            species.setName(f'{metabolite_name}[c0]')
            species.setCharge(charge)
            species.setBoundaryCondition(False)

        cytosol_species = model.getSpecies(species_id)

        # create the extracellular species
        species = model.createSpecies()
        species.setId(f'M_{metabolite_code}_e0')
        species.setCompartment('e0')
        species.setName(f'{metabolite_name}[e0]')
        species.setCharge(int(cytosol_species.getCharge()))
        species.setBoundaryCondition(False)


        # Create the export/import reaction
        reaction = model.createReaction()
        reaction.setId(f'EX_{metabolite_code}_e0')
        reaction.setName(f'{metabolite_name} export/import')
        reaction.setReversible(True) # Set reversibility

        # Add reactant to the reaction
        reactant1 = reaction.createReactant()
        reactant1.setSpecies(f'M_{metabolite_code}_e0')  # Use the species ID created above
        reactant1.setStoichiometry(1)
        reactant1.setConstant(False)

        # 6. Define the kinetic law (e.g., Mass Action kinetics: k * S1)
        kinetic_law = reaction.createKineticLaw()
        # Create a parameter for the rate constant
        lb = kinetic_law.createParameter()
        lb.setId('LOWER_BOUND')
        lb.setValue(-1000)
        lb.setName('mmol_per_gDW_per_hr')
        ub = kinetic_law.createParameter()
        ub.setId('UPPER_BOUND')
        ub.setValue(1000)
        ub.setName('mmol_per_gDW_per_hr')
        obj = kinetic_law.createParameter()
        obj.setId('OBJECTIVE_COEFFICIENT')
        obj.setValue(0)
        flx = kinetic_law.createParameter()
        flx.setId('FLUX_VALUE')
        flx.setValue(0)
        flx.setName('mmol_per_gDW_per_hr')


        # Set the math for the kinetic law using MathML
        # You can use libsbml.parseL3Formula to convert from infix string to MathML AST
        math_ml_string = (
            '<math xmlns="http://www.w3.org/1998/Math/MathML">'
            '<ci> FLUX_VALUE </ci>'
            '</math>'
        )
        math_ast = libsbml.readMathMLFromString(math_ml_string)
        if math_ast:
            kinetic_law.setMath(math_ast)
        else:
            print("Error: Could not parse MathML string.")

        # create the reaction to convert from extracellular to cytosol
        transport_reaction = model.createReaction()
        transport_reaction.setId(f'R_{metabolite_code}_transport')
        transport_reaction.setName(f'{metabolite_name} transport')
        transport_reaction.setReversible(True) # Set reversibility

        # Add reactant to the reaction
        cytosol = transport_reaction.createReactant()
        cytosol.setSpecies(f'M_{metabolite_code}_c0')  # Use the species ID created above
        cytosol.setStoichiometry(1)
        cytosol.setConstant(False)

        # Add product to the reaction
        extracellular = transport_reaction.createProduct()
        extracellular.setSpecies(f'M_{metabolite_code}_e0')  # Use the species ID created above
        extracellular.setStoichiometry(1)
        extracellular.setConstant(False)

        # 6. Define the kinetic law (e.g., Mass Action kinetics: k * S1)
        kinetic_law = transport_reaction.createKineticLaw()
        # Create a parameter for the rate constant
        lb = kinetic_law.createParameter()
        lb.setId('LOWER_BOUND')
        lb.setValue(-1000)
        lb.setName('mmol_per_gDW_per_hr')
        ub = kinetic_law.createParameter()
        ub.setId('UPPER_BOUND')
        ub.setValue(1000)
        ub.setName('mmol_per_gDW_per_hr')
        obj = kinetic_law.createParameter()
        obj.setId('OBJECTIVE_COEFFICIENT')
        obj.setValue(0)
        flx = kinetic_law.createParameter()
        flx.setId('FLUX_VALUE')
        flx.setValue(0)
        flx.setName('mmol_per_gDW_per_hr')


        # Set the math for the kinetic law using MathML
        # You can use libsbml.parseL3Formula to convert from infix string to MathML AST
        math_ml_string = (
            '<math xmlns="http://www.w3.org/1998/Math/MathML">'
            '<ci> FLUX_VALUE </ci>'
            '</math>'
        )
        math_ast = libsbml.readMathMLFromString(math_ml_string)
        if math_ast:
            kinetic_law.setMath(math_ast)
        else:
            print("Error: Could not parse MathML string.")

        libsbml.writeSBMLToFile(document, f'model files/{file_name}')


    def add_version(file_name, version):
        # Define the SBML document and model
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{file_name}')
        model = document.getModel()

        # Set the version in the model's annotation
        model.setNotes(version)

        # Write the updated SBML document back to file
        libsbml.writeSBMLToFile(document, f'model files/{file_name}')

    def check_version(file_name, version):
        # Define the SBML document and model
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{file_name}')
        model = document.getModel()

        # Check if the version matches
        notes = model.getNotesString()
        return notes == f'<notes>{version}</notes>'

    version = 'v2.5'

    if check_version('M. gottschalkii.xml', version) is False:
        print('M. gottschalkii.xml is not up to date, updating...')
        add_reaction('M. gottschalkii.xml', 'cpd00035', 'L-Alanine')
        add_reaction('M. gottschalkii.xml', 'cpd00107', 'L-Leucine')
        add_reaction('M. gottschalkii.xml', 'cpd00033', 'Glycine')
        add_version('M. gottschalkii.xml', version)

    if check_version('P. ruminicola.xml', version) is False:
        print('P. ruminicola.xml is not up to date, updating...')
        add_reaction('P. ruminicola.xml', 'cpd00035', 'L-Alanine')
        add_reaction('P. ruminicola.xml', 'cpd00107', 'L-Leucine')
        add_reaction('P. ruminicola.xml', 'cpd00033', 'Glycine')
        add_reaction('P. ruminicola.xml', 'cpd11657', 'Starch')
        add_reaction('P. ruminicola.xml', 'cpd00076', 'Sucrose')
        add_reaction('P. ruminicola.xml', 'cpd00053', 'L-Glutamine')
        add_reaction('P. ruminicola.xml', 'cpd00161', 'L-Threonine')
        add_reaction('P. ruminicola.xml', 'cpd00348', 'D-Galactose 1-phosphate')
        add_reaction('P. ruminicola.xml', 'cpd00084', 'L-Cysteine')
        add_reaction('P. ruminicola.xml', 'cpd00052', 'CTP')
        add_reaction('P. ruminicola.xml', 'cpd00002', 'ATP')
        add_reaction('P. ruminicola.xml', 'cpd00062', 'UTP')
        add_reaction('P. ruminicola.xml', 'cpd00356', 'dCTP')
        add_reaction('P. ruminicola.xml', 'cpd00073', 'Urea')
        add_version('P. ruminicola.xml', version)

    if check_version('R. flavefaciens.xml', version) is False:
        print('R. flavefaciens.xml is not up to date, updating...')
        add_reaction('R. flavefaciens.xml', 'cpd00035', 'L-Alanine')
        add_reaction('R. flavefaciens.xml', 'cpd00033', 'Glycine')
        add_reaction('R. flavefaciens.xml', 'cpd00053', 'L-Glutamine')
        add_reaction('R. flavefaciens.xml', 'cpd00161', 'L-Threonine')
        add_reaction('R. flavefaciens.xml', 'cpd00348', 'D-Galactose 1-phosphate')
        add_reaction('R. flavefaciens.xml', 'cpd00084', 'L-Cysteine')
        add_reaction('R. flavefaciens.xml', 'cpd00052', 'CTP')
        add_reaction('R. flavefaciens.xml', 'cpd00002', 'ATP')
        add_reaction('R. flavefaciens.xml', 'cpd00062', 'UTP')
        add_reaction('R. flavefaciens.xml', 'cpd00356', 'dCTP')
        add_reaction('R. flavefaciens.xml', 'cpd00073', 'Urea')
        add_version('R. flavefaciens.xml', version)


    def remove_duplicate_species_and_reactions(file_name):
        # Define the SBML document and model
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{file_name}')
        model = document.getModel()

        # --- Remove Duplicate Species ---
        seen_species = []
        species_to_remove = []

        for i in range(model.getNumSpecies()):
            species = model.getSpecies(i)
            id = species.getId()

            if id in seen_species:
                species_to_remove.append(species.getId())
            else:
                seen_species.append(species.getId())

        # Remove species (iterate in reverse to avoid index issues)
        for item in reversed(species_to_remove):
            model.removeSpecies(item)

        # --- Remove Duplicate Reactions ---
        seen_reactions = [] 
        reactions_to_remove = []

        for i in range(model.getNumReactions()):
            reaction = model.getReaction(i)
            id = reaction.getId()

            if id in seen_reactions:
                reactions_to_remove.append(reaction.getId())
            else:
                seen_reactions.append(reaction.getId())

        # Remove reactions
        for reaction_id in reversed(reactions_to_remove):
            model.removeReaction(reaction_id)
        
        # Save the modified model (optional)
        writer = libsbml.SBMLWriter()
        libsbml.writeSBMLToFile(document, f'model files/{file_name}')
    
    remove_duplicate_species_and_reactions('M. gottschalkii.xml')
    remove_duplicate_species_and_reactions('P. ruminicola.xml')
    remove_duplicate_species_and_reactions('R. flavefaciens.xml')

    # removing a duplicate product that slipped through the cracks

    reader = libsbml.SBMLReader()
    document = reader.readSBML(f'model files/R. flavefaciens.xml')
    model = document.getModel()

    reaction = model.getReaction('R_R01896_c0')
    reaction.removeProduct('M_cpd00067_c0')

    writer = libsbml.SBMLWriter()
    libsbml.writeSBMLToFile(document, f'model files/R. flavefaciens.xml')

def solve(solver_name='IPOPT'):


    global model
    # Create model
    model = Model(container=cowmunity, name="COWMUNITY", equations=cowmunity.getEquations(), 
                    problem="NLP", sense=Sense.MAX, objective=objective_variable)
    
    # Set solver options
    options = Options(nlp=solver_name, equation_listing_limit=10, variable_listing_limit=10, time_limit=5, threads=0)

    # Solve the model
    print(f"Solving with {solver_name}...")
    model.solve(options=options)
    
    # check solution status
    status = model.solve_status
    if status == SolveStatus.NormalCompletion:
        print("Optimal solution found!")
    else:
        print(f"Solver terminated with status: {status}")

def extract_results():
    """Extract and store results"""
    global results
    results = {
        'objective_value': objective_variable.records['level'].iloc[0],
        'mgk_biomass': v_mgk.records.loc[v_mgk.records['j_mgk'] == 'R_biomass0', 'level'].iloc[0],
        'prm_biomass': v_prm.records.loc[v_prm.records['j_prm'] == 'R_biomass0', 'level'].iloc[0],
        'rfl_biomass': v_rfl.records.loc[v_rfl.records['j_rfl'] == 'R_biomass0', 'level'].iloc[0],
        'methane_flux' : v_mgk.records.loc[v_mgk.records['j_mgk'] == 'EX_cpd01024_e0', 'level'].iloc[0]
    }

def print_results():
    """Print results in a formatted way"""
    print()
    print("********************* RESULTS *********************")
    print(f"Total Biomass = {results['objective_value']}")
    print()
    
    print("********************* MGK *************************")
    print(f"MGK Biomass Flux = {results['mgk_biomass']}")
    print(f"Methane Emission Flux = {results['methane_flux']}")
    print()
    
    print("********************* PRM *************************")
    print(f"PRM Biomass Flux = {results['prm_biomass']}")
    print()
    
    print("********************* RFL *************************")
    print(f"RFL Biomass Flux = {results['rfl_biomass']}")
    print()

def bug_huntin():
    # This function is for debugging purposes, to check the model and variable records
    reaction = 'EX_cpd00138_e0'

    def check_reaction(reaction, file_name):
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{file_name}')
        model = document.getModel()

        reaction = model.getReaction(reaction)

        if reaction is None:
            return None
        else:
            return reaction.getId()

    if check_reaction(reaction, 'M. gottschalkii.xml') is None:
        print(f'Reaction {reaction} not found in M. gottschalkii model.')
    else:
        mgk_flux = v_mgk.records.loc[v_mgk.records['j_mgk'] == reaction, 'level'].iloc[0]
        print(f'MGK {reaction}: {mgk_flux}')
    if check_reaction(reaction, 'P. ruminicola.xml') is None:
        print(f'Reaction {reaction} not found in P. ruminicola model.')
    else:
        prm_flux = v_prm.records.loc[v_prm.records['j_prm'] == reaction, 'level'].iloc[0]
        print(f'PRM {reaction}: {prm_flux}')
    if check_reaction(reaction, 'R. flavefaciens.xml') is None:
        print(f'Reaction {reaction} not found in R. flavefaciens model.')
    else:
        rfl_flux = v_rfl.records.loc[v_rfl.records['j_rfl'] == reaction, 'level'].iloc[0]
        print(f'RFL {reaction}: {rfl_flux}')

    def flux_investigation(file_name, v_set, j_set, i_set, metabolite):

        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{file_name}')
        model = document.getModel()

        relevant_reactions = []
        for i in range(model.getNumReactions()):
            reaction = model.getReaction(i)
            product = reaction.getProduct(metabolite)
            if product is None:
                continue
            else:
                relevant_reactions.append(reaction.id)

        # species = model.getSpecies(metabolite)
        name = i_set.records.loc[i_set.records['index'] == metabolite, 'element_text'].iloc[0]
        print(file_name)
        print(f'\n*** {name} FLUXES ***')
        for item in relevant_reactions:
            flux = v_set.records.loc[v_set.records[j_set] == f'{item.strip()}', 'level'].iloc[0]
            print(f'{item} : {flux}')
    
    print()

    metabolite = 'M_cpd11640_c0'
    mgk = ('M. gottschalkii.xml', v_mgk, 'j_mgk', i_mgk)
    prm = ('P. ruminicola.xml', v_prm, 'j_prm', i_prm)
    rfl = ('R. flavefaciens.xml', v_rfl, 'j_rfl', i_rfl)

    flux_investigation(*mgk, metabolite)

    def biomass_fluxes(file_name, v_set, j_set, i_set):
        print('*'*10, file_name, '*'*10)

        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{file_name}')
        model = document.getModel()

        biomass_reactants = []
        biomass_reaction = model.getReaction('R_biomass0')
        for i in range(biomass_reaction.getNumReactants()):
            reactant = biomass_reaction.getReactant(i)
            biomass_reactants.append(reactant.getSpecies())

        precursor_reactions = {}
        for item in biomass_reactants:
            relevant_reactions = []
            for i in range(model.getNumReactions()):
                reaction = model.getReaction(i)
                product = reaction.getProduct(f'{item}')
                if product is None:
                    continue
                else:
                    relevant_reactions.append(reaction.id)
            new_entry = {item : relevant_reactions}
            precursor_reactions.update(new_entry)

        for key in precursor_reactions:
            relevant_reactions = precursor_reactions[key]
            species = biomass_reaction.getReactant(f'{key}').getSpecies()
            name = i_set.records.loc[i_set.records['index'] == species, 'element_text'].iloc[0]
            print(f'\n*** {name} FLUXES ***')
            for item in relevant_reactions:
                flux = v_set.records.loc[v_set.records[j_set] == f'{item.strip()}', 'level'].iloc[0]
                print(f'{item} : {flux}')

    # biomass_fluxes(*mgk)
    # biomass_fluxes(*prm)
    # biomass_fluxes(*rfl)

    def zero_flux_reactions(file_name, v_set, j_set, i_set):
        reader = libsbml.SBMLReader()
        document = reader.readSBML(f'model files/{file_name}')
        model = document.getModel()

        """Return a list of reaction IDs in v_set where the flux is exactly zero."""
        zero_flux_df = v_set.records.loc[v_set.records['level'] == 0]
        zero_flux_list =  zero_flux_df[j_set].tolist()

        print(f'\n*** {file_name} REACTIONS WITH ZERO FLUX ***')
        for item in zero_flux_list:
            precursor_reactions = {}
            needy_dict = {}
            unmade_products = []
            zero_reaction = model.getReaction(item)
            for i in range(zero_reaction.getNumProducts()):
                product = zero_reaction.getProduct(i)
                unmade_products.append(product.getSpecies())
            print(f'\n{item}')
            for item in unmade_products:
                relevant_reactions = []
                needy_reactions = []
                for i in range(model.getNumReactions()):
                    reaction = model.getReaction(i)
                    product = reaction.getProduct(f'{item}')
                    if product is None:
                        continue
                    else:
                        relevant_reactions.append(reaction.id)
                new_entry = {item : relevant_reactions}
                precursor_reactions.update(new_entry)

                for i in range(model.getNumReactions()):
                    reaction = model.getReaction(i)
                    reactant = reaction.getReactant(f'{item}')
                    if reactant is None:
                        continue
                    else:
                        needy_reactions.append(reaction.id)
                new_entry = {item : relevant_reactions}
                precursor_reactions.update(new_entry)
                new_entry = {item : needy_reactions}
                needy_dict.update(new_entry)

            for key in precursor_reactions:
                relevant_reactions = precursor_reactions[key]
                product = zero_reaction.getProduct(f'{key}')
                species = product.getSpecies()
                name = i_set.records.loc[i_set.records['index'] == species, 'element_text'].iloc[0]
                print(f'Reactions that produce {name} ({species}):')
                for item in relevant_reactions:
                    flux = v_set.records.loc[v_set.records[j_set] == f'{item.strip()}', 'level'].iloc[0]
                    print(f'{item} : {flux}')
                print(f'Reactions that require {name} ({species}):')
                for item in needy_reactions:
                    flux = v_set.records.loc[v_set.records[j_set] == f'{item.strip()}', 'level'].iloc[0]
                    print(f'{item} : {flux}')

        

    zero_flux_reactions(*mgk)
    zero_flux_reactions(*prm)
    zero_flux_reactions(*rfl)
    
    





