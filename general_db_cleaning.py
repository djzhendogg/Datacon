import os
import pandas as pd
from pymatgen.core import Composition
from pymatgen.core.periodic_table import ElementBase, Element
from pymatgen.core.ion import Ion

Result = "https://raw.githubusercontent.com/nikolaichem/datacon_hackathon/main/general_db.xlsx"

result = pd.read_excel(Result, header=0)
col_ls = result.columns


result = result.sort_values(by='Material', ignore_index=True)
# # удалила нерепрезентативные
result.drop(["Number of atoms", "Type", "Biochemical metric", "Positive control (Y/N)", "Particle ID", 'Human_Animal'],
            axis=1, inplace=True)
# # удалила строчки с пропушенные для Coat
#  Line_Primary_Cell  Animal Cell_morphology Cell_age Cell_organ Time (h) Test  Test_indicator
# # мы их врядли вытащим с pymatgen
result = result.drop(result[result['Coat'].isna() == True].index)
result = result.drop(result[result['Diameter (nm)'].isna() == True].index)
result = result.drop(result[result['Concentration (g/L)'].isna() == True].index)
result = result.reset_index(drop=True)
result["Animal"] = result["Animal"].fillna(method="bfill", limit=1)
# # удалила Interference checked (Y/N) Colloidal stability checked (Y/N)
# Shape Synthesis_Method No_of_Cells (cells/well)    , мы их не выведем
result.drop(['Interference checked (Y/N)', 'Colloidal stability checked (Y/N)', 'Shape', 'Synthesis_Method',
             'No_of_Cells (cells/well)'], axis=1, inplace=True)
# незаполняемое говно
result.drop(['Core_size (nm)', 'toxicity', 'Surface_Charge (mV)', 'Surface area (m2/g)', 'Cell_type.1',
             'Topological polar surface area (Å²)'], axis=1, inplace=True)

# непонятные названия элиментов минус
drop_cols = ['Eudragit RL', 'Dendrimer', 'Eudragit RL', 'EudragitRL', 'Liposomes', 'Polystyrene', 'QD', 'SLN', 'SWCNT',
             'PLGA', 'PTFE-PMMA', 'HAP', 'MWCNT']
for i in range(len(drop_cols)):
    drop_cm = [i for i in result[result['Material'] == drop_cols[i]].index]
    result.drop(drop_cm, inplace=True)
# замена ошибок
result[col_ls[0]] = result[col_ls[0]].replace(["Alginate"], 'C6H9NaO7')
result[col_ls[0]] = result[col_ls[0]].replace(["Carbon"], 'C')
result[col_ls[0]] = result[col_ls[0]].replace(["Carbon NP"], 'C60')
result[col_ls[0]] = result[col_ls[0]].replace(["Carbon Nanotubes"], 'C60')
result[col_ls[0]] = result[col_ls[0]].replace(["Diamond"], 'C')
result[col_ls[0]] = result[col_ls[0]].replace(["Graphite"], 'C')
result[col_ls[0]] = result[col_ls[0]].replace(["IronOide"], 'Fe3O4')
result[col_ls[0]] = result[col_ls[0]].replace(["IronOxide"], 'Fe3O4')
result[col_ls[0]] = result[col_ls[0]].replace(["Ay"], 'Au')
result = result.reset_index(drop=True)
# fill weight
materials_list = result.Material
weight = []
for i in range(len(materials_list)):
    particle_weight = Composition(materials_list[i])
    wfpy = particle_weight.weight
    weight.append(wfpy)

result.drop(['Molecular weight (g/mol)'], axis=1, inplace=True)
result['Molecular weight (g/mol)'] = weight

# fill Electronegativity
elneg = []
for i in range(len(materials_list)):
    particle = Composition(materials_list[i])
    wfpy = particle.average_electroneg
    elneg.append(wfpy)

result.drop(['Electronegativity'], axis=1, inplace=True)
result['Electronegativity'] = elneg

# fill Elements
elements = []
for i in range(len(materials_list)):
    particle = Ion(materials_list[i])
    wfpy = particle.to_reduced_dict
    res = list(wfpy.keys())[0]
    elements.append(res)

result.drop(['Elements'], axis=1, inplace=True)
result['Elements'] = elements

# fill Ionic Radii
elements_list = result.Elements
ion_rad = []
for i in range(len(elements_list)):
    particle = Element(elements_list[i])
    wfpy = particle.average_ionic_radius
    ion_rad.append(wfpy)

result.drop(['Ionic radius'], axis=1, inplace=True)
result['Ionic radius'] = ion_rad

# убираем дубликаты
result = result.drop_duplicates()
result = result.reset_index(drop=True)

# к сожалению тоже в аут
result.drop(['Density (g/L)'], axis=1, inplace=True)
result.drop(['Material'], axis=1, inplace=True)

#  перевожу котегориальные в численные
categ_disc = ['Cell_type', 'Coat', 'Line_Primary_Cell', 'Animal', 'Cell_morphology', 'Cell_age', 'Cell_organ', 'Test',
              'Elements', 'Test_indicator']
for i in categ_disc:
    result[i] = result[i].astype('category').cat.codes

result.to_excel(str(os.getcwd()) + "/final_output.xlsx")
