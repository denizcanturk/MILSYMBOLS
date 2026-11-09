import tkinter as tk
from tkinter import ttk, messagebox

class MilStd2525EApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MIL-STD-2525E SIDC Oluşturucu ve Çözümleyici")
        self.root.geometry("950x820")
        self.init_data()
        self.build_ui()
        self.on_symset_change(init_mode=True)

    def init_data(self):
        # SET A Tabloları (Tablo A-I .. A-VIII)
        self.versions = {
            "13 - MIL-STD-2525E": "13", "12 - APP-06(D)(2)": "12",
            "11 - MIL-STD-2525D(1)": "11", "10 - MIL-STD-2525D / APP-06(D)(1)": "10"
        }
        self.contexts = {
            "0 - Reality": "0", "1 - Exercise": "1", "2 - Simulation": "2",
            "3 - Restricted Target - Reality": "3", "4 - No-Strike Entity - Reality": "4",
            "5 - Restricted Target - Exercise": "5", "6 - No-Strike Entity - Exercise": "6",
            "7 - Restricted Target - Simulation": "7", "8 - No-Strike Entity - Simulation": "8"
        }
        self.identities = {
            "0 - Pending": "0", "1 - Unknown": "1", "2 - Assumed Friend": "2",
            "3 - Friend": "3", "4 - Neutral": "4", "5 - Suspect/Joker": "5", "6 - Hostile/Faker": "6"
        }
        self.symbol_sets = {
            "00 - Unknown": "00", "01 - Air": "01", "02 - Air Missile": "02",
            "05 - Space": "05", "06 - Space Missile": "06", "10 - Land Unit": "10",
            "11 - Land Civilian Unit/Org": "11", "15 - Land Equipment": "15",
            "20 - Land Installation": "20", "25 - Control Measure": "25",
            "27 - Dismounted Individuals": "27", "30 - Sea Surface": "30",
            "35 - Sea Subsurface": "35", "36 - Mine Warfare": "36",
            "40 - Activities": "40", "45 - Atmospheric": "45",
            "46 - Oceanographic": "46", "47 - Meteorological Space": "47",
            "50 - Signals Intelligence (SIGINT)": "50", "60 - Cyberspace - Virtual": "60"
        }
        self.statuses = {
            "0 - Present": "0", "1 - Planned/Anticipated/Suspect": "1",
            "2 - Present/Fully capable": "2", "3 - Present/Damaged": "3",
            "4 - Present/Destroyed": "4", "5 - Present/Full to capacity": "5"
        }
        self.hq_tf = {
            "0 - Unknown (No Statement)": "0", "1 - Feint/Decoy/Dummy": "1",
            "2 - Headquarters": "2", "3 - Feint/Dummy Headquarters": "3",
            "4 - Task Force": "4", "5 - Feint/Dummy Task Force": "5",
            "6 - Task Force Headquarters": "6", "7 - Feint/Dummy Task Force HQ": "7"
        }
        self.amplifiers = {
            "00 - Unknown (No Statement)": "00", "11 - Team/Crew": "11", "12 - Squad": "12",
            "13 - Section": "13", "14 - Platoon/detachment": "14", "15 - Company/battery/troop": "15",
            "16 - Battalion/squadron": "16", "17 - Regiment/group": "17", "18 - Brigade": "18",
            "21 - Division": "21", "22 - Corps/MEF": "22", "23 - Army": "23",
            "24 - Army Group/front": "24", "25 - Region/Theater": "25", "26 - Command": "26",
            "31 - Wheeled limited cross country": "31", "32 - Wheeled cross country": "32",
            "33 - Tracked": "33", "34 - Wheeled and tracked": "34", "35 - Towed": "35",
            "36 - Rail": "36", "37 - Pack animals": "37", "41 - Over snow": "41", "42 - Sled": "42",
            "51 - Barge": "51", "52 - Amphibious": "52", "61 - Short towed array": "61",
            "62 - Long towed Array": "62", "71 - Leader Individual": "71"
        }

        # Tablo A-IX & A-X: Common Modifiers
        self.common_s1 = {
            "000 - Yok (Set Özel Mod. Kullan)": "000", "100 - UAV/UAS/RPV": "100", "101 - Robotic": "101",
            "102 - Fixed Wing": "102", "103 - Rotary Wing": "103", "104 - Tilt-Rotor": "104",
            "105 - VSTOL/VTOL": "105", "106 - Attack/Strike": "106", "107 - Armored": "107",
            "108 - Ballistic Missile/BMD": "108", "109 - Bridge": "109", "110 - Cargo": "110",
            "111 - Utility": "111", "112 - Light": "112", "113 - Medium": "113", "114 - Heavy": "114",
            "115 - Cyberspace": "115", "116 - Command Post Node": "116", "117 - Joint Network Node": "117",
            "118 - Retransmission Site": "118", "119 - Brigade Support": "119", "120 - Close Protection": "120",
            "121 - Combat": "121", "122 - Command and Control": "122", "123 - Crowd/Riot Control": "123",
            "124 - EOD": "124", "125 - ISR": "125", "126 - Maintenance": "126", "127 - Medevac/Medical": "127",
            "128 - Search and Rescue": "128", "129 - Security": "129", "130 - Sniper": "130",
            "131 - SOF": "131", "132 - SWAT": "132", "133 - Guided Missile": "133",
            "134 - Other Guided Missile": "134", "135 - POL": "135", "136 - Water": "136",
            "137 - Weapon(s)": "137", "138 - Chemical": "138", "140 - Radiological": "140",
            "141 - Nuclear": "141", "142 - Decontamination": "142", "143 - Civilian": "143",
            "144 - Government Org": "144", "145 - Accident": "145", "146 - Assassination": "146",
            "147 - Execution": "147", "148 - Kidnapping": "148", "149 - Piracy": "149", "150 - Rape": "150",
            "151 - ASW": "151", "152 - Escort": "152", "153 - Mine Countermeasures": "153",
            "154 - Mine Warfare": "154", "155 - Surface Warfare": "155", "156 - Command Support": "156",
            "157 - Company Support": "157", "158 - Platoon Support": "158", "159 - Regiment Support": "159",
            "160 - Section Support": "160", "161 - Squad Support": "161", "162 - Team/Crew Support": "162",
            "163 - Battalion Support": "163", "164 - Directed Energy": "164", "165 - Hijacker": "165"
        }
        self.common_s2 = {
            "000 - Yok (Set Özel Mod. Kullan)": "000", "100 - Airborne": "100", "101 - Bicycle": "101",
            "102 - Railroad/Railway": "102", "103 - Ski": "103", "104 - Tracked": "104",
            "105 - Wheeled (Limited XC)": "105", "106 - Wheeled X (XC)": "106", "107 - Fixed Wing": "107",
            "108 - Rotary Wing": "108", "109 - Robotic": "109", "110 - Autonomous Control": "110",
            "111 - Remotely Piloted": "111", "112 - Expendable": "112", "113 - Mountain": "113",
            "114 - Long Range": "114", "115 - Medium Range": "115", "116 - Short Range": "116",
            "117 - Close Range": "117", "118 - Heavy": "118", "119 - Medium": "119",
            "120 - Light and Medium": "120", "121 - Light": "121", "122 - Cyberspace": "122",
            "123 - Security Force Assistance": "123", "124 - Medical Bed": "124", "125 - Multifunctional": "125"
        }

        # Tablo A-LX: Frame Shape
        self.frames = {
            "0 - Unknown": "0", "1 - Space": "1", "2 - Air": "2", "3 - Land Unit": "3",
            "4 - Land Equip/Sea Surface": "4", "5 - Land Installation": "5", "6 - Dismounted Ind": "6",
            "7 - Sea Subsurface": "7", "8 - Activity/Event": "8", "9 - Cyberspace": "9", "A - Unframed": "A"
        }
        self.def_frame = {
            "00": "0 - Unknown", "01": "2 - Air", "02": "2 - Air", "05": "1 - Space", "06": "1 - Space",
            "10": "3 - Land Unit", "11": "3 - Land Unit", "15": "4 - Land Equip/Sea Surface",
            "20": "5 - Land Installation", "25": "A - Unframed", "27": "6 - Dismounted Ind",
            "30": "4 - Land Equip/Sea Surface", "35": "7 - Sea Subsurface", "36": "7 - Sea Subsurface",
            "40": "8 - Activity/Event", "45": "A - Unframed", "46": "A - Unframed",
            "47": "A - Unframed", "50": "0 - Unknown", "60": "9 - Cyberspace"
        }

        # SET B Veritabanı (Tablo A-XI .. A-LIX)
        self.db = {
            "00": {"e": {"000000 - Unspecified": "000000"}, "s1": {"00 - Unspecified": "00"}, "s2": {"00 - Unspecified": "00"}},
            "01": {
                "e": {
                    "120100 - Civilian -> Fixed Wing": "120100", "120000 - Civilian": "120000",
                    "120200 - Civilian -> Rotary Wing": "120200", "120300 - Civilian -> UAV/UAS/RPV": "120300",
                    "120400 - Civilian -> Lighter Than Air": "120400", "120500 - Civilian -> Airship": "120500",
                    "120600 - Civilian -> Tethered LTA": "120600", "110000 - Military": "110000",
                    "110100 - Military -> Fixed Wing": "110100", "110101 - Military -> FW -> MEDEVAC": "110101",
                    "110102 - Military -> FW -> Attack/Strike": "110102", "110103 - Military -> FW -> Bomber": "110103",
                    "110104 - Military -> FW -> Fighter": "110104", "110105 - Military -> FW -> Fighter/Bomber": "110105",
                    "110107 - Military -> FW -> Cargo": "110107", "110108 - Military -> FW -> EC/Jammer": "110108",
                    "110109 - Military -> FW -> Tanker": "110109", "110110 - Military -> FW -> Patrol": "110110",
                    "110111 - Military -> FW -> Reconnaissance": "110111", "110112 - Military -> FW -> Trainer": "110112",
                    "110113 - Military -> FW -> Utility": "110113", "110114 - Military -> FW -> VSTOL": "110114",
                    "110115 - Military -> FW -> ACP": "110115", "110116 - Military -> FW -> AEW": "110116",
                    "110117 - Military -> FW -> Antisurface Warfare": "110117", "110118 - Military -> FW -> ASW": "110118",
                    "110119 - Military -> FW -> Communications": "110119", "110120 - Military -> FW -> CSAR": "110120",
                    "110121 - Military -> FW -> Electronic Support (ES)": "110121", "110122 - Military -> FW -> Government": "110122",
                    "110123 - Military -> FW -> Mine Countermeasures": "110123", "110124 - Military -> FW -> Personnel Recovery": "110124",
                    "110125 - Military -> FW -> Search and Rescue": "110125", "110126 - Military -> FW -> SOF": "110126",
                    "110127 - Military -> FW -> Ultra Light": "110127", "110128 - Military -> FW -> Photo Recon": "110128",
                    "110129 - Military -> FW -> VIP": "110129", "110130 - Military -> FW -> SEAD": "110130",
                    "110131 - Military -> FW -> Passenger": "110131", "110132 - Military -> FW -> Escort": "110132",
                    "110133 - Military -> FW -> Electromagnetic Attack (EA)": "110133", "110200 - Military -> Rotary Wing": "110200",
                    "110300 - Military -> UAV/UAS/RPV": "110300", "110400 - Military -> VT-UAV": "110400",
                    "110500 - Military -> Lighter Than Air": "110500", "110600 - Military -> Airship": "110600",
                    "110700 - Military -> Tethered LTA": "110700", "130000 - Weapon": "130000",
                    "130100 - Weapon -> Bomb": "130100", "130200 - Weapon -> Decoy": "130200",
                    "140000 - Manual Track": "140000", "000000 - Unspecified": "000000"
                },
                "s1": {
                    "09 - Passenger (Airliner)": "09", "00 - Not Applicable (No Statement)": "00",
                    "01 - Attack/Strike": "01", "02 - Bomber": "02", "03 - Cargo": "03", "04 - Fighter": "04",
                    "05 - Interceptor": "05", "06 - Tanker": "06", "07 - Utility": "07", "08 - VSTOL/VTOL": "08",
                    "22 - ASW": "22", "25 - Mine Countermeasures": "25", "26 - Search and Rescue": "26",
                    "10 - Ultra Light": "10", "11 - ACP": "11", "12 - AEW": "12", "16 - EC/Jammer": "16",
                    "17 - Patrol": "17", "18 - Reconnaissance": "18", "19 - Trainer": "19", "20 - Photo Recon": "20",
                    "21 - Personnel Recovery": "21", "23 - Communications": "23", "24 - Electronic Support (ES)": "24",
                    "29 - VIP Transport": "29", "30 - CSAR": "30", "32 - Antisurface Warfare": "32",
                    "33 - Fighter/Bomber": "33", "34 - Intensive Care": "34", "35 - Electromagnetic Attack (EA)": "35",
                    "36 - Multi-Mission": "36", "38 - ASW Helo LAMPS": "38", "39 - ASW Helo SH-60R": "39"
                },
                "s2": {
                    "00 - Not Applicable (No Statement)": "00", "01 - Heavy": "01", "02 - Medium": "02",
                    "03 - Light": "03", "04 - Boom-Only": "04",
                    "05 - Drogue-Only": "05", "06 - Boom and Drogue": "06", "11 - Downlinked": "11"
                }
            },
            "02": {
                "e": {"110000 - Missile": "110000", "000000 - Unspecified": "000000"},
                "s1": {
                    "00 - Unspecified": "00", "01 - Air Origin": "01", "02 - Surface Origin": "02",
                    "03 - Subsurface Origin": "03", "04 - Space Origin": "04", "05 - Anti-Ballistic": "05",
                    "06 - Ballistic": "06", "07 - Cruise": "07", "08 - Interceptor": "08", "09 - Hypersonic": "09"
                },
                "s2": {
                    "00 - Unspecified": "00", "01 - Air Dest": "01", "02 - Surface Dest": "02",
                    "03 - Subsurface Dest": "03", "04 - Space Dest": "04", "05 - Launched": "05",
                    "07 - Patriot": "07", "08 - SM-2": "08", "09 - SM-6": "09", "10 - ESSM": "10",
                    "11 - RAM": "11", "12 - Short Range": "12", "13 - Medium Range": "13",
                    "14 - Intermediate Range": "14", "15 - Long Range": "15", "16 - Intercontinental": "16"
                }
            },
            "05": {
                "e": {
                    "110000 - Military": "110000", "110100 - Military -> Space Vehicle": "110100",
                    "110200 - Military -> Re-Entry Vehicle": "110200", "110700 - Military -> Satellite": "110700",
                    "110800 - Military -> ASAT Weapon": "110800", "111100 - Military -> Comms Satellite": "111100",
                    "111200 - Military -> Earth Obs Satellite": "111200", "111400 - Military -> Nav Satellite": "111400",
                    "111500 - Military -> Recon Satellite": "111500", "111600 - Military -> Space Station": "111600",
                    "111800 - Military -> Weather Satellite": "111800", "120000 - Civilian": "120000",
                    "120300 - Civilian -> Satellite": "120300", "120600 - Civilian -> Comms Satellite": "120600",
                    "120900 - Civilian -> Nav Satellite": "120900", "121200 - Civilian -> Weather Satellite": "121200",
                    "130000 - Manual Track": "130000", "000000 - Unspecified": "000000"
                },
                "s1": {
                    "00 - Unspecified": "00", "01 - LEO": "01", "02 - MEO": "02", "03 - HEO": "03",
                    "04 - GSO": "04", "05 - GO": "05", "06 - Molniya (MO)": "06"
                },
                "s2": {
                    "00 - Unspecified": "00", "01 - Optical": "01", "02 - Infrared": "02", "03 - Radar": "03",
                    "04 - SIGINT": "04", "06 - EW (ASAT)": "06", "07 - HPM (ASAT)": "07", "08 - Laser (ASAT)": "08",
                    "09 - Mine (ASAT)": "09", "10 - Maintenance": "10", "11 - Refuel": "11", "12 - Tug": "12"
                }
            },
            "06": {
                "e": {"110000 - Missile": "110000", "000000 - Unspecified": "000000"},
                "s1": {"00 - Unspecified": "00", "01 - Ballistic": "01", "02 - Space": "02", "03 - Interceptor": "03", "04 - Hypersonic": "04"},
                "s2": {
                    "00 - Unspecified": "00", "01 - Short Range": "01", "02 - Medium Range": "02",
                    "03 - Intermediate Range": "03", "04 - Long Range": "04", "05 - Intercontinental": "05",
                    "06 - Arrow": "06", "07 - GBI": "07", "08 - Patriot": "08", "09 - SM-T": "09",
                    "10 - SM-3": "10", "11 - THAAD": "11", "12 - Space": "12", "13 - CRBM": "13",
                    "14 - Debris": "14", "15 - Unknown": "15"
                }
            },
            "10": {
                "e": {
                    "110000 - Command and Control": "110000", "110700 - C2 -> Radio": "110700",
                    "111000 - C2 -> Signal": "111000", "111500 - C2 -> Multi-Domain Ops": "111500",
                    "120000 - Movement and Maneuver": "120000", "120200 - Maneuver -> Air Traffic Services": "120200",
                    "120400 - Maneuver -> Antitank/Antiarmor": "120400", "120401 - Maneuver -> Antitank -> Armored": "120401",
                    "120402 - Maneuver -> Antitank -> Motorized": "120402", "120500 - Maneuver -> Armor/Mechanized": "120500",
                    "120600 - Maneuver -> Army Aviation Rotary": "120600", "120800 - Maneuver -> Aviation Fixed Wing": "120800",
                    "121100 - Maneuver -> Infantry": "121100", "121102 - Maneuver -> Infantry -> Mechanized": "121102",
                    "121104 - Maneuver -> Infantry -> Motorized": "121104", "121300 - Maneuver -> Recon/Cavalry/Scout": "121300",
                    "121700 - Maneuver -> Special Forces": "121700", "121800 - Maneuver -> SOF": "121800",
                    "121900 - Maneuver -> UAS": "121900", "130000 - Fires": "130000",
                    "130100 - Fires -> Air Defense": "130100", "130102 - Fires -> Air Defense -> Missile": "130102",
                    "130103 - Fires -> Air and Missile Defense": "130103", "130300 - Fires -> Field Artillery": "130300",
                    "130700 - Fires -> Missile": "130700", "130800 - Fires -> Mortar": "130800",
                    "140000 - Protection": "140000", "140100 - Protection -> CBRN Defense": "140100",
                    "140700 - Protection -> Engineer": "140700", "140800 - Protection -> EOD": "140800",
                    "141200 - Protection -> Military Police": "141200", "142200 - Protection -> Missile Defense": "142200",
                    "150000 - Intelligence": "150000", "150500 - Intelligence -> EW": "150500",
                    "150503 - Intelligence -> EW -> Intercept": "150503", "150504 - Intelligence -> EW -> Jamming": "150504",
                    "151000 - Intelligence -> Military Intelligence": "151000", "160000 - Sustainment": "160000",
                    "161100 - Sustainment -> Maintenance": "161100", "161300 - Sustainment -> Medical": "161300",
                    "162500 - Sustainment -> POL": "162500", "163600 - Sustainment -> Transportation": "163600",
                    "170000 - Naval": "170000", "180000 - Named HQ": "180000", "190000 - Emergency Op": "190000",
                    "200000 - Law Enforcement": "200000", "210000 - Cyber": "210000", "000000 - Unspecified": "000000"
                },
                "s1": {
                    "00 - Unspecified": "00", "01 - Tactical Satcom": "01", "02 - Area": "02", "25 - FDC": "25",
                    "27 - Forward": "27", "32 - Meteorological": "32", "34 - Missile": "34", "41 - MRL": "41",
                    "47 - UAS": "47", "50 - Radar": "50", "55 - Sensor": "55", "57 - SIGINT": "57",
                    "68 - Target Acquisition": "68", "88 - Network Ops": "88", "98 - HQ Element": "98", "99 - MDO": "99"
                },
                "s2": {
                    "00 - Unspecified": "00", "02 - Arctic": "02", "06 - Clearing": "06", "08 - Control": "08",
                    "16 - High Altitude": "16", "21 - Launcher": "21", "23 - Low Altitude": "23",
                    "25 - Medium Altitude": "25", "35 - Radio Relay LOS": "35", "44 - Strategic": "44",
                    "45 - Support": "45", "46 - Tactical": "46", "47 - Towed": "47", "59 - Air Assault": "59",
                    "60 - Amphibious": "60", "84 - Jamming": "84", "89 - Air Defense": "89"
                }
            },
            "11": {
                "e": {
                    "110000 - Civilian": "110000", "110100 - Environmental Protection": "110100",
                    "110200 - Government Organization": "110200", "110300 - Individual": "110300",
                    "110400 - Organization or Group": "110400", "111000 - Emergency Medical Op": "111000",
                    "000000 - Unspecified": "000000"
                },
                "s1": {"00 - Unspecified": "00", "09 - Refugee/Evacuee": "09", "14 - NGO": "14", "19 - Terrorist Org": "19"},
                "s2": {"00 - Unspecified": "00", "01 - Leader or Leadership": "01"}
            },
            "15": {
                "e": {
                    "110000 - Weapon System": "110000", "110100 - Rifle": "110100", "110200 - Machine Gun": "110200",
                    "110500 - Air Defense Gun": "110500", "110900 - Howitzer": "110900", "111000 - Missile Launcher": "111000",
                    "111100 - Air Defense Missile Launcher": "111100", "111102 - Light TLAR": "111102",
                    "111103 - Light TELAR": "111103", "111200 - Antitank Missile Launcher": "111200",
                    "111300 - SSM Launcher": "111300", "120000 - Vehicle": "120000", "120101 - AFV": "120101",
                    "120103 - APC": "120103", "120200 - Tank": "120200", "130000 - Engineer Vehicle": "130000",
                    "140000 - Utility Vehicle": "140000", "150000 - Train": "150000", "160000 - Civilian Vehicle": "160000",
                    "200000 - Other Equipment": "200000", "200500 - Computer System": "200500",
                    "210000 - Land Mines": "210000", "220000 - Sensors": "220000", "220300 - Sensors -> Radar": "220300",
                    "240000 - Manual Track": "240000", "000000 - Unspecified": "000000"
                },
                "s1": {"00 - Unspecified": "00", "01 - Biological": "01", "03 - Early Warning Radar": "03", "07 - Upgraded EW Radar": "07"},
                "s2": {"00 - Unspecified": "00", "06 - Tractor Trailer": "06"}
            },
            "20": {
                "e": {
                    "110000 - Military/Civilian Installation": "110000", "110100 - Aircraft Production": "110100",
                    "110600 - CBRN": "110600", "120000 - Infrastructure": "120000", "120500 - Energy Facility": "120500",
                    "120600 - Government Site": "120600", "120702 - Hospital": "120702", "120802 - Military Base": "120802",
                    "120803 - Airport/Air Base": "120803", "121200 - Telecommunications": "121200",
                    "121302 - Air Traffic Control Facility": "121302", "121309 - Sea Port/Naval Base": "121309",
                    "000000 - Unspecified": "000000"
                },
                "s1": {"00 - Unspecified": "00", "06 - Coal": "06", "08 - Hydroelectric": "08", "09 - Natural Gas": "09"},
                "s2": {"00 - Unspecified": "00", "03 - Nuclear Warfare Prod": "03", "05 - Atomic Reactor": "05", "10 - Transportation": "10"}
            },
            "25": {
                "e": {
                    "110000 - C2 Lines": "110000", "110100 - Boundary": "110100", "120100 - Area of Operations": "120100",
                    "130300 - Checkpoint": "130300", "131000 - Fly-To-Point": "131000", "131800 - Waypoint": "131800",
                    "140100 - FLOT": "140100", "140400 - FEBA": "140400", "151300 - Engagement Area": "151300",
                    "170100 - Air Corridor": "170100", "171000 - ROZ": "171000", "171400 - FEZ": "171400",
                    "171500 - JEZ": "171500", "171600 - MEZ": "171600", "171700 - LOMEZ": "171700", "171800 - HIMEZ": "171800",
                    "172000 - Weapons Free Zone": "172000", "180100 - Air Control Point": "180100", "180600 - TACAN": "180600",
                    "180700 - CAP Station": "180700", "180800 - AEW Station": "180800", "181200 - Tanking": "181200",
                    "182200 - Orbit": "182200", "190100 - IFF Off Line": "190100", "190200 - IFF On Line": "190200",
                    "213900 - Data Link Ref Point": "213900", "220100 - Bearing Line": "220100",
                    "242300 - Kill Box": "242300", "260100 - FSCL": "260100", "340000 - Mission Tasks": "340000"
                },
                "s1": {"00 - Unspecified": "00", "01 - Wheeled limited XC": "01", "03 - Tracked": "03", "13 - Mine": "13"},
                "s2": {"00 - Unspecified": "00"}
            },
            "27": {
                "e": {
                    "110000 - Military": "110000", "110201 - EOD": "110201", "110209 - Sniper": "110209",
                    "110210 - SOF": "110210", "110212 - Medic": "110212", "110215 - Infantry": "110215",
                    "110220 - Commander": "110220", "110301 - Rifle": "110301", "110400 - Non-Lethal": "110400"
                },
                "s1": {"00 - Unspecified": "00", "21 - Reconnaissance": "21", "22 - Infantry": "22", "23 - Commander": "23", "46 - Individual": "46"},
                "s2": {"00 - Unspecified": "00", "04 - Staff J1": "04", "05 - Staff J2": "05", "06 - Staff J3": "06", "14 - Rank OF-1": "14"}
            },
            "30": {
                "e": {
                    "110000 - Military": "110000", "120000 - Military Combatant": "120000", "120100 - Carrier": "120100",
                    "120200 - Surface Combatant, Line": "120200", "120201 - Battleship": "120201",
                    "120202 - Cruiser": "120202", "120203 - Destroyer": "120203", "120204 - Frigate": "120204",
                    "120205 - Corvette": "120205", "120206 - Littoral Combatant Ship": "120206",
                    "120300 - Amphibious Warfare Ship": "120300", "120400 - Mine Warfare Ship": "120400",
                    "120500 - Patrol Boat": "120500", "120700 - USV (Military)": "120700", "120801 - RHIB": "120801",
                    "130000 - Military Non-Combatant": "130000", "130100 - Auxiliary Ship": "130100",
                    "140000 - Civilian": "140000", "140100 - Merchant Ship": "140100", "140101 - Cargo, General": "140101",
                    "140102 - Container Ship": "140102", "140105 - Ferry": "140105", "140109 - Oiler/Tanker": "140109",
                    "140110 - Passenger": "140110", "140200 - Fishing Vessel": "140200", "140700 - USV (Civilian)": "140700",
                    "150000 - Own Ship": "150000", "160000 - Fused Track": "160000", "170000 - Manual Track": "170000",
                    "000000 - Unspecified": "000000"
                },
                "s1": {
                    "00 - Unspecified": "00", "01 - Own Ship": "01", "02 - Antiair Warfare": "02",
                    "05 - EW": "05", "08 - Missile Defense": "08", "09 - Medical": "09", "11 - RMV": "11",
                    "17 - Torpedo": "17", "18 - Drone-Equipped": "18", "21 - BMD LRS&T": "21", "22 - Sea-Base X-Band": "22"
                },
                "s2": {
                    "00 - Unspecified": "00", "01 - Nuclear Powered": "01", "05 - Dock": "05", "06 - Logistics": "06",
                    "07 - Tank": "07", "08 - Vehicle": "08", "09 - Fast": "09", "10 - Air-Cushioned (US)": "10", "12 - Hydrofoil": "12"
                }
            },
            "35": {
                "e": {
                    "110000 - Military": "110000", "110100 - Submarine": "110100", "110101 - Submarine, Surfaced": "110101",
                    "110102 - Submarine, Snorkeling": "110102", "110103 - Submarine, Bottomed": "110103",
                    "110400 - Military AUV/UUV": "110400", "110500 - Military Diver": "110500",
                    "120000 - Civilian": "120000", "120100 - Submersible": "120100", "120200 - Civilian AUV/UUV": "120200",
                    "130000 - Weapon": "130000", "130100 - Torpedo": "130100", "130300 - Decoy": "130300",
                    "140000 - ETC / POSCON": "140000", "150000 - Fused Track": "150000", "160000 - Manual Track": "160000",
                    "000000 - Unspecified": "000000"
                },
                "s1": {
                    "00 - Unspecified": "00", "02 - Auxiliary": "02", "13 - Possible Sub Low 1": "13",
                    "14 - Possible Sub Low 2": "14", "15 - Possible Sub High 3": "15", "16 - Possible Sub High 4": "16",
                    "17 - Probable Submarine": "17", "18 - Certain Submarine": "18", "19 - Anti-torpedo Torpedo": "19"
                },
                "s2": {
                    "00 - Unspecified": "00", "01 - AIP": "01", "02 - Diesel Electric": "02", "06 - Nuclear Powered": "06"
                }
            },
            "36": {
                "e": {
                    "110000 - Sea Mine, General": "110000", "110100 - Sea Mine, Bottom": "110100",
                    "110200 - Sea Mine, Moored": "110200", "110300 - Sea Mine, Floating": "110300",
                    "120000 - UXO": "120000", "130000 - Sea Mine Decoy": "130000", "140000 - MILCO": "140000",
                    "150000 - MILEC": "150000", "190000 - NMLO": "190000", "000000 - Unspecified": "000000"
                },
                "s1": {"00 - Unspecified": "00"}, "s2": {"00 - Unspecified": "00"}
            },
            "40": {
                "e": {
                    "110000 - Incident": "110000", "110100 - Criminal Activity": "110100", "110200 - Bomb/Bombing": "110200",
                    "110300 - IED Event": "110300", "110600 - Explosion": "110600", "120000 - Civil Disturbance": "120000",
                    "130000 - Operation": "130000", "131200 - Emergency Operation": "131200", "140000 - Fire Event": "140000",
                    "150000 - Hazardous Materials": "150000", "160100 - Air Incident": "160100",
                    "170000 - Natural Event": "170000", "000000 - Unspecified": "000000"
                },
                "s1": {"00 - Unspecified": "00", "06 - Murder": "06", "10 - Pirate": "10", "15 - Attempted": "15", "22 - Raid": "22"},
                "s2": {"00 - Unspecified": "00"}
            },
            "45": {
                "e": {
                    "110100 - Low Pressure Center": "110100", "110200 - High Pressure Center": "110200",
                    "110301 - Cold Front": "110301", "110305 - Warm Front": "110305", "120000 - Turbulence": "120000",
                    "130000 - Icing": "130000", "140300 - Jet Stream": "140300", "150000 - Cloud Cover": "150000",
                    "160100 - Rain": "160100", "160700 - Snow": "160700", "161400 - Storms": "161400",
                    "161500 - Fog": "161500", "170100 - IFR": "170100"
                },
                "s1": {"00 - Unspecified": "00"}, "s2": {"00 - Unspecified": "00"}
            },
            "46": {
                "e": {
                    "110000 - Ice Systems": "110000", "120000 - Hydrography": "120000", "120300 - Ports and Harbors": "120300",
                    "120400 - Aids to Navigation": "120400", "120500 - Dangers/Hazards": "120500",
                    "130000 - Oceanography": "130000", "140000 - Geophysics/Acoustics": "140000",
                    "150000 - Limits": "150000", "160000 - Man-Made Structures": "160000"
                },
                "s1": {"00 - Unspecified": "00"}, "s2": {"00 - Unspecified": "00"}
            },
            "47": {
                "e": {"110000 - Space": "110000"}, "s1": {"00 - Unspecified": "00"}, "s2": {"00 - Unspecified": "00"}
            },
            "50": {
                "e": {
                    "110000 - Signal Intercept": "110000", "110100 - Communications": "110100",
                    "110200 - Jammer": "110200", "110300 - Radar": "110300", "000000 - Unspecified": "000000"
                },
                "s1": {
                    "00 - Unspecified": "00", "01 - AA Fire Control": "01", "02 - Airborne Search/Bombing": "02",
                    "03 - Airborne Intercept": "03", "04 - Altimeter": "04", "05 - Airborne Recon/Mapping": "05",
                    "06 - Air Traffic Control": "06", "08 - Battlefield Surveillance": "08", "09 - Controlled Approach": "09",
                    "10 - Controlled Intercept": "10", "11 - Cellular/Mobile": "11", "12 - Coastal Surveillance": "12",
                    "14 - Data Transmission": "14", "16 - Early Warning": "16", "17 - Fire Control": "17",
                    "19 - Height Finding": "19", "21 - IFF Interrogator": "21", "22 - ILS": "22",
                    "24 - IFF Transponder": "24", "25 - Barrage Jammer": "25", "27 - Deceptive Jammer": "27",
                    "29 - Jammer (General)": "29", "30 - Noise Jammer": "30", "35 - Missile Acquisition": "35",
                    "40 - Missile Guidance": "40", "41 - Missile Homing": "41", "53 - Satellite Downlink": "53",
                    "55 - Surface Search": "55", "57 - Satellite Uplink": "57", "58 - Target Acquisition": "58",
                    "59 - Target Illumination": "59", "61 - Target Tracking": "61"
                },
                "s2": {"00 - Unspecified": "00"}
            },
            "60": {
                "e": {
                    "110000 - Cyberspace Unit": "110000", "110100 - Combat Mission Team": "110100",
                    "110200 - National Mission Team": "110200", "110300 - Cyber Protection Team": "110300",
                    "110600 - Defensive Cyberspace": "110600", "110700 - Offensive Cyberspace": "110700",
                    "120000 - Threat Actors": "120000", "120200 - Insider": "120200", "130000 - Agent": "130000",
                    "130100 - Firewall": "130100", "140000 - Application": "140000", "150000 - Threat": "150000",
                    "150100 - Malware": "150100", "150200 - Phishing": "150200", "160000 - Data": "160000",
                    "170000 - Endpoint": "170000", "170100 - Server": "170100", "170200 - Workstation": "170200",
                    "170600 - Router": "170600", "170700 - Switch": "170700", "180000 - Network": "180000",
                    "000000 - Unspecified": "000000"
                },
                "s1": {
                    "00 - Unspecified": "00", "01 - Defensive Cyberspace": "01", "02 - Offensive Cyberspace": "02",
                    "04 - Wired": "04", "05 - Wireless": "05", "06 - Radio Frequency": "06", "07 - OS": "07",
                    "09 - ISP": "09", "12 - Cloud": "12", "13 - Data": "13"
                },
                "s2": {
                    "00 - Unspecified": "00", "01 - Secured": "01", "02 - Open": "02", "03 - Response Actions": "03",
                    "05 - Internal Defense": "05", "06 - APT": "06", "07 - Nation State": "07", "08 - Nation State Sponsored": "08"
                }
            }
        }

    def build_ui(self):
        f_main = ttk.Frame(self.root, padding="10")
        f_main.pack(fill=tk.BOTH, expand=True)

        # SET A
        fa = ttk.LabelFrame(f_main, text="SET A (Pozisyon 1 - 10)", padding="6")
        fa.pack(fill=tk.X, pady=3)
        self.cb_ver = self.mk_cb(fa, "Poz 1-2 (Version):", self.versions, "13 - MIL-STD-2525E", 0)
        self.cb_ctx = self.mk_cb(fa, "Poz 3 (Context):", self.contexts, "0 - Reality", 1)
        self.cb_id = self.mk_cb(fa, "Poz 4 (Identity):", self.identities, "3 - Friend", 2)
        self.cb_ss = self.mk_cb(fa, "Poz 5-6 (Symbol Set):", self.symbol_sets, "01 - Air", 3)
        self.cb_ss.bind("<<ComboboxSelected>>", lambda e: self.on_symset_change())
        self.cb_st = self.mk_cb(fa, "Poz 7 (Status):", self.statuses, "0 - Present", 4)
        self.cb_hq = self.mk_cb(fa, "Poz 8 (HQ/TF/Dummy):", self.hq_tf, "0 - Unknown (No Statement)", 5)
        self.cb_amp = self.mk_cb(fa, "Poz 9-10 (Amplifier):", self.amplifiers, "00 - Unknown (No Statement)", 6)

        # SET B
        fb = ttk.LabelFrame(f_main, text="SET B (Pozisyon 11 - 20) & Ortak Değiştiriciler", padding="6")
        fb.pack(fill=tk.X, pady=3)
        ttk.Label(fb, text="Entity Arama (Filtre):", width=34).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ent_q = ttk.Entry(fb, width=36)
        self.ent_q.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
        self.ent_q.bind("<KeyRelease>", self.filter_ent)

        self.cb_ent = self.mk_cb(fb, "Poz 11-16 (Entity/Type/Subtype):", {}, "", 1)
        self.cb_s1 = self.mk_cb(fb, "Poz 17-18 (Set Sector 1 Mod):", {}, "", 2)
        self.cb_s2 = self.mk_cb(fb, "Poz 19-20 (Set Sector 2 Mod):", {}, "", 3)
        self.cb_c1 = self.mk_cb(fb, "Tablo A-IX (Common Sector 1):", self.common_s1, "000 - Yok (Set Özel Mod. Kullan)", 4)
        self.cb_c2 = self.mk_cb(fb, "Tablo A-X (Common Sector 2):", self.common_s2, "000 - Yok (Set Özel Mod. Kullan)", 5)

        # SET C
        fc = ttk.LabelFrame(f_main, text="SET C (Pozisyon 21 - 30)", padding="6")
        fc.pack(fill=tk.X, pady=3)
        ttk.Label(fc, text="Poz 21-22 (Common Mod ID 1 & 2):", width=34).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_cid = ttk.Label(fc, text="00", font=("Consolas", 10, "bold"))
        self.lbl_cid.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
        self.cb_frm = self.mk_cb(fc, "Poz 23 (Frame Shape - Tablo A-LX):", self.frames, "0 - Unknown", 1)
        ttk.Label(fc, text="Poz 24-27 (Reserved):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(fc, text="0000 (Sabit)").grid(row=2, column=1, sticky=tk.W, padx=10, pady=2)
        ttk.Label(fc, text="Poz 28-30 (Country Code):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.ent_cnt = ttk.Entry(fc, width=12)
        self.ent_cnt.insert(0, "000")
        self.ent_cnt.grid(row=3, column=1, sticky=tk.W, padx=10, pady=2)
        self.ent_cnt.bind("<KeyRelease>", lambda e: self.update_sidc())

        # ÇIKTI & ÇÖZÜMLEYİCİ
        fo = ttk.LabelFrame(f_main, text="30 Haneli SIDC Çıktısı & Tersine Çözümleyici", padding="8")
        fo.pack(fill=tk.X, pady=5)
        self.sidc_var = tk.StringVar()
        ttk.Entry(fo, textvariable=self.sidc_var, font=("Consolas", 15, "bold"), justify="center", state="readonly").pack(fill=tk.X, pady=3)
        self.brk_var = tk.StringVar()
        ttk.Label(fo, textvariable=self.brk_var, font=("Consolas", 10)).pack(pady=2)

        row_act = ttk.Frame(fo)
        row_act.pack(fill=tk.X, pady=4)
        ttk.Button(row_act, text="Panoya Kopyala", command=self.copy_sidc).pack(side=tk.LEFT, padx=5)
        ttk.Label(row_act, text=" | Çözümlenecek SIDC:").pack(side=tk.LEFT, padx=5)
        self.ent_dec = ttk.Entry(row_act, width=34, font=("Consolas", 11))
        self.ent_dec.insert(0, "100310021612040100060130000840")
        self.ent_dec.pack(side=tk.LEFT, padx=5)
        ttk.Button(row_act, text="SIDC Çözümle", command=self.decode_sidc).pack(side=tk.LEFT, padx=5)

    def mk_cb(self, parent, txt, d, def_k, r):
        ttk.Label(parent, text=txt, width=34).grid(row=r, column=0, sticky=tk.W, pady=2)
        cb = ttk.Combobox(parent, values=list(d.keys()), state="readonly", width=60)
        if def_k: cb.set(def_k)
        cb.grid(row=r, column=1, sticky=tk.W, padx=10, pady=2)
        cb.bind("<<ComboboxSelected>>", lambda e: self.update_sidc())
        return cb

    def on_symset_change(self, init_mode=False):
        ss = self.symbol_sets[self.cb_ss.get()]
        cur = self.db.get(ss, self.db["00"])
        self.cur_e, self.cur_s1, self.cur_s2 = cur["e"], cur["s1"], cur["s2"]
        self.ent_q.delete(0, tk.END)
        for cb, d in [(self.cb_ent, self.cur_e), (self.cb_s1, self.cur_s1), (self.cb_s2, self.cur_s2)]:
            cb["values"] = list(d.keys())
            cb.current(0)
        self.cb_frm.set("0 - Unknown" if init_mode else self.def_frame.get(ss, "0 - Unknown"))
        self.update_sidc()

    def filter_ent(self, event=None):
        q = self.ent_q.get().strip().lower()
        flt = [k for k in self.cur_e.keys() if q in k.lower()]
        if flt:
            self.cb_ent["values"] = flt
            self.cb_ent.current(0)
            self.update_sidc()

    def update_sidc(self):
        set_a = (
            f"{self.versions[self.cb_ver.get()]}{self.contexts[self.cb_ctx.get()]}"
            f"{self.identities[self.cb_id.get()]}{self.symbol_sets[self.cb_ss.get()]}"
            f"{self.statuses[self.cb_st.get()]}{self.hq_tf[self.cb_hq.get()]}"
            f"{self.amplifiers[self.cb_amp.get()]}"
        )
        ent = self.cur_e.get(self.cb_ent.get(), "000000")
        if ent == "000000":
            s1, s2, p21, p22 = "00", "00", "0", "0"
            for w in (self.cb_s1, self.cb_s2, self.cb_c1, self.cb_c2): w.configure(state="disabled")
        else:
            self.cb_c1.configure(state="readonly")
            self.cb_c2.configure(state="readonly")
            c1 = self.common_s1[self.cb_c1.get()]
            if c1 != "000":
                p21, s1 = c1[0], c1[1:3]
                self.cb_s1.configure(state="disabled")
            else:
                p21, s1 = "0", self.cur_s1.get(self.cb_s1.get(), "00")
                self.cb_s1.configure(state="readonly")
            c2 = self.common_s2[self.cb_c2.get()]
            if c2 != "000":
                p22, s2 = c2[0], c2[1:3]
                self.cb_s2.configure(state="disabled")
            else:
                p22, s2 = "0", self.cur_s2.get(self.cb_s2.get(), "00")
                self.cb_s2.configure(state="readonly")

        set_b = f"{ent}{s1}{s2}"
        self.lbl_cid.config(text=f"{p21}{p22} (Poz 21={p21}, Poz 22={p22})")
        cnt = self.ent_cnt.get().strip().upper().zfill(3)[:3]
        set_c = f"{p21}{p22}{self.frames[self.cb_frm.get()]}0000{cnt}"
        self.sidc_var.set(f"{set_a}{set_b}{set_c}")
        self.brk_var.set(f"Set A: {set_a}  |  Set B: {set_b}  |  Set C: {set_c}")

    def find_k(self, d, val):
        return next((k for k, v in d.items() if v == val), None)

    def _set_or_add(self, cb, attr, code):
        """`code` değerini combobox'ta seçer; tabloda yoksa geçici seçenek ekler.

        Böylece çözümlenen SIDC, menü tablosunda bulunmayan bir kod içerse bile
        varsayılan değere dönmez (SIDC birebir korunur). Eklenen seçenek
        sembol seti değişince (on_symset_change) kaybolur.
        """
        d = getattr(self, attr)
        k = self.find_k(d, code)
        if k is None:
            k = f"{code} - (Tabloda yok)"
            d = {k: code, **d}  # db tablosunu değiştirmemek için kopya
            setattr(self, attr, d)
            cb["values"] = list(d.keys())
        cb.set(k)

    def decode_sidc(self):
        c = self.ent_dec.get().strip().upper()
        if len(c) != 30:
            messagebox.showerror("Hata", "SIDC kodu 30 haneli olmalıdır!")
            return
        for cb, d, sl in [
            (self.cb_ver, self.versions, c[0:2]), (self.cb_ctx, self.contexts, c[2:3]),
            (self.cb_id, self.identities, c[3:4]), (self.cb_ss, self.symbol_sets, c[4:6])
        ]:
            k = self.find_k(d, sl)
            if k: cb.set(k)
        self.on_symset_change()
        for cb, d, sl in [
            (self.cb_st, self.statuses, c[6:7]), (self.cb_hq, self.hq_tf, c[7:8]),
            (self.cb_amp, self.amplifiers, c[8:10]),
            (self.cb_frm, self.frames, c[22:23])
        ]:
            k = self.find_k(d, sl)
            if k: cb.set(k)
        self._set_or_add(self.cb_ent, "cur_e", c[10:16])
        if c[20] != "0":
            k = self.find_k(self.common_s1, c[20] + c[16:18])
            if k: self.cb_c1.set(k)
        else:
            self.cb_c1.current(0)
            self._set_or_add(self.cb_s1, "cur_s1", c[16:18])
        if c[21] != "0":
            k = self.find_k(self.common_s2, c[21] + c[18:20])
            if k: self.cb_c2.set(k)
        else:
            self.cb_c2.current(0)
            self._set_or_add(self.cb_s2, "cur_s2", c[18:20])
        self.ent_cnt.delete(0, tk.END)
        self.ent_cnt.insert(0, c[27:30])
        self.update_sidc()

    def copy_sidc(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.sidc_var.get())
        messagebox.showinfo("Kopyalandı", f"Kopyalanan SIDC:\n{self.sidc_var.get()}")

if __name__ == "__main__":
    root = tk.Tk()
    MilStd2525EApp(root)
    root.mainloop()