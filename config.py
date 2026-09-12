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
    "b2b_services": {
        "label": "B2B Services",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["PAGE.L", "RWA.L", "STEM.L", "MRL.L"],  # PageGroup, Robert Walters, SThree, Marlowe
            "US": ["EFOR", "HSII"],                 # Everforth (renamed from ASGN Incorporated, Apr 2026), Heidrick & Struggles
        },
    },
    "cosmetics_beauty": {
        "label": "Cosmetics / Beauty",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["ITP.PA", "PZC.L"],              # Interparfums SA, PZ Cussons
            "US": ["ELF", "IPAR", "OLPX"],          # e.l.f. Beauty, Inter Parfums Inc, Olaplex
        },
    },
    "food": {
        "label": "Food",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["CWK.L", "GNC.L", "BON.PA", "FIF.L"],  # Cranswick, Greencore, Bonduelle, Finsbury Food Group (replaces Bakkavor, acquired by Greencore & delisted Jan 2026)
            "US": ["JBSS", "LANC", "SMPL"],         # John B. Sanfilippo & Son, Lancaster Colony, Simply Good Foods
        },
    },
    "fmcg": {
        "label": "FMCG",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["MCB.L", "FEVR.L"],              # McBride, Fever-Tree Drinks
            "US": ["CENT", "WDFC", "NUS"],          # Central Garden & Pet, WD-40, Nu Skin Enterprises
        },
    },
    "travel_services": {
        "label": "Travel Services",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["OTB.L", "JET2.L", "TUI1.DE"],   # On the Beach, Jet2, TUI AG
            "US": ["SABR", "TRVG", "TNL"],          # Sabre Corporation, trivago, Travel + Leisure Co
        },
    },
    "automotive": {
        "label": "Automotive",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["GMM.DE", "SFQ.DE", "POM.PA"],   # Grammer, SAF-Holland, Plastic Omnium
            "US": ["DORM", "MOD", "SMP"],           # Dorman Products, Modine Manufacturing, Standard Motor Products
        },
    },
    "utilities": {
        "label": "Utilities",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["PNN.L", "SVT.L"],               # Pennon Group, Severn Trent
            "US": ["AVA", "UTL", "MGEE", "NWE"],    # Avista, Unitil, MGE Energy, NorthWestern Energy
        },
    },
    "oil_gas": {
        "label": "Oil & Gas",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["TLW.L", "HBR.L", "SQZ.L"],      # Tullow Oil, Harbour Energy, Serica Energy
            "US": ["RRC", "MTDR", "CIVI"],          # Range Resources, Matador Resources, Civitas Resources
        },
    },
    "energy": {
        "label": "Energy",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            # Encavis and Neoen -- the two obvious EU renewable-energy comps -- were both
            # taken private in 2024/2025, so this bucket leans on smaller/thinner names;
            # expect it may need attention sooner than the others.
            "EU": ["VLTSA.PA", "SLR.MC"],           # Voltalia, Solaria Energía
            "US": ["ORA", "CWEN", "BE"],            # Ormat Technologies, Clearway Energy, Bloom Energy
        },
    },
    "defense": {
        "label": "Defense",
        "discount": 0.25,
        "weights": {"EU": 0.8, "US": 0.2},
        "companies": {
            "EU": ["QQ.L", "CHG.L", "HAG.DE", "R3NK.DE"],  # QinetiQ, Chemring, Hensoldt, Renk Group
            "US": ["KTOS", "MRCY", "VVX"],          # Kratos Defense, Mercury Systems, V2X
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
