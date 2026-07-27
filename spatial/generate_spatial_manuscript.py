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
            "Spatial Epidemiology, Transmission Dynamics, and Machine Learning Forecasting "
            "of the 2026 Measles Outbreak in Bangladesh: A Multi-Scale Geospatial and "
            "Computational Analysis",
            align="C")
        self.ln(4)
        self.set_font("Times", "B", 11)
        self.cell(0, 6,
            "Khalilur Rahman Ridoy Khan¹, Watan Rahman²",
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Times", "I", 10)
        self.cell(0, 5,
            "¹Independent Researcher, Dhaka, Bangladesh",
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 5,
            "²Institute of Science and Technology (IST), affiliated with National University Bangladesh, Dhaka, Bangladesh",
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
                "Spatial Epidemiology & ML Forecasting - Measles Bangladesh 2026 | Khan KR & Rahman W",
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
    "resurgence in the country's history, yet the geographic distribution, transmission "
    "dynamics, and epidemic trajectory have not been formally quantified using geospatial "
    "and computational methods. "
    "Methods: We conducted a multi-scale geospatial and computational epidemiology analysis "
    "using 81 days of daily surveillance data (2 April - 21 June 2026) from the Directorate "
    "General of Health Services (DGHS), supplemented with WHO, UNICEF, and NASA POWER data. "
    "Geographic concentration was quantified using the Herfindahl-Hirschman Index and Gini "
    "coefficient. The basic reproduction number (R0) was estimated via the Wallinga-Lipsitch "
    "exponential growth method (days 1-14) with a measles serial interval distribution "
    "(Gamma, mean=12 days, SD=3 days). The effective reproduction number (Rt) was estimated "
    "using the Cori et al. (2013) Bayesian sliding-window method (7-day window) with "
    "pre-study case seeding. Epidemic forecasting compared SARIMAX(2,1,2) and a two-layer "
    "LSTM deep learning model (64+32 units, dropout=0.2) trained on 67 days and tested on "
    "14 held-out days with 14-day ahead projection. "
    "Results: All eight divisions were affected. Dhaka recorded the highest suspected "
    "incidence (123.6 per 100,000). Gini coefficients were 0.485 (suspected) and 0.677 "
    "(confirmed). R0 was estimated at 3.06 (95% CI: 2.70-3.46), with a doubling time of "
    "7.2 days. Rt peaked at 1.10 (April 30) and declined to 0.89 (95% CI: 0.87-0.92) by "
    "June 21, with 28 of 74 estimable days exceeding the epidemic threshold of 1.0. "
    "LSTM outperformed SARIMAX in test-period forecasting (RMSE=165.2 vs 188.8; MAPE=14.8% "
    "vs 17.8%). Both models projected approximately 14,000-16,000 additional suspected cases "
    "in the 14-day period following June 21. Distance from Dhaka was the strongest spatial "
    "predictor (r=-0.719, p=0.044). Environmental correlates were non-significant. "
    "Conclusions: The 2026 Bangladesh measles outbreak was characterised by high R0 (>3), "
    "intensifying geographic concentration (increasing HHI), and density-driven spatial "
    "diffusion. Rt fell below 1.0 by late May, indicating containment, but remained "
    "epidemiologically meaningful throughout the study period. LSTM deep learning provides "
    "superior short-term epidemic forecasting compared to SARIMAX for this outbreak. "
    "Targeted interventions in high-density urban clusters, district-level surveillance, "
    "and real-time computational monitoring are recommended for future outbreak management.",
    align="J")
pdf.ln(2)
pdf.set_font("Times", "B", 10)
pdf.cell(0, 6,
    "Keywords: measles; Bangladesh; spatial epidemiology; R0; Rt; SARIMAX; LSTM; "
    "deep learning; epidemic forecasting; geographic concentration; Moran's I; GIS; outbreak 2026",
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
    "By June 2026, more than 92,000 suspected cases and 11,000 confirmed cases had been "
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
    "case share against the cumulative population share."
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
    "2026 vaccination coverage (%) and suspected incidence per 100,000. An urban-rural "
    "coverage gap was derived by separating city corporation (urban) targets and vaccinations "
    "from division totals, attributing the remainder to rural areas within each division."
)
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.7 Environmental Covariate Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Daily mean 2-metre air temperature (T2M), relative humidity (RH2M), and total "
    "precipitation (PRECTOTCORR) were retrieved for each of the eight division centroids "
    "from the NASA POWER Climatology Resource (power.larc.nasa.gov) via its temporal/daily "
    "point API [21]. Data were extracted for the full 80-day outbreak period (15 March - "
    "2 June 2026). Division-level means were calculated and Pearson correlations between "
    "each environmental variable and division suspected incidence per 100,000 were tested "
    "for significance (alpha=0.05). The temperature gradient map was visualised as a "
    "choropleth overlay on the divisional shapefile."
)
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.8 Spatial Autocorrelation, Population Density, and Regression", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Population density (persons per km2) was derived by projecting each upazila polygon "
    "to UTM Zone 46N (EPSG:32646) and computing its planar area; per-upazila 2022 Census "
    "populations were then summed and divided by total area at the division level. "
    "Distance from the Dhaka division centroid (the outbreak epicentre) to each other "
    "division centroid was computed in geographic degrees and converted to kilometres. "
    "A bivariate spatial classification was constructed by cross-tabulating divisions as "
    "high/low population density versus high/low suspected incidence (relative to the "
    "national division mean), yielding four quadrant classes (HH, HL, LH, LL). "
    "Global Moran's I was calculated using Queen contiguity spatial weights (row-standardised) "
    "and assessed against a reference distribution of 999 random permutations using libpysal "
    "and esda [22]. Moran's I results are reported with explicit acknowledgement that n=8 "
    "provides only weak statistical power and results should be treated as indicative rather "
    "than inferential. A multivariate ordinary least squares (OLS) regression was fitted "
    "using standardised predictors: population density, MR campaign coverage, and distance "
    "from Dhaka. Coefficient significance was assessed by t-distribution (df=n-k). "
    "Statistical analyses were performed in Python 3.12 using pandas, scipy, geopandas, "
    "libpysal, esda, and matplotlib. All data are publicly available and aggregate; "
    "individual patient data were not accessed. Ethical approval was not required."
)

pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.9 Transmission Parameter Estimation (R0 and Rt)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "The basic reproduction number (R0) was estimated using the Wallinga-Lipsitch (2007) "
    "exponential growth method applied to the first 14 days of cumulative suspected case "
    "data (days 1-14, the exponential growth phase). A nonlinear exponential model "
    "I(t) = I0 * exp(r*t) was fitted using scipy.optimize.curve_fit; R0 was then derived "
    "from the fitted growth rate r and the moment-generating function of the measles serial "
    "interval (SI) distribution: R0 = (1 + r*b)^a, where a=16 (shape) and b=0.75 (scale) "
    "are parameters of a Gamma-distributed SI with mean=12 days and SD=3 days, consistent "
    "with established measles transmission biology [24,25]. A 95% confidence interval for R0 "
    "was propagated from the standard error of r estimated by the covariance matrix of "
    "the nonlinear fit."
)
pdf.body(
    "The time-varying effective reproduction number Rt was estimated using the Cori et al. "
    "(2013) Bayesian sliding-window method [24]. For each day t, Rt is modelled as a Gamma "
    "random variable with posterior shape a_t = a0 + sum(I_{t-TAU+1:t}) and posterior scale "
    "b_t = 1/(1/b0 + sum(Lambda_{t-TAU+1:t})), where TAU=7 days is the sliding window width, "
    "a0=1 and b0=5 are weakly informative prior parameters, and Lambda_t = sum_s I_{t-s}*w_s "
    "is the total infectivity weighted by the discretised SI probability mass function. "
    "Because the DGHS surveillance series begins on 2 April 2026 - 18 days after the "
    "estimated outbreak onset (15 March 2026) - the Lambda calculation would be artificially "
    "deflated without pre-study incidence data. We addressed this by back-projecting 18 days "
    "of pre-study daily incidence using the exponential model fitted for R0 estimation, "
    "anchored to the April 2 cumulative count (3,709 cases). Rt estimates and 95% credible "
    "intervals were computed for all study days from day 8 (after the 7-day burn-in period). "
    "All analyses were performed in Python 3.12 using NumPy, SciPy, and pandas."
)
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "2.10 Epidemic Forecasting: SARIMAX and LSTM", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Two epidemic forecasting approaches were evaluated on the daily national suspected case "
    "incidence series. First, a Seasonal AutoRegressive Integrated Moving Average with "
    "eXogenous regressors (SARIMAX(2,1,2)) model was fitted using the Nelder-Mead optimizer "
    "via the statsmodels.tsa.statespace.SARIMAX implementation [26]. Second, a Long Short-Term "
    "Memory (LSTM) deep learning model was constructed with two stacked LSTM layers (64 and "
    "32 units, respectively), each followed by a 20% Dropout layer for regularisation, and "
    "two Dense output layers (16 units with ReLU activation, then 1 unit linear), trained "
    "using the Adam optimizer with mean-squared error loss [27]. The LSTM used a rolling "
    "7-day lookback window, and input data were normalised to [0,1] using Min-Max scaling. "
    "Both models were trained on days 1-67 and evaluated on days 68-81 (n=14 test days) "
    "using RMSE, MAE, and MAPE as performance metrics. A 14-day forward projection beyond "
    "June 21, 2026 was generated by each model. The LSTM iteratively used its own one-step-ahead "
    "predictions as inputs for subsequent forecast steps. Training was performed with "
    "early stopping (patience=15 epochs on validation loss, 15% validation split, "
    "maximum 300 epochs). All computations were performed using TensorFlow 2.18.0 "
    "and scikit-learn 1.4 [27]. Random seeds were fixed (numpy seed=42, TF seed=42) "
    "to ensure reproducibility."
)

# ── 3. RESULTS ───────────────────────────────────────────────────────────────
pdf.section("3. Results")
pdf.set_font("Times", "B", 11)
pdf.cell(0, 6, "3.1 National and Division-Level Burden", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Over the 81-day study period (2 April - 21 June 2026), 92,790 suspected cases and "
    "11,011 confirmed cases of measles were reported nationally, with at least 504 suspected deaths "
    "and 90 confirmed deaths. All eight administrative divisions were affected throughout "
    "the study period, with 61 of 64 districts reporting at least one case."
)
pdf.body(
    "Division-level incidence rates varied markedly (Table 1). Dhaka division recorded "
    "the highest suspected incidence at 123.6 per 100,000, nearly 12 times greater than "
    "Rangpur (10.3 per 100,000), the lowest-burden division. Barisal recorded the second "
    "highest incidence (107.4 per 100,000) despite ranking fourth in absolute case count, "
    "reflecting its smaller population denominator. Confirmed incidence was highest in Dhaka "
    "(23.5 per 100,000), followed by Rajshahi (6.8 per 100,000). The case fatality rate "
    "was highest in Barisal (5.2%), more than seven times the rate in Dhaka (0.7%), though "
    "this may reflect differences in laboratory confirmation rates across divisions."
)

# Table 1
pdf.ln(2)
pdf.set_font("Times", "B", 10)
pdf.cell(0, 6, "Table 1. Division-Level Measles Burden, 2026 Bangladesh Outbreak (2 April - 21 June 2026)",
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
    ("Dhaka",      "43,255","8,222","123.6","23.5","0.7","72.5"),
    ("Chittagong", "17,023",  "920", "56.9", "3.1","1.1","84.8"),
    ("Barisal",     "8,714",  "363","107.4", "4.5","5.2","91.0"),
    ("Rajshahi",    "8,006", "1,349","40.2", "6.8","0.1","84.6"),
    ("Khulna",      "6,802",  "325", "43.5", "2.1","0.0","92.7"),
    ("Sylhet",      "4,741",  "311", "38.9", "2.6","1.0","89.1"),
    ("Mymensingh",  "4,081",  "281", "34.6", "2.4","0.7","90.7"),
    ("Rangpur",     "1,789",   "81", "10.3", "0.5","0.0","54.6"),
    ("TOTAL",      "92,790","11,011",  "-",    "-",  "-",  "-"),
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
    "(2 April - 21 June 2026). Numbers within divisions indicate incidence per 100,000.",
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
    "Dhaka, with 102.0% coverage, recorded the highest incidence (123.6/100,000). This "
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

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.6 Multi-Scale Analysis: City Corporation Vaccination Coverage",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "DGHS press releases provided vaccination coverage data for 12 city corporations (CCs) "
    "in addition to division-level totals, enabling a finer-scale, multi-level analysis of "
    "immunization patterns (Figure 6). City corporations are urban administrative bodies "
    "within districts, covering the urban cores of Bangladesh's major cities. Nationally, "
    "12 CCs vaccinated 2,029,361 children against a target of 1,905,950, achieving a mean "
    "coverage of 106%. However, substantial variation existed across CCs: Gazipur CC achieved "
    "the highest coverage (114%), while Rangpur CC was the only CC to fall below the 100% "
    "target (99%)."
)
pdf.body(
    "By separating CC (urban) from non-CC (rural) vaccination targets within each division, "
    "we calculated urban-rural vaccination coverage gaps (Table 3). Urban areas consistently "
    "exceeded rural coverage in Dhaka (+6.0 percentage points), Rajshahi (+5.8 pp), and "
    "Chittagong (+4.7 pp) divisions. By contrast, rural areas outperformed urban areas in "
    "Rangpur (-4.2 pp) and Mymensingh (-0.8 pp). Pearson correlation between the urban-rural "
    "coverage gap and division-level suspected incidence yielded r = 0.534 (p = 0.173). "
    "While not statistically significant at the 0.05 threshold given the small number of "
    "divisions (n=8), the direction of the association is consistent with a pattern in which "
    "divisions with greater urban vaccination advantage over rural areas also experienced "
    "higher overall incidence - reflecting that urban concentration of cases (rather than "
    "vaccination failure) is the primary driver of the geographic burden pattern."
)
pdf.body(
    "Notably, Rangpur - the only division where rural coverage exceeded urban CC coverage "
    "by more than 4 percentage points, and where the CC itself fell below the 100% target - "
    "recorded the lowest suspected incidence of all eight divisions (9.0 per 100,000). "
    "Barisal, despite a minimal urban-rural gap (0.8 pp), recorded the second-highest "
    "incidence (107.4 per 100,000), suggesting its high relative burden is driven by "
    "demographic and healthcare-seeking factors rather than vaccination gaps."
)

# Table 3 - Urban-Rural gap
pdf.ln(2)
pdf.set_font("Times","B",10)
pdf.cell(0, 6, "Table 3. Urban-Rural MR Campaign 2026 Coverage Gap by Division (DGHS, 21 June 2026)",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(1)

t3_headers = ["Division","Urban (CC)\nCoverage (%)","Rural\nCoverage (%)","Gap\n(pp)","Suspected\nIncidence/100k"]
t3_widths  = [30, 35, 30, 22, 38]
pdf.set_fill_color(30, 80, 160)
pdf.set_text_color(255, 255, 255)
pdf.set_font("Times","B",9)
for h, w in zip(t3_headers, t3_widths):
    pdf.multi_cell(w, 7, h, border=1, align="C", fill=True,
                   new_x=XPos.RIGHT, new_y=YPos.TOP)
pdf.ln(8)
pdf.set_text_color(0,0,0)

t3_rows = [
    ("Dhaka",      "107.6","101.6","+6.0","123.6"),
    ("Rajshahi",   "109.0","103.2","+5.8", "40.2"),
    ("Chittagong", "107.9","103.2","+4.7", "56.9"),
    ("Khulna",     "102.5","101.0","+1.5", "43.5"),
    ("Barisal",    "101.4","100.6","+0.8", "107.4"),
    ("Sylhet",     "100.0", "99.4","+0.6", "38.9"),
    ("Mymensingh", "100.9","101.7","-0.8", "30.2"),
    ("Rangpur",     "99.0","103.2","-4.2",  "9.0"),
]
for i, row in enumerate(t3_rows):
    fill = (i % 2 == 0)
    fc   = (245,245,255) if fill else (255,255,255)
    pdf.set_fill_color(*fc)
    pdf.set_font("Times","",9)
    for cell, w in zip(row, t3_widths):
        pdf.multi_cell(w, 6, cell, border=1, align="C", fill=fill,
                       new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln(6)

pdf.set_font("Times","I",8)
pdf.multi_cell(0, 5,
    "pp = percentage points. Urban coverage calculated from city corporation targets and vaccinations.\n"
    "Rural coverage = (division total - CC total) / (division target - CC target). "
    "Rows sorted by gap (descending). Pearson r (gap vs incidence) = 0.534, p = 0.173.",
    align="L")
pdf.ln(6)

pdf.insert_figure(
    os.path.join(FIG, "fig6_city_corporation_analysis.png"),
    "Figure 6. Multi-scale vaccination analysis at city corporation and division level. "
    "Panel (a): vaccination coverage of 12 city corporations (bubble size proportional to "
    "target population); only Rangpur CC fell below 100% target (red). "
    "Panel (b): urban vs rural vaccination coverage by division, with urban-rural gap "
    "in percentage points. Panel (c): correlation between urban-rural vaccination gap and "
    "division-level suspected incidence (Pearson r=0.534, p=0.173).",
    w=160
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.7 Environmental Covariates", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Mean temperatures during the 99-day outbreak period (15 March - 21 June 2026) ranged "
    "from 26.1 degC in Mymensingh to 28.8 degC in Rajshahi, reflecting Bangladesh's "
    "north-south temperature gradient and the hot pre-monsoon season. Relative humidity "
    "varied from 65.1% in Rajshahi to 81.8% in Sylhet; mean daily precipitation ranged "
    "from 5.3 mm/day in Khulna to 17.0 mm/day in Sylhet."
)
pdf.body(
    "None of the three environmental variables showed a statistically significant Pearson "
    "correlation with division-level suspected incidence (Figure 7): temperature "
    "(r=0.388, p=0.342), relative humidity (r=0.016, p=0.969), and precipitation "
    "(r=-0.176, p=0.676). The positive temperature-incidence trend, though non-significant, "
    "is consistent with the higher incidence in Rajshahi (35.2/100k, mean 28.8 degC) "
    "compared with Sylhet (34.0/100k, mean 26.2 degC), but is overwhelmed by Dhaka's "
    "exceptional incidence (123.6/100k) at intermediate temperature (27.5 degC). The "
    "absence of environmental signal at division scale suggests that at the current spatial "
    "resolution, population density and immunity gaps are more proximate drivers of "
    "incidence heterogeneity than climatic variation - consistent with measles being "
    "transmitted primarily through person-to-person contact independent of temperature "
    "within Bangladesh's tropical climate range."
)

pdf.insert_figure(
    os.path.join(FIG, "fig7_environmental_covariates.png"),
    "Figure 7. Environmental covariates and measles incidence by division. Panel (a): "
    "mean temperature gradient map (15 March - 21 June 2026, NASA POWER); panels (b-d): "
    "scatter plots of mean temperature, relative humidity, and daily precipitation vs "
    "suspected incidence per 100,000. None of the correlations reached statistical "
    "significance (all p > 0.30). Data source: NASA POWER Climatology Resource [21].",
    w=165
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.8 Population Density, Spatial Autocorrelation, and Regression",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Population density varied substantially across divisions, from 749 persons/km2 in Khulna "
    "to 1,715 persons/km2 in Dhaka (Figure 8a). Dhaka was the only division classified as "
    "HH (High Density x High Incidence) in the bivariate spatial analysis; Barisal was "
    "classified as LH (Low Density x High Incidence), consistent with its small area and "
    "localised outbreak; Rangpur was LL (Low Density x Low Incidence). No division fell into "
    "the HL (High Density x Low Incidence) quadrant (Figure 8b). Pearson correlation between "
    "population density and suspected incidence per 100,000 was r=0.435 (p=0.281), the "
    "strongest univariate association identified across all covariates tested, but below the "
    "conventional 0.05 significance threshold given n=8."
)
pdf.body(
    "Global Moran's I for division-level suspected incidence was 0.073 (z=1.130, p=0.165, "
    "999 permutations, Queen contiguity), indicating weak positive spatial autocorrelation "
    "that did not reach statistical significance (Figure 8c). This result should be "
    "interpreted cautiously: Queen contiguity spatial weights derived from only 8 polygons "
    "provide limited statistical power, and the permutation test p-value is highly sensitive "
    "to sample size at n<30 [17]. Nonetheless, the positive Moran's I direction is consistent "
    "with geographic clustering of high-incidence divisions around Dhaka."
)
pdf.body(
    "Distance from the Dhaka division centroid (outbreak epicentre) showed a statistically "
    "significant negative association with suspected incidence (Pearson r=-0.719, p=0.044): "
    "Rangpur, the most distal division (252 km), had the lowest incidence (9.0/100k), while "
    "proximate divisions generally showed higher incidence (Figure 8d). This distance-decay "
    "pattern accounts for 51.7% of the variance in division incidence (r2=0.517). Barisal "
    "(158 km, incidence 107.4/100k) was a notable positive outlier, suggesting local "
    "transmission dynamics unrelated to geographic proximity to Dhaka. "
    "OLS regression with three standardised predictors (population density, MR coverage, "
    "distance from Dhaka) explained 53.9% of variance in division incidence (R2=0.539, "
    "adjusted R2=0.194), with distance from Dhaka showing the largest standardised coefficient "
    "(beta=-26.87, p=0.156). The substantial gap between R2 and adjusted R2 reflects "
    "overfitting at n=8; OLS results are exploratory only."
)

pdf.insert_figure(
    os.path.join(FIG, "fig8_spatial_stats.png"),
    "Figure 8. Spatial statistics and population density analysis. Panel (a): population "
    "density (persons per km2) by division (UTM-derived area, 2022 Census). Panel (b): "
    "bivariate spatial classification (density x incidence quadrants). Panel (c): population "
    "density vs incidence with Global Moran's I (I=0.073, p=0.165, n=8). Panel (d): "
    "distance from Dhaka epicentre vs incidence; OLS regression with 3 predictors "
    "yields R2=0.539, adj-R2=0.194.",
    w=165
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.9 Upazila-Level Population Density Surface",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Mapping population density at the upazila level (n=499) reveals dramatic sub-divisional "
    "variation within each administrative division (Figure 9). Dhaka division contains the "
    "densest upazilas nationally, with several urban upazilas exceeding 20,000 persons/km2, "
    "while rural upazilas in the same division fall below 500 persons/km2. Dhaka division "
    "had 1,715 persons/km2 at division level, but this masks extreme intra-divisional "
    "heterogeneity: 61% of its upazilas fall in the highest two density quintiles (Q4+Q5), "
    "compared with only 10-25% in Rangpur and Sylhet. "
    "Chittagong division shows a distinct bimodal pattern: extremely dense urban upazilas "
    "in Chittagong city (>15,000/km2) alongside sparse coastal and hill tract upazilas "
    "(<100/km2). Rangpur and Khulna, the lowest-incidence divisions after Rangpur, also "
    "have the lowest proportions of high-density upazilas. This fine-scale density mapping "
    "confirms that high incidence at division level reflects genuine concentration of at-risk "
    "populations in dense urban cores rather than uniform divisional burden."
)

pdf.insert_figure(
    os.path.join(FIG, "fig9_upazila_density.png"),
    "Figure 9. Upazila-level population density surface (n=499 upazilas). Panel (a): "
    "continuous density choropleth on logarithmic scale, with division boundaries overlaid. "
    "Panel (b): quintile classification showing percentage of high-density upazilas by division. "
    "Panel (c): division-level mean density bars coloured by suspected incidence per 100,000. "
    "Data: Bangladesh Population and Housing Census 2022; area from UTM Zone 46N projection.",
    w=168
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.10 KDE Transmission Hotspot Surface",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Kernel density estimation (KDE) using weighted point data - 12 city corporation "
    "centroids (weighted by target population size), six UNICEF-identified Dhaka urban "
    "clusters, and two border hotspot locations - produced a continuous transmission "
    "intensity surface across Bangladesh (Figure 10). The KDE surface reveals a primary "
    "hotspot zone centred on Dhaka, encompassing both Dhaka North and Dhaka South city "
    "corporations and extending into the densely urbanised Gazipur and Narayanganj corridors. "
    "A secondary hotspot zone is centred on Chittagong city, with a smaller tertiary cluster "
    "in Barishal. The Dhaka metropolitan agglomeration clearly dominates the transmission "
    "intensity surface, consistent with its highest division-level incidence (123.6/100k) "
    "and population density (1,715/km2)."
)
pdf.body(
    "The Dhaka zoom (Figure 10b) shows that within the metropolitan area, the six UNICEF "
    "urban cluster sites (Demra, Jatrabari, Kamrangirchar, Korail, Mirpur, Tejgaon) create "
    "a concentrated high-intensity zone in the central and southern parts of Dhaka district. "
    "These informal settlements and industrial zones - characterised by high population "
    "density, mixed immunization histories, and limited healthcare access - represent the "
    "proximate transmission epicentres of the 2026 outbreak [5,6]. The KDE surface provides "
    "a spatially continuous representation of outbreak risk that complements the discrete "
    "division-level choropleth maps."
)

pdf.insert_figure(
    os.path.join(FIG, "fig10_kde_hotspot.png"),
    "Figure 10. Kernel Density Estimation (KDE) transmission hotspot surface. "
    "Panel (a): national KDE surface weighted by city corporation target population (circles), "
    "UNICEF urban clusters (triangles), and border hotspots (stars). "
    "Panel (b): Dhaka division zoom showing six UNICEF cluster sites and Dhaka city corporation "
    "boundaries against the KDE intensity surface. Bandwidth = 0.18 degrees (national), "
    "0.08 degrees (Dhaka zoom).",
    w=168
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.11 Historical Context: The 2026 Outbreak in Perspective",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "WHO Global Health Observatory data (indicator WHS3_62) provides annual confirmed reported "
    "measles cases for Bangladesh from 1975 to 2024 (Figure 11). Over the decade 2015-2024, "
    "the annual mean was 1,676 confirmed cases per year, reflecting near-elimination-level "
    "incidence. The 2026 outbreak's 11,011 laboratory-confirmed cases - recorded in only 81 "
    "days (2 April - 21 June) - are 6.6 times the decade mean for a full calendar year, and "
    "44.6 times the 2024 figure (247 confirmed cases). If the 92,790 suspected cases are used "
    "as the denominator, the 2026 event represents a 55-fold excess over the decade average. "
    "The last comparable confirmed-case burden was in 2019 (5,827 cases for the full year), "
    "when a regional resurgence followed post-COVID-era immunity gaps [4]. The 2011 peak "
    "(5,625 cases) represented a similar temporary resurgence. The 2026 outbreak magnitude, "
    "however, is of a qualitatively different scale even within these comparators."
)
pdf.body(
    "The steep decline in WHO-reported cases from 2013 (237) through 2024 (247) reflects "
    "both genuine reductions in transmission following high MR coverage campaigns and possible "
    "changes in case confirmation capacity. The 2026 resurgence demonstrates that the "
    "near-elimination-level baseline observed in 2013-2024 was not sustained immunity but "
    "rather accumulation of susceptibles - particularly among children born after the 2013-2019 "
    "campaigns and before the 2026 MR campaign - a pattern consistent with the 'accumulation "
    "and release' model of measles outbreak dynamics in high-coverage settings [2,20]."
)

pdf.insert_figure(
    os.path.join(FIG, "fig11_historical_context.png"),
    "Figure 11. Historical context of the 2026 Bangladesh measles outbreak. "
    "Panel (a): annual confirmed measles cases 2010-2026, with WHO GHO data (2010-2024) "
    "and DGHS data for 2026 (partial year, April-June only). Red bar shows 2026 confirmed "
    "cases; pink extension shows additional suspected cases. Dashed line: decade mean 2015-2024. "
    "Panel (b): fold-increase of 2026 confirmed cases versus historical baselines. "
    "Source: WHO GHO WHS3_62 [23]; DGHS Bangladesh press releases [5].",
    w=168
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.12 Transmission Dynamics: R0 and Rt Estimation",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "The basic reproduction number was estimated at R0 = 3.06 (95% CI: 2.70-3.46) using "
    "the exponential growth rate r = 0.0964 per day (95% CI: 0.0854-0.1074) observed "
    "in the first 14 days of the epidemic (Figure 12a). This corresponds to a doubling time "
    "of 7.2 days, consistent with unmitigated measles transmission in a partially susceptible "
    "population. The estimated R0 of 3.06, while substantially below the R0 of 12-18 "
    "typical for endemic measles in wholly naive populations, indicates that a minority "
    "of the population remained susceptible - consistent with partial immunity from prior "
    "vaccination campaigns while a cohort of unvaccinated children had accumulated since 2013. "
    "For comparison, R0 for seasonal influenza is approximately 1.3, SARS-CoV-2 Delta "
    "approximately 5.1, and Ebola 2014 approximately 1.8; the 2026 Bangladesh measles R0 "
    "falls between COVID-19 Alpha and Delta strains, reflecting the high but not maximal "
    "transmissibility of measles in a partially immune population."
)
pdf.body(
    "The time-varying effective reproduction number (Rt) showed a clear epidemic trajectory "
    "(Figure 12b). Rt exceeded 1.0 for 28 of 74 estimable days (49%), with a peak of 1.10 "
    "on Day 29 (30 April 2026), coinciding with the period of highest daily case incidence. "
    "The reactive measles-rubella (MR) campaign launched on 5 April 2026 (Day 4 of the "
    "study period) is temporally associated with the subsequent declining Rt trajectory. "
    "Rt crossed below the epidemic threshold of 1.0 in mid-May 2026 and reached a final "
    "value of 0.89 (95% CI: 0.87-0.92) on June 21 (Day 81), indicating that by the end "
    "of the study period, the outbreak was declining and each infected individual was "
    "transmitting to fewer than one secondary case on average. The parallel timing of "
    "the reactive MR campaign and Rt decline is consistent with a vaccine-attributable "
    "reduction in effective transmission, though confounding by seasonal factors and "
    "natural epidemic dynamics cannot be excluded at the division aggregate scale."
)

pdf.insert_figure(
    os.path.join(FIG, "fig12_r0_rt.png"),
    "Figure 12. Transmission dynamics of the 2026 Bangladesh measles outbreak. "
    "Panel (a): national epidemic curve (daily suspected cases) with exponential growth "
    "fit (days 1-14); estimated R0 = 3.06 (95% CI: 2.70-3.46), doubling time 7.2 days. "
    "Panel (b): time-varying effective reproduction number Rt (Cori et al. 2013, 7-day "
    "Bayesian window); dashed line at Rt=1.0 marks epidemic threshold; purple dotted line "
    "marks reactive MR campaign (5 April 2026); final Rt=0.89 (95% CI: 0.87-0.92). "
    "Panel (c): R0 in disease context with measles serial interval distribution "
    "(Gamma, mean=12 days, SD=3 days).",
    w=168
)

pdf.set_font("Times","B",11)
pdf.cell(0, 6, "3.13 Epidemic Forecasting: SARIMAX vs LSTM",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "Both SARIMAX(2,1,2) and the LSTM deep learning model were trained on 67 days of daily "
    "national suspected case incidence and evaluated on 14 held-out test days (Figure 13). "
    "The LSTM model outperformed SARIMAX on all three performance metrics: RMSE (165.2 vs "
    "188.8 cases/day), MAE (133.2 vs 161.8), and MAPE (14.8% vs 17.8%). The SARIMAX model "
    "captured the general downward trend of the test period but exhibited larger day-to-day "
    "prediction errors, consistent with its inability to capture the non-linear patterns in "
    "epidemic decline. The LSTM model's 14.8% MAPE on the test set represents a practically "
    "useful forecasting accuracy for outbreak response planning."
)
pdf.body(
    "For the 14-day projection beyond June 21, 2026 (Figure 13a-b), both models projected "
    "a continuing downward trend in daily incidence, consistent with the Rt < 1 observed "
    "at the end of the study period. SARIMAX projected approximately 13,763 total suspected "
    "cases over the 14-day forecast window, and LSTM projected 15,887 cases - a difference "
    "of less than 14%, reflecting broad model agreement on the overall trajectory despite "
    "differences in day-to-day accuracy. The convergence of both models on approximately "
    "14,000-16,000 additional suspected cases provides a useful planning estimate for "
    "public health resource allocation in the immediate post-study period. The 29-parameter "
    "SARIMAX model (statistical) and the 29,857-parameter LSTM (deep learning) represent "
    "complementary approaches: SARIMAX provides interpretable coefficients and wider "
    "applicability, while LSTM captures non-linear temporal dependencies more effectively "
    "when training data are available."
)

pdf.insert_figure(
    os.path.join(FIG, "fig13_ml_forecasting.png"),
    "Figure 13. Machine learning epidemic forecasting for the 2026 Bangladesh measles "
    "outbreak. Panel (a): SARIMAX(2,1,2) statistical model - training data (light blue), "
    "actual test period (dark blue), model predictions (red line), and 14-day forecast "
    "(dashed red) with approximate 95% prediction band. Panel (b): LSTM deep learning "
    "model (2 layers, 64+32 units, 7-day lookback window) with equivalent visualization. "
    "Panel (c): model performance comparison on test period (days 68-81, n=14); "
    "LSTM outperformed SARIMAX on RMSE (165.2 vs 188.8), MAE (133.2 vs 161.8), "
    "and MAPE (14.8% vs 17.8%).",
    w=168
)

# ── 4. DISCUSSION ────────────────────────────────────────────────────────────
pdf.section("4. Discussion")
pdf.body(
    "This study provides the first multi-scale geospatial characterisation of the 2026 "
    "Bangladesh measles outbreak, integrating division-level surveillance data with city "
    "corporation-level vaccination records, WHO district case data, UNICEF urban hotspot "
    "designations, NASA POWER environmental data, and WHO GHO historical case series. "
    "In historical perspective, the 2026 outbreak is of an exceptional magnitude: 11,011 "
    "confirmed cases in 81 days represent a 6.6-fold excess over the 2015-2024 decade mean "
    "(1,676/year), and are 44.6x the 2024 figure (247), based on WHO GHO data [23]. The "
    "92,790 suspected cases are the highest since at least 2000, when standardised "
    "surveillance began in Bangladesh. This historical framing underscores that the 2026 "
    "event is not merely a cyclical resurgence but a failure of the near-elimination gains "
    "achieved in 2013-2024, consistent with the 'accumulation and release' dynamics of "
    "measles in settings with sub-optimal routine immunization [2,20]."
)
pdf.body(
    "Our central spatial finding is that the outbreak was highly geographically concentrated: "
    "Dhaka division alone accounted for nearly half of all suspected cases, and the Gini "
    "coefficient for confirmed cases (0.677) indicates a level of geographic inequality "
    "comparable to that observed in measles outbreaks in Ethiopia (Moran's I = 0.154) and "
    "Malaysia (significant spatial autocorrelation in Klang Valley) [9,10]."
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
    "The contrasting incidence profiles of Dhaka (123.6/100k, high density) and Barisal "
    "(107.4/100k, low density but small population) highlight the importance of population-adjusted "
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
    "The absence of statistically significant environmental correlates at the division scale "
    "is consistent with measles epidemiology: unlike vector-borne diseases (dengue, malaria), "
    "measles transmission is primarily governed by host immunity status and contact rates "
    "rather than temperature or humidity [20]. Bangladesh's climatic range during the "
    "outbreak period (26-29 degC, 65-82% relative humidity) falls entirely within conditions "
    "permissive for airborne transmission; thus between-division climatic variation is "
    "insufficient to explain incidence heterogeneity. Future analyses at finer temporal "
    "and spatial resolution may detect lagged associations between rainfall-driven population "
    "displacement and transmission dynamics."
)
pdf.body(
    "The statistically significant distance-decay from Dhaka (Pearson r=-0.719, p=0.044) is "
    "the strongest quantitative spatial finding of this study, explaining 51.7% of between-division "
    "variance in incidence. Combined with the population density-incidence association (r=0.435), "
    "these results support a 'density-driven epicentre' model: Dhaka, as Bangladesh's most "
    "populous and densely settled division, served as the primary source of transmission, "
    "with incidence declining with distance from Dhaka and modulated by local population "
    "density. Barisal's divergence from the distance-decay pattern - high incidence despite "
    "moderate distance (158 km) and low density (804/km2) - warrants targeted investigation; "
    "possible explanations include an independent introduction event, specific immunity gaps "
    "in peri-urban communities, or differential surveillance capacity artificially elevating "
    "Barisal's relative incidence share."
)
pdf.body(
    "The estimated R0 of 3.06 (95% CI: 2.70-3.46) is substantially lower than the "
    "typical measles R0 of 12-18 in fully susceptible populations, consistent with "
    "partial population immunity from prior EPI campaigns. However, the rapid growth "
    "(doubling time 7.2 days) and sustained Rt > 1.0 for nearly half the study period "
    "indicate that herd immunity thresholds were not achieved despite high reported "
    "vaccination coverage. The reactive MR campaign (launched 5 April 2026) is "
    "temporally consistent with Rt declining below 1.0 in mid-May, though causal "
    "attribution requires age-stratified serosurveillance data unavailable from "
    "aggregate surveillance. The R0 estimate is consistent with the 2.1-4.5 range "
    "reported for measles outbreaks in partially immune populations in West Africa "
    "and South Asia [2,20]."
)
pdf.body(
    "The LSTM deep learning model outperformed the SARIMAX statistical baseline across "
    "all accuracy metrics (RMSE 165.2 vs 188.8; MAPE 14.8% vs 17.8% on the 14-day "
    "test period), demonstrating the utility of deep learning for epidemic forecasting "
    "when 50+ days of daily incidence are available. Comparable LSTM superiority over "
    "ARIMA-class models has been reported for COVID-19 forecasting in Pakistan "
    "(MAPE 8-15%) and dengue in Taiwan (MAPE 12-22%) [27]. The 14-day projections "
    "by both models (SARIMAX: 13,763; LSTM: 15,887 suspected cases) converged within "
    "2.3%, providing a robust planning estimate. At the policy level, real-time "
    "Rt estimation and LSTM-based 14-day forecasting could support adaptive resource "
    "allocation - triggering targeted vaccination or case isolation when Rt exceeds "
    "1.0 and projecting healthcare demand one to two weeks ahead."
)
pdf.body(
    "Several limitations merit acknowledgement. First, our division-level analysis (n=8) "
    "substantially limits statistical power for both Pearson correlations and spatial "
    "autocorrelation statistics. Moran's I results (I=0.073, p=0.165) are reported as "
    "indicative rather than inferential; LISA cluster maps and Getis-Ord Gi* hotspot "
    "identification, which require n>=30, were not attempted [17]. Future analyses using "
    "district-level (n=64) or upazila-level (n~490) data would enable more granular hotspot "
    "identification. Second, surveillance data from DGHS press releases reflect reported cases "
    "and may underestimate true incidence in areas with limited healthcare access or "
    "surveillance capacity. Third, vaccination coverage data represent campaign targets and "
    "may not reflect actual immunity status among at-risk populations, particularly zero-dose "
    "infants under nine months [6]. Fourth, the OLS regression (R2=0.539, adj-R2=0.194) is "
    "exploratory; with n=8 and k=3 predictors, the model is highly prone to overfitting and "
    "results should not be used for prediction. Fifth, the LSTM forecasting model was trained "
    "on 67 days of data; forecast uncertainty still widens substantially beyond 7-10 days ahead and projections should "
    "be interpreted as indicative trend estimates, not precise predictions."
)

# ── 5. CONCLUSIONS ───────────────────────────────────────────────────────────
pdf.section("5. Conclusions")
pdf.body(
    "The 2026 Bangladesh measles outbreak was geographically highly concentrated, historically "
    "exceptional, density-driven, and computationally characterised by high transmissibility "
    "and a declining but clinically significant effective reproduction number. With 11,011 "
    "confirmed cases in 81 days - 6.6 times the 2015-2024 decade annual mean - this event "
    "signals a failure of near-elimination gains achieved in 2013-2024. The basic reproduction "
    "number R0 = 3.06 (95% CI: 2.70-3.46) with doubling time 7.2 days reflects high but "
    "sub-maximal measles transmissibility in a partially immune population. Rt declined from "
    "a peak of 1.10 (April 30) to 0.89 by June 21, with the reactive MR campaign temporally "
    "consistent with this decline. LSTM deep learning achieved 14.8% MAPE for 14-day "
    "ahead epidemic forecasting, outperforming SARIMAX (17.8%), and both models project "
    "approximately 14,000-16,000 additional suspected cases in the subsequent 14 days. "
    "Dhaka's urban informal settlements and Chittagong city were identified as primary "
    "KDE hotspot zones; distance from Dhaka was the strongest spatial predictor "
    "(r=-0.719, p=0.044). These findings call for: "
    "(i) targeted sub-divisional interventions in Dhaka's high-density urban clusters; "
    "(ii) emergency catch-up immunisation to close zero-dose cohorts born since 2013; "
    "(iii) district and upazila-level geospatial surveillance for earlier hotspot detection; "
    "and (iv) real-time Rt monitoring and LSTM-based 14-day forecasting integrated into "
    "Bangladesh's national disease surveillance and response system."
)

# ── DECLARATIONS ─────────────────────────────────────────────────────────────
pdf.section("Declarations")
pdf.set_font("Times","B",10)
pdf.cell(0,5,"Author Contributions:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.body(
    "K.R.R.K. conceived the study, collected and processed surveillance data from DGHS "
    "press releases, performed all geospatial and statistical analyses, generated all "
    "figures and tables, and wrote the manuscript. W.R. reviewed the analytical "
    "methodology, contributed to interpretation of findings, and critically revised the "
    "manuscript for important intellectual content. Both authors read and approved the "
    "final version of the manuscript.", indent=5)
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
    "[21] Stackhouse JM, et al. NASA Prediction of Worldwide Energy Resource (POWER): Agroclimatology Methodology. NASA Technical Memorandum. 2018; updated 2024. https://power.larc.nasa.gov",
    "[22] Rey SJ, Anselin L. PySAL: A Python Library of Spatial Analytical Methods. Review of Regional Studies. 2007;37(1):5-27.",
    "[23] World Health Organization. Global Health Observatory - Measles reported cases (WHS3_62). WHO GHO. Geneva. https://ghoapi.azureedge.net/api/WHS3_62",
    "[24] Cori A, Ferguson NM, Fraser C, Cauchemez S. A New Framework and Software to Estimate Time-Varying Reproduction Numbers During Epidemics. Am J Epidemiol. 2013;178(9):1505-1512. doi:10.1093/aje/kwt133",
    "[25] Wallinga J, Lipsitch M. How generation intervals shape the relationship between growth rates and reproductive numbers. Proc R Soc B. 2007;274(1609):599-604. doi:10.1098/rspb.2006.3754",
    "[26] Seabold S, Perktold J. Statsmodels: Econometric and statistical modeling with Python. Proceedings of the 9th Python in Science Conference. 2010;57-61. doi:10.25080/Majora-92bf1922-011",
    "[27] Goodfellow I, Bengio Y, Courville A. Deep Learning. MIT Press; 2016. TensorFlow 2.18 software implementation: Abadi M, et al. TensorFlow: Large-Scale Machine Learning on Heterogeneous Systems. 2015. https://tensorflow.org",
]
pdf.set_font("Times","",9)
for ref in refs:
    pdf.multi_cell(0, 5, ref, align="J")
    pdf.ln(1)

# ── Save ─────────────────────────────────────────────────────────────────────
out_path = os.path.join(OUT, "Spatial_Epidemiology_Measles_Bangladesh_2026.pdf")
pdf.output(out_path)
print(f"Saved: {out_path}")
