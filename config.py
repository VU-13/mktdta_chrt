"""
Configuration for the EV/EBITDA sector multiples pipeline.

Edit tickers, weights, or discounts here as your comp set evolves —
fetch_multiples.py never needs to change for that.

Ticker suffixes follow Yahoo Finance conventions:
  .DE Germany (Xetra)        .PA France (Euronext Paris)
  .MI Italy (Milan)          .AS Netherlands (Amsterdam)
  .BR Belgium (Brussels)     .LS Portugal (Lisbon)
  .L  UK (London)            .ST Sweden (Stockholm)
  .HE Finland (Helsinki)     .CO Denmark (Copenhagen)
  (no suffix = US-listed, NYSE/Nasdaq)

NOTE: this is a first-draft basket built from general market knowledge,
not verified against live data. The first run will print [skip]/[error]
for any ticker yfinance can't resolve or that has no EV/EBITDA populated
(delisted, acquired, renamed, data gap) — prune/replace those as they show up.
"""

SECTORS = {
    "saas": {
        "label": "SaaS",
        "discount": 0.25,
        "weights": {"EU": 0.5, "US": 0.5},
        "companies": {
            "EU": ["NEM.DE", "SGE.L"],              # Nemetschek, Sage Group
            "US": ["MNDY", "PD", "FRSH"],           # monday.com, PagerDuty, Freshworks
        },
    },
    "it_services": {
        "label": "IT Services",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["SOP.PA", "REY.MI", "BC8.DE", "COK.DE", "ATE.PA"],  # Sopra Steria, Reply, Bechtle, Cancom, Alten
            "US": ["DAVA", "GDYN"],                 # Endava, Grid Dynamics (replaces PRFT/Perficient, taken private Oct 2024)
        },
    },
    "manufacturing": {
        "label": "Manufacturing",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["AALB.AS", "AAG.DE", "BOY.L", "ROR.L", "TRI.L"],  # Aalberts, Aumann, Bodycote, Rotork, Trifast (replaces Renold, being taken private)
            "US": ["MLI"],                          # Mueller Industries
        },
    },
    "healthcare_services": {
        "label": "Healthcare Services",
        "discount": 0.25,
        "weights": {"EU": 0.5, "US": 0.5},
        "companies": {
            "EU": ["KORI.PA", "FRE.DE"],             # Korian, Fresenius SE (Helios hospitals) -- Fresenius is larger than the sector's mid-cap target, added for reliable EU coverage since Korian alone keeps returning no data
            "US": ["CYH", "EHC", "ENSG", "MODV"],   # Community Health, Encompass Health (replaces SEM/Select Medical, taken private Jun 2026), Ensign, ModivCare
        },
    },
    "logistics": {
        "label": "Logistics",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["PNL.AS", "BPOST.BR", "CTT.LS", "STF.PA", "DSV.CO"],  # PostNL, bpost, CTT, Stef (replaces Wincanton, acquired by GXO), DSV
            "US": ["ARCB"],                         # ArcBest
        },
    },
    "ecommerce": {
        "label": "E-commerce",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["ZAL.DE", "GFG.DE", "CDON.ST", "ASC.L", "DEBS.L"],  # Zalando, Global Fashion Group (replaces About You, delisted), CDON, ASOS, Debenhams Group (boohoo's new ticker, same company)
            "US": ["FLWS", "SFIX", "ETSY"],         # 1-800-Flowers, Stitch Fix, Etsy (added -- usually profitable, should fix the recurring no-data weeks)
        },
    },
    "telecom": {
        "label": "Telecom",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["FNTN.DE", "UTDI.DE", "ELISA.HE", "TEL2-B.ST"],  # freenet, United Internet, Elisa, Tele2
            "US": ["SHEN"],                         # Shenandoah Telecom
        },
    },
}

HISTORY_FILE = "history.csv"
BVB_MANUAL_FILE = "bvb_manual.csv"
LATEST_OUTPUT_FILE = "latest.json"
ROLLING_WINDOW_DAYS = 92  # ~3 months, used for the rolling average

# Individual company EV/EBITDA readings outside this range are treated as
# outliers/data errors and excluded from the sector average (e.g. a near-zero
# EBITDA blowing up the ratio, or a stale/bad data point from the source).
MIN_PLAUSIBLE_MULTIPLE = 3
MAX_PLAUSIBLE_MULTIPLE = 80
