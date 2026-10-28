# Greece (GRE) focus tree, Greek Uprising mechanic, Hellenic Republic (HEL) tag.
import sys, os, re
REPO = sys.argv[1]
J = lambda *p: os.path.join(REPO, *p)

F = []
def focus(id, x, y, icon, name, desc, cost=10, pre=None, excl=None, avail=None, bypass=None, effect="", ai=1, filters=None):
    F.append(dict(id=id, x=x, y=y, icon=icon, name=name, desc=desc, cost=cost, pre=pre or [], excl=excl or [],
                  avail=avail, bypass=bypass, effect=effect, ai=ai, filters=filters or []))

def build(state, btype, level, slots=0):
    s = f"if = {{ limit = {{ {state} = {{ is_owned_and_controlled_by = ROOT }} }}\n\t{state} = {{\n"
    if slots: s += f"\t\tadd_extra_state_shared_building_slots = {slots}\n"
    s += f"\t\tadd_building_construction = {{ type = {btype} level = {level} instant_build = yes }}\n\t}}\n}}\n"
    return s
def tech(name, cat, bonus=0.5, uses=1):
    if cat.endswith("_doctrine"):
        return f"add_doctrine_cost_reduction = {{ name = {name} cost_reduction = 0.4 uses = {uses} category = {cat} }}\n"
    return f"add_tech_bonus = {{ name = {name} bonus = {bonus} uses = {uses} category = {cat} }}\n"

ROYAL = [70, 100, 99]     # East Macedonia (Salonika), Thessaly, West Macedonia
REPUB = [49, 62, 50]      # Attica (Athens), Peloponnese, Aegean Islands
GREEK = ROYAL + REPUB

UPRISING = (
    "# Royalist rebels rise in the north and join Greece\n"
    + "".join(f"if = {{ limit = {{ {s} = {{ is_owned_and_controlled_by = SPC }} }} transfer_state = {s} }}\n" for s in ROYAL)
    + "load_oob = \"GRE_uprising\"\n"
    + "if = { limit = { has_country_flag = GRE_royalist_committees SPC = { NOT = { has_country_flag = SPC_hetairists_suppressed } } }\n\tload_oob = \"GRE_uprising_extra\"\n}\n"
    + "add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 producer = GRE }\n"
    + "# Republican rebels rise in the south as the Hellenic Republic\n"
    + "".join(f"{s} = {{ add_core_of = HEL }}\n" for s in REPUB)
    + "SPC = { release = HEL }\n"
    + "HEL = {\n\tload_oob = \"HEL_uprising\"\n"
    + "\tif = { limit = { ROOT = { has_country_flag = GRE_republican_contacts } SPC = { NOT = { has_country_flag = SPC_hetairists_suppressed } } }\n\t\tload_oob = \"HEL_uprising_extra\"\n\t}\n"
    + "\tadd_equipment_to_stockpile = { type = infantry_equipment amount = 2000 producer = HEL }\n\tadd_ideas = GRE_the_great_uprising\n"
    + "}\n"
    + "# Aragon moves to crush both rebel governments\n"
    + "SPC = {\n\tdeclare_war_on = { target = ROOT type = annex_everything }\n"
    + "\tif = { limit = { country_exists = HEL } declare_war_on = { target = HEL type = annex_everything } }\n}\n"
    + "if = { limit = { has_country_flag = GRE_occitan_volunteers }\n\tload_oob = \"GRE_occitan_volunteers\"\n\tadd_equipment_to_stockpile = { type = infantry_equipment amount = 1000 producer = OCC }\n}\n"
    + "if = { limit = { has_country_flag = GRE_republican_contacts }\n"
    + "\tadd_opinion_modifier = { target = HEL modifier = positive_50 }\n"
    + "\tHEL = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n}\n"
    + "SPC = { country_event = { id = greek_uprising.1 } }\n"
    + "add_ideas = GRE_the_great_uprising\n"
)

# ---------------- uprising core ----------------
focus("GRE_the_last_free_greeks", 8, 0, "GFX_goal_generic_national_unity", "The Last Free Greeks",
      "Polygyros is all that remains of free Greece. Athens, Salonika and the islands groan under Aragonese rule. But every Greek in the occupied lands still looks north to the last Hellenic flag.",
      cost=5, effect="add_political_power = 75\nadd_stability = 0.05\n", ai=50, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_the_philiki_etaireia_reborn", 8, 1, "GFX_goal_generic_political_pressure", "The Philiki Etaireia Reborn",
      "A century ago the Friendly Society plotted the liberation of Greece from the Turks. Its heirs now plot liberation from Aragon, in cellars from Salonika to Nafplio.",
      pre=[["GRE_the_last_free_greeks"]],
      effect="".join(f"add_state_claim = {s}\n" for s in GREEK) + "add_war_support = 0.1\n",
      ai=20, filters=["FOCUS_FILTER_ANNEXATION", "FOCUS_FILTER_WAR_SUPPORT"])
focus("GRE_royalist_committees", 6, 2, "GFX_focus_hun_elect_a_king", "Royalist Committees in Salonika",
      "In Macedonia and Thessaly the old families remain loyal to the Greek crown. When the signal comes, their committees will raise the north for the king.",
      pre=[["GRE_the_philiki_etaireia_reborn"]],
      effect="set_country_flag = GRE_royalist_committees\nadd_popularity = { ideology = absolutist popularity = 0.05 }\n",
      ai=10, filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_smuggle_arms_across_the_aegean", 8, 2, "GFX_goal_generic_small_arms", "Smuggle Arms Across the Aegean",
      "Fishing boats by day, gun-runners by night. Every rifle that reaches the occupied lands is one more Aragonese garrison that will not sleep soundly.",
      pre=[["GRE_the_philiki_etaireia_reborn"]],
      effect="add_equipment_to_stockpile = { type = infantry_equipment amount = 1500 producer = GRE }\nadd_equipment_to_stockpile = { type = artillery_equipment amount = 36 producer = GRE }\n",
      ai=20, filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_the_athenian_republicans", 10, 2, "GFX_goal_support_democracy", "Reach Out to the Athenian Republicans",
      "The rebels of Athens and the Peloponnese want no king. They want a Hellenic Republic. They are not our friends, but they hate Aragon as much as we do.",
      pre=[["GRE_the_philiki_etaireia_reborn"]],
      effect="set_country_flag = GRE_republican_contacts\nadd_popularity = { ideology = democratic popularity = 0.05 }\n",
      ai=5, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_the_great_uprising", 8, 3, "GFX_goal_generic_major_war", "The Great Uprising",
      "The signal fires burn on Mount Olympus. Salonika, Volos and Florina rise for the king, while Athens and the islands proclaim a Hellenic Republic. Aragon will bleed for every Greek village it holds.",
      pre=[["GRE_smuggle_arms_across_the_aegean"], ["GRE_royalist_committees", "GRE_the_athenian_republicans"]],
      avail=("country_exists = SPC\nNOT = { has_war_with = SPC }\n"
             "OR = {\n" + "".join(f"\t{s} = {{ is_owned_by = SPC }}\n" for s in GREEK) + "}\n"
             "OR = { date > 1937.1.1 SPC = { has_war = yes } }"),
      effect=UPRISING, ai=50, filters=["FOCUS_FILTER_ANNEXATION"])

# ---------------- who leads Greece ----------------
focus("GRE_a_crown_for_all_hellenes", 6, 4, "GFX_focus_rom_royal_dictatorship", "A Crown for All Hellenes",
      "The royalists of the north fought for the king. Greece will be liberated as a kingdom, and the republican experiment in Athens is a dangerous distraction.",
      pre=[["GRE_the_great_uprising"]], excl=["GRE_the_republican_pact"],
      effect="add_popularity = { ideology = absolutist popularity = 0.1 }\nadd_stability = 0.05\n",
      ai=5, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_bring_athens_to_heel", 5, 5, "GFX_goal_generic_territory_or_war", "Bring Athens to Heel",
      "The war with Aragon is over. Now the self-proclaimed republic in Athens will submit to the crown, peacefully or otherwise.",
      pre=[["GRE_a_crown_for_all_hellenes"]],
      avail="country_exists = HEL\nNOT = { has_war_with = SPC }\nNOT = { has_war_with = HEL }",
      effect="create_wargoal = { type = annex_everything target = HEL }\n", filters=["FOCUS_FILTER_ANNEXATION"])
focus("GRE_the_king_in_athens", 7, 5, "GFX_goal_generic_national_unity", "The King in Athens",
      "Athens is the heart of Hellas. The court will move from little Polygyros to the city of Pericles.",
      pre=[["GRE_a_crown_for_all_hellenes"]], avail="owns_state = 49",
      effect="set_capital = { state = 49 }\nadd_stability = 0.1\nadd_political_power = 100\n", filters=["FOCUS_FILTER_STABILITY"])
focus("GRE_the_republican_pact", 10, 4, "GFX_goal_support_democracy", "The Republican Pact",
      "The uprising succeeded because royalists and republicans fought side by side. The king will step aside, and Greece will join the Hellenic Republic as one free nation.",
      pre=[["GRE_the_great_uprising"]], excl=["GRE_a_crown_for_all_hellenes"],
      effect=("set_politics = { ruling_party = democratic elections_allowed = yes last_election = \"1936.1.1\" election_frequency = 48 }\n"
              "set_popularities = { democratic = 60 absolutist = 35 fascism = 5 }\n"
              "if = { limit = { country_exists = HEL is_in_faction = no HEL = { is_in_faction = no } }\n"
              "\tcreate_faction_from_template = { template = faction_template_defensive_democratic name = GRE_hellenic_alliance }\n"
              "\tadd_to_faction = HEL\n}\n"),
      ai=2, filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_union_with_the_republic", 9, 5, "GFX_focus_generic_treaty", "Union with the Hellenic Republic",
      "With Aragon beaten back, the two Greek states will become one. The Hellenic Republic and the old kingdom unite under a single constitution in Athens.",
      pre=[["GRE_the_republican_pact"]],
      avail="country_exists = HEL\nHEL = { is_in_faction_with = ROOT }\nNOT = { has_war_with = SPC }",
      effect="annex_country = { target = HEL transfer_troops = yes }\nadd_stability = 0.1\n",
      filters=["FOCUS_FILTER_ANNEXATION"])
focus("GRE_a_constitution_for_hellas", 11, 5, "GFX_focus_generic_treaty", "A Constitution for Hellas",
      "A written constitution, a free parliament and an end to the arbitrary rule of kings and foreign governors.",
      pre=[["GRE_the_republican_pact"]],
      effect="add_ideas = GRE_hellenic_constitution\n", filters=["FOCUS_FILTER_STABILITY"])
focus("GRE_hellas_reborn", 8, 6, "GFX_goal_generic_national_unity", "Hellas Reborn",
      "From Salonika to Sparta, Greece is free and united for the first time in living memory.",
      pre=[["GRE_bring_athens_to_heel", "GRE_the_king_in_athens", "GRE_union_with_the_republic", "GRE_a_constitution_for_hellas"]],
      avail="owns_state = 49\nowns_state = 70",
      effect="".join(f"add_state_core = {s}\n" for s in GREEK) + "add_ideas = GRE_hellas_reborn\n",
      filters=["FOCUS_FILTER_ANNEXATION", "FOCUS_FILTER_STABILITY"])
focus("GRE_the_megali_idea", 8, 7, "GFX_goal_generic_more_territorial_claims", "The Megali Idea",
      "The Great Idea: a Greek state embracing every Greek, with Constantinople as its capital. The City is held by Aragon, and Smyrna too. Not for long.",
      pre=[["GRE_hellas_reborn"]], avail="country_exists = SPC",
      effect=("add_state_claim = 52\nadd_state_claim = 54\nadd_state_claim = 753\n"
              "create_wargoal = { type = take_state_focus target = SPC generator = { 52 54 } }\n"),
      filters=["FOCUS_FILTER_ANNEXATION"])

# ---------------- foreign friends ----------------
focus("GRE_appeal_to_occitania", 13, 1, "GFX_focus_generic_treaty", "Appeal to Occitania",
      "The enemy of our enemy is the strongest power in Europe. Occitania has no love for Greeks, but it will gladly arm anyone who bleeds Aragon.",
      pre=[["GRE_the_last_free_greeks"]], avail="country_exists = OCC",
      effect=("add_opinion_modifier = { target = OCC modifier = positive_50 }\n"
              "OCC = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "add_equipment_to_stockpile = { type = infantry_equipment amount = 1000 producer = OCC }\n"),
      filters=["FOCUS_FILTER_POLITICAL"])
focus("GRE_occitan_military_advisors", 13, 2, "GFX_goal_generic_army_doctrines", "Occitan Military Advisors",
      "Officers from the army that beat Aragon again and again will teach our guerrillas how it is done.",
      pre=[["GRE_appeal_to_occitania"]],
      effect="army_experience = 15\n" + tech("GRE_occitan_military_advisors", "land_doctrine", 0.5, 1),
      filters=["FOCUS_FILTER_ARMY_XP"])
focus("GRE_the_occitan_volunteer_corps", 12, 3, "GFX_goal_generic_allies_build_infantry", "The Occitan Volunteer Corps",
      "Occitania will not go to war for Greece. But nobody in Toulouse will stop veterans of the Aragonese wars from taking leave, crossing the Adriatic and fighting under a Greek flag.",
      pre=[["GRE_occitan_military_advisors"]], avail="country_exists = OCC\nOCC = { NOT = { has_war_with = ROOT } }",
      effect=("set_country_flag = GRE_occitan_volunteers\n"
              "if = { limit = { has_completed_focus = GRE_the_great_uprising has_war_with = SPC }\n"
              "\tload_oob = \"GRE_occitan_volunteers\"\n\tadd_equipment_to_stockpile = { type = infantry_equipment amount = 1000 producer = OCC }\n}\n"),
      filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_byzantine_brotherhood", 14, 3, "GFX_focus_generic_treaty", "Byzantine Brotherhood",
      "The Byzantine Empire also lost Thessaly and Macedonia to Aragon. Orthodox brothers should not fight each other while the Catalans rule our lands.",
      pre=[["GRE_appeal_to_occitania"]], avail="country_exists = X09\nNOT = { has_war_with = X09 }",
      effect=("add_opinion_modifier = { target = X09 modifier = positive_50 }\n"
              "X09 = { add_opinion_modifier = { target = ROOT modifier = positive_50 } }\n"
              "diplomatic_relation = { country = X09 relation = non_aggression_pact }\n"),
      filters=["FOCUS_FILTER_POLITICAL"])

# ---------------- army and economy ----------------
focus("GRE_the_klephts", 2, 1, "GFX_goal_generic_special_forces", "The Klephts",
      "The mountain bandits who fought the Turks for four centuries live on in every Greek village. Their tactics will be the backbone of our army.",
      pre=[["GRE_the_last_free_greeks"]], effect="add_ideas = GRE_klephts\n", filters=["FOCUS_FILTER_ARMY_XP"])
focus("GRE_the_evzones", 1, 2, "GFX_goal_generic_allies_build_infantry", "The Evzones",
      "The kilted mountain infantry of the old royal guard will be revived as the elite of the liberation army.",
      pre=[["GRE_the_klephts"]], effect="army_experience = 15\n" + tech("GRE_the_evzones", "infantry_weapons", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_ARMY_XP"])
focus("GRE_mountain_warfare", 3, 2, "GFX_goal_generic_cavalry", "Mountain Warfare",
      "Pindus and Olympus are our fortresses. Our soldiers will learn to fight in them.",
      pre=[["GRE_the_klephts"]], effect=tech("GRE_mountain_warfare", "mountaineers_tech", 0.5, 2),
      filters=["FOCUS_FILTER_RESEARCH"])
focus("GRE_the_diaspora_volunteers", 2, 3, "GFX_goal_generic_allies_build_infantry", "Volunteers from the Diaspora",
      "Greeks from Alexandria to Odessa answer the call of the motherland.",
      pre=[["GRE_the_evzones"], ["GRE_mountain_warfare"]], effect="add_manpower = 15000\n",
      filters=["FOCUS_FILTER_MANPOWER"])
focus("GRE_rebuild_polygyros", 0, 1, "GFX_goal_generic_construct_civ_factory", "Rebuild Polygyros",
      "Our only province must also be our workshop.",
      pre=[["GRE_the_last_free_greeks"]], effect=build(329, "industrial_complex", 1, 1) + build(329, "infrastructure", 1),
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_aegean_fishing_fleets", 0, 2, "GFX_goal_generic_construct_naval_dockyard", "Aegean Fishing Fleets",
      "The fishing boats of Chalkidiki will become the core of a Greek navy, and of our smuggling routes.",
      pre=[["GRE_rebuild_polygyros"]], effect=build(329, "dockyard", 1, 1) + "navy_experience = 10\n",
      filters=["FOCUS_FILTER_INDUSTRY"])
focus("GRE_industry_of_a_free_greece", 2, 5, "GFX_goal_generic_construct_mil_factory", "Industry of a Free Greece",
      "The workshops of Athens and Salonika will now arm Greeks instead of Aragonese.",
      pre=[["GRE_the_great_uprising"], ["GRE_the_diaspora_volunteers"]],
      effect=build(70, "industrial_complex", 1, 1) + build(70, "arms_factory", 1, 1) + build(49, "arms_factory", 1, 1),
      filters=["FOCUS_FILTER_INDUSTRY"])

# ---------------- emit focus tree ----------------
def indent(text, n):
    pad = "\t" * n
    return "".join(pad + l + "\n" if l.strip() else "\n" for l in text.strip("\n").split("\n"))
out = ["focus_tree = {\n\tid = GRE_focus\n\n\tcountry = {\n\t\tfactor = 0\n\t\tmodifier = {\n\t\t\tadd = 10\n\t\t\toriginal_tag = GRE\n\t\t}\n\t}\n\n\tdefault = no\n\n\tinitial_show_position = { focus = GRE_the_last_free_greeks }\n\n"]
for f in F:
    s = "\tfocus = {\n" + f"\t\tid = {f['id']}\n\t\ticon = {f['icon']}\n\t\tx = {f['x']}\n\t\ty = {f['y']}\n\t\tcost = {f['cost']}\n"
    for g in f["pre"]: s += "\t\tprerequisite = { " + " ".join(f"focus = {p}" for p in g) + " }\n"
    if f["excl"]: s += "\t\tmutually_exclusive = { " + " ".join(f"focus = {p}" for p in f["excl"]) + " }\n"
    if f["avail"]: s += "\t\tavailable = {\n" + indent(f["avail"], 3) + "\t\t}\n"
    if f["bypass"]: s += "\t\tbypass = {\n" + indent(f["bypass"], 3) + "\t\t}\n"
    if f["filters"]: s += "\t\tsearch_filters = { " + " ".join(f["filters"]) + " }\n"
    s += "\t\tcompletion_reward = {\n" + indent(f["effect"], 3) + "\t\t}\n"
    s += f"\t\tai_will_do = {{ factor = {f['ai']} }}\n\t}}\n\n"
    out.append(s)
out.append("}\n")
open(J("common/national_focus/GRE_NF.txt"), "w", encoding="utf-8", newline="\n").write("".join(out))

# ---------------- ideas ----------------
IDEAS = [
    ("GRE_the_great_uprising", "generic_war_of_national_liberation", "war_support_factor = 0.15\nconscription = 0.02\nstability_factor = 0.1\narmy_defence_factor = 0.15\narmy_core_defence_factor = 0.1",
     "The Great Uprising", "All of Greece is in arms against Aragon."),
    ("GRE_klephts", "warrior_traditions_idea", "army_defence_factor = 0.05\nspecial_forces_cap = 0.1",
     "The Klephts", "Greek soldiers fight like the mountain guerrillas of old."),
    ("GRE_hellenic_constitution", "generic_democratic_drift_bonus", "stability_factor = 0.1\npolitical_power_gain = 0.1",
     "A Constitution for Hellas", "Greece is governed by a written constitution and a freely elected parliament."),
    ("GRE_hellas_reborn", "generic_national_unification", "stability_factor = 0.1\nwar_support_factor = 0.1\nindustrial_capacity_factory = 0.05",
     "Hellas Reborn", "Greece is free and united."),
]
s = "ideas = {\n\tcountry = {\n"
for key, pic, mod, _, _ in IDEAS:
    s += f"\t\t{key} = {{\n\t\t\tpicture = {pic}\n\t\t\tallowed = {{ always = no }}\n\t\t\tremoval_cost = -1\n\t\t\tmodifier = {{\n" + indent(mod, 4) + "\t\t\t}\n\t\t}\n"
s += ("\t\tSPC_greek_insurgency = {\n\t\t\tpicture = generic_army_problems\n\t\t\tallowed = { always = no }\n\t\t\tremoval_cost = -1\n"
      "\t\t\tmodifier = {\n\t\t\t\tstability_factor = -0.1\n\t\t\t\twar_support_factor = -0.05\n\t\t\t\tpolitical_power_gain = -0.1\n\t\t\t}\n\t\t}\n")
s += "\t}\n}\n"
open(J("common/ideas/GRE_focus_ideas.txt"), "w", encoding="utf-8", newline="\n").write(s)

# ---------------- events ----------------
EV = '''add_namespace = greek_uprising

# Aragon learns of the uprising
country_event = {
	id = greek_uprising.1
	title = greek_uprising.1.t
	desc = greek_uprising.1.d
	picture = GFX_report_event_chinese_soldiers_fighting
	is_triggered_only = yes

	option = {
		name = greek_uprising.1.a
		add_war_support = 0.05
		add_timed_idea = { idea = SPC_greek_insurgency days = 730 }
		country_event = { id = greek_uprising.2 days = 365 }
		country_event = { id = greek_uprising.10 days = 7 }
	}
}

# Aragon: negotiate or fight on (first after 1 year, then every 3 weeks while the revolt lasts)
country_event = {
	id = greek_uprising.2
	title = greek_uprising.2.t
	desc = greek_uprising.2.d
	picture = GFX_report_event_journalists_speech
	is_triggered_only = yes

	trigger = {
		NOT = { has_country_flag = SPC_greek_peace }
		OR = {
			has_war_with = GRE
			has_war_with = HEL
		}
	}

	option = {
		name = greek_uprising.2.a
		set_country_flag = SPC_greek_peace
		if = {
			limit = { has_war_with = GRE }
			white_peace = GRE
			GRE = { country_event = { id = greek_uprising.5 } }
		}
		if = {
			limit = { has_war_with = HEL }
			white_peace = HEL
			HEL = { country_event = { id = greek_uprising.5 } }
		}
		remove_ideas = SPC_greek_insurgency
		add_war_support = -0.05
		ai_chance = {
			base = 20
			modifier = { factor = 4 has_war_with = OCC }
			modifier = { factor = 2 has_stability < 0.4 }
		}
	}

	option = {
		name = greek_uprising.2.b
		add_war_support = 0.02
		country_event = { id = greek_uprising.2 days = 21 }
		ai_chance = { base = 80 }
	}
}

# Aragon: the revolt has been crushed
country_event = {
	id = greek_uprising.3
	title = greek_uprising.3.t
	desc = greek_uprising.3.d
	picture = GFX_report_event_soldiers_marching
	is_triggered_only = yes

	option = {
		name = greek_uprising.3.a
		set_country_flag = SPC_greek_peace
		remove_ideas = SPC_greek_insurgency
		add_stability = 0.1
		add_war_support = 0.05
	}
}

# Greek side: Aragon recognises independence
country_event = {
	id = greek_uprising.5
	title = greek_uprising.5.t
	desc = greek_uprising.5.d
	picture = GFX_report_event_iww_demonstration
	is_triggered_only = yes

	option = {
		name = greek_uprising.5.a
		add_stability = 0.1
		add_political_power = 100
	}
}

# Hidden weekly check: has Aragon crushed every rebel government?
country_event = {
	id = greek_uprising.10
	hidden = yes
	is_triggered_only = yes

	immediate = {
		if = {
			limit = {
				NOT = { has_country_flag = SPC_greek_peace }
				NOT = { has_war_with = GRE }
				NOT = { has_war_with = HEL }
			}
			country_event = { id = greek_uprising.3 }
		}
		else_if = {
			limit = { NOT = { has_country_flag = SPC_greek_peace } }
			country_event = { id = greek_uprising.10 days = 7 }
		}
	}

	option = {
		name = greek_uprising.10.a
	}
}
'''
open(J("events/greek_uprising.txt"), "w", encoding="utf-8", newline="\n").write(EV)

# ---------------- OOBs ----------------
def oob(tag, name, units):
    s = ""
    if not tag.endswith("_extra"):
        s = "division_template = {\n\tname = \"%s\"\n\tregiments = {\n" % name
        for x in range(2):
            for y in range(3):
                s += f"\t\tinfantry = {{ x = {x} y = {y} }}\n"
        s += "\t}\n}\n\n"
    s += "units = {\n"
    for i, (label, prov) in enumerate(units, 1):
        s += f"\tdivision = {{\n\t\tname = \"{label}\"\n\t\tlocation = {prov}\n\t\tdivision_template = \"{name}\"\n\t\tstart_experience_factor = 0.5\n\t\tstart_equipment_factor = 1.0\n\t}}\n"
    s += "}\n"
    open(J("history/units", tag + ".txt"), "w", encoding="utf-8", newline="\n").write(s)
oob("GRE_uprising", "Royalist Insurgents", [("Salonika Legion", 11818), ("Macedonian Volunteers", 3526), ("Thessalian Insurgents", 3973), ("Florina Brigade", 9837), ("Volos Defenders", 3914), ("Sacred Band of Macedonia", 6990)])
oob("GRE_uprising_extra", "Royalist Insurgents", [("Chalkidiki Rifles", 9791), ("Olympus Klephts", 863), ("Pindus Mountaineers", 841)])
oob("HEL_uprising", "Republican Militia", [("Athenian Republican Guard", 4109), ("Piraeus Workers' Militia", 976), ("Peloponnesian Militia", 10203), ("Aegean Volunteers", 6550), ("Spartan Republican Brigade", 4078), ("Euboea Militia", 1205)])
oob("GRE_occitan_volunteers", "Occitan Volunteers", [("1st Occitan Volunteer Brigade", 895), ("2nd Occitan Volunteer Brigade", 3936)])
oob("HEL_uprising_extra", "Republican Militia", [("Corinth Militia", 1106), ("Attica Volunteers", 3864)])

# ---------------- localisation ----------------
def q(t): return t.replace('"', '\\"')
L = ["l_english:", " # Greece focus tree"]
for f in F:
    L.append(f' {f["id"]}:0 "{q(f["name"])}"'); L.append(f' {f["id"]}_desc:0 "{q(f["desc"])}"')
for key, _, _, name, desc in IDEAS:
    L.append(f' {key}:0 "{q(name)}"'); L.append(f' {key}_desc:0 "{q(desc)}"')
L += [
 ' SPC_greek_insurgency:0 "Greek Insurgency"',
 ' SPC_greek_insurgency_desc:0 "Greek rebels hold the mountains of Macedonia and the streets of Athens. Every garrison in Greece is under attack."',
 ' GRE_hellenic_alliance:0 "Hellenic Alliance"',
 ' greek_uprising.1.t:0 "Revolt in Greece!"',
 ' greek_uprising.1.d:0 "Signal fires burned on Mount Olympus last night. By morning, royalist insurgents had seized Salonika, Volos and Florina and declared for the King of Greece in Polygyros. In Athens, the Peloponnese and the islands, republican militias have proclaimed a Hellenic Republic. Our garrisons are cut off and under fire across the whole of Greece."',
 ' greek_uprising.1.a:0 "Crush the traitors!"',
 ' greek_uprising.2.t:0 "The Greek Question"',
 ' greek_uprising.2.d:0 "A year of fighting has not broken the Greek rebels. Our garrisons are pinned down, the foreign press reports every burned village, and the generals warn that the army is needed elsewhere. Some ministers now quietly suggest that Greece is not worth the cost: recognise the rebel governments and bring the troops home."',
 ' greek_uprising.2.a:0 "Let Greece go. Aragon has bigger enemies."',
 ' greek_uprising.2.b:0 "Never! Not one village will be surrendered."',
 ' greek_uprising.3.t:0 "The Greek Revolt Crushed"',
 ' greek_uprising.3.d:0 "The last rebel strongholds have fallen. Royalist and republican leaders alike have fled into exile or been captured. Order is restored across Greece, and the army can finally turn its attention back to Occitania."',
 ' greek_uprising.3.a:0 "Aragon endures."',
 ' greek_uprising.5.t:0 "Aragon Recognises Greek Independence"',
 ' greek_uprising.5.d:0 "Unable to break our resistance, the Aragonese government has agreed to a ceasefire and withdrawn its garrisons. For the first time in generations, Greeks govern Greek lands. The question of what kind of Greece it will be can wait until the celebrations are over."',
 ' greek_uprising.5.a:0 "Zito i Ellas!"',
 ' greek_uprising.10.a:0 "OK"',
 ' # Hellenic Republic',
 ' HEL:0 "Hellenic Republic"', ' HEL_ADJ:0 "Hellenic"', ' HEL_DEF:0 "the Hellenic Republic"',
 ' HEL_democratic:0 "Hellenic Republic"', ' HEL_democratic_ADJ:0 "Hellenic"', ' HEL_democratic_DEF:0 "the Hellenic Republic"',
 ' HEL_absolutist:0 "Hellenic State"', ' HEL_absolutist_ADJ:0 "Hellenic"', ' HEL_absolutist_DEF:0 "the Hellenic State"',
 ' HEL_fascism:0 "Hellenic State"', ' HEL_fascism_ADJ:0 "Hellenic"', ' HEL_fascism_DEF:0 "the Hellenic State"',
 ' HEL_neutrality:0 "Hellenic Republic"', ' HEL_neutrality_ADJ:0 "Hellenic"', ' HEL_neutrality_DEF:0 "the Hellenic Republic"',
 ' HEL_democratic_party:0 "Republican Union"', ' HEL_democratic_party_long:0 "Republican Union of Hellas"',
 ' HEL_absolutist_party:0 "Royalists"', ' HEL_fascism_party:0 "National Front"', ' HEL_neutrality_party:0 "Independents"',
 ' HEL_alexandros_karavias:0 "Alexandros Karavias"',
]
open(J("localisation/english/GRE_focus_l_english.yml"), "w", encoding="utf-8-sig", newline="\n").write("\n".join(L) + "\n")
print(len(F), "GRE focuses")
