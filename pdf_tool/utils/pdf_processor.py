import pdfplumber
import pandas as pd


def convert_pdf_to_template_excel(pdf_path):

    data = {}

    # ------------------ PDF READ ------------------
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")

            for line in lines:
                line = line.strip()

                # ----------- KEY VALUE EXTRACTION ------------

                if "Audit Ref" in line or "Audit Reference" in line:
                    data["audit ref"] = line.split(":")[-1].strip()

                elif "Audited Facility" in line:
                    data["audited facility"] = line.split(":")[-1].strip()

                elif "Overall Audit Score" in line:
                    data["overall audit score"] = line.split(":")[-1].strip()

                elif "Site Name" in line:
                    data["site name"] = line.split(":")[-1].strip()

                elif "Address" in line:
                    data["address"] = line.split(":")[-1].strip()

                elif "Country" in line:
                    data["country"] = line.split(":")[-1].strip()
                

    print("🔥 PDF DATA:", data)

    # ------------------ TEMPLATE LOAD ------------------
    template_path = "static/template/template.xlsx"
    template_df = pd.read_excel(template_path)

    # ------------------ MAPPING ------------------
    mapping = {
        "Audit Reference Number": ["audit ref"],
        "Audited Facility": ["audited facility"],
        "Overall Audit Score": ["overall audit score"],
        "Site Name": ["site name"],
        "Site Address": ["address"],
        "Country": ["country"],
    }

    # ------------------ FILL TEMPLATE ------------------
    for i, row in template_df.iterrows():
        field = str(row["Data Field"]).strip()

        if field in mapping:
            for keyword in mapping[field]:
                if keyword in data:
                    template_df.at[i, "Answer"] = data[keyword]

    # ------------------ SAVE FILE ------------------
    output_path = pdf_path.replace(".pdf", "_final.xlsx")
    template_df.to_excel(output_path, index=False)

    return output_path
