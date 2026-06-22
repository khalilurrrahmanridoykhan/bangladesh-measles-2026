"""
Generates the spatial epidemiology manuscript as PDF using fpdf2.
Output: spatial/Spatial_Epidemiology_Measles_Bangladesh_2026.pdf
"""

from fpdf import FPDF, XPos, YPos
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FIG  = os.path.join(BASE, "figures")
OUT  = BASE

class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(left=25, top=25, right=20)
        self.set_auto_page_break(auto=True, margin=22)
        self.add_page()

    def title_block(self):
        self.set_font("Times", "B", 15)
        self.multi_cell(0, 8,
            "Geographic Distribution and Spatial Concentration of the 2026 Measles "
            "Outbreak in Bangladesh: A Division-Level Geospatial Analysis",
            align="C")
        self.ln(4)
        self.set_font("Times", "B", 11)
        self.cell(0, 6, "Khalilur Rahman Ridoy Khan", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Times", "I", 10)
        self.cell(0, 5, "Department of Computer Science and Engineering, East West University, Dhaka, Bangladesh",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Times", "", 10)
        self.cell(0, 5, "Correspondence: khalilurrahmanridoykhan@gmail.com",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_draw_color(180, 180, 180)
        self.line(25, self.get_y(), 170, self.get_y())
        self.ln(4)

    def section(self, title):
        self.ln(4)
        self.set_font("Times", "B", 12)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def body(self, text, indent=0):
        self.set_font("Times", "", 11)
        self.set_left_margin(25 + indent)
        self.multi_cell(0, 6, text, align="J")
        self.set_left_margin(25)
        self.ln(2)

    def insert_figure(self, path, caption, w=160):
        if os.path.exists(path):
            self.ln(3)
            x = (210 - w) / 2
            self.image(path, x=x, w=w)
            self.ln(2)
            self.set_font("Times", "I", 9)
            self.multi_cell(0, 5, caption, align="C")
            self.ln(4)
        else:
            self.body(f"[Figure not found: {path}]")

    def table_row(self, cells, widths, bold=False, fill=False, fill_color=(240,240,255)):
        self.set_font("Times", "B" if bold else "", 9)
        if fill:
            self.set_fill_color(*fill_color)
        x0 = self.get_x()
        y0 = self.get_y()
        max_h = 0
        for cell, w in zip(cells, widths):
            h = 5
            self.multi_cell(w, h, str(cell), border=1, align="C", fill=fill, new_x=XPos.RIGHT, new_y=YPos.TOP)
            max_h = max(max_h, h)
        self.ln(max_h + 1)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Times", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5,
                "Spatial Epidemiology of Measles 2026 - Bangladesh | Khan KR",
                align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)
            self.line(25, self.get_y(), 190, self.get_y())
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


pdf = PDF()
pdf.title_block()

# ── ABSTRACT ─────────────────────────────────────────────────────────────────
pdf.section("Abstract")
pdf.set_font("Times", "B", 11)
pdf.set_left_margin(25)
pdf.multi_cell(0, 6,
    "Background: The 2026 measles outbreak in Bangladesh represents the largest documented "
    "resurgence in the country's history, yet the geographic distribution and spatial "
    "concentration of the outbreak across administrative divisions have not been formally "
    "quantified. Methods: We conducted a division-level geospatial analysis using 62 days of "
    "daily surveillance data (2 April - 2 June 2026) from the Directorate General of Health "
    "Services (DGHS), supplemented with data from WHO and UNICEF situation reports. We "
    "mapped suspected incidence, confirmed incidence, case fatality rate, and hospitalization "
    "rate across all eight administrative divisions using choropleth maps generated from a "
    "nationally validated shapefile. Geographic concentration was quantified using the "
    "Herfindahl-Hirschman Index (HHI) and Gini coefficient. Temporal spatial diffusion was "
    "assessed through weekly progression maps. The association between division-level MR "
    "campaign vaccination coverage and incidence was tested using Pearson correlation. "
    "Results: All eight divisions were affected throughout the study period. Dhaka division "
    "recorded the highest suspected incidence (108.0 per 100,000) and Barisal the second "
    "highest (93.9 per 100,000), despite Barisal having fewer absolute cases. Rangpur "
    "recorded the lowest incidence (9.0 per 100,000). The Gini coefficient of geographic "
    "concentration was 0.485 for suspected cases and 0.677 for confirmed cases, indicating "
    "highly unequal distribution. The top two divisions (Dhaka and Chittagong) accounted for "
    "63.2% of all suspected cases. HHI increased from 0.217 (April 15) to 0.271 (June 2), "
    "indicating that geographic concentration intensified as the outbreak progressed. "
    "Vaccination coverage showed no significant correlation with incidence (Pearson r = 0.083, "
    "p = 0.845). Conclusions: The 2026 Bangladesh measles outbreak was highly geographically "
    "concentrated, with Dhaka and Barisal divisions bearing the greatest relative burden. The "
    "intensifying HHI over time suggests persistent focal transmission rather than diffuse "
    "spread. Targeted sub-divisional interventions in high-incidence areas are needed alongside "
    "strengthened routine immunization.",
    align="J")
pdf.ln(2)
pdf.set_font("Times", "B", 10)
pdf.cell(0, 6, "Keywords: measles; Bangladesh; spatial epidemiology; geographic concentration; GIS; Gini; outbreak 2026",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_left_margin(25)
pdf.ln(3)
pdf.set_draw_color(180, 180, 180)
pdf.line(25, pdf.get_y(), 190, pdf.get_y())

# ── 1. INTRODUCTION ──────────────────────────────────────────────────────────
pdf.section("1. Introduction")
pdf.body(
    "Measles remains one of the most contagious vaccine-preventable diseases, with an "
    "estimated 10.3 million cases and 107,500 deaths globally in 2023 [1]. The COVID-19 "
    "pandemic disrupted routine immunization services worldwide, creating large cohorts of "
    "susceptible children and fuelling measles resurgences in countries previously approaching "
    "elimination [2]. Bangladesh, which has maintained an Expanded Programme on Immunization "
    "(EPI) since 1979 and achieved national measles-rubella (MR) vaccine coverage exceeding "
    "90% historically, began experiencing an unprecedented measles resurgence from March 2026 [3,4]."
)
pdf.body(
    "By June 2026, more than 81,000 suspected cases and 9,800 confirmed cases had been "
    "reported across all eight administrative divisions, making this the largest measles "
    "outbreak recorded in Bangladesh's surveillance history [5,6]. Prior descriptive analyses "
    "have documented the national burden, age distribution, and vaccination status of cases [7,8]. "
    "However, no study has formally quantified the geographic concentration of the outbreak "
    "or examined its temporal spatial diffusion across divisions using geospatial methods and "
    "formal inequality metrics."
)
pdf.body(
    "Understanding the spatial epidemiology of measles outbreaks is critical for targeted "
    "response. Studies in Ethiopia, Malaysia, and sub-Saharan Africa have demonstrated that "
    "measles cases cluster non-uniformly even within countries with high national vaccination "
    "coverage, driven by local immunity gaps, population density, and healthcare access [9,10,11]. "
    "In Bangladesh, spatiotemporal analysis has been applied to COVID-19 and dengue at the "
    "district level [12,13], but no equivalent analysis has been conducted for the 2026 measles "
    "outbreak. This study addresses that gap by providing the first geospatial characterisation "
    "of the 2026 Bangladesh measles outbreak, quantifying geographic inequality of case burden, "
    "mapping temporal spread, and assessing the spatial relationship between vaccination "
    "coverage and incidence at the division level."
)

# ── 2. METHODS ───────────────────────────────────────────────────────────────
pdf.section("2. Methods")
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.1 Data Sources", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Case data were obtained from three publicly available sources. Primary data consisted of "
    "62 consecutive daily press release PDFs published by the Directorate General of Health "
    "Services (DGHS), Bangladesh, covering 2 April to 2 June 2026. These were supplemented "
    "with division-level cumulative totals from the WHO Disease Outbreak News (DON598) [5] "
    "and the UNICEF Bangladesh Measles Situation Report No.1 (8 April 2026) [6]. Division-level "
    "MR campaign 2026 vaccination coverage was sourced from DGHS press releases. Division "
    "population denominators were derived from the Bangladesh Population and Housing Census "
    "2022 as embedded in the study shapefile [14]."
)
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.2 Geographic Data", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Administrative boundary shapefiles were obtained from a nationally validated upazila-level "
    "(Level 3) dataset with 499 upazila polygons (WGS84 coordinate reference system). "
    "Division-level geometries were derived by dissolving upazila boundaries by division "
    "using GeoPandas 1.0 [15]. The shapefile incorporates 2022 Census population estimates "
    "at the upazila level, which were aggregated to division level to produce population "
    "denominators."
)
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.3 Epidemiological Indicators", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "For each division, we calculated: (i) suspected case incidence per 100,000 population; "
    "(ii) confirmed case incidence per 100,000 population; (iii) case fatality rate (CFR) "
    "as confirmed deaths divided by confirmed cases, expressed as a percentage; and "
    "(iv) hospitalization rate as cumulative hospitalizations divided by cumulative suspected "
    "cases. A suspected case was defined according to the WHO clinical case definition "
    "(generalised rash lasting 3+ days, fever, and one of: cough, coryza, or conjunctivitis). "
    "A confirmed case was laboratory-confirmed by IgM serology."
)
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.4 Geographic Concentration Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Geographic concentration was quantified using two complementary metrics. The "
    "Herfindahl-Hirschman Index (HHI) was calculated as the sum of squared division-level "
    "case shares: HHI = sum(s_i^2), where s_i is division i's share of total national cases. "
    "HHI ranges from 1/n (perfect equality across n units) to 1.0 (complete concentration). "
    "The Gini coefficient was computed as a standardised measure of statistical dispersion "
    "of the case distribution across divisions, ranging from 0 (perfect equality) to 1 "
    "(maximum inequality) [16]. A Lorenz curve was constructed to visualise the cumulative "
    "case share against the cumulative population share. Given the small number of "
    "administrative units (n=8 divisions), formal spatial autocorrelation statistics such as "
    "Moran's I were not applied, as these require a minimum of approximately 30 observations "
    "for stable inference [17]."
)
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.5 Temporal Progression Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Weekly cumulative incidence per 100,000 was calculated for each division across eight "
    "epidemiological weeks using DGHS daily data. Weekly progression maps were generated to "
    "visualise the spatial diffusion of the outbreak over time."
)
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.6 Vaccination Coverage and Incidence", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "The Pearson correlation coefficient was calculated between division-level MR campaign "
    "2026 vaccination coverage (%) and suspected incidence per 100,000. Statistical analyses "
    "were performed in Python 3.12 using pandas, scipy, geopandas, and matplotlib. "
    "All data are publicly available and aggregate; individual patient data were not accessed. "
    "Ethical approval was therefore not required under Bangladeshi regulatory guidelines for "
    "analyses of publicly available aggregate surveillance data."
)

# ── 3. RESULTS ───────────────────────────────────────────────────────────────
pdf.section("3. Results")
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "3.1 National and Division-Level Burden", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Over the 62-day study period (2 April - 2 June 2026), 81,084 suspected cases and "
    "9,833 confirmed cases of measles were reported nationally, with 539 suspected deaths "
    "and 92 confirmed deaths. All eight administrative divisions were affected throughout "
    "the study period, with 61 of 64 districts reporting at least one case."
)
pdf.body(
    "Division-level incidence rates varied markedly (Table 1). Dhaka division recorded "
    "the highest suspected incidence at 108.0 per 100,000, nearly 12 times greater than "
    "Rangpur (9.0 per 100,000), the lowest-burden division. Barisal recorded the second "
    "highest incidence (93.9 per 100,000) despite ranking fourth in absolute case count, "
    "reflecting its smaller population denominator. Confirmed incidence was highest in Dhaka "
    "(19.5 per 100,000), followed by Rajshahi (5.6 per 100,000). The case fatality rate "
    "was highest in Barisal (6.3%), more than eight times the rate in Dhaka (0.8%), though "
    "this may reflect differences in laboratory confirmation rates across divisions."
)

# Table 1
pdf.ln(2)
pdf.set_font("Times", "B", 10)
pdf.cell(0, 6, "Table 1. Division-Level Measles Burden, 2026 Bangladesh Outbreak (2 April - 2 June 2026)",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(1)

headers = ["Division","Suspected\nTotal","Confirmed\nTotal","Suspected\n/100k","Confirmed\n/100k","CFR\n(%)","Hosp\nRate (%)"]
widths  = [28, 22, 22, 25, 25, 18, 25]
pdf.set_fill_color(30, 80, 160)
pdf.set_text_color(255, 255, 255)
pdf.set_font("Times","B",9)
for h, w in zip(headers, widths):
    pdf.multi_cell(w, 7, h, border=1, align="C", fill=True,
                   new_x=XPos.RIGHT, new_y=YPos.TOP)
pdf.ln(8)
pdf.set_text_color(0,0,0)

rows = [
    ("Dhaka",      "37,798","6,822","108.0","19.5","0.8","72.5"),
    ("Chittagong", "13,459",  "763", "45.0", "2.6","1.3","93.7"),
    ("Barisal",     "7,615",  "301", "93.9", "3.7","6.3","91.0"),
    ("Rajshahi",    "6,996", "1,119","35.2", "5.6","0.2","84.6"),
    ("Khulna",      "5,944",  "270", "38.0", "1.7","0.0","92.7"),
    ("Sylhet",      "4,143",  "258", "34.0", "2.1","1.2","89.1"),
    ("Mymensingh",  "3,566",  "233", "30.2", "2.0","0.9","90.7"),
    ("Rangpur",     "1,563",   "67",  "9.0", "0.4","0.0","54.6"),
    ("TOTAL",      "81,084","9,833",  "-",    "-",  "-",  "-"),
]
for i, row in enumerate(rows):
    fill = (i % 2 == 0)
    fc   = (245,245,255) if fill else (255,255,255)
    bold = (i == len(rows) - 1)
    pdf.set_font("Times","B" if bold else "",9)
    pdf.set_fill_color(*fc)
    for cell, w in zip(row, widths):
        pdf.multi_cell(w, 6, cell, border=1, align="C", fill=fill,
                       new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln(6)

pdf.set_font("Times","I",8)
pdf.cell(0, 5, "CFR = Case Fatality Rate (confirmed deaths / confirmed cases); Hosp Rate = Hospitalization Rate (hospitalizations / suspected cases)",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(2)

pdf.insert_figure(
    os.path.join(FIG, "fig1_choropleth_maps.png"),
    "Figure 1. Geographic distribution of the 2026 measles outbreak across Bangladesh's eight administrative "
    "divisions. Panel (a): suspected case incidence per 100,000; (b): confirmed case incidence per 100,000; "
    "(c): case fatality rate (%); (d): hospitalization rate (%). Darker shading indicates higher burden.",
    w=165
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.2 Geographic Concentration", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "The geographic distribution of cases was highly unequal. Dhaka division alone accounted "
    "for 46.6% of all suspected cases and 69.4% of all confirmed cases nationally. The top "
    "two divisions (Dhaka and Chittagong) collectively contributed 63.2% of suspected cases. "
    "The Gini coefficient of suspected case distribution across divisions was 0.485, and for "
    "confirmed cases was 0.677, indicating substantially greater geographic concentration of "
    "laboratory-confirmed disease compared to suspected cases."
)
pdf.body(
    "The Herfindahl-Hirschman Index (HHI) for suspected cases was 0.271 at the end of the "
    "study period (2 June 2026), compared to an HHI of 0.217 reported by Kamrujjaman et al. "
    "on April 15 [7], indicating that geographic concentration intensified as the outbreak "
    "progressed rather than dispersing. An HHI of 0.271 indicates moderate-to-high "
    "concentration (competitive markets threshold is typically HHI > 0.25). The Lorenz curve "
    "for confirmed cases showed a greater deviation from the equality line than suspected "
    "cases, consistent with the higher Gini coefficient (Figure 2)."
)

pdf.insert_figure(
    os.path.join(FIG, "fig2_geographic_concentration.png"),
    "Figure 2. Geographic concentration of the 2026 Bangladesh measles outbreak. Panel (a): suspected case "
    "burden share by division; (b): suspected incidence rate per 100,000 by division; (c): Lorenz curves for "
    "suspected cases (Gini=0.485), confirmed cases (Gini=0.677), and population distribution. Shaded area "
    "represents the inequality gap between confirmed cases and perfect equality.",
    w=165
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.3 Temporal Spatial Progression", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Temporal progression maps reveal that Dhaka division dominated the spatial burden "
    "throughout all eight epidemiological weeks of the study period (Figure 3). From Week 1, "
    "Dhaka showed the highest cumulative incidence, with the gap between Dhaka and other "
    "divisions widening progressively. Barisal emerged as the second highest incidence "
    "division from Week 3 onwards despite lower absolute case counts, reflecting the "
    "population-adjusted burden. Rangpur consistently recorded the lowest incidence across "
    "all time points. The pattern suggests a predominantly Dhaka-centred outbreak with "
    "sustained elevated incidence in the Barisal division, rather than a wave-like geographic "
    "diffusion across contiguous divisions."
)

pdf.insert_figure(
    os.path.join(FIG, "fig3_temporal_progression.png"),
    "Figure 3. Temporal progression of cumulative suspected measles incidence per 100,000 population "
    "across Bangladesh's eight administrative divisions, shown for eight epidemiological weeks "
    "(2 April - 2 June 2026). Numbers within divisions indicate incidence per 100,000.",
    w=165
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.4 Vaccination Coverage and Spatial Incidence", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "The national MR campaign 2026 achieved an overall coverage of 102%, with division-level "
    "coverage ranging from 97.6% (Sylhet) to 105.4% (Rangpur). Pearson correlation analysis "
    "between division-level vaccination coverage and suspected incidence per 100,000 showed "
    "no significant association (r = 0.083, p = 0.845), consistent with findings from the "
    "earlier national analysis of this outbreak [18]. The spatial map of vaccination coverage "
    "(Figure 4, panel a) shows a contrasting pattern to the incidence map (panel b): Rangpur, "
    "with the highest coverage (105.4%), recorded the lowest incidence (9.0/100,000), while "
    "Dhaka, with 102.0% coverage, recorded the highest incidence (108.0/100,000). This "
    "paradox is consistent with a reactive campaign launched during active transmission, "
    "where coverage reflects response intensity rather than pre-existing immunity."
)

pdf.insert_figure(
    os.path.join(FIG, "fig4_vaccination_spatial.png"),
    "Figure 4. Spatial relationship between MR vaccination coverage and measles incidence. "
    "Panel (a): division-level MR campaign 2026 coverage; (b): suspected incidence per 100,000; "
    "(c): scatter plot of coverage vs incidence with regression line (Pearson r=0.083, p=0.845).",
    w=165
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.5 District-Level Burden: WHO and UNICEF Data", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "The WHO Disease Outbreak News DON598 (14 April 2026) provided suspected case counts for "
    "four district capitals: Dhaka (8,263 cases), Rajshahi (3,747), Chittagong (2,514), and "
    "Khulna (1,568), representing the four highest-burden divisional headquarters [5]. "
    "These four districts collectively accounted for 79% of all nationally reported suspected "
    "cases at the time of reporting (15,092 of 19,161 cases). Within each of these divisions, "
    "the district capital contributed 60-67% of the division total: Dhaka district 60.4% of "
    "Dhaka division, Rajshahi district 64.2% of Rajshahi division, Chittagong district 61.8% "
    "of Chittagong division, and Khulna district 67.1% of Khulna division (Table 2). This "
    "indicates that in each high-burden division, the majority of cases were concentrated "
    "within the urban district capital rather than distributed across rural districts."
)
pdf.body(
    "The UNICEF Bangladesh Situation Report No.1 (8 April 2026) identified six specific urban "
    "transmission clusters within Dhaka district: Demra, Jatrabari, Kamrangirchar, Korail, "
    "Mirpur, and Tejgaon [6]. These are densely populated informal settlements and industrial "
    "zones with high population density and accumulated immunity gaps. Additionally, two border "
    "districts were flagged as hotspots due to cross-border movement with India: Jessore "
    "(Jashore) in Khulna division and Chapainawabganj (Nawabganj) in Rajshahi division, both "
    "sharing active land border crossings."
)

# Table 2 - WHO district data
pdf.ln(2)
pdf.set_font("Times","B",10)
pdf.cell(0, 6,
    "Table 2. District-Level Case Burden from WHO DON598 (14 April 2026) and "
    "UNICEF Situation Report No.1",
    new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(1)

t2_headers = ["District","Division","Suspected\nCases","Division\nTotal","District\nShare (%)","Source"]
t2_widths  = [28, 28, 25, 25, 25, 34]
pdf.set_fill_color(30, 80, 160)
pdf.set_text_color(255, 255, 255)
pdf.set_font("Times","B",9)
for h, w in zip(t2_headers, t2_widths):
    pdf.multi_cell(w, 7, h, border=1, align="C", fill=True,
                   new_x=XPos.RIGHT, new_y=YPos.TOP)
pdf.ln(8)
pdf.set_text_color(0,0,0)

t2_rows = [
    ("Dhaka",      "Dhaka",      "8,263","13,685","60.4","WHO DON598"),
    ("Rajshahi",   "Rajshahi",   "3,747", "5,832","64.2","WHO DON598"),
    ("Chittagong", "Chittagong", "2,514", "4,065","61.8","WHO DON598"),
    ("Khulna",     "Khulna",     "1,568", "2,337","67.1","WHO DON598"),
    ("Jessore",    "Khulna",       "-",     "-",   "-",  "UNICEF (border hotspot)"),
    ("Nawabganj",  "Rajshahi",     "-",     "-",   "-",  "UNICEF (border hotspot)"),
]
for i, row in enumerate(t2_rows):
    fill = (i % 2 == 0)
    fc = (245,245,255) if fill else (255,255,255)
    pdf.set_fill_color(*fc)
    pdf.set_font("Times","",9)
    for cell, w in zip(row, t2_widths):
        pdf.multi_cell(w, 6, cell, border=1, align="C", fill=fill,
                       new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln(6)

pdf.set_font("Times","I",8)
pdf.multi_cell(0, 5,
    "Data date: 14 April 2026 for WHO cases; 8 April 2026 for UNICEF hotspot designations.\n"
    "District share = district cases / division total x 100.",
    align="L")
pdf.ln(8)

pdf.insert_figure(
    os.path.join(FIG, "fig5_district_who_unicef.png"),
    "Figure 5. District-level analysis using WHO and UNICEF data (April 2026). "
    "Panel (a): national district map highlighting four WHO-reported districts (coloured by "
    "case count) and two UNICEF-designated border hotspots (stars); "
    "panel (b): Dhaka division zoom showing six UNICEF-identified urban transmission clusters "
    "within Dhaka district; panel (c): comparison of district capital case counts against "
    "full division totals, showing 60-67% concentration in district capitals.",
    w=155
)

# ── 4. DISCUSSION ────────────────────────────────────────────────────────────
pdf.section("4. Discussion")
pdf.body(
    "This study provides the first geospatial characterisation of the 2026 Bangladesh measles "
    "outbreak using formal geographic concentration metrics and temporal progression mapping. "
    "Our central finding is that the outbreak was highly spatially concentrated: Dhaka division "
    "alone accounted for nearly half of all suspected cases, and the Gini coefficient for "
    "confirmed cases (0.677) indicates a level of geographic inequality comparable to that "
    "observed in measles outbreaks in Ethiopia (Moran's I = 0.154) and Malaysia (significant "
    "spatial autocorrelation in Klang Valley) [9,10]."
)
pdf.body(
    "A key novel finding is the increase in HHI from 0.217 (mid-April) to 0.271 (early June), "
    "indicating that geographic concentration of the outbreak intensified over time. This "
    "pattern is inconsistent with a simple diffusion model where cases spread outward from an "
    "epicentre to surrounding areas. Instead, it suggests sustained focal transmission in "
    "Dhaka's high-density urban informal settlements - including Demra, Jatrabari, "
    "Kamrangirchar, and Mirpur - where population density, overcrowding, and accumulated "
    "immunity gaps create conditions for persistent measles transmission [5,6]. This pattern "
    "has been described as 'epidemiological connectivity' in high-density urban clusters, where "
    "spatial proximity amplifies transmission within clusters rather than between them [19]."
)
pdf.body(
    "The contrasting incidence profiles of Dhaka (108.0/100k, high density) and Barisal "
    "(93.9/100k, low density but small population) highlight the importance of population-adjusted "
    "metrics alongside absolute case counts. Barisal's high incidence relative to its total "
    "case burden suggests a local outbreak with high attack rates, possibly linked to specific "
    "immunity gaps in peri-urban or rural communities in the division."
)
pdf.body(
    "The null correlation between vaccination coverage and incidence (r = 0.083, p = 0.845) "
    "is consistent with our earlier report on this outbreak [18] and with findings from "
    "sub-Saharan Africa, where high national coverage coexists with spatially clustered "
    "populations of unvaccinated children [11]. The reactive MR campaign, launched on "
    "5 April 2026, targeted 1.2 million children in 30 hotspot upazilas, yet the outbreak "
    "continued through June 2026, consistent with the limitations of reactive immunization "
    "once active transmission is established [2,8]."
)
pdf.body(
    "Several limitations merit acknowledgement. First, our analysis is at the division level "
    "(n=8), which precludes formal spatial autocorrelation statistics (Moran's I, LISA) that "
    "require larger observation sets [17]. Future analyses using district-level (n=64) or "
    "upazila-level (n~490) data would enable more granular hotspot identification, as "
    "demonstrated for dengue in Bangladesh [13]. Second, surveillance data from DGHS press "
    "releases reflect reported cases and may underestimate true incidence in areas with limited "
    "healthcare access or surveillance capacity. Third, vaccination coverage data represent "
    "campaign targets and may not reflect actual immunity status among the at-risk population, "
    "particularly among zero-dose infants under nine months [6]. Fourth, no socioeconomic, "
    "demographic, or climate covariates were included in this ecological analysis; residual "
    "confounding cannot be excluded."
)

# ── 5. CONCLUSIONS ───────────────────────────────────────────────────────────
pdf.section("5. Conclusions")
pdf.body(
    "The 2026 Bangladesh measles outbreak was geographically highly concentrated, with Dhaka "
    "and Barisal divisions bearing disproportionate burden relative to their populations. "
    "The increasing Herfindahl-Hirschman Index over the outbreak's course indicates intensifying "
    "focal transmission rather than geographic diffusion, pointing to persistent transmission "
    "in high-density urban clusters. The null correlation between MR campaign coverage and "
    "incidence underscores that reactive immunization is insufficient to interrupt active "
    "transmission. These findings support targeted sub-divisional interventions - particularly "
    "in Dhaka's urban informal settlements - and call for strengthened routine EPI to reduce "
    "the accumulation of susceptible cohorts before future outbreaks occur. Geospatial "
    "surveillance at district and upazila levels should be integrated into Bangladesh's "
    "routine disease monitoring systems to enable earlier hotspot identification."
)

# ── DECLARATIONS ─────────────────────────────────────────────────────────────
pdf.section("Declarations")
pdf.set_font("Times","B",10)
pdf.cell(0,5,"Funding:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body("This research received no external funding.", indent=5)
pdf.set_font("Times","B",10)
pdf.cell(0,5,"Competing Interests:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body("The author declares no competing interests.", indent=5)
pdf.set_font("Times","B",10)
pdf.cell(0,5,"Data Availability:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "All data and analysis scripts are publicly available at: "
    "https://github.com/khalilurrrahmanridoykhan/bangladesh-measles-2026. "
    "Source data are publicly available from DGHS Bangladesh (https://dghs.gov.bd).", indent=5)
pdf.set_font("Times","B",10)
pdf.cell(0,5,"Ethics:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "This study used only publicly available aggregated surveillance data. "
    "No individual patient data were accessed. Formal ethics review was not required.", indent=5)

# ── REFERENCES ───────────────────────────────────────────────────────────────
pdf.section("References")
refs = [
    "[1]  World Health Organization. Measles. WHO Fact Sheet. 2024. https://www.who.int/news-room/fact-sheets/detail/measles",
    "[2]  Patel MK, et al. Progress Toward Regional Measles Elimination - Worldwide, 2000-2022. MMWR. 2023;72(46):1262-1268.",
    "[3]  Bangladesh EPI Programme. Expanded Programme on Immunization, Annual Report. DGHS Bangladesh. 2024.",
    "[4]  World Health Organization. Nationwide Response Mobilized to Contain Measles Outbreak in Bangladesh. WHO SEARO. April 2026.",
    "[5]  World Health Organization. Measles - Bangladesh. Disease Outbreak News DON598. April 2026. https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON598",
    "[6]  UNICEF. Bangladesh: Humanitarian Situation Report No.1 - Measles Outbreak. 8 April 2026.",
    "[7]  Kamrujjaman M, Khondaker F, Sarker AA, Rivu NNK, et al. Measles Resurgence in Bangladesh, 2026: A Situational Analysis for Urgent Public Health Response. arXiv:2604.25951. 2026.",
    "[8]  Rahman MM, Kader SB, Sujon H, Gupta S. Post-Honeymoon Measles Resurgence in a Near-Elimination Setting: Transmission Dynamics and the Impact of Emergency Vaccination in Bangladesh, 2026. SSRN 6925103. 2026.",
    "[9]  Getachew A, et al. Spatio-temporal patterns and determinants of measles incidence in Ethiopia between 2018 and 2024. Frontiers in Public Health. 2026;14:1760450.",
    "[10] Zakaria Z, et al. Incidence rate and spatial clustering of measles cases in Malaysia, 2018-2022. Epidemiology and Infection. 2025.",
    "[11] Utazi CE, et al. Spatial clustering of measles vaccination coverage among children in sub-Saharan Africa. BMC Medicine. 2018;16:210.",
    "[12] Islam MZ, et al. Geospatial dynamics of COVID-19 clusters and hotspots in Bangladesh. Transboundary and Emerging Diseases. 2021;68(6):3643-3657.",
    "[13] Ahmed S, et al. Dengue fever mapping in Bangladesh: A spatial modeling approach. PLOS ONE. 2024.",
    "[14] Bangladesh Bureau of Statistics. Bangladesh Population and Housing Census 2022. BBS. Dhaka, Bangladesh.",
    "[15] Jordahl K, et al. GeoPandas: Python tools for working with geospatial data. Journal of Open Source Software. 2021.",
    "[16] Gastwirth JL. The Estimation of the Lorenz Curve and Gini Index. Review of Economics and Statistics. 1972;54(3):306-316.",
    "[17] Anselin L. Local Indicators of Spatial Association - LISA. Geographical Analysis. 1995;27(2):93-115.",
    "[18] Khan KRR. Epidemiology of the 2026 Measles Outbreak in Bangladesh: A Descriptive Analysis of National Surveillance Data with Vaccine Coverage Assessment. Zenodo. 2026. doi:10.5281/zenodo.20569837",
    "[19] Bharti N, et al. Measles hotspots and epidemiological connectivity. Epidemiology and Infection. 2010;138(9):1308-1316.",
    "[20] Tuite AR, et al. Estimated burden of measles infection and associated complications: Implications for outbreak response and control. Vaccine. 2019;37(32):4537-4543.",
]
pdf.set_font("Times","",9)
for ref in refs:
    pdf.multi_cell(0, 5, ref, align="J")
    pdf.ln(1)

# ── Save ─────────────────────────────────────────────────────────────────────
out_path = os.path.join(OUT, "Spatial_Epidemiology_Measles_Bangladesh_2026.pdf")
pdf.output(out_path)
print(f"Saved: {out_path}")
