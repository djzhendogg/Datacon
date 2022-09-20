import xlsxwriter
import pandas as pd
import os
import numpy as np
from pymatgen.core import Composition


# functions for processing the original databases
def db1():
    # upload data
    raw_data = pd.read_excel("https://raw.githubusercontent.com/nikolaichem/datacon_hackathon/main/Database_1.xlsx")
    col_ls = raw_data.columns

    # clean the df
    raw_data[col_ls[1]].replace(to_replace="cobalt", value="Co")
    raw_data[col_ls[1]].replace(to_replace="Iron", value="Fe")
    raw_data.drop(raw_data[raw_data[col_ls[2]] == "Co"].index, inplace=True)
    raw_data.drop(raw_data[raw_data[col_ls[2]] == "Fe"].index, inplace=True)
    raw_data[col_ls[2]] = raw_data[col_ls[2]].fillna(method="bfill", limit=1)
    raw_data[col_ls[7]] = raw_data[col_ls[7]].fillna(method="ffill", limit=1)
    raw_data["Ionic radius"] = raw_data["Ionic radius"].fillna(method="bfill", limit=1)
    raw_data["Hydro size (nm)"] = raw_data["Hydro size (nm)"].fillna(method="bfill", limit=1)
    raw_data[col_ls[9]] = raw_data[col_ls[9]] * 10 ** (-3)
    raw_data.rename(columns={"Material type": "Material", "Exposure dose (ug/mL)": "Concentration (g/L)",
                             "Core size (nm)": "Core_size (nm)", "Hydro size (nm)": "Diameter (nm)",
                             "Surface charge (mV)": "Surface_Charge (mV)", "Cell type": "Cell_type"}, inplace=True)
    raw_data[col_ls[11]] = raw_data[col_ls[11]].fillna(method="bfill", limit=1)
    raw_data[col_ls[13]] = raw_data[col_ls[13]].fillna(method="ffill", limit=1)
    raw_data[col_ls[15]] = raw_data[col_ls[15]].fillna(method="bfill", limit=1)
    raw_data.drop(raw_data[raw_data[col_ls[20]] == 50200.0].index, inplace=True)
    raw_data["Density (g/cm3)"] = raw_data["Density (g/cm3)"] * 10 ** (-3)
    raw_data.rename(columns={"Density (g/cm3)": "Density (g/L)"}, inplace=True)
    data = raw_data.drop(raw_data[raw_data[col_ls[20]] < 0].index)
    data.drop(["a (Å)", "b (Å)", "c (Å)", "α (°)", "β (°)", "γ (°)"], axis=1, inplace=True)
    data = data.sort_values(by="Material", ignore_index=True)
    data = data.reindex(copy=False)

    # save processed data
    data.to_excel(str(os.getcwd() + "/processed_db1.xlsx"))


def db2():
    # upload data
    raw_df = pd.read_excel("https://raw.githubusercontent.com/nikolaichem/datacon_hackathon/main/Database_2.xlsx",
                           header=0)
    col_ls = raw_df.columns

    # remove edge spaces in string
    def stripper(column: pd.Series, col_name="col_name"):
        ls = column.tolist()
        try:
            str_ls = [str(i).strip() for i in ls]
            return pd.Series(np.array(str_ls), name=col_name)
        except:
            return column

    # remove strange symbols
    def encoding_remover(column: pd.Series, col_name="col_name"):
        ls = column.tolist()
        good_ls = [str(i).replace("\xad", "-") for i in ls]
        best_ls = [str(i).replace("\xa0", "") for i in good_ls]
        return pd.Series(np.array(best_ls), name=col_name)

    # skip the difference in register
    def lower(column: pd.Series, col_name="col_name"):
        ls = column.tolist()
        try:
            n_ls = [i.lower() for i in ls]
            return pd.Series(np.array(n_ls), name=col_name)
        except:
            return column

    # to change the units of co
    def change_concentr(form_ser: pd.Series, conc_ser: pd.Series, drop_form):
        form_ls = form_ser.tolist()
        conc_ls = conc_ser.tolist()
        n_ls = []
        for i in range(len(form_ls)):
            if form_ls[i] in drop_form:
                n_ls.append(np.nan)
            else:
                particle = Composition(form_ls[i])
                conc = conc_ls[i] * particle.weight * 10 ** (-6)
                n_ls.append(conc)
        return pd.Series(np.array(n_ls), name="Concentration (g/L)")

    formula_replace = {"Copper oxide": "CuO", "Zinc oxide": "ZnO", "Copper Oxide": "CuO",
                       "Hydroxyapatite": "Ca5(PO4)3OH", "Iron oxide": "Fe3O4", "Chitosan": "C56H103N9O39",
                       "QDs": "C9H15N3O6", "Polystyrene": "C8H8", "HAP": "C5H5N5O", "SLN": "C23H40N2O18"}

    for key, form in formula_replace.items():
        raw_df.Nanoparticle.replace(to_replace=key, value=form, inplace=True)

    raw_df[col_ls[1]] = np.array([str(i).replace("0", "O") for i in raw_df[col_ls[1]].tolist()])

    for i in col_ls: raw_df[i] = encoding_remover(raw_df[i], i)
    for i in col_ls: raw_df[i] = stripper(raw_df[i], i)
    for i in col_ls: raw_df[i] = raw_df[i].replace(["nan"], np.nan)

    raw_df["coat"] = raw_df["coat"].fillna(0)
    # raw_df.coat.replace(to_replace="nan", value=0, inplace=True)
    drop_o = raw_df[raw_df.Nanoparticle == "O"].index
    raw_df.drop(drop_o, inplace=True)
    raw_df.drop(raw_df[raw_df["Diameter (nm)"] == "Hyaluronic acid"].index, inplace=True)
    raw_df.coat.replace(to_replace="cysteamine (NH2)", value="cysteamine", inplace=True)
    # fill NaN in the column
    raw_df["Cell line (L)/primary cells (P)"] = raw_df["Cell line (L)/primary cells (P)"].fillna(0)
    raw_df["Animal?"].replace(to_replace="Mice", value="Mouse", inplace=True)
    raw_df["Animal?"].replace(to_replace="rat", value="Rat", inplace=True)

    # fill NaN in the column
    raw_df["Animal?"] = raw_df["Animal?"].fillna("Human")
    # raw_df["Animal?"].replace(to_replace="nan", value="Human")
    r_an = raw_df["Animal?"].to_list()
    check_an = raw_df["Human(H)/Animal(A) cells"].tolist()
    for i in range(len(r_an)): r_an[i] = r_an[i].replace("Human", "0") if not check_an[i] == "H" else r_an[i]
    raw_df["Animal?"] = np.array(r_an)

    # drop a mess
    drop_cm = [i for i in raw_df[raw_df["Cell morphology"] == "Rat"].index]
    raw_df = raw_df.drop(drop_cm)
    drop_cm = [i for i in raw_df[raw_df["Cell morphology"] == "Mouse"].index]
    raw_df.drop(drop_cm, inplace=True)

    # fill NaN with neighbours
    raw_df["Cell morphology"] = raw_df["Cell morphology"].fillna(method="bfill", limit=1)
    raw_df["Cell age: embryonic (E), Adult (A)"] = raw_df["Cell age: embryonic (E), Adult (A)"].fillna(method="bfill",
                                                                                                       limit=1)

    raw_df["Cell-organ/tissue source"] = lower(raw_df["Cell-organ/tissue source"], col_name="Cell-organ/tissue source")

    raw_df["Test"] = raw_df["Test"].fillna("0")

    raw_df["Test indicator"] = raw_df["Test indicator"].fillna(method="bfill", limit=1)

    # for escaping problems with different registers of the same words
    raw_df["Test indicator"] = lower(raw_df["Test indicator"], col_name="Test indicator")
    raw_df["Cell-organ/tissue source"] = lower(raw_df["Cell-organ/tissue source"], col_name="Cell-organ/tissue source")

    raw_df["Biochemical metric"] = raw_df["Biochemical metric"].fillna(method="bfill", limit=1)

    raw_df[col_ls[3]] = raw_df[col_ls[3]].astype("float64")
    raw_df[col_ls[4]] = raw_df[col_ls[4]].astype("float64")
    raw_df[col_ls[13]] = raw_df[col_ls[13]].astype("int64")
    raw_df[col_ls[17]] = raw_df[col_ls[17]].astype("float64")

    # uploading molecular weight to change the units of concentration
    out_formula = {"SWCNT", "QD", "PTFE-PMMA", "PLGA", "MWCNT", "Eudragit RL",
                   "Dendrimer", "Liposomes", "Diamond",
                   "Carbon NP", "Carbon Nanotubes"}

    raw_df["Concentration μM"] = change_concentr(raw_df.Nanoparticle, raw_df["Concentration μM"], out_formula)
    raw_df.rename(columns={"Concentration μM": "Concentration (g/L)"}, inplace=True)

    data = raw_df.drop(raw_df[raw_df["% Cell viability"] < 0].index)
    data.drop(["Reference DOI", "Publication year"], axis=1, inplace=True)

    data.rename(columns={"Nanoparticle": "Material", "Type: Organic (O)/inorganic (I)": "Type", "coat": "Coat",
                         "Zeta potential (mV)": "Surface_Charge (mV)", "Cells": "Cell_type",
                         "Cell line (L)/primary cells (P)": "Line_Primary_Cell",
                         "Human(H)/Animal(A) cells": "Human_Animal", "Animal?": "Animal",
                         "Cell morphology": "Cell_morphology",
                         "Cell age: embryonic (E), Adult (A)": "Cell_age",
                         "Cell-organ/tissue source": "Cell_organ", "Exposure time (h)": "Time (h)",
                         "Test indicator": "Test_indicator", "% Cell viability": "Viability (%)"}, inplace=True)
    data = data.sort_values(by="Material", ignore_index=True)
    data = data.reindex(copy=False)
    data.to_excel(str(os.getcwd() + "/processed_db2.xlsx"))


def db3():
    Database_3 = "https://raw.githubusercontent.com/nikolaichem/datacon_hackathon/main/Database_3.xlsx"

    raw_data = pd.read_excel(Database_3, header=0)

    raw_data.drop(
        ["No", "Year", "DOI", "PDI",
         "Article_ID", "Aspect_Ratio", "Zeta_in_Water (mV)", "Zeta_in_Medium (mV)", "Surface_Charge",
         "Size_in_Water (nm)",
         "Size_in_Medium (nm)"],
        axis=1, inplace=True)

    col_ls = raw_data.columns
    raw_data = raw_data.sort_values(by=col_ls[0], ignore_index=True)
    raw_data[col_ls[4]] = raw_data[col_ls[4]].fillna(method="bfill", limit=1)
    raw_data.Material.replace(to_replace="Dendrmer", value="Dendrimer", inplace=True)
    raw_data.Material.replace(to_replace="Chitosan", value="C56H103N9O39", inplace=True)
    raw_data.Shape.replace(to_replace="Sphee", value="Sphere", inplace=True)
    raw_data.Cell_Tissue.replace(to_replace="SubcutaneousConnectiveTissue", value="Connective Tissue", inplace=True)
    raw_data.Type.replace(to_replace=0, value="O", inplace=True)

    raw_data.rename(columns={"Time (hr)": "Time (h)", "Concentration (ug/ml)": "Concentration (g/L)",
                             "Coat/Functional Group": "Coat", "Cell_Source": "Animal", "Cell_Tissue": "Cell_organ",
                             "Cell_Morphology": "Cell_morphology", "Cell_Age": "Cell_age",
                             "Cell Line_Primary Cell": "Line_Primary_Cell", "Test_Indicator": "Test_indicator",
                             "Cell_Viability (%)": "Viability (%)",
                             "Cell_Type": "Cell_type"}, inplace=True)

    raw_data["Concentration (g/L)"] = raw_data["Concentration (g/L)"] * 10 ** (-3)
    raw_data.Coat.fillna(0, inplace=True)
    raw_data.Coat.replace(to_replace="None", value=0, inplace=True)
    data = raw_data.copy()
    data.to_excel(str(os.getcwd() + "/processed_db3.xlsx"))


def db4():
    Database_4 = "https://raw.githubusercontent.com/nikolaichem/datacon_hackathon/main/Database_4.xlsx"
    raw_data = pd.read_excel(Database_4, header=0)
    raw_data = raw_data.sort_values(by="Elements", ignore_index=True)
    col_ls = raw_data.columns
    raw_data[col_ls[0]] = raw_data[col_ls[0]].replace(["don't remember"], "ZnO")
    raw_data[col_ls[9]] = raw_data[col_ls[9]].interpolate(method="linear", limit_direction="both")  # среднее между
    # соседями
    cols_with_nan = [0, 4, 5, 6, 7, 10, 11]
    for i in cols_with_nan:
        raw_data[col_ls[i]] = raw_data[col_ls[i]].fillna(method="bfill", limit=1)
    raw_data["Exposure dose (ug/mL)"] = raw_data["Exposure dose (ug/mL)"] * 10 ** (-3)
    data = raw_data.copy()
    data.drop(["a (Å)", "b (Å)", "c (Å)", "α (°)", "β (°)", "γ (°)", "Density (g/cm3)"], axis=1, inplace=True)
    data = data.sort_values(by=col_ls[0], ignore_index=True)
    data = data.reindex(copy=False)
    data.rename(columns={"Material type": "Material", "Core size (nm)": "Core_size (nm)",
                         "Hydro size (nm)": "Diameter (nm)", "Surface charge (mV)": "Surface_Charge (mV)",
                         "Cell type": "Cell_type", "Exposure dose (ug/mL)": "Concentration (g/L)"
                         }, inplace=True)
    data.to_excel(str(os.getcwd() + "/processed_db4.xlsx"))


def db5():
    Database_5 = "https://raw.githubusercontent.com/nikolaichem/datacon_hackathon/main/Database_5.xlsx"
    database_5 = pd.read_excel(Database_5, header=0)
    database_5.rename(columns={"material": "Material", "core_size": "Core_size (nm)", "hydro_size": "Diameter (nm)",
                               "surf_charge": "Surface_Charge (mV)", "surf_area": "Surface area (m2/g)",
                               "cell_line": "Cell_type", "cell_species": "Animal", "cell_origin": "Cell_organ",
                               "cell_type": "Cell_type", "time": "Time (h)", "viability": "Viability (%)"},
                      inplace=True)

    database_5.drop(["dose"], axis=1, inplace=True)
    database_5 = database_5.sort_values(by="Material", ignore_index=True)
    col_ls = database_5.columns
    cols_with_nan = [1, 3, 5]
    for i in cols_with_nan:
        database_5[col_ls[i]] = database_5[col_ls[i]].fillna(method="bfill", limit=1)
    database_5.to_excel(str(os.getcwd() + "/processed_db5.xlsx"))

# process all dataframes
db1()
print("db1 complete")
db2()
print("db2 complete")
db3()
print("db3 complete")
db4()
print("db4 complete")
db5()
print("db5 complete")

headers_1, headers_2, headers_3, headers_4, headers_5 = [], [], [], [], []

with pd.ExcelFile("processed_db1.xlsx") as xls:
    df1 = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    for i in df1:
        headers_1.append(i)
with pd.ExcelFile("processed_db2.xlsx") as xls:
    df2 = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    for i in df2:
        headers_2.append(i)
with pd.ExcelFile("processed_db3.xlsx") as xls:
    df3 = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    for i in df3:
        headers_3.append(i)
with pd.ExcelFile("processed_db4.xlsx") as xls:
    df4 = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    for i in df4:
        headers_4.append(i)
with pd.ExcelFile("processed_db5.xlsx") as xls:
    df5 = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    for i in df5:
        headers_5.append(i)
xls.close()

output_1 = {}
line = []
for i in range(len(headers_1)):
    for j in range(len(df1[headers_1[i]])):
        line.append(df1[headers_1[i]][j])
    output_1[headers_1[i]] = line
    line = []

output_2 = {}
line = []
for i in range(len(headers_2)):
    for j in range(len(df2[headers_2[i]])):
        line.append(df2[headers_2[i]][j])
    output_2[headers_2[i]] = line
    line = []

output_3 = {}
line = []
for i in range(len(headers_3)):
    for j in range(len(df3[headers_3[i]])):
        line.append(df3[headers_3[i]][j])
    output_3[headers_3[i]] = line
    line = []

output_4 = {}
line = []
for i in range(len(headers_4)):
    for j in range(len(df4[headers_4[i]])):
        line.append(df4[headers_4[i]][j])
    output_4[headers_4[i]] = line
    line = []

output_5 = {}
line = []
for i in range(len(headers_5)):
    for j in range(len(df5[headers_5[i]])):
        line.append(df5[headers_5[i]][j])
    output_5[headers_5[i]] = line
    line = []

# create general database as a concatenation of all databases
workbook = xlsxwriter.Workbook("general_db.xlsx")
worksheet = workbook.add_worksheet()

headers_done = []
for i in range(len(headers_1) - 1):
    worksheet.write(0, i, headers_1[i + 1])
    if headers_1[i + 1] not in headers_done:
        headers_done.append(headers_1[i + 1])
    for j in range(len(output_1[headers_1[i + 1]])):
        worksheet.write(j + 1, i, str(output_1[headers_1[i + 1]][j]))

for i in range(len(headers_2) - 1):
    if headers_2[i + 1] not in headers_done:
        worksheet.write(0, len(headers_done), headers_2[i + 1])
        headers_done.append(headers_2[i + 1])
    for j in range(len(output_2[headers_2[i + 1]])):
        worksheet.write(j + 489, headers_done.index(headers_2[i + 1]), str(output_2[headers_2[i + 1]][j]))

for i in range(len(headers_3) - 1):
    if headers_3[i + 1] not in headers_done:
        worksheet.write(0, len(headers_done), headers_3[i + 1])
        headers_done.append(headers_3[i + 1])
    for j in range(len(output_3[headers_3[i + 1]])):
        worksheet.write(j + 3373, headers_done.index(headers_3[i + 1]), str(output_3[headers_3[i + 1]][j]))

for i in range(len(headers_4) - 1):
    if headers_4[i + 1] not in headers_done:
        worksheet.write(0, len(headers_done), headers_4[i + 1])
        headers_done.append(headers_4[i + 1])
    for j in range(len(output_4[headers_4[i + 1]])):
        worksheet.write(j + 7484, headers_done.index(headers_4[i + 1]), str(output_4[headers_4[i + 1]][j]))

for i in range(len(headers_5) - 1):
    if headers_5[i + 1] not in headers_done:
        worksheet.write(0, len(headers_done), headers_5[i + 1])
        headers_done.append(headers_5[i + 1])
    for j in range(len(output_5[headers_5[i + 1]])):
        worksheet.write(j + 8552, headers_done.index(headers_5[i + 1]), str(output_5[headers_5[i + 1]][j]))

print("General db complete")
workbook.close()
