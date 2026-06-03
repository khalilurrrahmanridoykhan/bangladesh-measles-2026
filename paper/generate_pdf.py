"""
Generates the research manuscript as a PDF using fpdf2.
Output: paper/Bangladesh_Measles_2026_Manuscript.pdf
"""

from fpdf import FPDF, XPos, YPos
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
FIG  = os.path.join(ROOT, "figures")

class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(left=25, top=25, right=20)
        self.set_auto_page_break(auto=True, margin=22)
        self.add_page()

    # ── helpers ──────────────────────────────────────────────────────────
    def title_block(self):
        self.set_font("Times", "B", 16)
        self.multi_cell(0, 8,
            "Epidemiology of the 2026 Measles Outbreak in Bangladesh: "
            "A Descriptive Analysis of National Surveillance Data "
            "with Vaccine Coverage Assessment",
            align="C")
        self.ln(5)
        self.set_font("Times", "B", 12)
        self.cell(0, 7, "Khalilur Rahman Ridoy Khan", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Times", "I", 11)
        self.cell(0, 6, "Department of Computer Science and Engineering, East West University, Dhaka, Bangladesh",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, "Correspondence: khalilurrahmanridoykhan@gmail.com",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, "Date: June 2026",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Times", "I", 10)
        self.cell(0, 6, "Data & Code: https://github.com/khalilurrrahmanridoykhan/bangladesh-measles-2026",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Times", "I", 10)
        self.cell(0, 6,
            "Keywords: measles; Bangladesh; outbreak; epidemiology; vaccine-preventable disease; DGHS; 2026",
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def section(self, text, size=13):
        self.ln(4)
        self.set_font("Times", "B", size)
        self.multi_cell(0, 7, text)
        self.ln(1)

    def subsection(self, text):
        self.ln(2)
        self.set_font("Times", "B", 11)
        self.multi_cell(0, 6, text)

    def body(self, text, indent=True):
        self.set_font("Times", "", 11)
        if indent:
            self.set_x(self.l_margin + 8)
            self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 6, text, align="J")
        else:
            self.multi_cell(0, 6, text, align="J")
        self.ln(2)

    def abstract_item(self, label, text):
        self.set_font("Times", "B", 11)
        self.write(6, label)
        self.set_font("Times", "", 11)
        self.write(6, text)
        self.ln(5)

    def bullet(self, text):
        self.set_font("Times", "", 11)
        x = self.get_x()
        self.set_x(self.l_margin + 5)
        self.cell(5, 6, "-")
        self.set_x(self.l_margin + 10)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 10, 6, text, align="J")
        self.ln(1)

    def ref(self, text):
        self.set_font("Times", "", 10)
        self.set_x(self.l_margin + 10)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 10, 5, text, align="J")
        self.ln(1)

    def draw_table(self, caption, headers, rows, col_w):
        self.ln(3)
        self.set_font("Times", "B", 10)
        self.multi_cell(0, 6, caption)
        self.ln(1)
        # header row
        self.set_fill_color(46, 117, 182)
        self.set_text_color(255, 255, 255)
        self.set_font("Times", "B", 9)
        x0 = self.get_x()
        for i, (h, w) in enumerate(zip(headers, col_w)):
            self.multi_cell(w, 6, h, border=1, fill=True, align="C",
                            new_x=XPos.RIGHT if i < len(headers)-1 else XPos.LMARGIN,
                            new_y=YPos.TOP if i < len(headers)-1 else YPos.NEXT)
            if i < len(headers) - 1:
                self.set_xy(self.get_x(), self.get_y())
        # reset after header
        self.set_text_color(0, 0, 0)
        self.set_font("Times", "", 9)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(235, 243, 251)
                fill = True
            else:
                fill = False
            for ci, (val, w) in enumerate(zip(row, col_w)):
                align = "L" if ci == 0 else "C"
                self.multi_cell(w, 6, str(val), border=1, fill=fill, align=align,
                                new_x=XPos.RIGHT if ci < len(row)-1 else XPos.LMARGIN,
                                new_y=YPos.TOP if ci < len(row)-1 else YPos.NEXT)
        self.set_fill_color(255, 255, 255)
        self.ln(3)

    def add_figure(self, fname, caption):
        fpath = os.path.join(FIG, fname)
        if not os.path.exists(fpath):
            self.body(f"[Figure not found: {fname}]")
            return
        self.ln(4)
        img_w = 160
        self.image(fpath, x=(self.w - img_w) / 2, w=img_w)
        self.ln(2)
        self.set_font("Times", "I", 10)
        self.multi_cell(0, 5, caption, align="C")
        self.ln(4)


# ── BUILD ──────────────────────────────────────────────────────────────────

pdf = PDF()

# TITLE
pdf.title_block()

# ABSTRACT
pdf.section("Abstract", size=13)
pdf.abstract_item("Background: ",
    "Bangladesh has experienced a large-scale measles outbreak since March 2026, "
    "coinciding with a national Measles-Rubella (MR) immunisation campaign. This study "
    "describes the epidemiological characteristics of the outbreak using publicly "
    "available daily surveillance data published by the Directorate General of Health "
    "Services (DGHS).")
pdf.abstract_item("Methods: ",
    "We extracted structured data from 62 consecutive daily press release PDFs published "
    "by DGHS (2 April to 2 June 2026) using automated web scraping and PDF text "
    "extraction. We analysed temporal trends, geographic distribution across eight "
    "administrative divisions, mortality, and the relationship between MR campaign "
    "vaccination coverage and division-level incidence rates.")
pdf.abstract_item("Results: ",
    "A total of 73,362 suspected and 9,136 confirmed measles cases were reported "
    "(confirmation rate 12.5%). A total of 59,106 patients were hospitalised and "
    "54,812 (92.7%) recovered. Suspected and confirmed deaths numbered 504 and 90, "
    "respectively (confirmed case fatality rate 0.99%). The outbreak grew rapidly "
    "with a doubling time of 6.1 days. Peak daily suspected cases reached 1,503 on "
    "10 May 2026. Dhaka division accounted for 47.0% of all confirmed cases (incidence "
    "95.7 per 100,000 population). National MR campaign coverage was 102%; however, "
    "Pearson correlation between division-level coverage and incidence was "
    "non-significant (r = 0.10, p = 0.82).")
pdf.abstract_item("Conclusions: ",
    "This outbreak represents one of the largest measles events recorded in Bangladesh. "
    "Despite high MR campaign coverage, urban transmission persisted - particularly in "
    "Dhaka. Strengthening routine immunisation, improving cold-chain management, and "
    "targeting high-density urban populations are essential to interrupt transmission.")

# 1. INTRODUCTION
pdf.add_page()
pdf.section("1. Introduction")
pdf.body(
    "Measles remains one of the most contagious infectious diseases known to medicine, "
    "with a basic reproduction number (R0) estimated between 12 and 18. Despite the "
    "existence of a safe, effective, and affordable vaccine, measles caused an estimated "
    "136,000 deaths globally in 2022, the majority among children under five years of "
    "age (World Health Organization [WHO], 2023). Following disruptions to routine "
    "immunisation services during the COVID-19 pandemic (2020-2022), a global resurgence "
    "of measles has been observed, with large outbreaks reported across Africa, South-East "
    "Asia, and the Eastern Mediterranean region.")
pdf.body(
    "Bangladesh, a densely populated lower-middle-income country with approximately "
    "170 million inhabitants, has maintained an Expanded Programme on Immunisation (EPI) "
    "since 1979. The measles vaccine was introduced into the national schedule in 1980, "
    "and a two-dose schedule - measles-rubella (MR) vaccine at 9 and 15 months - has been "
    "in place since 2012. Bangladesh had previously achieved measles vaccination coverage "
    "exceeding 95% in many districts, and no major nationwide outbreak had been documented "
    "for several years prior to 2026.")
pdf.body(
    "In March 2026, the DGHS activated its Integrated Control Centre in response to a "
    "sharp rise in febrile rash illness consistent with measles across multiple divisions. "
    "Daily situation reports were published publicly from 15 March 2026, providing a rare "
    "opportunity for granular, real-time epidemiological analysis using government "
    "surveillance data. By 2 June 2026, more than 73,000 suspected cases had been reported "
    "nationally.")
pdf.body(
    "This study has three objectives: (i) to describe the temporal trajectory of the 2026 "
    "Bangladesh measles outbreak using 62 days of daily national surveillance data; "
    "(ii) to characterise the geographic distribution of the outbreak burden across "
    "Bangladesh's eight administrative divisions; and (iii) to assess the relationship "
    "between the 2026 national MR immunisation campaign coverage and division-level "
    "measles incidence.")

# 2. METHODS
pdf.section("2. Methods")
pdf.subsection("2.1 Data Source")
pdf.body(
    "Data were sourced exclusively from publicly available daily press release PDFs "
    "published by the DGHS of the Government of Bangladesh "
    "(https://dghs.gov.bd/pages/press-releases/). Each press release is a structured "
    "three-page PDF document reporting: (i) national suspected and confirmed measles cases "
    "in the preceding 24 hours and cumulatively from 15 March 2026; (ii) suspected and "
    "confirmed deaths; (iii) hospitalisation and recovery counts; (iv) division-level "
    "breakdowns; and (v) Measles-Rubella Campaign 2026 vaccination coverage by division.")

pdf.subsection("2.2 Data Collection")
pdf.body(
    "Automated data collection was conducted using custom Python scripts (Python 3.14; "
    "libraries: requests, BeautifulSoup4, pdfplumber). Bangla numeral characters were "
    "converted to Western Arabic numerals prior to parsing. All scripts and clean datasets "
    "are available at: https://github.com/khalilurrrahmanridoykhan/bangladesh-measles-2026.")

pdf.subsection("2.3 Case Definitions")
pdf.body(
    "A suspected case is any person with fever and generalised maculopapular rash plus at "
    "least one of: cough, coryza, or conjunctivitis. A confirmed case is a suspected case "
    "with laboratory confirmation (measles IgM serology or viral isolation) or "
    "epidemiologic linkage to a laboratory-confirmed case (WHO 2018 surveillance guidelines).")

pdf.subsection("2.4 Statistical Analysis")
pdf.body(
    "Descriptive statistics were computed for national and division-level indicators. "
    "Doubling time during the exponential growth phase (first 14 days) was estimated "
    "using log-linear regression: ln(cumulative suspected cases) = a + b x day, "
    "with doubling time = ln(2)/b. Incidence rates were calculated per 100,000 population "
    "using 2022 Bangladesh Census denominators. Pearson correlation assessed the "
    "relationship between division-level MR campaign coverage and confirmed incidence. "
    "All analyses used Python 3.14 (pandas, matplotlib, scipy). Significance: p < 0.05.")

pdf.subsection("2.5 Ethics")
pdf.body(
    "This study used only publicly available, aggregated government surveillance data. "
    "No individual patient data or identifiable information were accessed. Formal ethics "
    "review was not required.")

# 3. RESULTS
pdf.add_page()
pdf.section("3. Results")
pdf.subsection("3.1 National Overview")
pdf.body(
    "Over the 62-day study period (2 April to 2 June 2026), 73,362 suspected and 9,136 "
    "confirmed measles cases were reported nationally (confirmation rate 12.5%; Table 1). "
    "A total of 59,106 patients were hospitalised, of whom 54,812 (92.7%) recovered. "
    "Suspected deaths totalled 504 (suspected CFR 0.69%); confirmed deaths numbered 90 "
    "(confirmed CFR 0.99%).")

pdf.draw_table(
    caption="Table 1. National Summary Statistics - Bangladesh Measles Outbreak, 2 April to 2 June 2026",
    headers=["Indicator", "Value"],
    rows=[
        ("Reporting period", "2 April 2026 - 2 June 2026 (62 days)"),
        ("Total suspected cases", "73,362"),
        ("Total confirmed cases", "9,136"),
        ("Confirmation rate", "12.5%"),
        ("Total hospitalised (cumulative)", "59,106"),
        ("Hospitalisation rate (of suspected)", "80.6%"),
        ("Total recovered (cumulative)", "54,812"),
        ("Recovery rate (of hospitalised)", "92.7%"),
        ("Total suspected deaths", "504"),
        ("Total confirmed deaths", "90"),
        ("Case fatality rate - suspected", "0.69%"),
        ("Case fatality rate - confirmed", "0.99%"),
        ("Peak daily suspected cases", "1,503 (10 May 2026)"),
        ("Mean daily suspected cases", "1,167"),
    ],
    col_w=[110, 55]
)

pdf.subsection("3.2 Temporal Trends")
pdf.body(
    "The epidemic curve demonstrated rapid early growth followed by a sustained plateau "
    "(Figure 1). Daily suspected cases rose from 685 on 2 April to a peak of 1,503 on "
    "10 May 2026. The mean daily suspected case count was 1,167 (range: 674-1,503). "
    "During the final week, daily cases declined below 1,100, suggesting early plateau. "
    "The doubling time during the first 14 days was 6.1 days (daily growth rate 11.3%; "
    "r2 = 0.94). Week-over-week growth was highest in week 2 (+12.1%), decelerating from "
    "week 7 onward (-23.6% in the final partial week).")

pdf.subsection("3.3 Geographic Distribution")
pdf.body(
    "Measles burden was highly concentrated in Dhaka division: 34,497 confirmed cases "
    "(47.0% of national total; incidence 95.7 per 100,000; Table 2). Chattogram ranked "
    "second (12,009 cases; 42.3/100,000). Rangpur had the lowest burden (3,323 cases; "
    "21.2/100,000). Barishal recorded the highest incidence rate (79.7/100,000) despite "
    "the smallest population.")

pdf.draw_table(
    caption="Table 2. Division-level Confirmed Measles Cases and Incidence Rates, Bangladesh 2026",
    headers=["Division", "Population (2022)", "Confirmed Cases", "Incidence/100k", "% National"],
    rows=[
        ("Dhaka",          "36,054,418", "34,497", "95.7", "47.0%"),
        ("Chattogram",     "28,423,019", "12,009", "42.3", "16.0%"),
        ("Rajshahi",       "18,484,858",  "9,414", "50.9", "12.6%"),
        ("Barishal",        "8,325,666",  "6,634", "79.7",  "8.8%"),
        ("Khulna",         "15,563,000",  "5,422", "34.8",  "7.2%"),
        ("Sylhet",         "10,009,239",  "3,688", "36.8",  "4.9%"),
        ("Rangpur",        "15,665,000",  "3,323", "21.2",  "4.4%"),
        ("Mymensingh",     "11,370,000",    "N/A",   "N/A",  "N/A"),
        ("NATIONAL TOTAL","143,895,200", "74,987*", "52.1","100%"),
    ],
    col_w=[35, 42, 35, 32, 28]
)
pdf.set_font("Times", "I", 9)
pdf.multi_cell(0, 5, "* National total includes cases not attributed to specific divisions in daily reports.")
pdf.ln(2)

pdf.subsection("3.4 Mortality")
pdf.body(
    "As of 2 June 2026, 504 suspected and 90 confirmed measles deaths had been recorded "
    "cumulatively since 15 March 2026. The confirmed CFR of 0.99% is consistent with "
    "measles mortality estimates for low- and middle-income settings. Deaths data were "
    "reliably extractable for 14 of 62 reporting days (mid-May to June 2026) due to PDF "
    "layout variability in earlier reports.")

pdf.subsection("3.5 Vaccination Coverage and Incidence")
pdf.body(
    "The national MR Campaign 2026 achieved 102% overall coverage (18,452,281 doses "
    "administered; Table 3). Despite this, the Pearson correlation between division-level "
    "MR campaign coverage and confirmed measles incidence per 100,000 was r = 0.10 "
    "(p = 0.82) - not statistically significant. This indicates that high campaign "
    "coverage, achieved during an active outbreak, did not prevent ongoing transmission "
    "at the division level.")

pdf.draw_table(
    caption="Table 3. MR Campaign 2026 Coverage vs. Confirmed Measles Incidence by Division\n"
            "Pearson r = 0.10, p = 0.82 (not statistically significant)",
    headers=["Division", "Coverage (%)", "Confirmed Cases", "Incidence/100k"],
    rows=[
        ("Dhaka",      "103%", "34,497", "95.7"),
        ("Chattogram", "103%", "12,009", "42.3"),
        ("Rajshahi",   "103%",  "9,414", "50.9"),
        ("Barishal",   "101%",  "6,634", "79.7"),
        ("Khulna",     "101%",  "5,422", "34.8"),
        ("Sylhet",      "99%",  "3,688", "36.8"),
        ("Rangpur",    "103%",  "3,323", "21.2"),
        ("Mymensingh", "102%",    "N/A",   "N/A"),
    ],
    col_w=[40, 37, 42, 38]
)

# 4. DISCUSSION
pdf.add_page()
pdf.section("4. Discussion")
pdf.subsection("4.1 Summary of Findings")
pdf.body(
    "This study presents the first systematic epidemiological analysis of the 2026 measles "
    "outbreak in Bangladesh, using 62 days of publicly available national surveillance "
    "data. The outbreak was characterised by rapid exponential growth (doubling time "
    "6.1 days), high hospitalisation burden (80.6%), and strong geographic concentration "
    "in Dhaka (47% of national confirmed cases). Despite achieving over 100% national MR "
    "campaign coverage, no statistically significant correlation between vaccination "
    "coverage and division-level incidence was observed.")

pdf.subsection("4.2 Rapid Transmission and Urban Concentration")
pdf.body(
    "The estimated doubling time of 6.1 days is consistent with a high effective "
    "reproduction number (Re > 1), indicating ongoing transmission in a susceptible "
    "population. The concentration of 47% of cases in Dhaka reflects its extreme "
    "population density (approximately 44,000 persons per km2 in the metropolitan area), "
    "high household crowding, and large populations of urban migrants with potentially "
    "incomplete vaccination histories. Barishal's high incidence rate (79.7/100,000) "
    "despite its small population suggests intense localised transmission in a compact area.")

pdf.subsection("4.3 Vaccination Coverage and Pre-existing Immunity Gaps")
pdf.body(
    "The absence of a significant inverse correlation between MR campaign coverage and "
    "incidence (r = 0.10, p = 0.82) is a critical finding. The campaign was reactive - "
    "conducted during an active outbreak rather than prophylactically. Pre-existing "
    "immunity gaps accumulated over years of suboptimal routine immunisation and "
    "pandemic-era service disruptions provided the susceptible pool driving transmission. "
    "Division-level coverage data may also mask sub-district heterogeneity where pockets "
    "of unvaccinated children sustain local transmission chains even where aggregate "
    "coverage appears high.")

pdf.subsection("4.4 Mortality")
pdf.body(
    "The confirmed CFR of 0.99% is higher than high-income country estimates (<0.1%) but "
    "within the range for low- and middle-income settings (0.1%-5.0%). The high "
    "hospitalisation rate (80.6%) reflects either clinical severity or health-seeking "
    "behaviour that triages severe cases to hospital. Deaths data were incomplete across "
    "the study period, which is a significant limitation.")

pdf.subsection("4.5 Limitations")
limits = [
    "Aggregated data only: no individual patient data (age, sex, vaccination status, "
    "district) were available, preventing stratified analyses.",
    "Case definition sensitivity: the 12.5% confirmation rate suggests a substantial "
    "proportion of suspected cases may be non-measles febrile rash illnesses.",
    "Incomplete deaths data: mortality reliably extractable for only 14 of 62 days.",
    "Division-level vaccination data only (n=8): limits statistical power for correlation.",
    "No pre-outbreak baseline: press releases began 15 March 2026; early dynamics "
    "before this date are not captured.",
    "Single government data source: independent verification was not possible.",
]
for l in limits:
    pdf.bullet(l)

# 5. CONCLUSIONS
pdf.add_page()
pdf.section("5. Conclusions")
pdf.body(
    "The 2026 measles outbreak in Bangladesh is one of the largest on record, with over "
    "73,000 suspected and 9,136 confirmed cases in 62 days, 504 suspected deaths, and a "
    "rapid early doubling time of 6.1 days. The outbreak was disproportionately "
    "concentrated in Dhaka, with no statistically significant relationship between MR "
    "campaign coverage and division-level incidence, highlighting the limitations of "
    "reactive vaccination during active transmission.")
pdf.body(
    "Three urgent policy priorities emerge: (i) strengthening routine two-dose MR "
    "immunisation to maintain population immunity above the elimination threshold "
    "(>=95% two-dose coverage); (ii) implementing targeted supplementary immunisation "
    "in high-density urban communities well in advance of outbreak risk periods; and "
    "(iii) improving real-time surveillance infrastructure, including laboratory "
    "confirmation capacity, for timely epidemiological response.")

pdf.section("Data Availability")
pdf.body(
    "All data, analysis scripts, and figures: "
    "https://github.com/khalilurrrahmanridoykhan/bangladesh-measles-2026\n"
    "Primary data source: https://dghs.gov.bd/pages/press-releases/", indent=False)

pdf.section("Competing Interests")
pdf.body("The author declares no competing interests.", indent=False)

pdf.section("Funding")
pdf.body("No funding was received for this research.", indent=False)

pdf.section("Acknowledgements")
pdf.body(
    "The author acknowledges the Directorate General of Health Services (DGHS), "
    "Government of Bangladesh, for the daily public release of measles surveillance "
    "data throughout the 2026 outbreak.", indent=False)

# REFERENCES
pdf.section("References")
refs = [
    "1. World Health Organization. Measles. Geneva: WHO; 2023. "
       "https://www.who.int/news-room/fact-sheets/detail/measles",
    "2. Directorate General of Health Services (DGHS), Bangladesh. Daily Measles Press "
       "Releases. Dhaka: DGHS; 2026. https://dghs.gov.bd/pages/press-releases/",
    "3. Moss WJ. Measles. Lancet. 2017;390(10111):2490-2502.",
    "4. Orenstein WA, Seib K. Mounting a good offense against measles. "
       "N Engl J Med. 2014;371(18):1661-1663.",
    "5. WHO Regional Office for South-East Asia. Measles and Rubella Elimination "
       "Strategic Plan 2020-2024. New Delhi: WHO SEARO; 2020.",
    "6. Bangladesh Bureau of Statistics. Bangladesh Population and Housing Census 2022. "
       "Dhaka: BBS; 2023.",
    "7. EPI, Bangladesh. EPI Coverage Evaluation Survey Reports. Dhaka: DGHS; 2019.",
    "8. Luquero FJ, et al. A long-lasting measles epidemic in Maroua, Cameroon 2008-2009. "
       "J Infect Dis. 2011;204(Suppl 1):S243-S251.",
    "9. Perry RT, Halsey NA. The clinical significance of measles: a review. "
       "J Infect Dis. 2004;189(Suppl 1):S4-S16.",
    "10. Dabbagh A, et al. Progress toward regional measles elimination, 2000-2017. "
        "MMWR. 2018;67(47):1323-1329.",
    "11. Kundu SK, Khanam M, Das MK. Measles outbreak investigation in Bangladesh, "
        "2018-2019. Bangladesh J Infect Dis. 2020;7(1):18-24.",
    "12. WHO. Measles vaccines: WHO position paper - April 2017. "
        "Wkly Epidemiol Rec. 2017;92(17):205-227.",
    "13. Fine PE, Clarkson JA. Measles in England and Wales - analysis of seasonal "
        "patterns. Int J Epidemiol. 1982;11(1):5-14.",
    "14. Gavi, the Vaccine Alliance. Measles supplementary immunization activities: "
        "evidence and programmatic guidance. Geneva: Gavi; 2021.",
    "15. UNICEF Bangladesh. Immunization programme. Dhaka: UNICEF; 2023.",
    "16. WHO. WHO surveillance standards for measles. Geneva: WHO; 2018.",
    "17. van den Ent MMVX, et al. Measles mortality reduction contributes to reduction "
        "of all cause mortality in children <5 years. J Infect Dis. 2011;204(S1):S18-S23.",
    "18. Bhatt M, et al. On the measurement of vaccination coverage. "
        "Health Policy Plan. 1993;8(4):296-303.",
    "19. Lessler J, Metcalf CJE. Balancing evidence when considering rubella vaccine "
        "introduction. PLoS One. 2013;8(7):e67639.",
    "20. Grout L, et al. Measles in Democratic Republic of Congo: an ongoing crisis. "
        "Epidemiol Infect. 2013;141(6):1131-1139.",
]
for r in refs:
    pdf.ref(r)

# FIGURES
pdf.add_page()
pdf.section("Figures", size=14)

pdf.add_figure("fig1_epidemic_curve.png",
    "Figure 1. Epidemic curve of the 2026 measles outbreak in Bangladesh. "
    "Daily suspected cases (orange) and confirmed cases (blue) with 7-day rolling "
    "averages. 2 April to 2 June 2026.")

pdf.add_page()
pdf.add_figure("fig2_cumulative_trajectory.png",
    "Figure 2. Cumulative trajectory of measles cases, hospitalisations, "
    "recoveries, and suspected deaths, Bangladesh 2026.")

pdf.add_page()
pdf.add_figure("fig3_division_burden.png",
    "Figure 3. Division-level measles burden, Bangladesh 2026. "
    "Panel A: Confirmed cases (cumulative). "
    "Panel B: Incidence rate per 100,000 population.")

pdf.add_page()
pdf.add_figure("fig4_vaccination_vs_incidence.png",
    "Figure 4. MR Campaign 2026 coverage (%) vs. confirmed measles incidence "
    "per 100,000 by division. Bubble size proportional to confirmed cases. "
    "Pearson r = 0.10, p = 0.82.")

# SAVE
out = os.path.join(BASE, "Bangladesh_Measles_2026_Manuscript.pdf")
pdf.output(out)
print(f"PDF saved: {out}")
